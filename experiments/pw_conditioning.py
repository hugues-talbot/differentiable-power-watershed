#!/usr/bin/env python3
"""
Conditioning study: finite-p Random Walker versus the Power Watershed limit.

First experiment of pw_unrolling_note.tex (section "Open questions", item 3):
measure the usable range of the exponent p against the CG / unrolled iteration
budget at target resolution.

For every test case (an 8-bit image with two-label seeds) and every p:

  * weights  w_e = exp(-p * c_e),  c_e = ((I_u - I_v)/255)^2 in [0,1], floored at WFLOOR;
    p is the inverse temperature of the note (beta = 1, so "p" is really p*beta);
  * reference solution x^p of  L_U x_U = -B^T x_M  by sparse LU in float64;
  * lambda_min, lambda_max of L_U by ARPACK, hence kappa;
  * CG and Jacobi-preconditioned CG, float32 and float64, on the GPU when
    available: iterations to relative residual 1e-3 and 1e-6, error to x^p after
    K steps for K in KS, and the Lanczos (Ritz) estimate of kappa seen by CG;
  * unrolled Jacobi: error to x^p after K steps;
  * the exact PW limit x^inf (maximum spanning forest + RW on plateaus, using the
    integer costs so that ties are exact), and the distance of x^p to it;
  * the gradient of l = 1/2 ||x_U - t_U||^2 (t = reference labels) with respect
    to the normalised edge costs, and how concentrated it is.

Output: one JSON record per (case, p) appended to --out (JSON lines), plus a
.npz per case with x^inf and x^p at a few p.  No plotting here; see plot_results.py.

Dependencies: numpy, scipy.  Optional: torch (GPU solvers), scikit-image
(natural test images).  Without torch the iterative solvers run in numpy.
"""
import argparse, json, os, sys, time
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from scipy import ndimage
from scipy.linalg import eigvalsh_tridiagonal

WFLOOR64 = 1e-300        # weight floor for the float64 reference and fp64 solvers
WFLOOR32 = 1e-30         # weight floor for the float32 (unrolled-network) solvers
KS = (5, 10, 15, 20, 30, 50, 100, 200)
TOLS = (1e-3, 1e-6)

try:
    import torch
    HAVE_TORCH = True
except ImportError:
    HAVE_TORCH = False


# ----------------------------------------------------------------------------
# graph construction
# ----------------------------------------------------------------------------
def grid_edges(H, W):
    idx = np.arange(H * W).reshape(H, W)
    u = np.concatenate([idx[:, :-1].ravel(), idx[:-1, :].ravel()])
    v = np.concatenate([idx[:, 1:].ravel(), idx[1:, :].ravel()])
    return u, v


def int_costs(img8, u, v):
    d = img8[u].astype(np.int64) - img8[v].astype(np.int64)
    return d * d                      # 0 .. 255^2 = 65025


def normalised_costs(cint, transform):
    """Map integer costs (I_u-I_v)^2 to [0,1]; every choice is monotone, so the
    PW limit is the same for all of them and only the finite-p path changes."""
    if transform == "sq":
        return cint / 65025.0
    if transform == "abs":
        return np.sqrt(cint) / 255.0
    if transform == "rank":                      # dense rank over the distinct values
        vals, inv = np.unique(cint, return_inverse=True)
        return inv / max(vals.size - 1, 1)
    raise ValueError(transform)


def weights(cnorm, p, floor):
    return np.maximum(np.exp(-p * cnorm), floor)


class ScaledLU:
    """LU of the Jacobi-scaled matrix S A S, S = D^-1/2, with iterative refinement.

    Solves A x = b far more reliably than LU of A when the ill-conditioning comes
    from nodes whose every edge is tiny (isolated pixels at large p)."""

    def __init__(self, A):
        self.A = A.tocsr()
        self.s = 1.0 / np.sqrt(A.diagonal())
        self.As = sp.diags(self.s) @ self.A @ sp.diags(self.s)
        self.lu = spla.splu(self.As.tocsc())

    def solve(self, b, refine=2):
        x = self.s * self.lu.solve(self.s * b)
        for _ in range(refine):
            r = b - self.A @ x
            x = x + self.s * self.lu.solve(self.s * r)
        return x


