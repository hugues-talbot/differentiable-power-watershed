#!/usr/bin/env python3
"""Figures and a Markdown summary for exp_softmax_synthetic.py.

usage: plot_softmax.py results_softmax --outdir figures_softmax
"""
import argparse, json, os
from collections import defaultdict
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

METRICS = (("bf2", "boundary F-score, 2 px"), ("bf1", "boundary F-score, 1 px"),
           ("iou", "IoU"), ("soft_frac", "fraction of pixels in (0.1, 0.9)"))


def load(path):
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


def group(recs):
    """-> {(sigma, shift, alpha): {method: {p: [values per image]}}}"""
    g = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for r in recs:
        key = (r["sigma"], r["edge_shift"], r["unary_scale"])
        g[key][r["method"]][r.get("p")].append(r)
    return g


def mean(rs, m):
    return float(np.mean([r[m] for r in rs]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("resdir")
    ap.add_argument("--outdir", default="figures_softmax")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    recs = load(os.path.join(args.resdir, "softmax_synthetic.jsonl"))
    g = group(recs)
    sigmas = sorted({k[0] for k in g}); shifts = sorted({k[1] for k in g}); alphas = sorted({k[2] for k in g})

    # --- figure 1: metrics versus p, one panel per (sigma, shift), one line per alpha
    for m, mlabel in METRICS:
        fig, axs = plt.subplots(len(sigmas), len(shifts), figsize=(6 * len(shifts), 4.2 * len(sigmas)), squeeze=False)
        for i, sg in enumerate(sigmas):
            for j, sh in enumerate(shifts):
                ax = axs[i, j]
                for a in alphas:
                    d = g[(sg, sh, a)]
                    ps = sorted(p for p in d["rw_implicit"])
                    ax.plot(ps, [mean(d["rw_implicit"][p], m) for p in ps], "o-", ms=3, label=f"RW layer, alpha={a:g}")
                    lim = mean(d["pw_limit"][float("inf")], m)
                    ax.plot([ps[-1] * 2.5], [lim], "s", color=ax.lines[-1].get_color(), ms=6)
                d0 = g[(sg, sh, alphas[0])]
                ax.axhline(mean(d0["soft_prediction"][None], m), color="k", ls="--", label="soft prediction (thresholded)")
                ax.set_xscale("log"); ax.set_xlabel("p   (squares: exact PW limit)"); ax.set_ylabel(mlabel)
                ax.set_title(f"noise {sg:g}, image edge shifted by {sh} px")
                ax.grid(True, which="both", alpha=0.3)
                if i == 0 and j == 0:
                    ax.legend(fontsize=7)
        fig.tight_layout(); fig.savefig(os.path.join(args.outdir, f"vs_p_{m}.png"), dpi=130); plt.close(fig)

    # --- figure 2: truncated solvers, label disagreement with the converged solve and bf2
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.5))
    key = (sigmas[0], 0, alphas[min(1, len(alphas) - 1)])
    d = g[key]
    for mode, ls in (("unrolled", "-"), ("jacobi", "--")):
        for p in sorted({r["p"] for meth in d for r in sum(d[meth].values(), []) if meth.startswith(mode)}):
            Ks = sorted(int(meth.split("_K")[1]) for meth in d if meth.startswith(mode))
            axs[0].plot(Ks, [mean(d[f"{mode}_K{K}"][p], "lab_vs_converged") for K in Ks], "o" + ls, ms=4,
                        label=f"{mode}, p={p:g}")
            axs[1].plot(Ks, [mean(d[f"{mode}_K{K}"][p], "bf2") for K in Ks], "o" + ls, ms=4, label=f"{mode}, p={p:g}")
    for ax in axs:
        ax.set_xlabel("K (solver steps = layers)"); ax.set_xscale("log"); ax.grid(True, which="both", alpha=0.3)
    axs[0].set_ylabel("label disagreement with the converged solve"); axs[0].set_yscale("log")
    axs[1].set_ylabel("boundary F-score, 2 px"); axs[1].axhline(mean(d["soft_prediction"][None], "bf2"), color="k", ls=":")
    axs[0].legend(fontsize=7)
    fig.suptitle(f"Truncated layer, noise {key[0]:g}, aligned edge, alpha={key[2]:g}")
    fig.tight_layout(); fig.savefig(os.path.join(args.outdir, "truncation.png"), dpi=130); plt.close(fig)

    # --- figure 3: example images
    ex = np.load(os.path.join(args.resdir, "examples.npz"))
    tags = sorted({k.split("__")[0] for k in ex.files})
    show = [t for t in tags if f"_a{alphas[min(1, len(alphas) - 1)]:g}" in t]
    cols = ["img", "s", "x5", "x20", "x100", "x500", "xinf", "gt"]
    titles = ["image", "soft prediction", "p=5", "p=20", "p=100", "p=500", "PW limit", "ground truth"]
    fig, axs = plt.subplots(len(show), len(cols), figsize=(2.1 * len(cols), 2.1 * len(show)), squeeze=False)
    for i, t in enumerate(show):
        for j, c in enumerate(cols):
            a = ex[f"{t}__{c}"]
            axs[i, j].imshow(a, cmap="gray", vmin=0, vmax=255 if c == "img" else 1, interpolation="nearest")
            axs[i, j].set_xticks([]); axs[i, j].set_yticks([])
            if i == 0:
                axs[i, j].set_title(titles[j], fontsize=9)
        axs[i, 0].set_ylabel(t.replace("_", " "), fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(args.outdir, "examples.png"), dpi=110); plt.close(fig)

    # --- Markdown table
    lines = ["| noise | edge shift | alpha | soft bf2 | soft IoU | best p (bf2) | bf2 at best p | IoU at best p | soft frac at best p | limit bf2 | limit IoU |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for (sg, sh, a), d in sorted(g.items()):
        ps = sorted(d["rw_implicit"])
        best = max(ps, key=lambda p: mean(d["rw_implicit"][p], "bf2"))
        lines.append(f"| {sg:g} | {sh} | {a:g} | {mean(d['soft_prediction'][None], 'bf2'):.3f} | {mean(d['soft_prediction'][None], 'iou'):.3f} "
                     f"| {best:g} | {mean(d['rw_implicit'][best], 'bf2'):.3f} | {mean(d['rw_implicit'][best], 'iou'):.3f} "
                     f"| {mean(d['rw_implicit'][best], 'soft_frac'):.3f} | {mean(d['pw_limit'][float('inf')], 'bf2'):.3f} "
                     f"| {mean(d['pw_limit'][float('inf')], 'iou'):.3f} |")
    with open(os.path.join(args.outdir, "summary.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
