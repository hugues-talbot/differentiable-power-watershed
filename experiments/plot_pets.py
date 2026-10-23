#!/usr/bin/env python3
"""Table, training curves and example panels for exp_unet_pets.py.

usage: plot_pets.py results_pets --outdir figures_pets
"""
import argparse, glob, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

VARIANTS = ("unet", "rw_img", "rw_learned")
MODES = ("logits", "layer", "converged", "limit")
MET = (("iou", "IoU"), ("bf1", "BF 1px"), ("bf2", "BF 2px"), ("band_acc", "band acc"), ("soft_frac", "soft frac"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("resdir")
    ap.add_argument("--outdir", default="figures_pets")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    runs = {}
    for v in VARIANTS:
        f = os.path.join(args.resdir, f"{v}.json")
        if os.path.exists(f):
            runs[v] = json.load(open(f))

    # --- table
    lines = ["| variant | output | n | " + " | ".join(m[1] for m in MET) + " |",
             "|---|---|---|" + "---|" * len(MET)]
    for v, r in runs.items():
        for mode in MODES:
            if mode in r["test"]:
                t = r["test"][mode]
                lines.append(f"| {v} | {mode} | {t['n']} | " + " | ".join(f"{t[m[0]]:.3f}" for m in MET) + " |")
    md = "\n".join(lines) + "\n"
    open(os.path.join(args.outdir, "summary.md"), "w").write(md)
    print(md)

    # --- training curves
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.2))
    for v, r in runs.items():
        ep = [e["epoch"] for e in r["log"]]
        axs[0].plot(ep, [e["loss"] for e in r["log"]], label=v)
        ev = [e for e in r["log"] if "val" in e]
        for mode in ("logits", "layer"):
            if ev and mode in ev[0]["val"]:
                axs[1].plot([e["epoch"] for e in ev], [e["val"][mode]["iou"] for e in ev], "o-",
                            label=f"{v} / {mode}")
                axs[2].plot([e["epoch"] for e in ev], [e["val"][mode]["soft_frac"] for e in ev], "o-",
                            label=f"{v} / {mode}")
    axs[0].set_ylabel("training loss"); axs[1].set_ylabel("IoU (400 test images)"); axs[2].set_ylabel("fraction of soft pixels")
    for ax in axs:
        ax.set_xlabel("epoch"); ax.grid(alpha=0.3); ax.legend(fontsize=7)
    if "rw_img" in runs:
        ax2 = axs[0].twinx(); ax2.plot([e["epoch"] for e in runs["rw_img"]["log"]], [e["p"] for e in runs["rw_img"]["log"]],
                                       "k:", label="p"); ax2.set_ylabel("p (annealed)"); ax2.set_yscale("log")
    fig.tight_layout(); fig.savefig(os.path.join(args.outdir, "training.png"), dpi=130); plt.close(fig)

    # --- examples
    for v in runs:
        f = os.path.join(args.resdir, f"{v}_examples.npz")
        if not os.path.exists(f):
            continue
        ex = np.load(f)
        ids = sorted({int(k.split("__")[0]) for k in ex.files})
        cols = [c for c in ("img", "s", "xk", "xc", "xinf", "ch", "y") if f"{ids[0]}__{c}" in ex.files]
        titles = dict(img="image", s="U-Net logits (sigmoid)", xk="layer, K steps", xc="converged", xinf="PW limit",
                      ch="edge costs (horizontal)", y="ground truth")
        fig, axs = plt.subplots(len(ids), len(cols), figsize=(2.3 * len(cols), 2.3 * len(ids)), squeeze=False)
        for i, k in enumerate(ids):
            for j, c in enumerate(cols):
                a = ex[f"{k}__{c}"]
                if c == "img":
                    axs[i, j].imshow(a.transpose(1, 2, 0))
                elif c == "ch":
                    axs[i, j].imshow(a, cmap="magma", vmin=0, vmax=max(float(a.max()), 1e-3))
                else:
                    axs[i, j].imshow(a, cmap="gray", vmin=0, vmax=1, interpolation="nearest")
                axs[i, j].set_xticks([]); axs[i, j].set_yticks([])
                if i == 0:
                    axs[i, j].set_title(titles[c], fontsize=9)
        fig.suptitle(v); fig.tight_layout()
        fig.savefig(os.path.join(args.outdir, f"examples_{v}.png"), dpi=110); plt.close(fig)


if __name__ == "__main__":
    main()