def dirichlet_system(n, u, v, w, seed_mask, seed_val):
    """L_U and b = -B^T x_M for L = D - W with x fixed on seeds."""
    U = np.flatnonzero(~seed_mask)
    pos = -np.ones(n, dtype=np.int64)
    pos[U] = np.arange(U.size)
    nU = U.size
    deg = np.bincount(u, weights=w, minlength=n) + np.bincount(v, weights=w, minlength=n)
    uu, vv = ~seed_mask[u], ~seed_mask[v]
    inner = uu & vv
    rows = np.concatenate([pos[u[inner]], pos[v[inner]], np.arange(nU)])
    cols = np.concatenate([pos[v[inner]], pos[u[inner]], np.arange(nU)])
    vals = np.concatenate([-w[inner], -w[inner], deg[U]])
    A = sp.csr_matrix((vals, (rows, cols)), shape=(nU, nU))
    A.sum_duplicates()
    b = np.zeros(nU)
    m = uu & ~vv                       # u free, v seed
    np.add.at(b, pos[u[m]], w[m] * seed_val[v[m]])
    m = ~uu & vv
    np.add.at(b, pos[v[m]], w[m] * seed_val[u[m]])
    return A, b, U


# ----------------------------------------------------------------------------
# exact Power Watershed limit (q = 2, p -> inf), Couprie et al. 2011, Alg. 1
# ----------------------------------------------------------------------------
def _compress(parent):
    while True:
        pp = parent[parent]
        if np.array_equal(pp, parent):
            return parent
        parent = pp


def _backend(backend):
    """'auto' (default, or $PW_BACKEND): the Numba back end of pw_fast.py when numba is
    installed, else NumPy; 'numpy' / 'numba' force one.  Both give identical results."""
    if backend is None:
        backend = os.environ.get("PW_BACKEND", "auto")
    if backend == "auto":
        try:
            import pw_fast                                   # noqa: F401  (needs numba)
        except ImportError:
            return "numpy"
        return "numba"
    return backend


