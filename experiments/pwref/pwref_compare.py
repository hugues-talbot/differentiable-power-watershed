#!/usr/bin/env python3
"""Compare our Power Watershed limit (pw_conditioning.power_watershed, pw_layer.power_watershed_multi)
with Couprie's reference PowerWatershed_q2 (PW_1.0.1), called through pwref_wrap on the same
4-connected grid, the same integer weights (the reference's own 255 - |I_u - I_v|, read back
from its dump) and the same seeds.

Usage: pwref_compare.py --repo <ell-zero> --wrap <pwref_wrap> --out <dir> [--res 512] [--cases ...]
"""
import argparse, ast, json, os, subprocess, sys, time
import numpy as np
from scipy import ndimage


def load_pw(repo):
    sys.path.insert(0, os.path.join(repo, "unrolling", "experiments"))
    import pw_conditioning as pc
    # power_watershed_multi lives in pw_layer.py, which imports torch at module level (not on the Mac):
    # take the two functions out of the source and run them with numpy only.
    src = open(os.path.join(repo, "unrolling", "experiments", "pw_layer.py")).read()
    tree = ast.parse(src)
    keep = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ("power_watershed_multi", "_compress_parent")]
    ns = {"np": np}
    exec(compile(ast.Module(body=keep, type_ignores=[]), "pw_layer.py", "exec"), ns)
    return pc, ns["power_watershed_multi"]


def write_pgm(name, a):
    a = np.ascontiguousarray(a, dtype=np.uint8)
    with open(name, "wb") as f:
        f.write(f"P5\n{a.shape[1]} {a.shape[0]}\n255\n".encode()); f.write(a.tobytes())


def ref_edges(H, W):
    """The reference's edge order: vertical edges (row i, row i+1) first, then horizontal."""
    idx = np.arange(H * W).reshape(H, W)
    u = np.concatenate([idx[:-1, :].ravel(), idx[:, :-1].ravel()])
    v = np.concatenate([idx[1:, :].ravel(), idx[:, 1:].ravel()])
    return u, v


def run_ref(wrap, img8, seeds8, mode, prefix, labels, sort):
    write_pgm(prefix + ".img.pgm", img8); write_pgm(prefix + ".seeds.pgm", seeds8)
    t0 = time.time()
    out = subprocess.run([wrap, prefix + ".img.pgm", prefix + ".seeds.pgm", mode, prefix, labels, sort],
                         capture_output=True, text=True, check=True)
    wall = time.time() - t0
    line = [l for l in out.stdout.splitlines() if l.startswith("pw_time")][0].split()
    N = img8.size
    rec = dict(t_pw=float(line[1]), t_wall=wall, nlabels=int(line[-1]),
               msgs=[l for l in out.stdout.splitlines() if not l.startswith("pw_time")])
    rec["mask"] = np.fromfile(prefix + ".mask.u8", np.uint8)
    rec["proba8"] = np.fromfile(prefix + ".proba8.u8", np.uint8)
    rec["normal"] = np.fromfile(prefix + ".normal.u32", np.uint32)
    rec["recon"] = np.fromfile(prefix + ".recon.u32", np.uint32)
    rec["proba"] = np.fromfile(prefix + ".proba.f32", np.float32).reshape(rec["nlabels"] - 1, N).astype(np.float64)
    for ext in ("mask.u8", "proba8.u8", "normal.u32", "recon.u32", "proba.f32", "img.pgm", "seeds.pgm"):
        os.remove(prefix + "." + ext)
    return rec


def compare_two(x_ours, p_ref, mask_ref):
    """x_ours = P(fg) (n,), p_ref = reference proba[0] = P(label 1 = fg), mask_ref 0 <-> fg."""
    lab_ref = mask_ref == 0
    lab_ours = x_ours >= 0.5                      # the reference's own rule at exactly 0.5
    lab_ours_strict = x_ours > 0.5
    d = np.abs(x_ours - p_ref)
    plateau = ((x_ours > 0) & (x_ours < 1)) | ((p_ref > 0) & (p_ref < 1))
    out = dict(n=int(x_ours.size), label_diff=int((lab_ref != lab_ours).sum()),
               label_diff_strict=int((lab_ref != lab_ours_strict).sum()),
               ties_half_ours=int((x_ours == 0.5).sum()), ties_half_ref=int((p_ref == 0.5).sum()),
               plateau_pixels=int(plateau.sum()), pot_max_diff=float(d.max()),
               pot_max_diff_plateau=float(d[plateau].max()) if plateau.any() else 0.0,
               pot_diff_gt_1e5=int((d > 1e-5).sum()), pot_diff_gt_1e3=int((d > 1e-3).sum()),
               frac_label_diff=float((lab_ref != lab_ours).mean()))
    # consistency of the reference's own 8-bit map with its float potentials
    return out


