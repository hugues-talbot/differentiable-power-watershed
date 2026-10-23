#!/usr/bin/env python3
"""Tables, training curves and example panels for exp_unet_seg.py on PanNuke.

usage: plot_pannuke.py results/pannuke --outdir results/pannuke/figures
       plot_pannuke.py results/pannuke/gap --runs unet=unet_gap.json rw_p50=rw_learned_gap_p50.json ...
(--runs: label=json file in resdir; the examples npz is looked up next to each json)
"""
import argparse, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from scipy import ndimage

VARIANTS = ("unet", "rw_img", "rw_learned", "unet_edge")
MODES = ("logits", "layer", "converged", "limit", "pp_contour", "pp_ws", "pp_wsc")
MODE_NAME = dict(logits="logits", layer="layer, 20 steps", converged="converged", limit="PW limit",
                 pp_contour="logits − contour", pp_ws="watershed (seg markers)", pp_wsc="watershed (contour markers)")
PIX = (("iou", "IoU"), ("bf1", "BF₁"), ("bf2", "BF₂"), ("bf3", "BF₃"), ("band_acc", "band acc."),
       ("soft_frac", "soft px"), ("edge_align", "edge align."))
INST = (("f1_05", "F1@0.5"), ("pq", "PQ"), ("aji", "AJI"), ("count_err", "count err."), ("count_bias", "count bias"))


def fmt(v, k):
    if k in ("soft_frac",):
        return f"{100 * v:.1f} %"
    if k == "count_bias":
        return f"{v:+.1f}"
    return f"{v:.3f}"


def table(runs, key=None, cols=PIX + INST, title=None):
    head = "| variant | output | n | " + " | ".join(c[1] for c in cols) + " |"
    lines = ([f"**{title}**", ""] if title else []) + [head, "|---|---|---|" + "---|" * len(cols)]
    for v, r in runs.items():
        for mode in MODES:
            if mode in r["test"]:
                t = r["test"][mode] if key is None else r["test"][mode]["per_type"].get(key)
                if t is None:
                    continue
                lines.append(f"| {v} | {MODE_NAME[mode]} | {t['n']} | " + " | ".join(fmt(t[c[0]], c[0]) for c in cols) + " |")
    r = next(iter(runs.values()))
    if "gt_binary" in r["test"]:
        t = r["test"]["gt_binary"] if key is None else r["test"]["gt_binary"]["per_type"][key]
        lines.append(f"| ground truth | binary mask | {t['n']} | " + " | ".join(fmt(t[c[0]], c[0]) for c in cols) + " |")
    return "\n".join(lines) + "\n"


def inst_cmap(n, seed=0):
    rng = np.random.default_rng(seed)
    cols = rng.random((max(n, 1) + 1, 3)) * 0.8 + 0.2
    cols[0] = 1.0
    return ListedColormap(cols)


def touching_mask(inst):
    t = np.zeros(inst.shape, bool)
    a, b = inst[:, 1:], inst[:, :-1]; d = (a != b) & (a > 0) & (b > 0); t[:, 1:] |= d; t[:, :-1] |= d
    a, b = inst[1:, :], inst[:-1, :]; d = (a != b) & (a > 0) & (b > 0); t[1:, :] |= d; t[:-1, :] |= d
    return t


