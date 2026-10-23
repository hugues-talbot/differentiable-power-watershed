#!/usr/bin/env python3
"""Bit-for-bit validation of the Numba back end (pw_fast.py) against the NumPy code, on
random coarse images (2 and 3-5 labels, both plateau paths), the 512^2 cases of
pw_conditioning.make_cases, and the learned-cost regime (continuous costs quantised to 2^-20 on
the label-augmented graph of pw_limit_numpy / pw_limit_multi_numpy), with timings.
Run from unrolling/experiments (needs numpy, scipy, numba, scikit-image; no torch)."""
import ast, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pw_conditioning as pc
import pw_fast as pf
src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pw_layer.py")).read()
tree = ast.parse(src)
ns = {"np": np}
exec(compile(ast.Module(body=[nd for nd in tree.body if isinstance(nd, ast.FunctionDef) and nd.name in ("power_watershed_multi", "_compress_parent")], type_ignores=[]), "pw_layer.py", "exec"), ns)
pw_multi_np = ns["power_watershed_multi"]

def same(a, b):
    return np.array_equal(np.asarray(a), np.asarray(b), equal_nan=True)

def check_scalar(tag, n, u, v, cint, sm, sv, small=64):
    t0 = time.time(); x, s = pc.power_watershed(n, u, v, cint, sm, sv, small=small, backend="numpy"); t1 = time.time() - t0
    t0 = time.time(); xf, sf = pf.power_watershed_fast(n, u, v, cint, sm, sv, small=small); t2 = time.time() - t0
    ok = same(x, xf) and s == sf
    if not ok:
        d = np.nanmax(np.abs(x - xf)); print(f"  MISMATCH {tag}: max diff {d:.3e}, differing {int((x != xf).sum())}, stats {s} vs {sf}")
    return ok, t1, t2

def check_multi(tag, n, u, v, cint, sm, slab, K, small=64):
    t0 = time.time(); (l, p), s = pw_multi_np(n, u, v, cint, sm, slab, K, small=small, want_probs=True, backend="numpy"); t1 = time.time() - t0
    t0 = time.time(); (lf, pf_), sf = pf.power_watershed_multi_fast(n, u, v, cint, sm, slab, K, small=small, want_probs=True); t2 = time.time() - t0
    ok = same(l, lf) and same(p, pf_) and s == sf
    if not ok:
        print(f"  MISMATCH {tag}: labels differ {int((l != lf).sum())}, probs max diff {np.nanmax(np.abs(p - pf_)):.3e}, stats {s} vs {sf}")
    return ok, t1, t2

def grid(H, W):
    return pc.grid_edges(H, W)

def augmented(H, W, ch, cv, c1, c0, quant):
    n = H * W; idx = np.arange(n).reshape(H, W)
    u = np.concatenate([idx[:, :-1].ravel(), idx[:-1, :].ravel(), idx.ravel(), idx.ravel()])
    v = np.concatenate([idx[:, 1:].ravel(), idx[1:, :].ravel(), np.full(n, n), np.full(n, n + 1)])
    c = np.round(np.concatenate([ch.ravel(), cv.ravel(), c1.ravel(), c0.ravel()]) * quant).astype(np.int64)
    sm = np.zeros(n + 2, bool); sm[n:] = True; sv = np.zeros(n + 2); sv[n] = 1.0
    return n + 2, u, v, c, sm, sv

def augmented_multi(H, W, ch, cv, c0, c1, lab, quant):
    n = H * W; idx = np.arange(n).reshape(H, W)
    labs = np.unique(lab[lab > 0]); K = labs.size
    remap = np.zeros(int(lab.max()) + 1, np.int64); remap[labs] = np.arange(1, K + 1); labc = remap[lab]
    mpix = np.flatnonzero(labc.ravel())
    u = np.concatenate([idx[:, :-1].ravel(), idx[:-1, :].ravel(), idx.ravel(), mpix])
    v = np.concatenate([idx[:, 1:].ravel(), idx[1:, :].ravel(), np.full(n, n), n + labc.ravel()[mpix]])
    c = np.round(np.concatenate([ch.ravel(), cv.ravel(), c0.ravel(), c1.ravel()[mpix]]) * quant).astype(np.int64)
    sm = np.zeros(n + K + 1, bool); sm[n:] = True; slab = np.zeros(n + K + 1, np.int64); slab[n:] = np.arange(K + 1)
    return n + K + 1, u, v, c, sm, slab, K + 1