def compare_multi(lab_ours, probs_ours, p_ref, mask_ref, K):
    """lab_ours in 0..K-1 (ref labels 1..K), probs_ours (K, n); p_ref (K-1, n); mask = argmax*255//(K-1)."""
    pr = np.vstack([p_ref, 1.0 - p_ref.sum(0)])
    # the reference's argmax: first strict maximum among labels 1..K-1, label K only if strictly larger
    maxi = np.zeros(p_ref.shape[1]); arg = np.zeros(p_ref.shape[1], int)
    for k in range(K - 1):
        better = p_ref[k] > maxi
        maxi = np.where(better, p_ref[k], maxi); arg = np.where(better, k, arg)
    arg = np.where(pr[K - 1] > maxi, K - 1, arg)
    mask_lab = (mask_ref.astype(int) * (K - 1) + 127) // 255
    d = np.abs(probs_ours - pr)
    plateau = ((probs_ours > 0) & (probs_ours < 1)).any(0) | ((pr > 0) & (pr < 1)).any(0)
    srt = np.sort(probs_ours, 0)
    ties = (srt[-1] - srt[-2]) < 1e-9
    return dict(n=int(lab_ours.size), label_diff=int((lab_ours != arg).sum()), label_diff_mask=int((lab_ours != mask_lab).sum()),
                ref_mask_vs_argmax=int((mask_lab != arg).sum()), ties_ours=int(ties.sum()),
                plateau_pixels=int(plateau.sum()), pot_max_diff=float(d.max()),
                pot_max_diff_plateau=float(d[:, plateau].max()) if plateau.any() else 0.0,
                pot_diff_gt_1e5=int((d.max(0) > 1e-5).sum()), pot_diff_gt_1e3=int((d.max(0) > 1e-3).sum()),
                frac_label_diff=float((lab_ours != arg).mean()), unassigned=int((lab_ours < 0).sum()))