def power_watershed(n, u, v, cint, seed_mask, seed_val, small=64, backend=None):
    """Plateau-by-plateau MSF with RW solves on ambiguous plateaus.

    Plateaus of at most `small` edges are handled in pure Python (the general
    numpy/scipy path costs ~1 ms per plateau, which dominates when continuous
    costs are quantised: ~40k plateaus of 2-7 edges on a 256^2 image).
    Returns x (float64, length n) and a few statistics.
    backend: see _backend; the Numba version (pw_fast.py) is 10-50x faster and
    bit-for-bit identical (validated in experiments/pwref/validate_fast.py)."""
    if _backend(backend) == "numba":
        from pw_fast import power_watershed_fast
        return power_watershed_fast(n, u, v, cint, seed_mask, seed_val, small)
    parent = np.arange(n)
    val = np.full(n, np.nan)
    val[seed_mask] = seed_val[seed_mask]
    order = np.argsort(cint, kind="stable")
    cs = cint[order]
    bounds = np.flatnonzero(np.diff(cs)) + 1
    starts = np.concatenate([[0], bounds]); ends = np.concatenate([bounds, [cs.size]])
    stats = dict(plateaus=int(starts.size), solved_plateaus=0, solved_nodes=0, max_solve=0)
    sizes = ends - starts

    def find(a):
        r = a
        while parent[r] != r:
            r = parent[r]
        while parent[a] != r:
            parent[a], a = r, parent[a]
        return r

    i = 0
    while i < starts.size:
        s, e = starts[i], ends[i]
        if sizes[i] == 1:
            # fast path: a run of singleton plateaus (continuous costs) processed
            # edge by edge with a scalar union-find; no RW solve can be needed
            j = i
            while j < starts.size and sizes[j] == 1:
                j += 1
            for eidx in order[s:starts[j - 1] + 1]:
                ru, rv = find(u[eidx]), find(v[eidx])
                if ru == rv:
                    continue
                ku, kv = not np.isnan(val[ru]), not np.isnan(val[rv])
                if ku and kv:
                    if val[ru] != val[rv]:
                        continue                      # boundary edge: both sides decided
                    parent[ru] = rv
                elif ku:
                    parent[rv] = ru
                else:
                    parent[ru] = rv                   # rv known or both unknown
            i = j
            continue
        if sizes[i] <= small:
            # small plateau (ties from quantised continuous costs): same logic as the
            # general path below, but on the handful of roots involved, in pure Python
            i += 1
            ed = order[s:e]
            pairs = [(a, b) for a, b in zip((find(x) for x in u[ed]), (find(x) for x in v[ed])) if a != b]
            if not pairs:
                continue
            lp = {}

            def lfind(a):
                while lp.get(a, a) != a:
                    a = lp[a]
                return a
            for a, b in pairs:
                ra, rb = lfind(a), lfind(b)
                if ra != rb:
                    lp[ra] = rb
            comps = {}
            for a, b in pairs:
                comps.setdefault(lfind(a), set()).update((a, b))
            for c, members in comps.items():
                members = sorted(members)
                knowns = {val[r] for r in members if not np.isnan(val[r])}
                if len(knowns) <= 1:
                    rep = members[0]
                    for r in members:
                        parent[r] = rep
                    if knowns:
                        val[rep] = knowns.pop()
                    continue
                unknown = [r for r in members if np.isnan(val[r])]
                if not unknown:
                    continue                          # boundary plateau: all sides decided
                pos = {r: k for k, r in enumerate(unknown)}
                k = len(unknown); A = np.zeros((k, k)); b = np.zeros(k)
                for a, bb in pairs:
                    if lfind(a) != c:
                        continue
                    pa, pb = pos.get(a), pos.get(bb)
                    if pa is not None:
                        A[pa, pa] += 1
                    if pb is not None:
                        A[pb, pb] += 1
                    if pa is not None and pb is not None:
                        A[pa, pb] -= 1; A[pb, pa] -= 1
                    elif pa is not None:
                        b[pa] += val[bb]
                    elif pb is not None:
                        b[pb] += val[a]
                val[unknown] = np.linalg.solve(A, b)
                stats["solved_plateaus"] += 1
                stats["solved_nodes"] += k
                stats["max_solve"] = max(stats["max_solve"], k)
            continue
        i += 1
        parent = _compress(parent)
        eu, ev = parent[u[order[s:e]]], parent[v[order[s:e]]]
        keep = eu != ev
        if not keep.any():
            continue
        eu, ev = eu[keep], ev[keep]
        G = sp.coo_matrix((np.ones(eu.size), (eu, ev)), shape=(n, n))
        ncomp, comp = sp.csgraph.connected_components(G, directed=False)
        roots = np.unique(np.concatenate([eu, ev]))
        croots = comp[roots]
        known = ~np.isnan(val[roots])
        # per component: number of distinct known values (0, 1, or >=2)
        kc, kv = croots[known], val[roots[known]]
        cmin = np.full(ncomp, np.inf); cmax = np.full(ncomp, -np.inf)
        np.minimum.at(cmin, kc, kv); np.maximum.at(cmax, kc, kv)
        ambiguous = cmax > cmin                       # >= 2 distinct known values
        amb_root = ambiguous[croots]
        # --- merge the non-ambiguous components into one node each
        mroots = roots[~amb_root]
        if mroots.size:
            mcomp = croots[~amb_root]
            rep = np.full(ncomp, -1, dtype=np.int64)
            rep[mcomp] = mroots                        # any member as representative
            parent[mroots] = rep[mcomp]
            has = np.isfinite(cmin) & ~ambiguous
            # the representative inherits the (unique) known value
            cval = np.where(has, cmin, np.nan)
            val[rep[np.flatnonzero(has)]] = cval[has]
        # --- solve RW on the ambiguous components (one block system)
        if ambiguous.any():
            sel = ambiguous[comp[eu]]
            au, av = eu[sel], ev[sel]
            aroots = roots[amb_root]
            unknown = aroots[np.isnan(val[aroots])]
            if unknown.size:
                lpos = -np.ones(n, dtype=np.int64); lpos[unknown] = np.arange(unknown.size)
                w1 = np.ones(au.size)
                deg = np.bincount(au, weights=w1, minlength=n) + np.bincount(av, weights=w1, minlength=n)
                fu, fv = lpos[au] >= 0, lpos[av] >= 0
                inner = fu & fv
                k = unknown.size
                rows = np.concatenate([lpos[au[inner]], lpos[av[inner]], np.arange(k)])
                cols = np.concatenate([lpos[av[inner]], lpos[au[inner]], np.arange(k)])
                vals = np.concatenate([-w1[inner], -w1[inner], deg[unknown]])
                A = sp.csc_matrix((vals, (rows, cols)), shape=(k, k)); A.sum_duplicates()
                b = np.zeros(k)
                m = fu & ~fv; np.add.at(b, lpos[au[m]], val[av[m]])
                m = ~fu & fv; np.add.at(b, lpos[av[m]], val[au[m]])
                val[unknown] = spla.splu(A).solve(b)
                stats["solved_plateaus"] += 1
                stats["solved_nodes"] += int(k)
                stats["max_solve"] = max(stats["max_solve"], int(k))
    parent = _compress(parent)
    x = val[parent]
    stats["unassigned"] = int(np.isnan(x).sum())
    return x, stats


