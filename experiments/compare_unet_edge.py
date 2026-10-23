#!/usr/bin/env python3
"""Section 10.1: the edge-target layer (section 10, results/pannuke/leads/edge_gap_p10) against
the fair baseline, a plain U-Net with a contour head trained on the same edge target and
post-processed classically (unet_edge).  Tables over all of fold 2, the min-area-8 instance
numbers, paired per-patch differences with bootstrap intervals (pixel metrics; dataset-level
F1 / PQ differences bootstrapped over patches), per tissue and by crowding, seam statistics.
Numpy only (no GPU, no matplotlib): runs on the Mac from the per-image npz files.

usage: compare_unet_edge.py --edge results/pannuke/leads/edge_gap_p10 --gap results/pannuke/gap \
           --ue results/pannuke/leads/unet_edge --minarea results/pannuke/leads/minarea.json \
           --outdir results/pannuke/leads/unet_edge
"""
import argparse, json, os
import numpy as np

PIX = (("iou", "IoU"), ("bf1", "BF₁"), ("bf2", "BF₂"), ("bf3", "BF₃"), ("band_acc", "band acc."), ("soft_frac", "soft px"),
       ("edge_align", "edge align."), ("f1_05", "F1@0.5"), ("pq", "PQ"), ("count_err", "count err."))
PP_NAME = dict(logits="logits", pp_contour="logits − contour (c > 0.5)", pp_ws="watershed, seg markers",
               pp_wsc="watershed, contour markers", layer="layer, 20 steps", converged="converged", limit="PW limit")


def fmt(v, k):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "–"
    return f"{100 * v:.1f} %" if k == "soft_frac" else f"{v:.3f}"


def sub(per, mode):
    return {k.split("__", 1)[1]: v for k, v in per.items() if k.startswith(mode + "__")}


def boot_idx(n, B=2000, seed=0):
    return np.random.default_rng(seed).integers(0, n, (B, n))


def ci(d, idx):
    m = d[idx].mean(1)
    return float(d.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5)), float((d > 0).mean())


def inst_agg(s, sel=None):
    """Dataset-level F1@0.5, PQ, count error from per-image instance counts (optionally on sel)."""
    g = (lambda k: s[f"inst_{k}"] if sel is None else s[f"inst_{k}"][sel])
    tp, fp, fn, iou_sum = g("tp").sum(), g("fp").sum(), g("fn").sum(), g("iou_sum").sum()
    f1 = 2 * tp / max(2 * tp + fp + fn, 1); pq = iou_sum / max(tp + 0.5 * fp + 0.5 * fn, 1e-9)
    ce = float(np.mean(np.abs(g("n_pred") - g("n_gt")) / np.maximum(g("n_gt"), 1)))
    return dict(f1_05=f1, pq=pq, count_err=ce, n_pred=float(g("n_pred").mean()))


def inst_boot(a, b, idx):
    """Bootstrap (over patches) of the difference of dataset-level F1 and PQ, a − b."""
    out = {}
    for k in ("f1_05", "pq"):
        diffs = np.array([inst_agg(a, i)[k] - inst_agg(b, i)[k] for i in idx[:500]])
        out[k] = (inst_agg(a)[k] - inst_agg(b)[k], float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5)))
    return out