def two_label_case(pc, pw_multi, wrap, name, img8, seed_mask, seed_val, outdir, save_maps=True):
    H, W = img8.shape; n = H * W
    u, v = ref_edges(H, W)
    seeds8 = np.full((H, W), 128, np.uint8); seeds8[seed_mask & (seed_val > 0.5)] = 255; seeds8[seed_mask & (seed_val < 0.5)] = 0
    prefix = os.path.join(outdir, "tmp_" + name)
    recs = {}
    for mode, sort in (("raw", "stoch"), ("raw", "bucket"), ("geod", "stoch"), ("prog", "stoch"), ("prog", "bucket")):
        recs[(mode, sort)] = run_ref(wrap, img8, seeds8, mode, prefix, "two", sort)
    r = recs[("raw", "stoch")]
    normal, recon = r["normal"].astype(np.int64), r["recon"].astype(np.int64)
    dI = np.abs(img8.ravel()[u].astype(np.int64) - img8.ravel()[v].astype(np.int64))
    assert np.array_equal(normal, 255 - dI), "edge layout mismatch"
    assert (recon <= normal).all()
    sm, sv = seed_mask.ravel(), seed_val.ravel().astype(np.float64)
    out = dict(case=name, H=H, W=W, n=n, nseeds=int(sm.sum()), nedges=int(u.size),
               recon_changed_edges=int((recon != normal).sum()), cost_levels=int(np.unique(dI).size))
    # ours on the raw weights
    t0 = time.time(); x_raw, st = pc.power_watershed(n, u, v, 255 - normal, sm, sv); out["t_ours_raw"] = time.time() - t0
    out["stats_ours_raw"] = st
    t0 = time.time(); x_rec, st2 = pc.power_watershed(n, u, v, 255 - recon, sm, sv); out["t_ours_recon"] = time.time() - t0
    out["stats_ours_recon"] = st2
    # ours, multi-label path with K = 2 (one-hot vectors), on the raw weights
    slab = np.where(sv > 0.5, 0, 1)
    t0 = time.time(); (lab_m, probs_m), stm = pw_multi(n, u, v, 255 - normal, sm, slab, 2, want_probs=True); out["t_ours_multi2"] = time.time() - t0
    out["ours_multi2_vs_scalar"] = dict(label_diff=int(((lab_m == 0) != (x_raw > 0.5)).sum()), pot_max_diff=float(np.nanmax(np.abs(probs_m[0] - x_raw))))
    for (mode, sort), rr in recs.items():
        key = f"ref_{mode}_{sort}"
        out[key] = dict(t_pw=rr["t_pw"], t_wall=rr["t_wall"], msgs=rr["msgs"][:5])
        p0 = rr["proba"][0]
        out[key]["proba8_consistent"] = int((np.abs((255 - 255 * p0).astype(np.uint8).astype(int) - rr["proba8"].astype(int)) > 1).sum())
        xo = x_rec if mode == "geod" else x_raw
        out[key]["vs_ours"] = compare_two(xo, p0, rr["mask"])
        out[key]["vs_ours_raw"] = compare_two(x_raw, p0, rr["mask"])
    # reference against itself: stochastic vs bucket sort (order dependence), raw vs geod vs prog
    a, b = recs[("raw", "stoch")], recs[("raw", "bucket")]
    out["ref_raw_stoch_vs_bucket"] = dict(label_diff=int((a["mask"] != b["mask"]).sum()), pot_max_diff=float(np.abs(a["proba"] - b["proba"]).max()))
    pa, pb = recs[("prog", "stoch")], recs[("prog", "bucket")]
    out["ref_prog_stoch_vs_bucket"] = dict(label_diff=int((pa["mask"] != pb["mask"]).sum()), pot_max_diff=float(np.abs(pa["proba"] - pb["proba"]).max()))
    for m2 in ("geod", "prog"):
        c = recs[(m2, "stoch")]
        out[f"ref_raw_vs_{m2}"] = dict(label_diff=int((a["mask"] != c["mask"]).sum()), pot_max_diff=float(np.abs(a["proba"] - c["proba"]).max()))
    if save_maps:
        np.savez_compressed(os.path.join(outdir, f"{name}.npz"), img8=img8, seed_mask=seed_mask, seed_val=seed_val,
                            x_ours_raw=x_raw.reshape(H, W).astype(np.float32), x_ours_recon=x_rec.reshape(H, W).astype(np.float32),
                            p_ref_raw=a["proba"][0].reshape(H, W).astype(np.float32), mask_ref_raw=a["mask"].reshape(H, W),
                            p_ref_geod=recs[("geod", "stoch")]["proba"][0].reshape(H, W).astype(np.float32),
                            p_ref_prog=recs[("prog", "stoch")]["proba"][0].reshape(H, W).astype(np.float32),
                            mask_ref_prog=recs[("prog", "stoch")]["mask"].reshape(H, W), recon=recon.astype(np.int32))
    return out


