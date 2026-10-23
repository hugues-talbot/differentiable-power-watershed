#!/usr/bin/env python3
"""
A differentiable Random Walker / Power Watershed layer on image grids.

Energy (prior-augmented Random Walker, Grady 2005, with everything raised to p):

    E(x) = sum_e w_e (x_u - x_v)^2 + sum_i a1_i (x_i - 1)^2 + sum_i a0_i x_i^2

with  w_e = exp(-p c_e),  a1_i = exp(-p c1_i),  a0_i = exp(-p c0_i),  costs >= 0.
Stationarity gives the SPD system

    (L(w) + diag(a0 + a1)) x = a1 .

x_i is the probability that a random 2-forest at inverse temperature p connects
pixel i to the foreground label; p -> inf gives the Power Watershed on the grid
augmented with two virtual label nodes (edge i--fg with cost c1_i, i--bg with c0_i).

Everything is written with dense shifted-grid tensors (B,1,H,W), so it is
batched, runs on the GPU, and autograd works through the unrolled solvers.
Two ways to differentiate:

  * unrolled:  x = pcg(..., K) with a fixed number of Jacobi-PCG steps, autograd
    through the iterations (what one deploys if the truncated solver is the layer);
  * implicit:  ImplicitRW.apply(...) solves to tolerance in the forward pass and
    solves one adjoint system in the backward pass (memory independent of depth).

`pw_limit_numpy` evaluates the exact p -> inf limit for one image (numpy, CPU).
"""
import numpy as np
import torch
import torch.nn.functional as F

# ----------------------------------------------------------------------------
# grid operators
# ----------------------------------------------------------------------------
def hdiff(x):                       # (B,1,H,W) -> (B,1,H,W-1): x[j+1]-x[j]
    return x[..., :, 1:] - x[..., :, :-1]


def vdiff(x):                       # (B,1,H,W) -> (B,1,H-1,W)
    return x[..., 1:, :] - x[..., :-1, :]


def hdiv(f):                        # adjoint of hdiff: (B,1,H,W-1) -> (B,1,H,W)
    return F.pad(f, (1, 0)) - F.pad(f, (0, 1))


def vdiv(f):
    return F.pad(f, (0, 0, 1, 0)) - F.pad(f, (0, 0, 0, 1))


def laplacian(wh, wv, x):
    """L(w) x for horizontal weights wh (B,1,H,W-1) and vertical wv (B,1,H-1,W)."""
    return hdiv(wh * hdiff(x)) + vdiv(wv * vdiff(x))


def degree(wh, wv):
    return F.pad(wh, (1, 0)) + F.pad(wh, (0, 1)) + F.pad(wv, (0, 0, 1, 0)) + F.pad(wv, (0, 0, 0, 1))


class System:
    """A x = b with A = L(w) + diag(a0 + a1), b = a1."""

    def __init__(self, wh, wv, a0, a1):
        self.wh, self.wv, self.a = wh, wv, a0 + a1
        self.b = a1
        self.diag = degree(wh, wv) + self.a

    def matvec(self, x):
        return laplacian(self.wh, self.wv, x) + self.a * x


def bdot(x, y):
    return (x * y).sum(dim=(1, 2, 3), keepdim=True)


def pcg(sysm, K, x0=None, tol=None, record=None, stats=None):
    """Batched Jacobi-preconditioned CG, K iterations (or until every batch
    element has relative residual <= tol).  Differentiable through the loop."""
    b = sysm.b
    x = torch.zeros_like(b) if x0 is None else x0
    r = b - sysm.matvec(x) if x0 is not None else b.clone()
    Minv = 1.0 / sysm.diag
    z = Minv * r
    p = z.clone()
    rz = bdot(r, z)
    bnorm = bdot(b, b).sqrt().clamp_min(1e-30)
    for k in range(K):
        Ap = sysm.matvec(p)
        alpha = rz / bdot(p, Ap).clamp_min(1e-30)
        x = x + alpha * p
        r = r - alpha * Ap
        if record is not None:
            record.append(x)
        if tol is not None and (bdot(r, r).sqrt() / bnorm).max() <= tol:
            break
        z = Minv * r
        rz_new = bdot(r, z)
        p = z + (rz_new / rz.clamp_min(1e-30)) * p
        rz = rz_new
    if stats is not None:
        stats["iters"] = stats.get("iters", 0) + k + 1
        stats["last_iters"] = k + 1
        stats["final_rel"] = float((bdot(r, r).sqrt() / bnorm).max())
    return x


def jacobi(sysm, K, record=None):
    x = torch.zeros_like(sysm.b)
    Dinv = 1.0 / sysm.diag
    for _ in range(K):
        x = x + Dinv * (sysm.b - sysm.matvec(x))
        if record is not None:
            record.append(x)
    return x