# ----------------------------------------------------------------------------
# iterative solvers (numpy or torch, column vectors)
# ----------------------------------------------------------------------------
class Backend:
    def __init__(self, A, b, xref, dtype, device):
        self.n = b.size
        if HAVE_TORCH:
            td = torch.float32 if dtype == "f32" else torch.float64
            Ac = A.tocsr().astype(np.float64)
            self.A = torch.sparse_csr_tensor(
                torch.from_numpy(Ac.indptr.astype(np.int64)),
                torch.from_numpy(Ac.indices.astype(np.int64)),
                torch.from_numpy(Ac.data).to(td), size=Ac.shape).to(device)
            self.d = torch.from_numpy(A.diagonal()).to(td).to(device).reshape(-1, 1)
            self.b = torch.from_numpy(b).to(td).to(device).reshape(-1, 1)
            self.xref = torch.from_numpy(xref).to(torch.float64).to(device).reshape(-1, 1)
            self.zeros = lambda: torch.zeros_like(self.b)
            self.torch = True
        else:
            nd = np.float32 if dtype == "f32" else np.float64
            self.A = A.tocsr().astype(nd)
            self.d = A.diagonal().astype(nd).reshape(-1, 1)
            self.b = b.astype(nd).reshape(-1, 1)
            self.xref = xref.reshape(-1, 1)
            self.zeros = lambda: np.zeros_like(self.b)
            self.torch = False

    def mv(self, x):
        return self.A @ x

    def dot(self, x, y):
        return float((x * y).sum())

    def err(self, x):
        e = (x.double() if self.torch else x.astype(np.float64)) - self.xref
        linf = float(abs(e).max())
        lab = float(((x > 0.5) != (self.xref > 0.5)).double().mean()) if self.torch \
            else float(((x > 0.5) != (self.xref > 0.5)).mean())
        return linf, lab

    def sync(self):
        if self.torch and self.A.device.type == "cuda":
            torch.cuda.synchronize()


def _bookkeep(rec, k, rel, x, be, bnorm, tols_hit):
    for t in TOLS:
        if t not in tols_hit and rel <= t:
            tols_hit[t] = k
            linf, lab = be.err(x)
            rec[f"it_{t:g}"] = k; rec[f"err_at_{t:g}"] = linf; rec[f"lab_at_{t:g}"] = lab
    if k in KS:
        linf, lab = be.err(x)
        rec[f"err_K{k}"] = linf; rec[f"lab_K{k}"] = lab