def multi_label_case(pc, pw_multi, wrap, name, img8, lab, outdir, save_maps=True):
    """lab (H, W) int: 0 = no seed, 1..K = seed labels."""
    H, W = img8.shape; n = H * W
    u, v = ref_edges(H, W)
    labs = np.unique(lab[lab > 0]); K = labs.size
    remap = np.zeros(lab.max() + 1, int); remap[labs] = np.arange(1, K + 1); lab = remap[lab]
    prefix = os.path.join(outdir, "tmp_" + name)
    recs = {}
    for mode, sort in (("raw", "stoch"), ("raw", "bucket"), ("geod", "stoch"), ("prog", "stoch"), ("prog", "bucket")):
        recs[(mode, sort)] = run_ref(wrap, img8, lab.astype(np.uint8), mode, prefix, "multi", sort)
    r = recs[("raw", "stoch")]
    normal, recon = r["normal"].astype(np.int64), r["recon"].astype(np.int64)
    sm = lab.ravel() > 0; slab = np.where(sm, lab.ravel() - 1, 0)
    out = dict(case=name, H=H, W=W, n=n, K=K, nseeds=int(sm.sum()), nedges=int(u.size),
               recon_changed_edges=int((recon != normal).sum()))
    t0 = time.time(); (lab_raw, pr_raw), st = pw_multi(n, u, v, 255 - normal, sm, slab, K, want_probs=True); out["t_ours_raw"] = time.time() - t0
    out["stats_ours_raw"] = st
    t0 = time.time(); (lab_rec, pr_rec), st2 = pw_multi(n, u, v, 255 - recon, sm, slab, K, want_probs=True); out["t_ours_recon"] = time.time() - t0
    out["stats_ours_recon"] = st2
    # K one-hot scalar runs on the raw weights (the per-label solves) against the K-vector solve
    err = 0.0
    for k in range(K):
        xk, _ = pc.power_watershed(n, u, v, 255 - normal, sm, (slab == k).astype(np.float64))
        err = max(err, float(np.nanmax(np.abs(xk - pr_raw[k]))))
    out["ours_multi_vs_onehot_scalar"] = err
    for (mode, sort), rr in recs.items():
        key = f"ref_{mode}_{sort}"
        out[key] = dict(t_pw=rr["t_pw"], t_wall=rr["t_wall"], msgs=rr["msgs"][:5])
        lo, po = (lab_rec, pr_rec) if mode == "geod" else (lab_raw, pr_raw)
        out[key]["vs_ours"] = compare_multi(lo, po, rr["proba"], rr["mask"], K)
    a, b = recs[("raw", "stoch")], recs[("raw", "bucket")]
    out["ref_raw_stoch_vs_bucket"] = dict(label_diff=int((a["mask"] != b["mask"]).sum()), pot_max_diff=float(np.abs(a["proba"] - b["proba"]).max()))
    pa, pb = recs[("prog", "stoch")], recs[("prog", "bucket")]
    out["ref_prog_stoch_vs_bucket"] = dict(label_diff=int((pa["mask"] != pb["mask"]).sum()), pot_max_diff=float(np.abs(pa["proba"] - pb["proba"]).max()))
    for m2 in ("geod", "prog"):
        c = recs[(m2, "stoch")]
        out[f"ref_raw_vs_{m2}"] = dict(label_diff=int((a["mask"] != c["mask"]).sum()), pot_max_diff=float(np.abs(a["proba"] - c["proba"]).max()))
    if save_maps:
        np.savez_compressed(os.path.join(outdir, f"{name}.npz"), img8=img8, lab=lab, lab_ours_raw=lab_raw.reshape(H, W),
                            probs_ours_raw=pr_raw.reshape(K, H, W).astype(np.float32),
                            p_ref_raw=a["proba"].reshape(K - 1, H, W).astype(np.float32), mask_ref_raw=a["mask"].reshape(H, W))
    return out


def erode_label(mask, r):
    return ndimage.binary_erosion(mask, pc_disc(2 * r + 1, r), border_value=0)


def pc_disc(size, r):
    yy, xx = np.mgrid[:size, :size]
    return (yy - r) ** 2 + (xx - r) ** 2 <= r * r


def make_multi_cases(pc, res, rng):
    cases = []
    img8, gt = pc.synth_image(res, 0.05, rng)
    comp, ncomp = ndimage.label(gt)
    lab = np.zeros(gt.shape, int)
    lab[erode_label(~gt, 5)] = 1
    for c in range(1, ncomp + 1):
        lab[erode_label(comp == c, 5)] = c + 1
    cases.append(("synth%d_multi%d_r5" % (res, len(np.unique(lab)) - 1), img8, lab))
    for name, im in pc.natural_images(res).items():
        sm = ndimage.gaussian_filter(im.astype(np.float64), 2.0)
        q = np.digitize(sm, np.quantile(sm, [1 / 3, 2 / 3]))      # 3 intensity classes
        lab = np.zeros(im.shape, int)
        for c in range(3):
            lab[erode_label(q == c, 5)] = c + 1
        cases.append((f"{name}{res}_multi3_r5", im, lab))
    return cases