# ----------------------------------------------------------------------------
# implicit differentiation
# ----------------------------------------------------------------------------
class ImplicitRW(torch.autograd.Function):
    """x = argmin E; forward solves to tolerance, backward solves one adjoint system.

    d l / d w_e  = -(x_u - x_v)(lam_u - lam_v)
    d l / d a1_i = lam_i (1 - x_i)
    d l / d a0_i = -lam_i x_i           with  A lam = d l / d x.
    """

    @staticmethod
    def forward(ctx, wh, wv, a0, a1, maxit, tol, stats=None):
        with torch.no_grad():
            sysm = System(wh, wv, a0, a1)
            x = pcg(sysm, maxit, tol=tol, stats=stats)
        ctx.save_for_backward(wh, wv, a0, a1, x)
        ctx.maxit, ctx.tol = maxit, tol
        return x

    @staticmethod
    def backward(ctx, g):
        wh, wv, a0, a1, x = ctx.saved_tensors
        with torch.no_grad():
            sysm = System(wh, wv, a0, a1)
            sysm.b = g
            lam = pcg(sysm, ctx.maxit, tol=ctx.tol)
            gwh = -hdiff(x) * hdiff(lam)
            gwv = -vdiff(x) * vdiff(lam)
            ga1 = lam * (1 - x)
            ga0 = -lam * x
        return gwh, gwv, ga0, ga1, None, None, None


# ----------------------------------------------------------------------------
# the layer
# ----------------------------------------------------------------------------
def reweight(d, eps, kind):
    """Multiplier on an edge weight given the jump d of the current solution across it.

    "cauchy": eps^2 / (eps^2 + d^2)   (Geman-McClure / smoothed-l0 half-quadratic weight)
    "l1":     1 / (1 + |d| / eps)      (smoothed-l1 / IRLS weight)
    Both equal 1 for d = 0 and are bounded below by about (eps/|d|)^2 resp. eps/|d|."""
    if kind == "cauchy":
        return eps * eps / (eps * eps + d * d)
    if kind == "l1":
        return 1.0 / (1.0 + d.abs() / eps)
    raise ValueError(kind)


class RWLayer(torch.nn.Module):
    """Costs in, probabilities out.

    ce = (ch, cv): edge costs >= 0 on horizontal / vertical edges;
    c1, c0: unary costs >= 0 (foreground / background);  p: inverse temperature.
    mode: "unrolled"   (K Jacobi-PCG steps, autograd through them),
          "jacobi"     (K Jacobi steps),
          "implicit"   (solve to tol, adjoint backward),
          "reweighted" (fixed-point reweighting: solve at the base weights exp(-p c),
                        then `outer` times multiply each edge weight by
                        reweight(jump of the current solution, eps, kind) and solve
                        again; inner solves implicit, autograd through the outer loop.
                        With reweight_unaries the unary weights, which are edges to the
                        two label nodes of the augmented graph, are reweighted by the
                        jump to their label, (x - 1) resp. x, in the same way).
    `stats` (a dict) collects inner-solver iteration counts when given.
    """

    def __init__(self, mode="unrolled", K=20, tol=1e-6, maxit=2000, wfloor=None,
                 outer=5, eps=0.1, kind="cauchy", eps_schedule=None, reweight_unaries=True):
        super().__init__()
        self.mode, self.K, self.tol, self.maxit, self.wfloor = mode, K, tol, maxit, wfloor
        self.outer, self.eps, self.kind, self.eps_schedule = outer, eps, kind, eps_schedule
        self.reweight_unaries = reweight_unaries

    def forward(self, ch, cv, c1, c0, p, stats=None, record=None):
        floor = self.wfloor or (1e-300 if ch.dtype == torch.float64 else 1e-30)
        wh = torch.exp(-p * ch).clamp_min(floor)
        wv = torch.exp(-p * cv).clamp_min(floor)
        a1 = torch.exp(-p * c1).clamp_min(floor)
        a0 = torch.exp(-p * c0).clamp_min(floor)
        if self.mode == "implicit":
            return ImplicitRW.apply(wh, wv, a0, a1, self.maxit, self.tol, stats)
        if self.mode == "reweighted":
            x = ImplicitRW.apply(wh, wv, a0, a1, self.maxit, self.tol, stats)
            if stats is not None:
                stats.setdefault("per_solve", []).append(stats["last_iters"])
            if record is not None:
                record.append(x)
            for k in range(self.outer):
                eps = self.eps_schedule[k] if self.eps_schedule else self.eps
                whk = (wh * reweight(hdiff(x), eps, self.kind)).clamp_min(floor)
                wvk = (wv * reweight(vdiff(x), eps, self.kind)).clamp_min(floor)
                if self.reweight_unaries:
                    a1k = (a1 * reweight(x - 1.0, eps, self.kind)).clamp_min(floor)
                    a0k = (a0 * reweight(x, eps, self.kind)).clamp_min(floor)
                else:
                    a1k, a0k = a1, a0
                x = ImplicitRW.apply(whk, wvk, a0k, a1k, self.maxit, self.tol, stats)
                if stats is not None:
                    stats.setdefault("per_solve", []).append(stats["last_iters"])
                    stats["wmin"] = float(min(whk.min(), wvk.min()))
                if record is not None:
                    record.append(x)
            return x
        sysm = System(wh, wv, a0, a1)
        if self.mode == "jacobi":
            return jacobi(sysm, self.K)
        return pcg(sysm, self.K)


