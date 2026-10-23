#!/usr/bin/env python3
"""Section 11: tables, paired statistics and figures for the multi-marker (instances-as-labels)
layer, exp_instance_pannuke.py, against the plain U-Net + components pipeline (section 6,
results_pannuke/unet) and the contour-head U-Net + tuned watershed (section 10.1,
results_pannuke_leads/unet_edge).  Runs where the per-image npz files and matplotlib are
(jacobian); writes <res>/figures/summary.md and the figures.

usage: plot_instances.py --res results_pannuke_instances --unet results_pannuke --ue results_pannuke_leads/unet_edge
       plot_instances.py --res results_pannuke_instances/dist --ref results_pannuke_instances   (section 11.1: paired
       against the section 11 run as well)
"""
import argparse, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from scipy import ndimage
from plot_pannuke import crop_centre, touching_mask

MODE_NAME = dict(logits="s > 0.5, components", layer="layer, converged (predicted markers)",
                 layer_fb="layer + fallback markers", layer_gtmk="layer, ground-truth markers (oracle)",
                 layer_img="layer, image-gradient costs", ws="marker watershed on the contour map",
                 limit="PW limit, learned costs", limit_img="PW limit, image-gradient costs",
                 gt_inst="ground truth instances")
MODES = ("logits", "layer", "layer_fb", "layer_gtmk", "layer_img", "ws", "limit", "limit_img", "gt_inst")
COLS = (("iou", "IoU"), ("bf1", "BF₁"), ("bf2", "BF₂"), ("band_acc", "band acc."), ("edge_align", "edge align."),
        ("f1_05", "F1@0.5"), ("pq", "PQ"), ("aji", "AJI"), ("count_err", "count err."), ("n_pred_mean", "n_pred"))


def fmt(v, k=None):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "–"
    if k == "n_pred_mean":
        return f"{v:.1f}"
    return f"{v:.3f}"


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
    return dict(f1_05=f1, pq=pq, aji=aji, count_err=ce, n_pred=float(g("n_pred").mean()))


def boot_idx(n, B=1000, seed=0):
    return np.random.default_rng(seed).integers(0, n, (B, n))


def paired(a, b, idx, pix=("iou", "bf2", "edge_align"), inst=("f1_05", "pq", "aji")):
    cells = []
    for m in pix:
        if m not in a or m not in b:
            cells.append("–"); continue
        d = a[m] - b[m]; ok = ~np.isnan(d); d = d[ok]
        if idx.shape[1] != d.size:
            ii = boot_idx(d.size, idx.shape[0])
        else:
            ii = idx
        means = d[ii].mean(1)
        cells.append(f"{d.mean():+.3f} [{np.percentile(means, 2.5):+.3f}, {np.percentile(means, 97.5):+.3f}]")
    for m in inst:
        full = inst_agg(a)[m] - inst_agg(b)[m]
        diffs = np.array([inst_agg(a, i)[m] - inst_agg(b, i)[m] for i in idx[:400]])
        cells.append(f"{full:+.3f} [{np.percentile(diffs, 2.5):+.3f}, {np.percentile(diffs, 97.5):+.3f}]")
    return cells