def random_small_cases(rng, count, size=24, levels=4):
    """Coarsely quantised random images (huge plateaus) with a few random seed pixels."""
    out = []
    for i in range(count):
        img8 = (rng.integers(0, levels, (size, size)) * (255 // (levels - 1))).astype(np.uint8)
        if i % 2 == 0:
            m = np.zeros((size, size), bool); vmap = np.zeros((size, size))
            for lab in (1.0, 0.0):
                for _ in range(3):
                    y, x = rng.integers(0, size, 2); m[y, x] = True; vmap[y, x] = lab
            out.append((f"rand{i}_two", img8, ("two", m, vmap)))
        else:
            K = int(rng.integers(3, 6)); lab = np.zeros((size, size), int)
            for k in range(1, K + 1):
                for _ in range(2):
                    y, x = rng.integers(0, size, 2); lab[y, x] = k
            out.append((f"rand{i}_multi{K}", img8, ("multi", lab)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True); ap.add_argument("--wrap", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--res", type=int, default=512); ap.add_argument("--cases", default="")
    ap.add_argument("--skip-random", action="store_true"); ap.add_argument("--skip-big", action="store_true")
    ap.add_argument("--nrandom", type=int, default=80)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    pc, pw_multi = load_pw(args.repo)
    results = []
    jl = open(os.path.join(args.out, "compare.jsonl"), "a")

    def emit(rec):
        results.append(rec); jl.write(json.dumps(rec) + "\n"); jl.flush()
        r = rec.get("ref_raw_stoch", {}).get("vs_ours", {})
        print(f"[{rec['case']}] n={rec['n']} ours {rec['t_ours_raw']:.2f}s ref {rec.get('ref_raw_stoch', {}).get('t_pw', float('nan')):.2f}s "
              f"| raw: label diff {r.get('label_diff')} pot max {r.get('pot_max_diff', float('nan')):.2e} (>1e-5: {r.get('pot_diff_gt_1e5')}) "
              f"| geod: label diff {rec.get('ref_geod_stoch', {}).get('vs_ours', {}).get('label_diff')} "
              f"| prog vs ours(raw): {rec.get('ref_prog_stoch', {}).get('vs_ours', {}).get('label_diff')} "
              f"| ref raw stoch vs bucket: {rec['ref_raw_stoch_vs_bucket']['label_diff']} | prog stoch vs bucket {rec['ref_prog_stoch_vs_bucket']['label_diff']} pot {rec['ref_prog_stoch_vs_bucket']['pot_max_diff']:.1e} "
              f"| prog pot max {rec.get('ref_prog_stoch', {}).get('vs_ours', {}).get('pot_max_diff', float('nan')):.2e} (>1e-5: {rec.get('ref_prog_stoch', {}).get('vs_ours', {}).get('pot_diff_gt_1e5')}) "
              f"| geod pot max {rec.get('ref_geod_stoch', {}).get('vs_ours', {}).get('pot_max_diff', float('nan')):.2e}", flush=True)

    rng = np.random.default_rng(0)
    if not args.skip_random:
        for name, img8, spec in random_small_cases(rng, args.nrandom):
            if spec[0] == "two":
                emit(two_label_case(pc, pw_multi, args.wrap, name, img8, spec[1], spec[2], args.out, save_maps=False))
            else:
                emit(multi_label_case(pc, pw_multi, args.wrap, name, img8, spec[1], args.out, save_maps=False))
    if not args.skip_big:
        rng = np.random.default_rng(0)
        want = [s for s in args.cases.split(",") if s]
        for c in pc.make_cases(args.res, want, rng):
            emit(two_label_case(pc, pw_multi, args.wrap, c["name"], c["img8"], c["seed_mask"], c["seed_val"], args.out))
        rng = np.random.default_rng(0)
        for name, img8, lab in make_multi_cases(pc, args.res, rng):
            if not want or any(w in name for w in want):
                emit(multi_label_case(pc, pw_multi, args.wrap, name, img8, lab, args.out))
    jl.close()


if __name__ == "__main__":
    main()