def unary_costs_from_prob(s, eps=1e-6, cmax=None):
    """Soft foreground probability s in (0,1) -> costs (c1, c0) = (-log s, -log(1-s))."""
    s = s.clamp(eps, 1 - eps)
    c1, c0 = -torch.log(s), -torch.log1p(-s)
    if cmax is not None:
        c1, c0 = c1.clamp_max(cmax), c0.clamp_max(cmax)
    return c1, c0


# ----------------------------------------------------------------------------
# exact limit (numpy)
# ----------------------------------------------------------------------------
def pw_limit_numpy(ch, cv, c1, c0, quant=2 ** 20):
    """Power Watershed (p -> inf) on the grid augmented with two label nodes.

    ch (H,W-1), cv (H-1,W), c1, c0 (H,W): numpy float costs.  Costs are
    quantised to 1/quant so that exact ties are honoured."""
    from pw_conditioning import power_watershed
    H, W = c1.shape
    n = H * W
    idx = np.arange(n).reshape(H, W)
    u = np.concatenate([idx[:, :-1].ravel(), idx[:-1, :].ravel(), idx.ravel(), idx.ravel()])
    v = np.concatenate([idx[:, 1:].ravel(), idx[1:, :].ravel(), np.full(n, n), np.full(n, n + 1)])
    c = np.concatenate([ch.ravel(), cv.ravel(), c1.ravel(), c0.ravel()])
    cint = np.round(c * quant).astype(np.int64)
    seed_mask = np.zeros(n + 2, dtype=bool); seed_mask[n:] = True
    seed_val = np.zeros(n + 2); seed_val[n] = 1.0
    x, stats = power_watershed(n + 2, u, v, cint, seed_mask, seed_val)
    return x[:n].reshape(H, W), stats


# ----------------------------------------------------------------------------
# multi-marker layer: the instances are the labels
# ----------------------------------------------------------------------------
# For K+1 labels (0 = background) with per-label attachment weights a_k >= 0 the
# energy  sum_k [ sum_e w_e (x_k,u - x_k,v)^2 + sum_i a_k,i (x_k,i - 1)^2 + sum_i (sum_{j!=k} a_j,i) x_k,i^2 ]
# is minimised by  (L(w) + diag(sum_j a_j)) x_k = a_k  for every k: one matrix per image,
# one right-hand side per label, and  sum_k x_k = 1  because L 1 = 0.  The K+1 systems of
# every image of a batch are stacked along the batch axis (M = sum_b (K_b + 1) systems,
# `group` (M,) says which image each belongs to), so the PCG above runs unchanged on
# (M,1,H,W) tensors with the weights gathered per image.  The number of labels is thus
# free per image, as it is for the Power Watershed, and the solve is affine in K.
class ImplicitRWMulti(torch.autograd.Function):
    """x (M,1,H,W) = the stacked solutions; a (M,1,H,W) the label attachments (>= 0, zero
    outside the markers of nucleus labels; the background label carries exp(-p c0)
    everywhere); wh, wv (B,1,...) the shared edge weights; group (M,) long.

    Adjoint, with A lam_k = dl/dx_k for every k:
      dl/dw_e   = -sum_k (x_k,u - x_k,v)(lam_k,u - lam_k,v)          (summed over the image's labels)
      dl/da_k,i = lam_k,i - sum_j lam_j,i x_j,i                        (own right-hand side, shared diagonal)
    which reduces to ImplicitRW's formulas for two labels with the loss on x_1 only."""

    @staticmethod
    def forward(ctx, wh, wv, a, group, B, maxit, tol, stats=None):
        with torch.no_grad():
            asum = torch.zeros(B, *a.shape[1:], dtype=a.dtype, device=a.device).index_add_(0, group, a)
            sysm = System(wh[group], wv[group], asum[group] - a, a)
            sysm.a, sysm.diag = asum[group], degree(sysm.wh, sysm.wv) + asum[group]
            x = pcg(sysm, maxit, tol=tol, stats=stats)
        ctx.save_for_backward(wh, wv, a, group, x)
        ctx.B, ctx.maxit, ctx.tol = B, maxit, tol
        return x

    @staticmethod
    def backward(ctx, g):
        wh, wv, a, group, x = ctx.saved_tensors
        B = ctx.B
        with torch.no_grad():
            asum = torch.zeros(B, *a.shape[1:], dtype=a.dtype, device=a.device).index_add_(0, group, a)
            sysm = System(wh[group], wv[group], asum[group] - a, a)
            sysm.a, sysm.diag = asum[group], degree(sysm.wh, sysm.wv) + asum[group]
            sysm.b = g
            lam = pcg(sysm, ctx.maxit, tol=ctx.tol)
            gwh = torch.zeros_like(wh).index_add_(0, group, -hdiff(x) * hdiff(lam))
            gwv = torch.zeros_like(wv).index_add_(0, group, -vdiff(x) * vdiff(lam))
            lx = torch.zeros(B, *a.shape[1:], dtype=a.dtype, device=a.device).index_add_(0, group, lam * x)
            ga = lam - lx[group]
        return gwh, gwv, ga, None, None, None, None, None


