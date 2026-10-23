"""Are the remaining label differences (released mode vs ours) all ties?  Plus the timing table."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pwref_compare import load_pw, make_multi_cases, run_ref, ref_edges
recs = [json.loads(l) for l in open("results_512/compare.jsonl")]
print("case | n | ours raw (s) | ours multi2/multiK (s) | ref prog PW call (s) | ref prog wall incl. weights+reconstruction (s) | ref raw PW (s)")
for r in recs:
    tm = r.get("t_ours_multi2", r["t_ours_raw"])
    print(f"{r['case']} | {r['n']} | {r['t_ours_raw']:.2f} | {tm:.2f} | {r['ref_prog_stoch']['t_pw']:.3f} | {r['ref_prog_stoch']['t_wall']:.3f} | {r['ref_raw_stoch']['t_pw']:.3f}")
print()
print("two-label cases: label differences released mode vs ours, and how far those pixels are from 0.5")
for r in recs:
    if "K" in r:
        continue
    z = np.load(f"results_512/{r['case']}.npz")
    x = z["x_ours_raw"].astype(np.float64).ravel(); p = z["p_ref_prog"].astype(np.float64).ravel(); m = z["mask_ref_prog"].ravel()
    d = ((x >= 0.5) != (m == 0)); d2 = ((x > 0.5) != (m == 0))
    far = np.abs(x[d] - 0.5).max() if d.any() else 0.0
    far2 = np.abs(x[d2] - 0.5).max() if d2.any() else 0.0
    print(f"  {r['case']:26s} diff(>=): {int(d.sum()):4d} max|x-0.5| {far:.1e} | diff(>): {int(d2.sum()):4d} max|x-0.5| {far2:.1e} | exact 0.5 ours {int((x == 0.5).sum())} ref {int((p == 0.5).sum())} | pot max diff {np.abs(x - p).max():.1e} | |x-0.5|<1e-6: {int((np.abs(x - 0.5) < 1e-6).sum())}")
print()
print("multi-label cases: label differences and the top-two gap of our probabilities there")
pc, pw_multi = load_pw(os.environ.get("ELLZERO", "../../.."))
rng = np.random.default_rng(0)
os.makedirs("tmp_ties", exist_ok=True)
for name, img8, lab in make_multi_cases(pc, 512, rng):
    H, W = img8.shape; n = H * W; u, v = ref_edges(H, W)
    labs = np.unique(lab[lab > 0]); K = labs.size
    remap = np.zeros(lab.max() + 1, int); remap[labs] = np.arange(1, K + 1); lab = remap[lab]
    rr = run_ref("./pwref_wrap", img8, lab.astype(np.uint8), "prog", "tmp_ties/o", "multi", "stoch")
    sm = lab.ravel() > 0; slab = np.where(sm, lab.ravel() - 1, 0)
    (lo, po), st = pw_multi(n, u, v, 255 - rr["normal"].astype(np.int64), sm, slab, K, want_probs=True)
    pr = np.vstack([rr["proba"], 1 - rr["proba"].sum(0)])
    maxi = np.zeros(n); arg = np.zeros(n, int)
    for k in range(K - 1):
        b = rr["proba"][k] > maxi; maxi = np.where(b, rr["proba"][k], maxi); arg = np.where(b, k, arg)
    arg = np.where(pr[K - 1] > maxi, K - 1, arg)
    d = lo != arg
    srt = np.sort(po, 0); gap = srt[-1] - srt[-2]
    print(f"  {name:26s} K={K} label diff {int(d.sum())}, top-two gap at those pixels max {gap[d].max() if d.any() else 0:.1e}; pixels with gap < 1e-6: {int((gap < 1e-6).sum())}; pot max diff {np.abs(po - pr).max():.1e}")