def paired_line(label, a, b, idx, metrics=("iou", "bf1", "bf2", "bf3", "band_acc")):
    cells = []
    for m in metrics:
        d = a[m] - b[m]; ok = ~np.isnan(d)
        mean, lo, hi, fb = ci(d[ok], idx)
        cells.append(f"{mean:+.3f} [{lo:+.3f}, {hi:+.3f}]")
    ib = inst_boot(a, b, idx)
    cells += [f"{v[0]:+.3f} [{v[1]:+.3f}, {v[2]:+.3f}]" for v in ib.values()]
    d = a["iou"] - b["iou"]; d2 = a["bf2"] - b["bf2"]
    return f"| {label} | " + " | ".join(cells) + f" | {100 * (d > 0).mean():.0f} % / {100 * (d2 > 0).mean():.0f} % |"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--edge", default="results/pannuke/leads/edge_gap_p10")
    ap.add_argument("--gap", default="results/pannuke/gap")
    ap.add_argument("--ue", default="results/pannuke/leads/unet_edge")
    ap.add_argument("--outdir", default="results/pannuke/leads/unet_edge")
    ap.add_argument("--types", nargs="+", default=("Breast", "Colon", "HeadNeck", "Adrenal_gland"))
    args = ap.parse_args()
    E = json.load(open(os.path.join(args.edge, "rw_learned.json"))); pe = dict(np.load(os.path.join(args.edge, "rw_learned_perimage.npz")))
    G = json.load(open(os.path.join(args.gap, "unet_gap.json"))); pg = dict(np.load(os.path.join(args.gap, "unet_gap_perimage.npz")))
    U = json.load(open(os.path.join(args.ue, "unet_edge.json"))); pu = dict(np.load(os.path.join(args.ue, "unet_edge_perimage.npz")))
    types = pu["types"].astype(str)
    n = len(types); idx = boot_idx(n)
    rows = [("U-Net, gap target (sec. 6.1)", "unet", "logits", G["test"]["logits"], sub(pg, "logits"))]
    for m in ("logits", "pp_contour", "pp_ws", "pp_wsc"):
        rows.append(("U-Net + contour head, edge target", "unet_edge", m, U["test"][m], sub(pu, m)))
    for m in ("layer", "converged"):
        rows.append(("layer, edge target (sec. 10)", "rw_learned", m, E["test"][m], sub(pe, m)))
    rows.append(("layer, edge target (sec. 10)", "rw_learned", "limit", E["test"]["limit"], None))

    md = [f"**PanNuke fold 1 → fold 2, gap target: the edge-target layer against a U-Net with the same edge supervision "
          f"and classical post-processing** ({n} patches; PW limit on {E['test']['limit']['n']}). Watershed marker spacing "
          f"chosen on fold {U['args']['pp_tune_fold']} ({U['args']['pp_tune_n']} patches): {U['args']['pp_md']}.", "",
          "| run | variant | output | " + " | ".join(c[1] for c in PIX) + " |", "|---|---|---|" + "---|" * len(PIX)]
    for lab, v, m, t, _ in rows:
        md.append(f"| {lab} | {v} | {PP_NAME[m]} | " + " | ".join(fmt(t.get(c[0]), c[0]) for c in PIX) + " |")
    t = U["test"]["gt_binary"]
    md.append("| ground truth | | gap mask | " + " | ".join(fmt(t.get(c[0]), c[0]) for c in PIX) + " |")

    # --- fold-3 tuning table
    if U.get("pp_tune"):
        md += ["", f"**Marker spacing on fold {U['args']['pp_tune_fold']}** (PQ / F1 / count error / components per patch):", ""]
        md.append("| spacing | " + " | ".join(f"pp_ws md={k.split('=')[1]}" for k in U["pp_tune"] if k.startswith("pp_ws/")) + " |")
        for name in ("pp_ws", "pp_wsc"):
            ks = [k for k in U["pp_tune"] if k.startswith(name + "/")]
            md.append(f"| {name} | " + " | ".join(f"{U['pp_tune'][k]['pq']:.3f} / {U['pp_tune'][k]['f1_05']:.3f} / "
                                                  f"{U['pp_tune'][k]['count_err']:.2f} / {U['pp_tune'][k]['n_pred_mean']:.1f}" for k in ks) + " |")

    # --- min-area filter (8 px as in sections 7 and 10, and 32 px), with the paired bootstrap of F1 / PQ at 8 px
    ma = json.load(open(os.path.join(args.ue, "minarea_ref.json"))); mu = json.load(open(os.path.join(args.ue, "minarea.json")))
    pma = dict(np.load(os.path.join(args.ue, "minarea_ref_perimage.npz"))); pmu = dict(np.load(os.path.join(args.ue, "minarea_perimage.npz")))
    md += ["", "**Instance metrics after removing components smaller than 8 px, and than 32 px** (IoU against the binary mask)", "",
           "| run | output | IoU (8) | F1@0.5 (8) | PQ (8) | count err. (8) | components / patch (raw → 8) | F1@0.5 (32) | PQ (32) | count err. (32) |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    def ma_row(lab, d, key):
        r1, r8, r32 = d[f"{key}/min_area=1"], d[f"{key}/min_area=8"], d[f"{key}/min_area=32"]
        return (f"| {lab} | {PP_NAME[key.split('/')[-1]]} | {r8['iou']:.3f} | {r8['f1_05']:.3f} | {r8['pq']:.3f} | {r8['count_err']:.3f} | "
                f"{r1['n_pred_mean']:.1f} → {r8['n_pred_mean']:.1f} | {r32['f1_05']:.3f} | {r32['pq']:.3f} | {r32['count_err']:.3f} |")
    md.append(ma_row("U-Net, gap target (sec. 6.1)", ma, "gap/unet/logits"))
    for m in ("logits", "pp_contour", "pp_ws", "pp_wsc"):
        md.append(ma_row("U-Net + contour head, edge target", mu, f"unet_edge/unet_edge/{m}"))
    md.append(ma_row("layer, edge target (sec. 10)", ma, "edge_gap_p10/rw_learned/layer"))
    def per_ma(per, key):
        return {f"inst_{k}": per[f"{key}/{k}"] for k in ("n_pred", "n_gt", "tp", "fp", "fn", "iou_sum")} | {"iou": per[f"{key}/iou"]}
    lay8 = per_ma(pma, "edge_gap_p10/rw_learned/layer/min_area=8"); gu8 = per_ma(pma, "gap/unet/logits/min_area=8")
    ue8 = {m: per_ma(pmu, f"unet_edge/unet_edge/{m}/min_area=8") for m in ("logits", "pp_ws", "pp_wsc")}
    md += ["", "Paired bootstrap of the dataset-level F1@0.5 / PQ differences after the 8-px filter (layer = 20 steps):", ""]
    for lab, a, b in (("layer − gap U-Net", lay8, gu8), ("layer − U-Net + contour head, logits", lay8, ue8["logits"]),
                      ("layer − U-Net + contour head, watershed, seg markers", lay8, ue8["pp_ws"]),
                      ("layer − U-Net + contour head, watershed, contour markers", lay8, ue8["pp_wsc"]),
                      ("U-Net + contour head, watershed, seg markers − its logits", ue8["pp_ws"], ue8["logits"])):
        ib = inst_boot(a, b, idx)
        md.append(f"- {lab}: F1 {ib['f1_05'][0]:+.3f} [{ib['f1_05'][1]:+.3f}, {ib['f1_05'][2]:+.3f}], PQ {ib['pq'][0]:+.3f} [{ib['pq'][1]:+.3f}, {ib['pq'][2]:+.3f}]")

    # --- paired differences
    conv, lay = sub(pe, "converged"), sub(pe, "layer")
    gu = sub(pg, "logits")
    ue = {m: sub(pu, m) for m in ("logits", "pp_contour", "pp_ws", "pp_wsc")}
    best = max(("pp_contour", "pp_ws", "pp_wsc"), key=lambda m: U["test"][m]["pq"])
    md += ["", f"**Paired per-patch differences** ({n} patches, 95 % bootstrap intervals; F1 and PQ are dataset-level, "
           f"bootstrapped over patches). Best post-processed U-Net output by PQ: `{best}`.", "",
           "| comparison | IoU | BF₁ | BF₂ | BF₃ | band acc. | F1@0.5 | PQ | first better on (IoU / BF₂) |",
           "|---|---|---|---|---|---|---|---|---|"]
    md.append(paired_line("converged layer − gap U-Net (sec. 10)", conv, gu, idx))
    md.append(paired_line("U-Net + contour head, logits − gap U-Net", ue["logits"], gu, idx))
    for m in ("pp_contour", "pp_ws", "pp_wsc"):
        md.append(paired_line(f"U-Net + contour head, {PP_NAME[m]} − its logits", ue[m], ue["logits"], idx))
    md.append(paired_line("converged layer − U-Net + contour head, logits", conv, ue["logits"], idx))
    for m in ("pp_contour", "pp_ws", "pp_wsc"):
        md.append(paired_line(f"converged layer − U-Net + contour head, {PP_NAME[m]}", conv, ue[m], idx))
    md.append(paired_line(f"layer (20 steps) − U-Net + contour head, {PP_NAME[best]}", lay, ue[best], idx))

    # --- per tissue and by crowding: converged vs best pp
    md += ["", f"**Per tissue** (converged layer vs `{best}`; IoU / BF₂ / F1 / PQ / count err.)", "",
           "| tissue (n) | converged layer | U-Net + contour head, " + PP_NAME[best] + " |", "|---|---|---|"]
    def cell(s, sel):
        a = inst_agg(s, sel)
        return f"{s['iou'][sel].mean():.3f} / {s['bf2'][sel].mean():.3f} / {a['f1_05']:.3f} / {a['pq']:.3f} / {a['count_err']:.2f}"
    for t in args.types:
        sel = types == t
        md.append(f"| {t} ({sel.sum()}) | {cell(conv, sel)} | {cell(ue[best], sel)} |")
    all_types = sorted(set(types)); wins_iou = wins_f1 = n_t = 0
    for t in all_types:
        sel = types == t
        if sel.sum() >= 50:
            n_t += 1
            wins_iou += conv["iou"][sel].mean() > ue[best]["iou"][sel].mean()
            wins_f1 += inst_agg(conv, sel)["f1_05"] > inst_agg(ue[best], sel)["f1_05"]
    md.append(f"\nThe converged layer has the higher IoU on {wins_iou} and the higher F1 on {wins_f1} of the {n_t} tissue types with ≥ 50 patches.")
    md += ["", "**By crowding** (nuclei per patch; IoU / F1 / PQ / count err.)", "",
           "| nuclei (n) | gap U-Net | U-Net + contour head, logits | " + PP_NAME[best] + " | converged layer |", "|---|---|---|---|---|"]
    ngt = conv["inst_n_gt"]
    for lo, hi in ((0, 10), (10, 30), (30, 60), (60, 10 ** 6)):
        sel = (ngt >= lo) & (ngt < hi)
        def c2(s):
            a = inst_agg(s, sel)
            return f"{s['iou'][sel].mean():.3f} / {a['f1_05']:.3f} / {a['pq']:.3f} / {a['count_err']:.2f}"
        md.append(f"| {lo}–{hi if hi < 10 ** 6 else '∞'} ({sel.sum()}) | {c2(gu)} | {c2(ue['logits'])} | {c2(ue[best])} | {c2(conv)} |")

    # --- seam statistics
    ss_u = json.load(open(os.path.join(args.ue, "seam_stats.json")))["unet_edge"]
    ss_e = json.load(open(os.path.join(args.edge, "seam_stats.json")))["rw_learned"]
    ss_g = json.load(open(os.path.join(args.gap, "seam_stats.json")))["unet_gap"]["logits"]
    md += ["", f"**Seam statistics** (fraction of the {ss_g['touch_px']} seam pixels of fold 2 predicted as background / "
           f"fraction of the {ss_g['seams']} seams entirely background)", "", "| output | seam px bg | seams cut |", "|---|---|---|"]
    md.append(f"| gap U-Net, logits | {100 * ss_g['touch_bg_frac']:.0f} % | {100 * ss_g['seams_cut_frac']:.0f} % |")
    for m in ("logits", "pp_contour", "pp_ws", "pp_wsc"):
        md.append(f"| U-Net + contour head, {PP_NAME[m]} | {100 * ss_u[m]['touch_bg_frac']:.0f} % | {100 * ss_u[m]['seams_cut_frac']:.0f} % |")
    for m in ("logits", "layer", "converged"):
        md.append(f"| layer, edge target (sec. 10), {PP_NAME[m]} | {100 * ss_e[m]['touch_bg_frac']:.0f} % | {100 * ss_e[m]['seams_cut_frac']:.0f} % |")
    text = "\n".join(md) + "\n"
    os.makedirs(args.outdir, exist_ok=True)
    open(os.path.join(args.outdir, "compare.md"), "w").write(text)
    print(text)


if __name__ == "__main__":
    main()