def label_systems(lab, core=None):
    """Label maps -> the stacked marker indicators of a batch.

    lab (B,1,H,W) integer label maps (0 = background, any positive ids); core (B,1,H,W)
    bool or None: the pixels that act as markers (e.g. the eroded instances); None means
    the whole label.  Returns dict with
      mk      (M,1,H,W) float: 1 on the marker pixels of each label system (the background
              system of every image is all ones: its attachment is the background unary),
      group   (M,) long image index of every system,
      is_bg   (M,) bool,
      offsets list of the first system index of every image,
      K       list of the number of nucleus labels per image,
      target  (B,H,W) long: lab relabelled to 0..K_b, the label index of every pixel.
    Labels with no marker pixel keep their system (its attachment is zero: x_k = 0)."""
    B, _, H, W = lab.shape
    mks, groups, is_bg, offsets, Ks, targets = [], [], [], [], [], []
    off = 0
    for b in range(B):
        lb = lab[b, 0].long()
        uniq, inv = torch.unique(lb, return_inverse=True)
        if uniq[0] != 0:                                       # no background pixel: keep slot 0 for it
            inv = inv + 1; uniq = torch.cat([uniq.new_zeros(1), uniq])
        K = int(uniq.numel()) - 1
        oh = F.one_hot(inv, K + 1).permute(2, 0, 1).to(torch.float32)     # (K+1,H,W)
        if core is not None:
            oh[1:] = oh[1:] * core[b, 0].to(torch.float32)[None]
        oh[0] = 1.0
        mks.append(oh[:, None])
        groups.append(torch.full((K + 1,), b, dtype=torch.long, device=lab.device))
        flag = torch.zeros(K + 1, dtype=torch.bool, device=lab.device); flag[0] = True
        is_bg.append(flag); offsets.append(off); Ks.append(K); targets.append(inv)
        off += K + 1
    return dict(mk=torch.cat(mks), group=torch.cat(groups), is_bg=torch.cat(is_bg),
                offsets=offsets, K=Ks, target=torch.stack(targets))


class MultiRWLayer(torch.nn.Module):
    """Costs in, label probabilities out, for a batch with a variable number of markers.

    forward(ch, cv, c0, c1, sysd, p): edge costs (B,1,H,W-1), (B,1,H-1,W); c0 the background
    cost (-log(1-s)), c1 the marker-attachment cost at marker pixels (-log s); sysd from
    label_systems.  Attachments  a = mk * exp(-p c)  with c = c0 on the background system and
    c1 on the nucleus systems; the solve is implicit (ImplicitRWMulti).  Returns x (M,1,H,W)."""

    def __init__(self, tol=1e-4, maxit=100, wfloor=None):
        super().__init__()
        self.tol, self.maxit, self.wfloor = tol, maxit, wfloor

    def forward(self, ch, cv, c0, c1, sysd, p, stats=None):
        floor = self.wfloor or (1e-300 if ch.dtype == torch.float64 else 1e-30)
        wh = torch.exp(-p * ch).clamp_min(floor)
        wv = torch.exp(-p * cv).clamp_min(floor)
        group, is_bg = sysd["group"], sysd["is_bg"]
        c = torch.where(is_bg[:, None, None, None], c0[group], c1[group])
        a = torch.exp(-p * c).clamp_min(floor) * sysd["mk"].to(c.dtype)
        return ImplicitRWMulti.apply(wh, wv, a, group, ch.shape[0], self.maxit, self.tol, stats)


def split_labels(x, sysd):
    """x (M,1,H,W) -> list over images of (K_b+1,H,W) label probabilities."""
    return [x[o:o + K + 1, 0] for o, K in zip(sysd["offsets"], sysd["K"])]


def multi_cross_entropy(x, sysd, weight=None, eps=1e-6):
    """Per-pixel cross-entropy of the label probabilities against sysd['target'] (B,H,W),
    averaged over all pixels (weight (B,H,W) optional)."""
    tot, n = 0.0, 0
    for b, xb in enumerate(split_labels(x, sysd)):
        pt = xb.gather(0, sysd["target"][b][None])[0].clamp_min(eps)        # (H,W)
        l = -torch.log(pt)
        if weight is not None:
            l = l * weight[b]
        tot = tot + l.sum(); n += l.numel()
    return tot / n