def run_cg(be, maxit, precond=False):
    rec = {}
    x = be.zeros(); r = be.b.clone() if be.torch else be.b.copy()
    bnorm = np.sqrt(be.dot(r, r))
    z = r / be.d if precond else r
    pvec = z.clone() if be.torch else z.copy()
    rz = be.dot(r, z)
    alphas, betas = [], []
    tols_hit = {}
    be.sync(); t0 = time.time()
    k = 0; rel = 1.0
    while k < maxit:
        Ap = be.mv(pvec)
        pAp = be.dot(pvec, Ap)
        if not np.isfinite(pAp) or pAp <= 0:
            rec["breakdown"] = k; break
        alpha = rz / pAp
        x = x + alpha * pvec
        r = r - alpha * Ap
        k += 1
        rel = np.sqrt(be.dot(r, r)) / bnorm
        _bookkeep(rec, k, rel, x, be, bnorm, tols_hit)
        z = r / be.d if precond else r
        rz_new = be.dot(r, z)
        beta = rz_new / rz
        alphas.append(alpha); betas.append(beta)
        rz = rz_new
        pvec = z + beta * pvec
        if all(t in tols_hit for t in TOLS) and k >= max(KS):
            break
    be.sync(); rec["time"] = time.time() - t0; rec["iters_run"] = k
    rec["final_rel"] = float(rel)
    # Lanczos / Ritz estimate of the condition number of (M^-1) A seen by CG
    m = len(alphas)
    if m >= 2:
        a = np.array(alphas); bb = np.array(betas)
        diag = 1.0 / a
        diag[1:] += bb[:-1] / a[:-1]
        off = np.sqrt(np.maximum(bb[:-1], 0)) / a[:-1]
        try:
            ev = eigvalsh_tridiagonal(diag, off)
            ev = ev[ev > 0]
            rec["ritz_min"] = float(ev.min()); rec["ritz_max"] = float(ev.max())
            rec["ritz_kappa"] = float(ev.max() / ev.min())
        except Exception as ex:                        # noqa
            rec["ritz_error"] = str(ex)
    return rec


def run_jacobi(be, maxit):
    rec = {}
    x = be.zeros()
    bnorm = np.sqrt(be.dot(be.b, be.b))
    tols_hit = {}
    be.sync(); t0 = time.time()
    for k in range(1, maxit + 1):
        r = be.b - be.mv(x)
        x = x + r / be.d
        rel = np.sqrt(be.dot(r, r)) / bnorm
        _bookkeep(rec, k, rel, x, be, bnorm, tols_hit)
    be.sync(); rec["time"] = time.time() - t0; rec["iters_run"] = maxit
    rec["final_rel"] = float(rel)
    return rec


# ----------------------------------------------------------------------------
# spectrum
# ----------------------------------------------------------------------------
def _eig_pair(A, solve, maxiter, tag):
    out = {}
    try:
        out["lmax" + tag] = float(spla.eigsh(A, k=1, which="LA", maxiter=maxiter, tol=1e-6,
                                             return_eigenvectors=False)[0])
    except Exception as ex:                            # noqa
        out["lmax_error" + tag] = str(ex)[:120]
    try:
        op = spla.LinearOperator(A.shape, matvec=solve, dtype=np.float64)
        out["lmin" + tag] = float(spla.eigsh(A, k=1, sigma=0, which="LM", OPinv=op, maxiter=maxiter,
                                             tol=1e-6, return_eigenvectors=False)[0])
    except Exception as ex:                            # noqa
        out["lmin_error" + tag] = str(ex)[:120]
    if "lmax" + tag in out and "lmin" + tag in out and out["lmin" + tag] > 0:
        out["kappa" + tag] = out["lmax" + tag] / out["lmin" + tag]
    return out


def extreme_eigs(slu, maxiter=3000):
    """kappa of A (what plain CG sees) and of S A S (what Jacobi-PCG sees)."""
    out = _eig_pair(slu.A, lambda r: slu.solve(r, refine=1), maxiter, "")
    out.update(_eig_pair(slu.As, lambda r: slu.lu.solve(r), maxiter, "_scaled"))
    return out


