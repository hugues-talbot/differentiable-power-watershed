#!/usr/bin/env python3
"""Section 11.2: tables, paired statistics and figures for the three-head U-Net + HoVer-Net-style
post-processing of exp_unet_dist.py against the plain U-Net (section 6, results_pannuke), the
contour-head U-Net + tuned watershed (section 10.1, results_pannuke_leads/unet_edge) and the
multi-marker layer runs of section 11.1 (results_pannuke_instances/{dist,bce_tuned}).  The tables
need numpy only (summary.md is written first, so the script also runs on the Mac from the results
folders); the figures need matplotlib and the examples npz (jacobian).

usage: plot_unet_dist.py --res results_pannuke_instances/unet_dist --unet results_pannuke \
           --ue results_pannuke_leads/unet_edge --dist results_pannuke_instances/dist --bce results_pannuke_instances/bce_tuned
"""
import argparse, json, os
import numpy as np
from scipy import ndimage

COLS = (("iou", "IoU"), ("bf1", "BF₁"), ("bf2", "BF₂"), ("band_acc", "band acc."), ("edge_align", "edge align."),
        ("f1_05", "F1@0.5"), ("pq", "PQ"), ("sq", "SQ"), ("dq", "DQ"), ("aji", "AJI"), ("count_err", "count err."), ("n_pred_mean", "n_pred"))
MODE_NAME = dict(logits="s > 0.5, components", ws="tuned post-processing (markers of the distance head, watershed of the chosen relief)",
                 ws_contour="markers of the distance head, watershed of the contour map", ws_dist="markers of the distance head, watershed of −distance",
                 ws_both="markers of the distance head, watershed of contour − distance", ws_fb="tuned post-processing + unmarked components kept",
                 ws_gtmk="watershed from the ground-truth markers (oracle)",
                 layer="sec. 11.1 layer, reproduced (its markers, its solve)", lmk_ws="layer's markers, this model's foreground + watershed",
                 lmk_ws_own="layer's markers, layer's own foreground + watershed of its maps", bmk_layer="this model's markers, layer's solve",
                 gt_inst="ground truth instances")
MODES = ("logits", "ws", "ws_contour", "ws_dist", "ws_both", "ws_fb", "ws_gtmk", "layer", "lmk_ws", "lmk_ws_own", "bmk_layer", "gt_inst")


def fmt(v, k=None):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "–"
    return f"{v:.1f}" if k == "n_pred_mean" else f"{v:.3f}"


def row(label, t, cols=COLS):
    return f"| {label} | {t.get('n', '')} | " + " | ".join(fmt(t.get(c[0]), c[0]) for c in cols) + " |"


def sub(per, mode):
    return {k.split("__", 1)[1]: v for k, v in per.items() if k.startswith(mode + "__")}


def inst_agg(s, sel=None):
    g = (lambda k: s[f"inst_{k}"] if sel is None else s[f"inst_{k}"][sel])
    tp, fp, fn, iou_sum = g("tp").sum(), g("fp").sum(), g("fn").sum(), g("iou_sum").sum()
    f1 = 2 * tp / max(2 * tp + fp + fn, 1); pq = iou_sum / max(tp + 0.5 * fp + 0.5 * fn, 1e-9)
    aji = g("aji_num").sum() / max(g("aji_den").sum(), 1e-9)
    ce = float(np.mean(np.abs(g("n_pred") - g("n_gt")) / np.maximum(g("n_gt"), 1)))
    return dict(f1_05=f1, pq=pq, sq=iou_sum / max(tp, 1), aji=aji, count_err=ce, n_pred=float(g("n_pred").mean()))


def boot_idx(n, B=1000, seed=0):
    return np.random.default_rng(seed).integers(0, n, (B, n))