def label_core_distance(inst, rmax=4):
    """inst (B,1,H,W) integer instance ids -> (d, dmax): d the number of r in 1..rmax for
    which the (2r+1)^2 window around the pixel lies inside its own instance (Chebyshev
    distance to a different label, capped), dmax the maximum of d over the pixel's
    instance.  Background pixels: 0.  (inst > 0) & ((d >= r) | (d == dmax)) is the
    instance eroded by r px with its core kept when the erosion would empty it."""
    f = inst.float()
    d = torch.zeros_like(f)
    fg = inst > 0
    for r in range(1, rmax + 1):
        same = (F.max_pool2d(f, 2 * r + 1, 1, r) == -F.max_pool2d(-f, 2 * r + 1, 1, r)) & fg
        d = d + same.float()
    B = inst.shape[0]
    flat = (inst.long() + torch.arange(B, device=inst.device)[:, None, None, None] * (int(inst.max()) + 1)).reshape(-1)
    table = torch.zeros(int(flat.max()) + 1, device=inst.device).scatter_reduce(0, flat, d.reshape(-1), "amax")
    dmax = table[flat].reshape(inst.shape)
    return d, dmax


def eroded_markers(inst, r):
    """Training markers: the instances eroded by r px (Chebyshev), each keeping its core."""
    d, dmax = label_core_distance(inst, rmax=max(r, 1))
    return (inst > 0) & ((d >= r) | (d == dmax))


def pw_limit_multi_numpy(ch, cv, c0, c1, lab, quant=2 ** 20, want_probs=False):
    """Exact p -> inf limit of the multi-marker layer: Power Watershed on the grid augmented
    with K+1 label nodes (node n+k for label k; pixel i -- node 0 with cost c0_i for every
    pixel, pixel i -- node k with cost c1_i for the marker pixels of label k).

    lab (H,W) int: marker label map (0 = none; labels 1..K).  Returns (labels (H,W) int in
    0..K: the argmax label of every pixel, stats[, probs (K+1,H,W)])."""
    H, W = c0.shape
    n = H * W
    idx = np.arange(n).reshape(H, W)
    labs = np.unique(lab[lab > 0])
    K = len(labs)
    remap = np.zeros(int(lab.max()) + 1, np.int64); remap[labs] = np.arange(1, K + 1)
    labc = remap[lab]
    mpix = np.flatnonzero(labc.ravel())
    u = np.concatenate([idx[:, :-1].ravel(), idx[:-1, :].ravel(), idx.ravel(), mpix])
    v = np.concatenate([idx[:, 1:].ravel(), idx[1:, :].ravel(), np.full(n, n), n + labc.ravel()[mpix]])
    c = np.concatenate([ch.ravel(), cv.ravel(), c0.ravel(), c1.ravel()[mpix]])
    cint = np.round(c * quant).astype(np.int64)
    seed_mask = np.zeros(n + K + 1, dtype=bool); seed_mask[n:] = True
    seed_lab = np.zeros(n + K + 1, dtype=np.int64); seed_lab[n:] = np.arange(K + 1)
    out, stats = power_watershed_multi(n + K + 1, u, v, cint, seed_mask, seed_lab, K + 1, want_probs=want_probs)
    if want_probs:
        labels, probs = out
        return labels[:n].reshape(H, W), stats, probs[:, :n].reshape(K + 1, H, W)
    return out[:n].reshape(H, W), stats