def crop_centre(touch, radius=12):
    """Centre of the densest cluster of touching-interface pixels."""
    if not touch.any():
        return 128, 128
    dens = ndimage.uniform_filter(touch.astype(float), 2 * radius + 1)
    cy, cx = np.unravel_index(dens.argmax(), dens.shape)
    return int(cy), int(cx)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("resdir")
    ap.add_argument("--outdir", default=None)
    ap.add_argument("--types", nargs="+", default=("Breast", "Colon", "HeadNeck"))
    ap.add_argument("--runs", nargs="+", default=None, help="label=file.json (in resdir); default: the three variants")
    args = ap.parse_args()
    outdir = args.outdir or os.path.join(args.resdir, "figures")
    os.makedirs(outdir, exist_ok=True)
    if args.runs:
        files = dict(r.split("=", 1) for r in args.runs)
    else:
        files = {v: f"{v}.json" for v in VARIANTS if os.path.exists(os.path.join(args.resdir, f"{v}.json"))}
    runs = {v: json.load(open(os.path.join(args.resdir, f))) for v, f in files.items()}

    # --- tables
    md = table(runs, title="All of fold 2")
    for t in args.types:
        md += "\n" + table(runs, key=t, cols=(("iou", "IoU"), ("bf1", "BF₁"), ("bf2", "BF₂"), ("edge_align", "edge align."),
                                              ("f1_05", "F1@0.5"), ("pq", "PQ"), ("aji", "AJI"), ("count_err", "count err.")),
                           title=t)
    open(os.path.join(outdir, "summary.md"), "w").write(md)
    print(md)

    # --- training curves
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.2))
    for v, r in runs.items():
        ep = [e["epoch"] for e in r["log"]]
        axs[0].plot(ep, [e["loss"] for e in r["log"]], label=v)
        ev = [e for e in r["log"] if "val" in e]
        for mode in ("logits", "layer"):
            if ev and mode in ev[0]["val"]:
                axs[1].plot([e["epoch"] for e in ev], [e["val"][mode]["iou"] for e in ev], "o-", label=f"{v} / {mode}")
                axs[2].plot([e["epoch"] for e in ev], [e["val"][mode]["soft_frac"] for e in ev], "o-", label=f"{v} / {mode}")
    axs[0].set_ylabel("training loss"); axs[1].set_ylabel("IoU (400 test patches)"); axs[2].set_ylabel("fraction of soft pixels")
    for ax in axs:
        ax.set_xlabel("epoch"); ax.grid(alpha=0.3); ax.legend(fontsize=7)
    rw = next((r for v, r in runs.items() if r["args"]["variant"] not in ("unet", "unet_edge")), None)
    if rw:
        ax2 = axs[0].twinx(); ax2.plot([e["epoch"] for e in rw["log"]], [e["p"] for e in rw["log"]], "k:", label="p")
        ax2.set_ylabel("p (annealed)"); ax2.set_yscale("log")
    fig.tight_layout(); fig.savefig(os.path.join(outdir, "training.png"), dpi=130); plt.close(fig)

    # --- example panels (the test patches with the most touching nuclei), full patch and a crop
    titles = dict(img="image", gt="instances (touching in red)", s="U-Net logits (sigmoid)", xk="layer, 20 steps",
                  xc="converged", xinf="PW limit", ch="edge costs (horizontal)", c="contour head",
                  pp_contour="logits − contour", pp_ws="watershed (seg markers)", pp_wsc="watershed (contour markers)")
    for v in runs:
        f = os.path.join(args.resdir, files[v].replace(".json", "_examples.npz"))
        if not os.path.exists(f):
            continue
        ex = np.load(f)
        ids = sorted({int(k.split("__")[0]) for k in ex.files})
        have = lambda k, c: f"{k}__{c}" in ex.files
        cols = [c for c in ("img", "gt", "s", "xk", "xc", "xinf", "ch", "c", "pp_contour", "pp_ws", "pp_wsc")
                if c in ("img", "gt") or have(ids[0], c)]
        for crop in (False, True):
            fig, axs = plt.subplots(len(ids), len(cols), figsize=(2.3 * len(cols), 2.3 * len(ids)), squeeze=False)
            for i, k in enumerate(ids):
                inst = ex[f"{k}__inst"]; touch = touching_mask(inst)
                if crop:
                    cy, cx = crop_centre(touch)
                    r = 32; y0 = int(np.clip(cy - r, 0, 256 - 2 * r)); x0 = int(np.clip(cx - r, 0, 256 - 2 * r))
                    sl = (slice(y0, y0 + 2 * r), slice(x0, x0 + 2 * r))
                else:
                    sl = (slice(None), slice(None))
                for j, c in enumerate(cols):
                    ax = axs[i, j]
                    if c == "img":
                        ax.imshow(ex[f"{k}__img"].transpose(1, 2, 0)[sl])
                    elif c == "gt":
                        n = int(inst.max())
                        ax.imshow(inst[sl], cmap=inst_cmap(n), vmin=0, vmax=n, interpolation="nearest")
                        tt = touch[sl]
                        if tt.any():
                            ov = np.zeros(tt.shape + (4,)); ov[tt] = (1, 0, 0, 1); ax.imshow(ov, interpolation="nearest")
                    elif c == "ch":
                        a = ex[f"{k}__ch"]
                        ax.imshow(a[sl[0], slice(sl[1].start, None if sl[1].stop is None else sl[1].stop - 1)],
                                  cmap="magma", vmin=0, vmax=max(float(a.max()), 1e-3), interpolation="nearest")
                    else:
                        ax.imshow(ex[f"{k}__{c}"][sl], cmap="gray", vmin=0, vmax=1, interpolation="nearest")
                    ax.set_xticks([]); ax.set_yticks([])
                    if i == 0:
                        ax.set_title(titles[c], fontsize=9)
                    if j == 0:
                        ax.set_ylabel(f"#{int(ex[f'{k}__idx'])} {str(ex[f'{k}__type'])}" if have(k, "type") else f"#{k}", fontsize=8)
            fig.suptitle(f"{v}" + (" (64 px crop around touching nuclei)" if crop else "")); fig.tight_layout()
            fig.savefig(os.path.join(outdir, f"examples_{v}{'_crop' if crop else ''}.png"), dpi=110); plt.close(fig)


if __name__ == "__main__":
    main()