def paired(a, b, idx, pix=("iou", "bf2", "edge_align"), inst=("f1_05", "pq", "aji")):
    cells = []
    for m in pix:
        if m not in a or m not in b:
            cells.append("–"); continue
        d = a[m] - b[m]; ok = ~np.isnan(d); d = d[ok]
        ii = idx if idx.shape[1] == d.size else boot_idx(d.size, idx.shape[0])
        means = d[ii].mean(1)
        cells.append(f"{d.mean():+.3f} [{np.percentile(means, 2.5):+.3f}, {np.percentile(means, 97.5):+.3f}]")
    for m in inst:
        full = inst_agg(a)[m] - inst_agg(b)[m]
        diffs = np.array([inst_agg(a, i)[m] - inst_agg(b, i)[m] for i in idx[:400]])
        cells.append(f"{full:+.3f} [{np.percentile(diffs, 2.5):+.3f}, {np.percentile(diffs, 97.5):+.3f}]")
    return cells


def load(d, name):
    R = json.load(open(os.path.join(d, f"{name}.json")))
    return R, dict(np.load(os.path.join(d, f"{name}_perimage.npz")))


def mk_line(M, label):
    return (f"- {label}: one {100 * M['frac_one']:.1f} %, none {100 * M['frac_zero']:.1f} %, several {100 * M['frac_multi']:.1f} %, "
            f"background {M['bg_per_patch']:.2f} per patch, {M['mk_per_patch']:.1f} markers per patch.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", default="results_pannuke_instances/unet_dist")
    ap.add_argument("--name", default="unet_dist")
    ap.add_argument("--unet", default="results_pannuke")
    ap.add_argument("--ue", default="results_pannuke_leads/unet_edge")
    ap.add_argument("--dist", default="results_pannuke_instances/dist")
    ap.add_argument("--bce", default="results_pannuke_instances/bce_tuned")
    ap.add_argument("--outdir", default=None)
    ap.add_argument("--examples-tag", default="", help="read <name>_examples_<tag>.npz and write examples_<tag>_{crop,full}.png")
    ap.add_argument("--types", nargs="+", default=("Breast", "Colon", "HeadNeck", "Adrenal_gland"))
    ap.add_argument("--no-figures", dest="figures", action="store_false")
    args = ap.parse_args()
    out = args.outdir or os.path.join(args.res, "figures"); os.makedirs(out, exist_ok=True)
    R, per = load(args.res, args.name); T = R["test"]; A = R["args"]
    U, pu = load(args.unet, "unet"); U = U["test"]
    E, pe = load(args.ue, "unet_edge"); E = E["test"]
    D, pd = load(args.dist, "instances"); D = D["test"]
    Bc, pb = load(args.bce, "instances"); Bc = Bc["test"]
    n_run = len(per["ws__iou"])
    for p in (pu, pe, pd, pb):                                    # a --test-n subset: the loader's evenly spaced indices
        n0 = len(p["logits__iou"])
        if n0 != n_run:
            sel = np.linspace(0, n0 - 1, n_run).astype(int)
            for k in list(p):
                if len(p[k]) == n0:
                    p[k] = p[k][sel]
    rel = A["relief"]
    lines = [f"# The fair baseline for the distance-head layer: three-head U-Net + HoVer-Net-style post-processing (fold 1 → fold 2)", "",
             f"Run `{args.res}/{args.name}`: {A['epochs']} epochs, batch {A['batch']}, {'gap' if A.get('gap') else 'binary'} foreground target (BCE), "
             f"edge target ×{A['w_edge']} on the contour head, distance head ×{A['w_mk']} (MSE, rmax {A['mk_rmax']}); post-processing: markers = h-maxima "
             f"h {A['mk_h']} of the predicted distance map grown to thr {A['mk_thr']}, min area {A['mk_min_area']} px, marker watershed of the "
             f"`{rel}` relief inside s > 0.5" + (f", all four chosen by PQ on {R['pp_tune']['n']} patches of fold {R['pp_tune']['fold']}" if R.get("pp_tune") else "") + ".", ""]
    if R.get("pp_tune"):
        tb = R["pp_tune"]["table"]; top = sorted(tb, key=lambda k: -tb[k]["pq"])[:10]
        lines += [f"## Post-processing chosen on fold {R['pp_tune']['fold']} ({R['pp_tune']['n']} patches): {R['pp_tune']['chosen']}", "",
                  "| setting | PQ | F1@0.5 | AJI | count err. | n_pred | one | none | several | bg / patch |", "|---|---|---|---|---|---|---|---|---|---|"]
        for k in top:
            v = tb[k]
            lines.append(f"| {k} | {v['pq']:.3f} | {v['f1_05']:.3f} | {v['aji']:.3f} | {v['count_err']:.3f} | {v['n_pred']:.1f} | "
                         f"{100 * v['frac_one']:.1f} % | {100 * v['frac_zero']:.1f} % | {100 * v['frac_multi']:.1f} % | {v['bg_per_patch']:.2f} |")
        lines.append(f"\n(top {len(top)} of {len(tb)} settings by PQ)\n")
        # best setting per relief, and the layer's marker setting
        lines += ["Best setting per relief, and the layer's own marker setting (thr 0.2 / min area 16 / h 0.2) with each relief:", "",
                  "| setting | PQ | F1@0.5 | AJI | count err. | n_pred |", "|---|---|---|---|---|---|"]
        for r in ("contour", "dist", "both"):
            ks = [k for k in tb if k.endswith("/" + r)]
            if ks:
                k = max(ks, key=lambda k: tb[k]["pq"]); v = tb[k]
                lines.append(f"| best {r}: {k} | {v['pq']:.3f} | {v['f1_05']:.3f} | {v['aji']:.3f} | {v['count_err']:.3f} | {v['n_pred']:.1f} |")
        for r in ("contour", "dist", "both"):
            k = f"thr=0.2/min_area=16/h=0.2/{r}"
            if k in tb:
                v = tb[k]; lines.append(f"| {k} | {v['pq']:.3f} | {v['f1_05']:.3f} | {v['aji']:.3f} | {v['count_err']:.3f} | {v['n_pred']:.1f} |")
        lines.append("")
    # --- main table
    head = "| output | n | " + " | ".join(c[1] for c in COLS) + " |"
    lines += ["## All of fold 2", "", head, "|---|---|" + "---|" * len(COLS)]
    lines.append(row("U-Net (sec. 6, binary target), s > 0.5, components", U["logits"]))
    lines.append(row("U-Net + contour head (sec. 10.1, gap target), logits", E["logits"]))
    lines.append(row("U-Net + contour head, tuned marker watershed (sec. 10.1 b)", E["pp_ws"]))
    lines.append(row("`bce_tuned` layer (sec. 11.1)", Bc["layer"]))
    lines.append(row("`dist` layer, converged (sec. 11.1)", D["layer"]))
    lines.append(row("`dist` layer + fallback markers", D["layer_fb"]))
    lines.append(row("`dist` layer, ground-truth markers (oracle)", D["layer_gtmk"]))
    lines.append(row("`dist` run: marker watershed of its contour map inside its s > 0.5 (sec. 11 `ws` row)", D["ws"]))
    for m in MODES:
        if m in T:
            lines.append(row(f"this model: {MODE_NAME[m]}", T[m]))
    lines.append("")
    # --- marker quality and timing
    M = T.get("markers", {})
    if M:
        lines += ["## Marker quality (predicted markers against the ground-truth nuclei)", "",
                  f"- {M['n_gt']} nuclei in fold 2 ({M['n_gt_per_patch']:.1f} per patch).", mk_line(M, "this model's markers")]
        if "lmarkers" in T:
            lines.append(mk_line(T["lmarkers"], "the `dist` layer's markers (recomputed)"))
        lines.append(mk_line(D["markers"], "the `dist` layer's markers (sec. 11.1 run)"))
        lines.append(mk_line(Bc["markers"], "the `bce_tuned` layer's markers"))
        lines.append("")
    tm = T.get("_timing", {})
    if tm:
        lines += ["## Inference cost", "",
                  f"- U-Net forward: {1000 * tm['unet_s_per_image']:.1f} ms per image; post-processing (markers + the three watersheds, one CPU core): "
                  f"{1000 * tm['post_s_per_image']:.0f} ms per image; the layer's converged solve: {1000 * tm['solve_s_per_image']:.0f} ms per image (GPU).", ""]
    # --- per tissue
    lines += ["## Per tissue type", ""]
    for tt in args.types:
        lines += [f"**{tt}**", "", head, "|---|---|" + "---|" * len(COLS)]
        for lab, t in (("U-Net (sec. 6)", U["logits"]), ("U-Net + contour head, watershed (b)", E["pp_ws"]), ("`bce_tuned` layer", Bc["layer"]),
                       ("`dist` layer", D["layer"]), ("`dist` layer, GT markers", D["layer_gtmk"])):
            if tt in t.get("per_type", {}):
                lines.append(row(lab, t["per_type"][tt]))
        for m in MODES:
            if m in T and tt in T[m].get("per_type", {}):
                lines.append(row(MODE_NAME[m], T[m]["per_type"][tt]))
        lines.append("")
    # --- paired differences
    n = n_run; idx = boot_idx(n)
    ws = sub(per, "ws")
    comps = [("this model's post-processing − `dist` layer", ws, sub(pd, "layer")),
             ("this model's post-processing − `bce_tuned` layer", ws, sub(pb, "layer")),
             ("this model's post-processing − contour-head U-Net, watershed (b)", ws, sub(pe, "pp_ws")),
             ("this model's post-processing − U-Net (sec. 6) logits", ws, sub(pu, "logits")),
             ("this model's post-processing − this model's logits", ws, sub(per, "logits")),
             ("watershed of −distance − watershed of the contour map (same markers)", sub(per, "ws_dist"), sub(per, "ws_contour")),
             ("watershed of contour − distance − watershed of the contour map (same markers)", sub(per, "ws_both"), sub(per, "ws_contour")),
             ("+ unmarked components kept − this model's post-processing", sub(per, "ws_fb"), ws),
             ("ground-truth markers (oracle) − this model's post-processing", sub(per, "ws_gtmk"), ws),
             ("this model's oracle − `dist` layer's oracle", sub(per, "ws_gtmk"), sub(pd, "layer_gtmk"))]
    if "lmk_ws__iou" in per:
        comps += [("layer reproduced − `dist` layer (sanity)", sub(per, "layer"), sub(pd, "layer")),
                  ("layer's markers, this model's watershed − `dist` layer (same markers: watershed vs solve)", sub(per, "lmk_ws"), sub(pd, "layer")),
                  ("layer's markers, layer's own foreground + watershed − `dist` layer (same markers, same foreground)", sub(per, "lmk_ws_own"), sub(pd, "layer")),
                  ("this model's markers, layer's solve − this model's post-processing (same markers: solve vs watershed)", sub(per, "bmk_layer"), ws),
                  ("this model's markers, layer's solve − `dist` layer (same solve: markers swapped)", sub(per, "bmk_layer"), sub(pd, "layer")),
                  ("layer's markers, this model's watershed − this model's post-processing (same watershed: markers swapped)", sub(per, "lmk_ws"), ws)]
    lines += [f"## Paired per-patch differences ({n} patches; bootstrap 95 % intervals; F1 / PQ / AJI dataset-level, bootstrapped over patches)", "",
              "| comparison | IoU | BF₂ | edge align. | F1@0.5 | PQ | AJI |", "|---|---|---|---|---|---|---|"]
    for lab, a, b in comps:
        lines.append(f"| {lab} | " + " | ".join(paired(a, b, idx)) + " |")
    lines.append("")
    # --- by crowding
    ngt = per["ws__inst_n_gt"]
    bins = [("< 10 nuclei", ngt < 10), ("10–30", (ngt >= 10) & (ngt < 30)), ("30–60", (ngt >= 30) & (ngt < 60)), ("> 60", ngt >= 60)]
    cross = "lmk_ws__iou" in per
    hdr = ["U-Net (sec. 6)", "contour-head U-Net, watershed (b)", "`dist` layer", "this model: post-processing", "+ unmarked kept", "oracle markers"]
    srcs = [sub(pu, "logits"), sub(pe, "pp_ws"), sub(pd, "layer"), ws, sub(per, "ws_fb"), sub(per, "ws_gtmk")]
    if cross:
        hdr += ["layer's markers, watershed", "this model's markers, layer's solve"]; srcs += [sub(per, "lmk_ws"), sub(per, "bmk_layer")]
    lines += ["## By crowding (F1@0.5 / PQ / count error)", "", "| patches | n | " + " | ".join(hdr) + " |", "|---|---|" + "---|" * len(hdr)]
    for lab, sel in bins:
        def cell(s, sl):
            if sl.sum() == 0:
                return "–"
            a = inst_agg(s, sl); return f"{a['f1_05']:.3f} / {a['pq']:.3f} / {a['count_err']:.2f}"
        lines.append(f"| {lab} | {int(sel.sum())} | " + " | ".join(cell(s, sel) for s in srcs) + " |")
    lines.append("")
    lines += ["## Marker quality by crowding (nuclei with one / none / several markers; background markers per patch)", "",
              "| patches | this model: one | none | several | bg / patch | `dist` layer: one | none | several | bg / patch |", "|---|---|---|---|---|---|---|---|---|"]
    for lab, sel in bins:
        cells = []
        for p, key in ((per, "markers"), (pd, "markers")):
            g = max(p[f"{key}__n_gt"][sel].sum(), 1)
            cells += [f"{100 * p[f'{key}__one'][sel].sum() / g:.1f} %", f"{100 * p[f'{key}__zero'][sel].sum() / g:.1f} %",
                      f"{100 * p[f'{key}__multi'][sel].sum() / g:.1f} %", f"{p[f'{key}__bg_mk'][sel].mean():.2f}"]
        lines.append(f"| {lab} | " + " | ".join(cells) + " |")
    lines.append("")
    # --- per-tissue summary line (IoU / F1 / PQ) for the report
    lines += ["## Per tissue (IoU / F1 / PQ): this model's post-processing vs the `dist` layer vs watershed (b)", ""]
    for tt in sorted(T["ws"].get("per_type", {})):
        a, b, c = T["ws"]["per_type"][tt], D["layer"]["per_type"].get(tt), E["pp_ws"]["per_type"].get(tt)
        f = lambda t: f"{t['iou']:.3f} / {t['f1_05']:.3f} / {t['pq']:.3f}" if t else "–"
        lines.append(f"- {tt} ({a['n']}): {f(a)} vs {f(b)} vs {f(c)}")
    lines.append("")
    open(os.path.join(out, "summary.md"), "w").write("\n".join(lines))
    print("\n".join(lines))
    if not args.figures:
        return

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from plot_instances import inst_cmap
    from plot_pannuke import crop_centre, touching_mask
    log = R["log"]
    if log:
        fig, ax = plt.subplots(1, 2, figsize=(9, 3.4))
        ep = [e["epoch"] for e in log]
        for k in ("loss_fg", "loss_edge", "loss_mk"):
            ax[0].plot(ep, [e[k] for e in log], label=k[5:])
        ax[0].set_title("training losses"); ax[0].legend(); ax[0].set_xlabel("epoch"); ax[0].set_yscale("log")
        ve = [e for e in log if "val" in e]
        if ve:
            x = [e["epoch"] for e in ve]
            ax[1].plot(x, [e["val"]["ws"]["f1_05"] for e in ve], "o-", label="post-processed F1@0.5")
            ax[1].plot(x, [e["val"]["ws"]["pq"] for e in ve], "s-", label="post-processed PQ")
            ax[1].plot(x, [e["val"]["logits"]["f1_05"] for e in ve], "o--", label="logits F1@0.5")
            ax[1].plot(x, [e["val"]["logits"]["iou"] for e in ve], "x--", label="logits IoU")
            ax[1].plot(x, [e["val"]["markers"]["frac_one"] for e in ve], "^-", label="nuclei with one marker")
            ax[1].set_title("validation (first %d test patches, default post-processing)" % A["val_n"]); ax[1].legend(fontsize=8); ax[1].set_xlabel("epoch")
        fig.tight_layout(); fig.savefig(os.path.join(out, "training.png"), dpi=120); plt.close(fig)
    exf = os.path.join(args.res, f"{args.name}_examples{'_' + args.examples_tag if args.examples_tag else ''}.npz")
    if os.path.exists(exf):
        ex = np.load(exf)
        ids = sorted({int(k.split("__")[0]) for k in ex.files})
        cols = [("img", "image"), ("inst", "GT instances"), ("m", "distance map + markers"), ("c", "contour map"), ("logits", "s > 0.5, components"),
                ("L_ws", f"post-processed ({rel})"), ("L_ws_dist" if rel != "dist" else "L_ws_contour", "watershed of −distance" if rel != "dist" else "watershed of contour"),
                ("L_ws_fb", "+ unmarked kept"), ("L_gtmk", "GT markers"), ("L_layer", "dist layer (sec. 11.1)"),
                ("L_lmk_ws_own", "layer's markers, watershed"), ("L_bmk_layer", "this model's markers, layer's solve")]
        cols = [c for c in cols if c[0] in ("img", "inst", "m", "c", "logits") or f"{ids[0]}__{c[0]}" in ex.files]
        for radius, tag in ((32, "crop"), (128, "full")):
            fig, axes = plt.subplots(len(ids), len(cols), figsize=(2.0 * len(cols), 2.0 * len(ids)))
            axes = np.atleast_2d(axes)
            for r, i in enumerate(ids):
                g = lambda k: ex[f"{i}__{k}"]
                inst = g("inst"); cy, cx = crop_centre(touching_mask(inst)) if radius < 128 else (128, 128)
                y0, x0 = min(max(cy - radius, 0), 256 - 2 * radius), min(max(cx - radius, 0), 256 - 2 * radius)
                sl = (slice(y0, y0 + 2 * radius), slice(x0, x0 + 2 * radius))
                img = g("img").transpose(1, 2, 0)[sl]
                for c, (k, title) in enumerate(cols):
                    a = axes[r, c]; a.set_xticks([]); a.set_yticks([])
                    if k == "img":
                        a.imshow(img)
                    elif k == "m":
                        a.imshow(g("m")[sl], cmap="gray", vmin=0, vmax=1)
                        a.contour(g("lab")[sl] > 0, levels=[0.5], colors="r", linewidths=0.6)
                    elif k == "c":
                        a.imshow(g("c")[sl], cmap="gray", vmin=0, vmax=1)
                    elif k == "logits":
                        L = ndimage.label(g("s") > 0.5, structure=ndimage.generate_binary_structure(2, 1))[0][sl]
                        a.imshow(L, cmap=inst_cmap(int(L.max()), seed=1), interpolation="nearest")
                    else:
                        L = g(k)[sl]
                        a.imshow(L, cmap=inst_cmap(int(max(L.max(), 1)), seed=r + c), interpolation="nearest")
                    if k not in ("img", "m", "c"):
                        a.contour(inst[sl] > 0, levels=[0.5], colors="k", linewidths=0.4, alpha=0.6)
                    if r == 0:
                        a.set_title(title, fontsize=7)
                    if c == 0:
                        a.set_ylabel(f"#{i}" + (f" {str(g('type'))[:8]}" if f"{i}__type" in ex.files else ""), fontsize=8)
            fig.tight_layout(pad=0.2); fig.savefig(os.path.join(out, f"examples_{args.examples_tag + '_' if args.examples_tag else ''}{tag}.png"), dpi=130); plt.close(fig)
    print("figures in", out)


if __name__ == "__main__":
    main()