rng = np.random.default_rng(0)
# warm-up (JIT compile, cached afterwards)
pf.power_watershed_fast(4, np.array([0, 1, 2]), np.array([1, 2, 3]), np.array([1, 1, 2]), np.array([True, False, False, True]), np.array([1.0, 0, 0, 0]))
pf.power_watershed_multi_fast(4, np.array([0, 1, 2]), np.array([1, 2, 3]), np.array([1, 1, 2]), np.array([True, False, False, True]), np.array([0, 0, 0, 1]), 2)

print("1. random coarse 24x24 images (4 grey levels), 2 labels / 3-5 labels, small = 64 and small = 0 (general path everywhere)")
bad = 0; cnt = 0
for i in range(200):
    H = W = 24; n = H * W
    levels = int(rng.integers(2, 6))
    img8 = (rng.integers(0, levels, (H, W)) * (255 // (levels - 1))).astype(np.uint8)
    u, v = grid(H, W); cint = np.abs(img8.ravel()[u].astype(np.int64) - img8.ravel()[v].astype(np.int64))
    for small in (64, 0):
        if i % 2 == 0:
            sm = np.zeros(n, bool); sv = np.zeros(n)
            for lab in (1.0, 0.0):
                for _ in range(int(rng.integers(1, 4))):
                    j = rng.integers(0, n); sm[j] = True; sv[j] = lab
            ok, _, _ = check_scalar(f"rand{i}_two_small{small}", n, u, v, cint, sm, sv, small)
        else:
            K = int(rng.integers(3, 6)); sm = np.zeros(n, bool); slab = np.zeros(n, np.int64)
            for k in range(K):
                for _ in range(2):
                    j = rng.integers(0, n); sm[j] = True; slab[j] = k
            ok, _, _ = check_multi(f"rand{i}_multi{K}_small{small}", n, u, v, cint, sm, slab, K, small)
        bad += not ok; cnt += 1
print(f"   {cnt} checks, {bad} mismatches")

print("2. 512^2 cases of pw_conditioning.make_cases (8-bit costs |dI|), scalar and K = 2 multi; timings NumPy / Numba")
rng = np.random.default_rng(0)
bad = 0
for c in pc.make_cases(512, [], rng):
    img8 = c["img8"]; H, W = img8.shape; n = H * W
    u, v = grid(H, W); cint = np.abs(img8.ravel()[u].astype(np.int64) - img8.ravel()[v].astype(np.int64))
    sm, sv = c["seed_mask"].ravel(), c["seed_val"].ravel()
    ok, t1, t2 = check_scalar(c["name"], n, u, v, cint, sm, sv)
    slab = np.where(sv > 0.5, 0, 1)
    ok2, t3, t4 = check_multi(c["name"] + "_multi2", n, u, v, cint, sm, slab, 2)
    bad += (not ok) + (not ok2)
    print(f"   {c['name']:26s} scalar {'ok ' if ok else 'BAD'} {t1:.2f}s -> {t2:.3f}s ({t1 / t2:.0f}x) | multi2 {'ok ' if ok2 else 'BAD'} {t3:.2f}s -> {t4:.3f}s")
print(f"   mismatches: {bad}")

print("3. learned-cost regime: continuous costs quantised to 2^-20 (and 2^4, 2^8) on the label-augmented graph, 256^2")
bad = 0
for quant in (2 ** 20, 2 ** 8, 2 ** 4):
    H = W = 256
    ch = rng.random((H, W - 1)); cv = rng.random((H - 1, W)); c1 = rng.random((H, W)) * 3; c0 = rng.random((H, W)) * 3
    n, u, v, cint, sm, sv = augmented(H, W, ch, cv, c1, c0, quant)
    ok, t1, t2 = check_scalar(f"learned_q{quant}", n, u, v, cint, sm, sv)
    lab = np.zeros((H, W), int)
    for k in range(1, 40):
        y, x = rng.integers(4, H - 4, 2); lab[y - 2:y + 3, x - 2:x + 3] = k
    n2, u2, v2, c2, sm2, slab2, K = augmented_multi(H, W, ch, cv, c0, c1, lab, quant)
    ok2, t3, t4 = check_multi(f"learned_multi_q{quant}", n2, u2, v2, c2, sm2, slab2, K)
    bad += (not ok) + (not ok2)
    print(f"   quant 2^{int(np.log2(quant))}: scalar {'ok ' if ok else 'BAD'} {t1:.2f}s -> {t2:.3f}s ({t1 / t2:.0f}x) | multi K={K} {'ok ' if ok2 else 'BAD'} {t3:.2f}s -> {t4:.3f}s ({t3 / t4:.0f}x)")
print(f"   mismatches: {bad}")