def inst_cmap(n, seed=0):
    rng = np.random.default_rng(seed)
    cols = rng.random((max(n, 1) + 1, 3)) * 0.75 + 0.25
    cols[0] = 1.0
    return ListedColormap(cols)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", default="results_pannuke_instances")
    ap.add_argument("--name", default="instances")
    ap.add_argument("--unet", default="results_pannuke")
    ap.add_argument("--ue", default="results_pannuke_leads/unet_edge")
    ap.add_argument("--ref", default="", help="section 11 run directory: adds its layer row and paired comparisons")
    ap.add_argument("--ref-name", default="instances")
    ap.add_argument("--ref-label", default="sec. 11 run", help="how the --ref run is named in the tables")
    ap.add_argument("--outdir", default=None)
    ap.add_argument("--examples-tag", default="", help="read <name>_examples_<tag>.npz and write examples_<tag>_{crop,full}.png")
    ap.add_argument("--types", nargs="+", default=("Breast", "Colon", "HeadNeck", "Adrenal_gland"))
    args = ap.parse_args()
    out = args.outdir or os.path.join(args.res, "figures"); os.makedirs(out, exist_ok=True)
    R = json.load(open(os.path.join(args.res, f"{args.name}.json"))); T = R["test"]
    per = dict(np.load(os.path.join(args.res, f"{args.name}_perimage.npz")))
    n_run = len(per["layer__iou"])
    U = E = None                                                  # the fold-2 baselines of sections 6 and 10.1 (--unet "" to skip, other test folds)
    if args.unet and args.ue:
        U = json.load(open(os.path.join(args.unet, "unet.json")))["test"]; pu = dict(np.load(os.path.join(args.unet, "unet_perimage.npz")))
        E = json.load(open(os.path.join(args.ue, "unet_edge.json")))["test"]; pe = dict(np.load(os.path.join(args.ue, "unet_edge_perimage.npz")))
        n_base = len(pu["logits__iou"])
        if n_run != n_base:                                       # a --test-n subset: the loader's evenly spaced indices
            sel = np.linspace(0, n_base - 1, n_run).astype(int)
            pu = {k: (v[sel] if len(v) == n_base else v) for k, v in pu.items()}; pe = {k: (v[sel] if len(v) == n_base else v) for k, v in pe.items()}
    Rr = Tr = pr = None
    if args.ref:
        Rr = json.load(open(os.path.join(args.ref, f"{args.ref_name}.json"))); Tr = Rr["test"]
        pr = dict(np.load(os.path.join(args.ref, f"{args.ref_name}_perimage.npz")))
        n_ref = len(pr["layer__iou"])
        if n_ref != n_run:
            sel = np.linspace(0, n_ref - 1, n_run).astype(int); pr = {k: (v[sel] if len(v) == n_ref else v) for k, v in pr.items()}
    A = R["args"]
    mk = f"marker head `{A.get('mk_head', 'bce')}`"
    if A.get("mk_head", "bce") == "dist":
        mk += f" ({A.get('mk_loss', 'mse')}, rmax {A.get('mk_rmax')}; markers = h-maxima h {A.get('mk_h')} grown to thr {A['mk_thr']}, min area {A['mk_min_area']} px)"
    else:
        mk += f" (thr {A['mk_thr']}, min area {A['mk_min_area']} px)"
    if R.get("mk_tune"):
        mk += f", chosen by PQ on {R['mk_tune']['n']} patches of fold {R['mk_tune']['fold']}"
    lines = [f"# Instances as labels: multi-marker layer on PanNuke (fold {A['train_fold']} → fold {A['test_fold']})", "",
             f"Run `{args.res}/{args.name}`: p {A['p0']} → {A['p1']}, erosion {A['erode']}, edge target ×{A['w_edge']}, "
             f"seam weight {A['w_seam']}, {A['epochs']} epochs, seed {A.get('seed', 0)}, training solve tol {A['tol']} / maxit {A['maxit']}"
             + (f", peak loss ×{A['w_peak']}" if A.get('w_peak') else "")
             + (f", training markers predicted from epoch {A['mk_sched'][0]} (all from {A['mk_sched'][1]}; thr {A.get('mk_train_thr')} / "
                f"min area {A.get('mk_train_min_area')} / h {A.get('mk_train_h')}, unmarked nuclei: {A.get('mk_unmarked')})" if A.get("mk_sched") else "")
             + f"; {mk}; "
             f"learned edge scale {T.get('_edge_scale', float('nan')):.2f}.", ""]
    if R.get("mk_tune"):
        tb = R["mk_tune"]["table"]; top = sorted(tb, key=lambda k: -tb[k]["pq"])[:8]
        lines += [f"## Marker post-processing chosen on fold {R['mk_tune']['fold']} ({R['mk_tune']['n']} patches): {R['mk_tune']['chosen']}", "",
                  "| setting | PQ | F1@0.5 | AJI | count err. | n_pred | one | none | several | bg / patch |", "|---|---|---|---|---|---|---|---|---|---|"]
        for k in top:
            v = tb[k]
            lines.append(f"| {k} | {v['pq']:.3f} | {v['f1_05']:.3f} | {v['aji']:.3f} | {v['count_err']:.3f} | {v['n_pred']:.1f} | "
                         f"{100 * v['frac_one']:.1f} % | {100 * v['frac_zero']:.1f} % | {100 * v['frac_multi']:.1f} % | {v['bg_per_patch']:.2f} |")
        dflt = [k for k in tb if k in ("thr=0.5/min_area=1", "thr=0.5/min_area=1/h=0.1")]
        for k in dflt:
            if k not in top:
                v = tb[k]
                lines.append(f"| {k} (untuned default) | {v['pq']:.3f} | {v['f1_05']:.3f} | {v['aji']:.3f} | {v['count_err']:.3f} | {v['n_pred']:.1f} | "
                             f"{100 * v['frac_one']:.1f} % | {100 * v['frac_zero']:.1f} % | {100 * v['frac_multi']:.1f} % | {v['bg_per_patch']:.2f} |")
        lines.append(f"\n(top {len(top)} of {len(tb)} settings by PQ)\n")
    # --- main table
    head = "| output | n | " + " | ".join(c[1] for c in COLS) + " |"
    lines += [f"## All of fold {A['test_fold']}", "", head, "|---|---|" + "---|" * len(COLS)]
    if U is not None:
        lines.append(row("U-Net (sec. 6, binary target), s > 0.5, components", U["logits"]))
        lines.append(row("U-Net + contour head (sec. 10.1, gap target), logits", E["logits"]))
        lines.append(row("U-Net + contour head, tuned marker watershed (b)", E["pp_ws"]))
    if Tr is not None:
        lines.append(row(f"{args.ref_label}: layer, converged (predicted markers)", Tr["layer"]))
    for m in MODES:
        if m in T:
            lines.append(row(f"this model: {MODE_NAME[m]}", T[m]))
    lines.append("")
    # --- marker quality and timing
    M = T.get("markers", {})
    if M:
        lines += ["## Marker quality (predicted markers against the ground-truth nuclei)", "",
                  f"- {M['n_gt']} nuclei in fold 2 ({M['n_gt_per_patch']:.1f} per patch); predicted markers {M['mk_per_patch']:.1f} per patch.",
                  f"- exactly one marker: {100 * M['frac_one']:.1f} %; none: {100 * M['frac_zero']:.1f} %; several: {100 * M['frac_multi']:.1f} %; "
                  f"markers in background: {M['bg_per_patch']:.2f} per patch."]
        if "fb_frac_one" in M:
            lines.append(f"- with fallback markers: one {100 * M['fb_frac_one']:.1f} %, none {100 * M['fb_frac_zero']:.1f} %, several "
                         f"{100 * M['fb_frac_multi']:.1f} %, background {M['fb_bg_per_patch']:.2f} per patch, {M['fb_mk_per_patch']:.1f} markers per patch.")
        if Tr is not None and "markers" in Tr:
            Mr = Tr["markers"]
            lines.append(f"- {args.ref_label}: one {100 * Mr['frac_one']:.1f} %, none {100 * Mr['frac_zero']:.1f} %, several {100 * Mr['frac_multi']:.1f} %, "
                         f"background {Mr['bg_per_patch']:.2f} per patch, {Mr['mk_per_patch']:.1f} markers per patch.")
        lines.append("")
    tm = T.get("_timing", {})
    if tm:
        lim = tm.get("limit", {})
        lines += ["## Inference cost", "",
                  f"- U-Net forward: {1000 * tm['unet_s_per_image']:.1f} ms per image; converged multi-marker solve (tol {R['args']['eval_tol']}): "
                  f"{1000 * tm['solve_s_per_image']:.1f} ms per image at K = {tm['K_per_image']:.1f} markers per image "
                  f"({tm['systems']} systems in {tm['batches']} batches of {R['args']['batch']}; {tm['iters_per_batch']:.0f} PCG iterations per batch).",
                  f"- exact K-label PW limit (one CPU core): {lim.get('learned_per_patch', float('nan')):.1f} s per patch with the learned costs, "
                  f"{lim.get('img_per_patch', float('nan')):.1f} s with image-gradient costs, K = {lim.get('K_per_patch', float('nan')):.1f}; "
                  f"{lim.get('solved_plateaus', 0)} ambiguous plateaus solved over {lim.get('n', 0)} patches.", ""]
    # --- per tissue
    lines += ["## Per tissue type", ""]
    for tt in args.types:
        lines += [f"**{tt}**", "", head, "|---|---|" + "---|" * len(COLS)]
        if U is not None and tt in U["logits"].get("per_type", {}):
            lines.append(row("U-Net (sec. 6)", U["logits"]["per_type"][tt]))
        if E is not None and tt in E["pp_ws"].get("per_type", {}):
            lines.append(row("U-Net + contour head, watershed (b)", E["pp_ws"]["per_type"][tt]))
        if Tr is not None and tt in Tr["layer"].get("per_type", {}):
            lines.append(row(f"{args.ref_label}: layer", Tr["layer"]["per_type"][tt]))
        for m in MODES:
            if m in T and tt in T[m].get("per_type", {}):
                lines.append(row(MODE_NAME[m], T[m]["per_type"][tt]))
        lines.append("")
    # --- paired differences
    n = len(per["layer__iou"]); idx = boot_idx(n)
    comps = []
    if U is not None:
        comps += [("layer − U-Net (sec. 6) logits", sub(per, "layer"), sub(pu, "logits")),
                  ("layer − contour-head U-Net, watershed (b)", sub(per, "layer"), sub(pe, "pp_ws"))]
    if pr is not None:
        comps += [(f"layer − {args.ref_label} layer", sub(per, "layer"), sub(pr, "layer")),
                  (f"layer, ground-truth markers − {args.ref_label} layer, ground-truth markers", sub(per, "layer_gtmk"), sub(pr, "layer_gtmk"))]
    comps += [
             ("layer − this model's own logits", sub(per, "layer"), sub(per, "logits")),
             ("layer − marker watershed, same markers", sub(per, "layer"), sub(per, "ws")),
             ("layer − layer with image costs", sub(per, "layer"), sub(per, "layer_img"))]
    if "layer_fb__iou" in per:
        if U is not None:
            comps += [("layer + fallback − U-Net (sec. 6) logits", sub(per, "layer_fb"), sub(pu, "logits")),
                      ("layer + fallback − contour-head U-Net, watershed (b)", sub(per, "layer_fb"), sub(pe, "pp_ws"))]
        comps += [("layer + fallback − layer", sub(per, "layer_fb"), sub(per, "layer"))]
    comps.append(("layer, ground-truth markers − layer", sub(per, "layer_gtmk"), sub(per, "layer")))
    lines += [f"## Paired per-patch differences ({n} patches; bootstrap 95 % intervals; F1 / PQ / AJI dataset-level, bootstrapped over patches)", "",
              "| comparison | IoU | BF₂ | edge align. | F1@0.5 | PQ | AJI |", "|---|---|---|---|---|---|---|"]
    for lab, a, b in comps:
        lines.append(f"| {lab} | " + " | ".join(paired(a, b, idx)) + " |")
    if "limit__iou" in per:
        li = per["limit__idx"]; ids = boot_idx(len(li))
        lay = {k: v[li] for k, v in sub(per, "layer").items()}
        lines.append(f"| on the {len(li)} limit patches: PW limit (learned) − layer | " + " | ".join(paired(sub(per, "limit"), lay, ids)) + " |")
        lines.append(f"| on the {len(li)} limit patches: PW limit (learned) − PW limit (image costs) | " + " | ".join(paired(sub(per, "limit"), sub(per, "limit_img"), ids)) + " |")
        if U is not None:
            lines.append(f"| on the {len(li)} limit patches: PW limit (learned) − U-Net (sec. 6) logits | " + " | ".join(paired(sub(per, "limit"), {k: v[li] for k, v in sub(pu, 'logits').items()}, ids)) + " |")
    lines.append("")
    # --- by crowding
    ngt = per["layer__inst_n_gt"]
    bins = [("< 10 nuclei", ngt < 10), ("10–30", (ngt >= 10) & (ngt < 30)), ("30–60", (ngt >= 30) & (ngt < 60)), ("> 60", ngt >= 60)]
    lines += ["## By crowding (F1@0.5 / PQ / count error)", "", "| patches | n | U-Net (sec. 6) | contour-head U-Net, watershed (b) | layer | layer + fallback | marker watershed, same markers | PW limit (learned, subset) |",
              "|---|---|---|---|---|---|---|---|"]
    for lab, sel in bins:
        def cell(s, sl):
            if sl.sum() == 0:
                return "–"
            a = inst_agg(s, sl); return f"{a['f1_05']:.3f} / {a['pq']:.3f} / {a['count_err']:.2f}"
        cells = [cell(sub(pu, "logits"), sel) if U is not None else "–", cell(sub(pe, "pp_ws"), sel) if E is not None else "–", cell(sub(per, "layer"), sel),
                 cell(sub(per, "layer_fb"), sel) if "layer_fb__iou" in per else "–", cell(sub(per, "ws"), sel)]
        if "limit__iou" in per:
            li = per["limit__idx"]; cells.append(cell(sub(per, "limit"), sel[li]))
        else:
            cells.append("–")
        lines.append(f"| {lab} | {int(sel.sum())} | " + " | ".join(cells) + " |")
    lines.append("")
    # marker quality by crowding
    if "markers__n_gt" in per:
        lines += ["## Marker quality by crowding (nuclei with one / none / several markers; background markers per patch)", "",
                  "| patches | one | none | several | bg markers / patch |", "|---|---|---|---|---|"]
        for lab, sel in bins:
            g = max(per["markers__n_gt"][sel].sum(), 1)
            lines.append(f"| {lab} | {100 * per['markers__one'][sel].sum() / g:.1f} % | {100 * per['markers__zero'][sel].sum() / g:.1f} % | "
                         f"{100 * per['markers__multi'][sel].sum() / g:.1f} % | {per['markers__bg_mk'][sel].mean():.2f} |")
        lines.append("")
    open(os.path.join(out, "summary.md"), "w").write("\n".join(lines))
    print("\n".join(lines))

    # --- training curves
    log = R["log"]
    if log:
        fig, ax = plt.subplots(1, 4, figsize=(16, 3.4))
        ep = [e["epoch"] for e in log]
        for k in ("loss_ce", "loss_aux", "loss_mk", "loss_edge"):
            ax[0].plot(ep, [e[k] for e in log], label=k[5:])
        ax[0].set_title("training losses"); ax[0].legend(); ax[0].set_xlabel("epoch")
        ax[1].plot(ep, [e["iters"] for e in log]); ax[1].set_title("PCG iterations per batch (tol %g)" % R["args"]["tol"]); ax[1].set_xlabel("epoch")
        a2 = ax[1].twinx(); a2.plot(ep, [e["p"] for e in log], "k:", label="p"); a2.set_ylabel("p")
        ax[2].plot(ep, [e["edge_scale"] for e in log]); ax[2].set_title("edge-cost scale"); ax[2].set_xlabel("epoch")
        ve = [e for e in log if "val" in e]
        if ve:
            x = [e["epoch"] for e in ve]
            ax[3].plot(x, [e["val"]["layer"]["f1_05"] for e in ve], "o-", label="layer F1@0.5")
            ax[3].plot(x, [e["val"]["layer"]["pq"] for e in ve], "s-", label="layer PQ")
            ax[3].plot(x, [e["val"]["logits"]["f1_05"] for e in ve], "o--", label="logits F1@0.5")
            ax[3].plot(x, [e["val"]["markers"]["frac_one"] for e in ve], "^-", label="nuclei with one marker")
            ax[3].set_title("validation (first %d test patches)" % R["args"]["val_n"]); ax[3].legend(fontsize=8); ax[3].set_xlabel("epoch")
        fig.tight_layout(); fig.savefig(os.path.join(out, "training.png"), dpi=120); plt.close(fig)

    # --- example crops around the densest cluster of touching nuclei
    exf = os.path.join(args.res, f"{args.name}_examples{'_' + args.examples_tag if args.examples_tag else ''}.npz")
    if os.path.exists(exf):
        ex = np.load(exf)
        ids = sorted({int(k.split("__")[0]) for k in ex.files})
        cols = [("img", "image"), ("inst", "GT instances"), ("m", "marker map + markers"), ("logits", "s > 0.5, components"),
                ("L_layer", "layer (pred. markers)"), ("L_layer_fb", "layer + fallback"), ("L_limit", "PW limit, learned"),
                ("L_limit_img", "PW limit, image costs"), ("L_ws", "marker watershed"), ("L_gtmk", "layer, GT markers")]
        cols = [c for c in cols if c[0] in ("img", "inst", "m", "logits") or f"{ids[0]}__{c[0]}" in ex.files]
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
                        lab = g("lab")[sl]
                        a.contour(lab > 0, levels=[0.5], colors="r", linewidths=0.6)
                    elif k == "logits":
                        L = ndimage.label(g("s") > 0.5, structure=ndimage.generate_binary_structure(2, 1))[0][sl]
                        a.imshow(L, cmap=inst_cmap(int(L.max()), seed=1), interpolation="nearest")
                    else:
                        L = g(k)[sl]
                        a.imshow(L, cmap=inst_cmap(int(max(L.max(), 1)), seed=r + c), interpolation="nearest")
                    if k not in ("img", "m"):
                        a.contour(inst[sl] > 0, levels=[0.5], colors="k", linewidths=0.4, alpha=0.6)
                    if r == 0:
                        a.set_title(title, fontsize=8)
                    if c == 0:
                        a.set_ylabel(f"#{i}" + (f" {str(g('type'))[:8]}" if f"{i}__type" in ex.files else ""), fontsize=8)
            fig.tight_layout(pad=0.2); fig.savefig(os.path.join(out, f"examples_{args.examples_tag + '_' if args.examples_tag else ''}{tag}.png"), dpi=130); plt.close(fig)
    print("figures in", out)


if __name__ == "__main__":
    main()