def power_watershed_multi(n, u, v, cint, seed_mask, seed_lab, K, small=64, want_probs=False, backend=None):
    """Power Watershed (q = 2, p -> inf) with K labels: the plateau-by-plateau maximum
    spanning forest of pw_conditioning.power_watershed, where every merged node carries a
    K-vector of label probabilities instead of a scalar.  Seeds carry one-hot vectors; on a
    plateau that touches at least two distinct known vectors the unit-weight Random Walker
    is solved with K right-hand sides at once, so the result is the exact limit of
    (L(w^p) + D) x_k = a_k for every label, not an interpolation of label indices.
    Returns the argmax label per node (-1 if unreachable) and stats; with want_probs also
    the (K, n) probability matrix.  backend: as pw_conditioning.power_watershed (Numba
    back end in pw_fast.py when available, bit-for-bit identical)."""
    from pw_conditioning import _backend
    if _backend(backend) == "numba":
        from pw_fast import power_watershed_multi_fast
        return power_watershed_multi_fast(n, u, v, cint, seed_mask, seed_lab, K, small, want_probs)
    parent = np.arange(n)
    vid = np.full(n, -1, dtype=np.int64)                         # id of the known vector of a root, -1 unknown
    table = [np.eye(K)[k] for k in range(K)]                     # id -> K-vector
    vid[seed_mask] = seed_lab[seed_mask]
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
            j = i
            while j < starts.size and sizes[j] == 1:
                j += 1
            for eidx in order[s:starts[j - 1] + 1]:
                ru, rv = find(u[eidx]), find(v[eidx])
                if ru == rv:
                    continue
                ku, kv = vid[ru] >= 0, vid[rv] >= 0
                if ku and kv:
                    if vid[ru] != vid[rv]:
                        continue                      # both sides decided (and different)
                    parent[ru] = rv
                elif ku:
                    parent[rv] = ru
                else:
                    parent[ru] = rv
            i = j
            continue
        if sizes[i] <= small:
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
                knowns = {int(vid[r]) for r in members if vid[r] >= 0}
                if len(knowns) <= 1:
                    rep = members[0]
                    for r in members:
                        parent[r] = rep
                    if knowns:
                        vid[rep] = knowns.pop()
                    continue
                unknown = [r for r in members if vid[r] < 0]
                if not unknown:
                    continue
                pos = {r: k for k, r in enumerate(unknown)}
                k = len(unknown); A = np.zeros((k, k)); b = np.zeros((k, K))
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
                        b[pa] += table[vid[bb]]
                    elif pb is not None:
                        b[pb] += table[vid[a]]
                sol = np.linalg.solve(A, b)
                for r, row in zip(unknown, sol):
                    vid[r] = len(table); table.append(row)
                stats["solved_plateaus"] += 1
                stats["solved_nodes"] += k
                stats["max_solve"] = max(stats["max_solve"], k)
            continue
        i += 1
        parent = _compress_parent(parent)
        eu, ev = parent[u[order[s:e]]], parent[v[order[s:e]]]
        keep = eu != ev
        if not keep.any():
            continue
        eu, ev = eu[keep], ev[keep]
        import scipy.sparse as sp
        import scipy.sparse.linalg as spla
        G = sp.coo_matrix((np.ones(eu.size), (eu, ev)), shape=(n, n))
        ncomp, comp = sp.csgraph.connected_components(G, directed=False)
        roots = np.unique(np.concatenate([eu, ev]))
        croots = comp[roots]
        known = vid[roots] >= 0
        kc, kv = croots[known], vid[roots[known]].astype(float)
        cmin = np.full(ncomp, np.inf); cmax = np.full(ncomp, -np.inf)
        np.minimum.at(cmin, kc, kv); np.maximum.at(cmax, kc, kv)
        ambiguous = cmax > cmin
        amb_root = ambiguous[croots]
        mroots = roots[~amb_root]
        if mroots.size:
            mcomp = croots[~amb_root]
            rep = np.full(ncomp, -1, dtype=np.int64)
            rep[mcomp] = mroots
            parent[mroots] = rep[mcomp]
            has = np.isfinite(cmin) & ~ambiguous
            vid[rep[np.flatnonzero(has)]] = cmin[has].astype(np.int64)
        if ambiguous.any():
            sel = ambiguous[comp[eu]]
            au, av = eu[sel], ev[sel]
            aroots = roots[amb_root]
            unknown = aroots[vid[aroots] < 0]
            if unknown.size:
                T = np.array(table)
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
                b = np.zeros((k, K))
                m = fu & ~fv; np.add.at(b, lpos[au[m]], T[vid[av[m]]])
                m = ~fu & fv; np.add.at(b, lpos[av[m]], T[vid[au[m]]])
                sol = spla.splu(A).solve(b)
                for r, row in zip(unknown, sol):
                    vid[r] = len(table); table.append(row)
                stats["solved_plateaus"] += 1
                stats["solved_nodes"] += int(k)
                stats["max_solve"] = max(stats["max_solve"], int(k))
    parent = _compress_parent(parent)
    T = np.array(table)
    ids = vid[parent]
    stats["unassigned"] = int((ids < 0).sum())
    labels = np.where(ids >= 0, T[np.maximum(ids, 0)].argmax(1), -1)
    if want_probs:
        probs = np.where(ids[None] >= 0, T[np.maximum(ids, 0)].T, np.nan)
        return (labels, probs), stats
    return labels, stats


def _compress_parent(parent):
    while True:
        pp = parent[parent]
        if np.array_equal(pp, parent):
            return parent
        parent = pp


# ----------------------------------------------------------------------------
# metrics
# ----------------------------------------------------------------------------
def boundary_fscore(pred, gt, tol=2):
    """Boundary F-score at a pixel tolerance (numpy bool arrays)."""
    from scipy import ndimage
    def contour(m):
        return m ^ ndimage.binary_erosion(m, border_value=0)
    bp, bg = contour(pred), contour(gt)
    if bp.sum() == 0 and bg.sum() == 0:
        return 1.0
    if bp.sum() == 0 or bg.sum() == 0:
        return 0.0
    dg = ndimage.distance_transform_edt(~bg)
    dp = ndimage.distance_transform_edt(~bp)
    prec = (dg[bp] <= tol).mean(); rec = (dp[bg] <= tol).mean()
    return 0.0 if prec + rec == 0 else 2 * prec * rec / (prec + rec)


def iou(pred, gt):
    i = (pred & gt).sum(); u = (pred | gt).sum()
    return 1.0 if u == 0 else i / u


def softness(x):
    """Fraction of pixels with potential in (0.1, 0.9) and mean binary entropy."""
    x = np.clip(x, 1e-7, 1 - 1e-7)
    ent = -(x * np.log2(x) + (1 - x) * np.log2(1 - x))
    return float(((x > 0.1) & (x < 0.9)).mean()), float(ent.mean())


