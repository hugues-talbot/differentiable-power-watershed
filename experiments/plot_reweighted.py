#!/usr/bin/env python3
"""Figures and a Markdown summary for exp_reweighted_synthetic.py.

usage: plot_reweighted.py results_reweighted --outdir figures_reweighted
"""
import argparse, json, os
from collections import defaultdict
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def load(path):
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


def mean(rs, m):
    v = [r[m] for r in rs if m in r and r[m] is not None]
    return float(np.mean(v)) if v else np.nan


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("resdir")
    ap.add_argument("--outdir", default="figures_reweighted")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    recs = load(os.path.join(args.resdir, "reweighted_synthetic.jsonl"))
    scenes = sorted({(r["sigma"], r["edge_shift"]) for r in recs})

    def sel(sg, sh, **kw):
        return [r for r in recs if r["sigma"] == sg and r["edge_shift"] == sh and all(r.get(a) == b for a, b in kw.items())]

    # --- figure 1: quality versus cost and versus gradient support, one row per scene
    fig, axs = plt.subplots(len(scenes), 3, figsize=(17, 4.4 * len(scenes)), squeeze=False)
    for i, (sg, sh) in enumerate(scenes):
        ax_cost, ax_grad, ax_soft = axs[i]
        soft_bf2 = mean(sel(sg, sh, family="soft"), "bf2")
        ann = [(p, sel(sg, sh, family="annealed", p=p)) for p in sorted({r["p"] for r in recs if r["family"] == "annealed"})]
        ax_cost.plot([mean(rs, "iters_last") for _, rs in ann], [mean(rs, "bf2") for _, rs in ann], "k-o", ms=4, label="annealed (p = 10 … 500)")
        for p, rs in ann:
            ax_cost.annotate(f"p={p:g}", (mean(rs, "iters_last"), mean(rs, "bf2")), fontsize=7, xytext=(3, 3), textcoords="offset points")
        ax_grad.plot([mean(rs, "n90_rand") for _, rs in ann], [mean(rs, "bf2") for _, rs in ann], "k-o", ms=4, label="annealed")
        ax_soft.plot([p for p, _ in ann], [mean(rs, "soft_frac") for _, rs in ann], "k-o", ms=4, label="annealed (x = p)")
        combos = sorted({(r["kind"], r["eps"], r["p0"]) for r in recs if r.get("family") == "reweighted"}, key=lambda t: (t[0], -t[1], t[2]))
        for kind, eps, p0 in combos:
            ls = "-" if kind == "cauchy" else "--"
            steps = sorted({r["step"] for r in recs if r.get("family") == "reweighted"})
            rs_by = [sel(sg, sh, family="reweighted", kind=kind, eps=eps, p0=p0, step=st) for st in steps]
            lab = f"reweighted {kind}, eps={eps:g}, p0={p0:g} (steps 0 … {steps[-1]})"
            ax_cost.plot([mean(rs, "iters_cum") for rs in rs_by], [mean(rs, "bf2") for rs in rs_by], ls, marker="s", ms=3, label=lab)
            last = rs_by[-1]
            ax_grad.plot([mean(last, "n90_rand")], [mean(last, "bf2")], "s" if kind == "cauchy" else "D", ms=6, label=f"{kind}, eps={eps:g}, p0={p0:g}, final")
            ax_soft.plot([p0 * 2 ** st for st in steps], [mean(rs, "soft_frac") for rs in rs_by], ls, marker="s", ms=3, label=f"{kind} eps={eps:g} p0={p0:g} (x = p0·2^step)")
        for ax in (ax_cost, ax_grad, ax_soft):
            ax.set_xscale("log"); ax.grid(True, which="both", alpha=0.3)
        ax_cost.axhline(soft_bf2, color="gray", ls=":", label="soft prediction"); ax_grad.axhline(soft_bf2, color="gray", ls=":")
        ax_cost.set_xlabel("inner PCG iterations (annealed: one solve; reweighted: cumulative)"); ax_cost.set_ylabel("boundary F-score, 2 px")
        ax_grad.set_xlabel("edges carrying 90 % of the sensitivity (random functional)"); ax_grad.set_ylabel("boundary F-score, 2 px")
        ax_soft.set_xlabel("p (annealed)  /  p0·2^step (reweighted)"); ax_soft.set_ylabel("fraction of soft pixels"); ax_soft.set_yscale("log")
        ax_cost.set_title(f"noise {sg:g}, image edge shifted by {sh} px")
        if i == 0:
            ax_cost.legend(fontsize=6); ax_grad.legend(fontsize=6)
    fig.tight_layout(); fig.savefig(os.path.join(args.outdir, "annealed_vs_reweighted.png"), dpi=130); plt.close(fig)

    # --- figure 2: examples
    ex = np.load(os.path.join(args.resdir, "examples.npz"))
    tags = sorted({k.split("__")[0] for k in ex.files})
    cols = ["img", "s", "ann_p100", "ann_p500", "rw_p10_e0.03_k5", "rw_p50_e0.03_k5", "rw_p100_e0.03_k1", "rw_p100_e0.03_k5", "gt"]
    titles = ["image", "soft prediction", "annealed p=100", "annealed p=500", "reweighted p0=10, 5 steps", "reweighted p0=50, 5 steps", "reweighted p0=100, 1 step", "reweighted p0=100, 5 steps", "ground truth"]
    fig, axs = plt.subplots(len(tags), len(cols), figsize=(2.1 * len(cols), 2.1 * len(tags)), squeeze=False)
    for i, t in enumerate(tags):
        for j, c in enumerate(cols):
            a = ex[f"{t}__{c}"]
            axs[i, j].imshow(a, cmap="gray", vmin=0, vmax=255 if c == "img" else 1, interpolation="nearest")
            axs[i, j].set_xticks([]); axs[i, j].set_yticks([])
            if i == 0:
                axs[i, j].set_title(titles[j], fontsize=8)
        axs[i, 0].set_ylabel(t.replace("_", " "), fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(args.outdir, "examples.png"), dpi=110); plt.close(fig)

    # --- table
    lines = ["| noise | shift | method | BF₂ | BF₁ | IoU | soft px | PCG iters (last / cum.) | w_min | loss-grad n90 | sensitivity n90 |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for sg, sh in scenes:
        rs = sel(sg, sh, family="soft")
        lines.append(f"| {sg:g} | {sh} | soft prediction | {mean(rs, 'bf2'):.3f} | {mean(rs, 'bf1'):.3f} | {mean(rs, 'iou'):.3f} | {mean(rs, 'soft_frac'):.3f} | | | | |")
        for p in sorted({r["p"] for r in recs if r["family"] == "annealed"}):
            rs = sel(sg, sh, family="annealed", p=p)
            lines.append(f"| {sg:g} | {sh} | annealed p={p:g} | {mean(rs, 'bf2'):.3f} | {mean(rs, 'bf1'):.3f} | {mean(rs, 'iou'):.3f} | {mean(rs, 'soft_frac'):.3f} | {mean(rs, 'iters_last'):.0f} | {mean(rs, 'wmin'):.1e} | {mean(rs, 'n90'):.0f} | {mean(rs, 'n90_rand'):.0f} |")
        for kind, eps, p0 in sorted({(r["kind"], r["eps"], r["p0"]) for r in recs if r.get("family") == "reweighted"}, key=lambda t: (t[0], -t[1], t[2])):
                steps = sorted({r["step"] for r in recs if r.get("family") == "reweighted"})
                rs = sel(sg, sh, family="reweighted", kind=kind, eps=eps, p0=p0, step=steps[-1])
                lines.append(f"| {sg:g} | {sh} | reweighted {kind} eps={eps:g} p0={p0:g}, {steps[-1]} steps | {mean(rs, 'bf2'):.3f} | {mean(rs, 'bf1'):.3f} | {mean(rs, 'iou'):.3f} | {mean(rs, 'soft_frac'):.3f} | {mean(rs, 'iters_last'):.0f} / {mean(rs, 'iters_cum'):.0f} | {mean(rs, 'wmin'):.1e} | {mean(rs, 'n90'):.0f} | {mean(rs, 'n90_rand'):.0f} |")
    with open(os.path.join(args.outdir, "summary.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