# ----------------------------------------------------------------------------
# test cases
# ----------------------------------------------------------------------------
def disc(H, W, cy, cx, r):
    yy, xx = np.mgrid[:H, :W]
    return (yy - cy) ** 2 + (xx - cx) ** 2 <= r * r


def synth_image(res, sigma, rng):
    H = W = res
    gt = disc(H, W, 0.45 * H, 0.35 * W, 0.22 * res)
    gt |= (np.mgrid[:H, :W][0] > 0.55 * H) & (np.mgrid[:H, :W][0] < 0.85 * H) \
        & (np.mgrid[:H, :W][1] > 0.55 * W) & (np.mgrid[:H, :W][1] < 0.9 * W)
    gt |= disc(H, W, 0.25 * H, 0.75 * W, 0.08 * res)
    illum = 0.1 * np.linspace(-1, 1, W)[None, :] + 0.05 * np.linspace(-1, 1, H)[:, None]
    img = np.where(gt, 0.65, 0.35) + illum + sigma * rng.standard_normal((H, W))
    img8 = np.clip(np.round(img * 255), 0, 255).astype(np.uint8)
    return img8, gt


def natural_images(res):
    try:
        from skimage import data, color, transform
    except ImportError:
        print("scikit-image not available: natural images skipped", file=sys.stderr)
        return {}
    out = {}
    for name in ("camera", "astronaut"):
        im = getattr(data, name)()
        if im.ndim == 3:
            im = color.rgb2gray(im)
        else:
            im = im / 255.0
        if im.shape != (res, res):
            im = transform.resize(im, (res, res), anti_aliasing=True)
        out[name] = np.clip(np.round(im * 255), 0, 255).astype(np.uint8)
    return out


def otsu(img8):
    hist = np.bincount(img8.ravel(), minlength=256).astype(np.float64)
    p = hist / hist.sum(); lv = np.arange(256)
    w0 = np.cumsum(p); m0 = np.cumsum(p * lv)
    mt = m0[-1]
    var = (mt * w0 - m0) ** 2 / np.maximum(w0 * (1 - w0), 1e-12)
    return int(np.argmax(var))


def erode_seeds(labels, r):
    se = disc(2 * r + 1, 2 * r + 1, r, r, r)
    fg = ndimage.binary_erosion(labels, se, border_value=0)
    bg = ndimage.binary_erosion(~labels, se, border_value=0)
    mask = fg | bg
    val = np.where(fg, 1.0, 0.0)
    return mask, val


def scribble_seeds(labels, rng, k=3, r=4):
    """k small discs inside each region: the global (sparse-seed) regime."""
    H, W = labels.shape
    mask = np.zeros_like(labels); val = np.zeros(labels.shape)
    for lab in (True, False):
        reg = ndimage.binary_erosion(labels == lab, disc(2 * r + 3, 2 * r + 3, r + 1, r + 1, r + 1))
        ys, xs = np.nonzero(reg)
        pick = rng.choice(ys.size, size=min(k, ys.size), replace=False)
        for i in pick:
            d = disc(H, W, ys[i], xs[i], r)
            mask |= d; val[d] = float(lab)
    return mask, val


def make_cases(res, want, rng):
    cases = []
    for sigma in (0.05, 0.1):
        img8, gt = synth_image(res, sigma, rng)
        for r in (5, 30):
            m, v = erode_seeds(gt, r)
            cases.append(dict(name=f"synth{res}_s{sigma:g}_r{r}", img8=img8, labels=gt, seed_mask=m, seed_val=v))
        m, v = scribble_seeds(gt, rng)
        cases.append(dict(name=f"synth{res}_s{sigma:g}_scribble", img8=img8, labels=gt, seed_mask=m, seed_val=v))
    for name, img8 in natural_images(res).items():
        sm = ndimage.gaussian_filter(img8.astype(np.float64), 2.0)
        lab = sm > otsu(np.clip(np.round(sm), 0, 255).astype(np.uint8))
        for r in (5, 30):
            m, v = erode_seeds(lab, r)
            if m.sum() == 0 or v[m].min() == v[m].max():
                continue
            cases.append(dict(name=f"{name}{res}_r{r}", img8=img8, labels=lab, seed_mask=m, seed_val=v))
    if want:
        cases = [c for c in cases if any(w in c["name"] for w in want)]
    ok = []
    for c in cases:
        sv = c["seed_val"][c["seed_mask"]]
        if sv.size == 0 or sv.min() == sv.max():
            print(f"skipping {c['name']}: seeds do not carry both labels", file=sys.stderr)
            continue
        ok.append(c)
    return ok


