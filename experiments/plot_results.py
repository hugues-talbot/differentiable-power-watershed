#!/usr/bin/env python3
"""Figures and a Markdown summary from the JSON lines written by pw_conditioning.py.

usage: plot_results.py results/conditioning_512.jsonl [more.jsonl ...] --outdir figures
"""
import argparse, json, os, sys
from collections import defaultdict
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

KS_SHOW = (10, 50, 200)


def load(paths):
    recs = []
    for p in paths:
        with open(p) as f:
            recs += [json.loads(l) for l in f if l.strip()]
    transforms = {r.get("cost_transform", "sq") for r in recs}
    by = defaultdict(list)
    for r in recs:
        t = r.get("cost_transform", "sq")
        by[r["case"] + (f" [{t}]" if len(transforms) > 1 else "")].append(r)
    for k in by:
        by[k].sort(key=lambda r: r["p"])
    return by


def get(r, *keys, default=np.nan):
    for k in keys:
        if not isinstance(r, dict) or k not in r:
            return default
        r = r[k]
    return r


def series(rs, *keys):
    """Records whose float64 reference is unreliable are masked out."""
    needs_ref = any(k.startswith(("err", "lab", "dist", "grad")) for k in keys)
    y = np.array([float(get(r, *keys)) if (r.get("ref_ok", True) or not needs_ref) else np.nan for r in rs])
    y[~np.isfinite(y) | (np.abs(y) > 1e60)] = np.nan      # astronomically large kappas break log axes
    return np.array([r["p"] for r in rs]), y


def panel(ax, by, keys, ylabel, logy=True, title=None):
    for case, rs in by.items():
        p, y = series(rs, *keys)
        ax.plot(p, y, "o-", ms=3, label=case)
    ax.set_xscale("log")
    if logy:
        ax.set_yscale("log")
    ax.set_xlabel("p (inverse temperature)"); ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.grid(True, which="both", alpha=0.3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--outdir", default="figures")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    by = load(args.paths)

    # --- figure 1: conditioning and CG cost
    fig, axs = plt.subplots(2, 2, figsize=(12, 9))
    panel(axs[0, 0], by, ("eig", "kappa"), "kappa(L_U)  [ARPACK]", title="Condition number")
    panel(axs[0, 1], by, ("cg_f32", "ritz_kappa"), "Ritz kappa seen by CG (fp32)", title="Condition number seen by CG")
    panel(axs[1, 0], by, ("cg_f32", "it_0.001"), "iterations", title="CG fp32: iterations to rel. residual 1e-3")
    panel(axs[1, 1], by, ("pcg_f64", "it_1e-06"), "iterations", title="Jacobi-PCG fp64: iterations to 1e-6")
    axs[0, 0].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(os.path.join(args.outdir, "conditioning.png"), dpi=130); plt.close(fig)

    # --- figure 2: truncated solvers
    fig, axs = plt.subplots(2, 3, figsize=(15, 8))
    for j, K in enumerate(KS_SHOW):
        panel(axs[0, j], by, ("jacobi_f32", f"err_K{K}"), "||x_K - x^p||_inf", title=f"Jacobi, K={K}")
        panel(axs[1, j], by, ("cg_f32", f"err_K{K}"), "||x_K - x^p||_inf", title=f"CG fp32, K={K}")
    axs[0, 0].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(os.path.join(args.outdir, "truncation.png"), dpi=130); plt.close(fig)

    # --- figure 3: distance to the PW limit and gradient concentration
    fig, axs = plt.subplots(2, 2, figsize=(12, 9))
    panel(axs[0, 0], by, ("dist_inf_lab",), "label disagreement x^p vs x^inf (free nodes)", title="Distance to PW limit: labels")
    panel(axs[0, 1], by, ("dist_inf_linf",), "||x^p - x^inf||_inf", title="Distance to PW limit: potentials")
    panel(axs[1, 0], by, ("grad", "n90"), "edges carrying 90% of |grad|", title="Gradient concentration")
    panel(axs[1, 1], by, ("grad", "l2"), "||d l / d c||_2", title="Gradient norm (loss vs reference labels)")
    axs[0, 0].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(os.path.join(args.outdir, "limit_and_gradient.png"), dpi=130); plt.close(fig)

    # --- figure 4: label error of x^p and of truncated Jacobi vs reference labels
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.5))
    panel(axs[0], by, ("lab_err_ref",), "label error vs reference labels", logy=False, title="x^p: label error")
    panel(axs[1], by, ("jacobi_f32", "lab_K10"), "label disagreement with x^p", logy=False, title="Jacobi K=10: labels vs x^p")
    axs[0].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(os.path.join(args.outdir, "labels.png"), dpi=130); plt.close(fig)

    # --- figure 5: distance to the limit against what it costs (parametric in p)
    fig, axs = plt.subplots(1, 3, figsize=(16, 4.8))
    for case, rs in by.items():
        _, d = series(rs, "dist_inf_lab")
        for ax, keys, xl in ((axs[0], ("cg_f32", "it_0.001"), "CG fp32 iterations to 1e-3"),
                             (axs[1], ("pcg_f64", "it_1e-06"), "Jacobi-PCG fp64 iterations to 1e-6"),
                             (axs[2], ("cg_f32", "ritz_kappa"), "Ritz kappa (fp32 CG)")):
            _, x = series(rs, *keys)
            ax.plot(x, np.maximum(d, 1e-5), "o-", ms=3, label=case)
            ax.set_xlabel(xl); ax.set_xscale("log"); ax.set_yscale("log")
            ax.set_ylabel("label disagreement with x^inf (floored at 1e-5)"); ax.grid(True, which="both", alpha=0.3)
    axs[0].legend(fontsize=7)
    fig.suptitle("Distance to the PW limit versus solver cost, each point one value of p")
    fig.tight_layout(); fig.savefig(os.path.join(args.outdir, "tradeoff.png"), dpi=130); plt.close(fig)

    # --- Markdown table
    lines = ["| case | p | kappa | Ritz kappa (fp32) | CG32 it 1e-3 | CG32 it 1e-6 | PCG64 it 1e-6 | Jacobi K=10 err | Jacobi K=50 err | CG32 K=10 err | labels vs x^inf | |x^p-x^inf|_inf | grad n90 | grad l2 |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for case, rs in by.items():
        for r in rs:
            lines.append("| {} | {:g} | {:.2e} | {:.2e} | {} | {} | {} | {:.2g} | {:.2g} | {:.2g} | {:.4f} | {:.2g} | {} | {:.2e} |".format(
                case, r["p"], get(r, "eig", "kappa"), get(r, "cg_f32", "ritz_kappa"),
                get(r, "cg_f32", "it_0.001", default="-"), get(r, "cg_f32", "it_1e-06", default="-"),
                get(r, "pcg_f64", "it_1e-06", default="-"),
                get(r, "jacobi_f32", "err_K10"), get(r, "jacobi_f32", "err_K50"), get(r, "cg_f32", "err_K10"),
                r["dist_inf_lab"], r["dist_inf_linf"], get(r, "grad", "n90", default="-"), get(r, "grad", "l2")))
    with open(os.path.join(args.outdir, "summary.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