# ----------------------------------------------------------------------------
# self-test
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    import scipy.sparse as sp
    import scipy.sparse.linalg as spla
    torch.manual_seed(0)
    H, W = 7, 9
    dt = torch.float64
    ch = torch.rand(1, 1, H, W - 1, dtype=dt); cv = torch.rand(1, 1, H - 1, W, dtype=dt)
    c1 = torch.rand(1, 1, H, W, dtype=dt) * 3; c0 = torch.rand(1, 1, H, W, dtype=dt) * 3
    p = 2.0
    wh, wv, a1, a0 = torch.exp(-p * ch), torch.exp(-p * cv), torch.exp(-p * c1), torch.exp(-p * c0)
    # 1. matvec against an explicit sparse matrix
    n = H * W; idx = np.arange(n).reshape(H, W)
    u = np.concatenate([idx[:, :-1].ravel(), idx[:-1, :].ravel()])
    v = np.concatenate([idx[:, 1:].ravel(), idx[1:, :].ravel()])
    w = np.concatenate([wh.numpy().ravel(), wv.numpy().ravel()])
    L = sp.coo_matrix((np.concatenate([-w, -w]), (np.concatenate([u, v]), np.concatenate([v, u]))), shape=(n, n)).tocsr()
    L = L + sp.diags(-np.asarray(L.sum(1)).ravel())
    A = L + sp.diags((a0 + a1).numpy().ravel())
    x = torch.rand(1, 1, H, W, dtype=dt)
    sysm = System(wh, wv, a0, a1)
    err = np.abs(sysm.matvec(x).numpy().ravel() - A @ x.numpy().ravel()).max()
    print(f"matvec vs sparse matrix: max abs err {err:.2e}")
    # 2. solvers against a direct solve
    xd = spla.spsolve(A.tocsc(), a1.numpy().ravel())
    xs = pcg(sysm, 500, tol=1e-12).numpy().ravel()
    print(f"pcg vs direct: {np.abs(xs - xd).max():.2e}; range [{xd.min():.3f},{xd.max():.3f}]")
    # 3. implicit gradient against autograd through a converged unrolled solve
    layer_u = RWLayer("unrolled", K=400); layer_i = RWLayer("implicit", tol=1e-13)
    target = torch.rand(1, 1, H, W, dtype=dt)
    grads = {}
    for name, layer in (("unrolled", layer_u), ("implicit", layer_i)):
        args = [t.clone().requires_grad_(True) for t in (ch, cv, c1, c0)]
        pp = torch.tensor(p, dtype=dt, requires_grad=True)
        loss = ((layer(*args, pp) - target) ** 2).sum()
        loss.backward()
        grads[name] = [a.grad.clone() for a in args] + [pp.grad.clone()]
    for i, nm in enumerate(("ch", "cv", "c1", "c0", "p")):
        gu, gi = grads["unrolled"][i], grads["implicit"][i]
        print(f"grad {nm}: implicit vs unrolled max abs err {float((gu - gi).abs().max()):.2e}  (|g| ~ {float(gu.abs().max()):.2e})")
    # 3b. reweighted mode: autograd (outer loop) + implicit (inner) against finite differences
    layer_r = RWLayer("reweighted", tol=1e-13, outer=3, eps=0.2)
    args = [t.clone().requires_grad_(True) for t in (ch, cv, c1, c0)]
    st = {}
    loss = ((layer_r(*args, p, stats=st) - target) ** 2).sum(); loss.backward()
    g_ch = args[0].grad.clone()
    i, j = 3, 4; h = 1e-6
    chp = ch.clone(); chp[0, 0, i, j] += h
    chm = ch.clone(); chm[0, 0, i, j] -= h
    fd = (((layer_r(chp, cv, c1, c0, p) - target) ** 2).sum() - ((layer_r(chm, cv, c1, c0, p) - target) ** 2).sum()) / (2 * h)
    print(f"reweighted grad ch[{i},{j}]: autograd {float(g_ch[0, 0, i, j]):.6e} finite diff {float(fd):.6e}; inner iters {st['iters']}")
    # 4. exact limit agrees with large p
    chn, cvn, c1n, c0n = (t.numpy()[0, 0] for t in (ch, cv, c1, c0))
    xinf, st = pw_limit_numpy(chn, cvn, c1n, c0n)
    for pp in (10, 30, 60):
        xp = RWLayer("implicit", tol=1e-12)(ch, cv, c1, c0, float(pp)).numpy()[0, 0]
        print(f"p={pp}: label disagreement with PW limit {((xp > 0.5) != (xinf > 0.5)).mean():.3f}, "
              f"max |x^p - x^inf| {np.abs(xp - xinf).max():.3f}")
    print("limit stats", st)
    # 5. multi-marker layer: sum to one, two-label case against the binary layer, adjoint
    #    against finite differences, exact K-label limit against large p
    print("--- multi-marker layer")
    torch.manual_seed(1)
    lab = torch.zeros(1, 1, H, W, dtype=torch.long)
    lab[0, 0, 1:3, 1:3] = 1; lab[0, 0, 4:6, 6:8] = 2; lab[0, 0, 0, 7:9] = 3
    sysd = label_systems(lab)
    mlayer = MultiRWLayer(tol=1e-13, maxit=5000)
    xm = mlayer(ch, cv, c0, c1, sysd, p)
    xs = split_labels(xm, sysd)[0]
    print(f"K={sysd['K'][0]} systems {xm.shape[0]}: sum over labels - 1: max abs {float((xs.sum(0) - 1).abs().max()):.2e}")
    # two labels, marker = every pixel: must equal the binary layer
    lab2 = torch.ones(1, 1, H, W, dtype=torch.long)
    x2 = split_labels(mlayer(ch, cv, c0, c1, label_systems(lab2), p), label_systems(lab2))[0]
    xb = RWLayer("implicit", tol=1e-13)(ch, cv, c1, c0, p)[0, 0]
    print(f"two labels vs binary layer: max abs diff {float((x2[1] - xb).abs().max()):.2e}")
    # adjoint vs finite differences (loss = cross-entropy against a random labelling)
    tgt = torch.randint(0, sysd["K"][0] + 1, (1, H, W))
    sysd_t = dict(sysd, target=tgt)
    def lossf(ch_, cv_, c0_, c1_):
        return multi_cross_entropy(mlayer(ch_, cv_, c0_, c1_, sysd_t, p), sysd_t)
    args = [t.clone().requires_grad_(True) for t in (ch, cv, c0, c1)]
    lossf(*args).backward()
    h = 1e-6
    for ai, nm, (ii, jj) in ((0, "ch", (3, 4)), (1, "cv", (2, 5)), (2, "c0", (4, 4)), (3, "c1", (1, 2))):
        base = [t.clone() for t in (ch, cv, c0, c1)]
        bp = [t.clone() for t in base]; bp[ai][0, 0, ii, jj] += h
        bm = [t.clone() for t in base]; bm[ai][0, 0, ii, jj] -= h
        fd = (lossf(*bp) - lossf(*bm)) / (2 * h)
        print(f"multi grad {nm}[{ii},{jj}]: adjoint {float(args[ai].grad[0, 0, ii, jj]):+.6e} finite diff {float(fd):+.6e}")
    # exact K-label limit: two-label case against pw_limit_numpy, K labels against large p
    labn = lab.numpy()[0, 0]
    l2, st2 = pw_limit_multi_numpy(chn, cvn, c0n, c1n, np.ones((H, W), int))
    print(f"multi limit, two labels vs pw_limit_numpy: label disagreement {((l2 == 1) != (xinf > 0.5)).mean():.3f}  stats {st2}")
    lk, stk, probs = pw_limit_multi_numpy(chn, cvn, c0n, c1n, labn, want_probs=True)
    print(f"multi limit K={labn.max()}: probs sum to one max abs err {np.abs(np.nansum(probs, 0) - 1).max():.2e}  stats {stk}")
    for pp in (10, 30, 60):
        xp = split_labels(mlayer(ch, cv, c0, c1, sysd, float(pp)), sysd)[0].numpy()
        print(f"p={pp}: argmax disagreement with the K-label limit {(xp.argmax(0) != lk).mean():.3f}, max |x^p - x^inf| {np.nanmax(np.abs(xp - probs)):.3f}")
    # coarsely quantised costs (large ambiguous plateaus): the K-vector solve must equal K one-hot
    # runs of the scalar power_watershed on the same augmented graph
    from pw_conditioning import power_watershed
    Hq, Wq = 12, 14
    rng = np.random.default_rng(3)
    chq, cvq = rng.integers(0, 3, (Hq, Wq - 1)) / 4.0, rng.integers(0, 3, (Hq - 1, Wq)) / 4.0
    c0q, c1q = rng.integers(0, 3, (Hq, Wq)) / 4.0 + 0.25, rng.integers(0, 2, (Hq, Wq)) / 4.0
    labq = np.zeros((Hq, Wq), int); labq[2:4, 2:4] = 1; labq[8:10, 9:11] = 2; labq[1, 11] = 3
    lq, stq, pq_ = pw_limit_multi_numpy(chq, cvq, c0q, c1q, labq, quant=4, want_probs=True)
    nq = Hq * Wq; idq = np.arange(nq).reshape(Hq, Wq); Kq = 3
    mpix = np.flatnonzero(labq.ravel())
    uq = np.concatenate([idq[:, :-1].ravel(), idq[:-1, :].ravel(), idq.ravel(), mpix])
    vq = np.concatenate([idq[:, 1:].ravel(), idq[1:, :].ravel(), np.full(nq, nq), nq + labq.ravel()[mpix]])
    cq = np.round(np.concatenate([chq.ravel(), cvq.ravel(), c0q.ravel(), c1q.ravel()[mpix]]) * 4).astype(np.int64)
    smq = np.zeros(nq + Kq + 1, bool); smq[nq:] = True
    err = 0.0
    for k in range(Kq + 1):
        sv = np.zeros(nq + Kq + 1); sv[nq + k] = 1.0
        xk, _ = power_watershed(nq + Kq + 1, uq, vq, cq, smq, sv)
        err = max(err, np.abs(xk[:nq].reshape(Hq, Wq) - pq_[k]).max())
    print(f"quantised costs, K={Kq}: multi limit vs {Kq + 1} one-hot scalar runs: max abs diff {err:.2e}; stats {stq}")