# ----------------------------------------------------------------------------
# main loop
# ----------------------------------------------------------------------------
def run_case(case, ps, args, device):
    img8 = case["img8"]; H, W = img8.shape; n = H * W
    u, v = grid_edges(H, W)
    cint = int_costs(img8.ravel(), u, v)
    cnorm = normalised_costs(cint, args.cost_transform)
    seed_mask = case["seed_mask"].ravel(); seed_val = case["seed_val"].ravel()
    labels = case["labels"].ravel().astype(np.float64)
    U = np.flatnonzero(~seed_mask)
    base = dict(case=case["name"], cost_transform=args.cost_transform, H=H, W=W, n=int(n), nU=int(U.size),
                nseeds=int(seed_mask.sum()), nedges=int(u.size))
    print(f"[{case['name']}] n={n} nU={U.size} edges={u.size}", flush=True)

    t0 = time.time()
    xinf, pwstats = power_watershed(n, u, v, cint, seed_mask, seed_val)
    t_pw = time.time() - t0
    base.update(pw=pwstats, t_pw=t_pw)
    lab_inf = (xinf > 0.5)
    print(f"  PW limit in {t_pw:.1f}s: {pwstats}; label err vs ref {float((lab_inf != (labels > 0.5))[U].mean()):.4f}",
          flush=True)
    saved = dict(x_inf=xinf.astype(np.float32).reshape(H, W), img8=img8,
                 seed_mask=case["seed_mask"], labels=case["labels"])

    for p in ps:
        rec = dict(base, p=p)
        t0 = time.time()
        w = weights(cnorm, p, WFLOOR64)
        A, b, _ = dirichlet_system(n, u, v, w, seed_mask, seed_val)
        w32 = weights(cnorm, p, WFLOOR32)
        A32, b32, _ = dirichlet_system(n, u, v, w32, seed_mask, seed_val)
        rec["wmin"] = float(w.min()); rec["wfloor_frac64"] = float((w <= WFLOOR64).mean())
        rec["wfloor_frac32"] = float((w32 <= WFLOOR32).mean())
        try:
            lu = ScaledLU(A)
        except RuntimeError as ex:                      # exactly singular at extreme p
            print(f"  p={p:<6g} skipped: {ex}", flush=True)
            continue
        xU = lu.solve(b)
        xp = seed_val.copy(); xp[U] = xU
        res = np.linalg.norm(A @ xU - b) / np.linalg.norm(b)
        rec["t_lu"] = time.time() - t0; rec["lu_rel_res"] = float(res)
        rec["ref_ok"] = bool(res < 1e-8 and xU.min() > -1e-6 and xU.max() < 1 + 1e-6)
        # distance to the PW limit
        d = xp[U] - xinf[U]
        rec["dist_inf_linf"] = float(np.abs(d).max()); rec["dist_inf_rms"] = float(np.sqrt((d * d).mean()))
        rec["dist_inf_lab"] = float(((xp[U] > 0.5) != lab_inf[U]).mean())
        rec["lab_err_ref"] = float(((xp[U] > 0.5) != (labels[U] > 0.5)).mean())
        # spectrum
        if not args.no_eig:
            t1 = time.time(); rec["eig"] = extreme_eigs(lu); rec["t_eig"] = time.time() - t1
        # gradient of 1/2 ||x_U - t_U||^2 w.r.t. normalised costs
        t1 = time.time()
        lam = np.zeros(n); lam[U] = lu.solve(xU - labels[U])
        g = p * w * (xp[u] - xp[v]) * (lam[u] - lam[v])
        ag = np.abs(g); tot = ag.sum()
        if tot > 0:
            srt = np.sort(ag)[::-1]; cum = np.cumsum(srt) / tot
            rec["grad"] = dict(l2=float(np.linalg.norm(g)), linf=float(ag.max()),
                               n90=int(np.searchsorted(cum, 0.9) + 1), n99=int(np.searchsorted(cum, 0.99) + 1),
                               nnz=int((ag > 1e-12 * ag.max()).sum()), loss=float(0.5 * ((xU - labels[U]) ** 2).sum()))
        rec["t_grad"] = time.time() - t1
        # iterative solvers
        for dtype in ("f32", "f64"):
            be = Backend(A32 if dtype == "f32" else A, b32 if dtype == "f32" else b, xU, dtype, device)
            rec[f"cg_{dtype}"] = run_cg(be, args.max_cg)
            rec[f"pcg_{dtype}"] = run_cg(be, args.max_cg, precond=True)
            if dtype == "f32":
                rec["jacobi_f32"] = run_jacobi(be, max(KS))
            del be
        rec["t_total"] = time.time() - t0
        cg = rec["cg_f32"]; pcg = rec["pcg_f64"]
        kap = rec.get("eig", {}).get("kappa", float("nan"))
        print(f"  p={p:<6g} {'ok ' if rec['ref_ok'] else 'BAD'} kappa={kap:.3g} ritz={cg.get('ritz_kappa', float('nan')):.3g} "
              f"cg32 it(1e-3)={cg.get('it_0.001', '-')} it(1e-6)={cg.get('it_1e-06', '-')} "
              f"pcg64 it(1e-6)={pcg.get('it_1e-06', '-')} jac K50 err={rec['jacobi_f32'].get('err_K50', float('nan')):.3g} "
              f"dist_inf lab={rec['dist_inf_lab']:.4f} linf={rec['dist_inf_linf']:.3g} lab_err={rec['lab_err_ref']:.4f} "
              f"grad n90={rec.get('grad', {}).get('n90', '-')} [{rec['t_total']:.1f}s]", flush=True)
        with open(args.out, "a") as f:
            f.write(json.dumps(rec) + "\n")
        if p in (1, 10, 100, 1000):
            saved[f"x_p{p:g}"] = xp.astype(np.float32).reshape(H, W)
    np.savez_compressed(os.path.join(args.outdir, f"{case['name']}{args.tag}.npz"), **saved)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", type=int, default=512)
    ap.add_argument("--ps", type=str, default="1,2,5,10,20,50,100,200,500,1000,2000")
    ap.add_argument("--cases", type=str, default="", help="comma-separated substrings to select cases")
    ap.add_argument("--outdir", type=str, default="results")
    ap.add_argument("--max-cg", type=int, default=20000)
    ap.add_argument("--no-eig", action="store_true")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--cost-transform", choices=("sq", "abs", "rank"), default="sq",
                    help="map from (I_u-I_v)^2 to the normalised cost c in [0,1]")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    args.tag = "" if args.cost_transform == "sq" else f"_{args.cost_transform}"
    args.out = os.path.join(args.outdir, f"conditioning_{args.res}{args.tag}.jsonl")
    ps = [float(s) for s in args.ps.split(",")]
    ps = [int(p) if p == int(p) else p for p in ps]
    device = "cpu"
    if HAVE_TORCH and torch.cuda.is_available():
        device = "cuda"
    print(f"torch={HAVE_TORCH} device={device} res={args.res} cost={args.cost_transform} ps={ps}", flush=True)
    rng = np.random.default_rng(args.seed)
    want = [s for s in args.cases.split(",") if s]
    for case in make_cases(args.res, want, rng):
        run_case(case, ps, args, device)


if __name__ == "__main__":
    main()
