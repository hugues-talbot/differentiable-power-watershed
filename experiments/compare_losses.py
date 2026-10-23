#!/usr/bin/env python3
"""Compare training losses (bce / boundary / instance) for the plain U-Net and the
U-Net + RW/PW layer: one table over losses, paired per-patch differences with
bootstrap intervals, and a dot chart.

usage: compare_losses.py --base results/pannuke \
           --losses boundary=results/pannuke_losses/boundary instance=results/pannuke_losses/instance \
           --outdir results/pannuke_losses
`--base` holds the plain-BCE runs (label "bce").  Per-image npz files (exp_unet_seg.py)
are needed for the paired statistics; the tables only need the json files.
"""
import argparse, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROWS = (("unet", "logits"), ("rw_learned", "logits"), ("rw_learned", "layer"), ("rw_learned", "converged"), ("rw_learned", "limit"))
MODE_NAME = dict(logits="logits", layer="layer, 20 steps", converged="converged", limit="PW limit")
PIX = (("iou", "IoU"), ("bf1", "BF₁"), ("bf2", "BF₂"), ("bf3", "BF₃"), ("band_acc", "band acc."), ("soft_frac", "soft px"))
EXTRA = (("edge_align", "edge align."), ("f1_05", "F1@0.5"), ("pq", "PQ"), ("count_err", "count err."))
# fixed series order and colours (identity never cycles): U-Net, layer, PW limit, ceiling
SERIES = (("unet", "logits", "U-Net (logits)", "#4C72B0", "o"),
          ("rw_learned", "layer", "U-Net + RW layer", "#DD8452", "s"),
          ("rw_learned", "limit", "U-Net + PW limit", "#8172B3", "D"))


def fmt(v, k):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "–"
    return f"{100 * v:.1f} %" if k == "soft_frac" else f"{v:.3f}"


def load(d):
    out = {}
    for v in ("unet", "rw_learned"):
        f = os.path.join(d, f"{v}.json")
        if os.path.exists(f):
            out[v] = json.load(open(f))
            g = os.path.join(d, f"{v}_perimage.npz")
            out[v]["perimage"] = dict(np.load(g)) if os.path.exists(g) else None
    return out


def table(runs_by_loss, cols, key=None):
    head = "| loss | variant | output | n | " + " | ".join(c[1] for c in cols) + " |"
    lines = [head, "|---|---|---|---|" + "---|" * len(cols)]
    for loss, runs in runs_by_loss.items():
        for v, mode in ROWS:
            if v not in runs or mode not in runs[v]["test"]:
                continue
            t = runs[v]["test"][mode] if key is None else runs[v]["test"][mode].get("per_type", {}).get(key)
            if t is None:
                continue
            lines.append(f"| {loss} | {v} | {MODE_NAME[mode]} | {t['n']} | " + " | ".join(fmt(t.get(c[0]), c[0]) for c in cols) + " |")
    r = next(iter(runs_by_loss.values()))
    r = r.get("unet") or r.get("rw_learned")
    if r and "gt_binary" in r["test"]:
        t = r["test"]["gt_binary"] if key is None else r["test"]["gt_binary"]["per_type"][key]
        lines.append(f"| – | ground truth | binary mask | {t['n']} | " + " | ".join(fmt(t.get(c[0]), c[0]) for c in cols) + " |")
    return "\n".join(lines) + "\n"


def boot_ci(x, n=2000, seed=0):
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(x), (n, len(x)))
    m = x[idx].mean(1)
    return float(x.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def paired(a, b, metrics=("iou", "bf2", "band_acc")):
    """a, b: per-image dicts (mode-prefixed arrays), same images.  Mean difference a - b
    with a 95 % bootstrap interval and the fraction of images where a > b."""
    out = {}
    for m in metrics:
        d = a[m] - b[m]
        ok = ~np.isnan(d)
        mean, lo, hi = boot_ci(d[ok])
        out[m] = dict(mean=mean, lo=lo, hi=hi, frac_better=float((d[ok] > 0).mean()), n=int(ok.sum()))
    return out


def sub(per, mode):
    return {k.split("__", 1)[1]: v for k, v in per.items() if k.startswith(mode + "__")}


def fmt_paired(p):
    return " ".join(f"{m}: {d['mean']:+.3f} [{d['lo']:+.3f}, {d['hi']:+.3f}] (better on {100 * d['frac_better']:.0f} %)"
                    for m, d in p.items())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="directory of the plain-BCE runs")
    ap.add_argument("--losses", nargs="+", default=(), help="label=dir pairs")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--types", nargs="+", default=("Breast", "Colon", "HeadNeck"))
    ap.add_argument("--title", default="PanNuke fold 1 → fold 2")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    runs_by_loss = {"bce": load(args.base)}
    for s in args.losses:
        lab, d = s.split("=", 1)
        runs_by_loss[lab] = load(d)
    any_run = next(iter(runs_by_loss["bce"].values()))
    has_inst = "f1_05" in any_run["test"]["logits"]
    cols = PIX + (EXTRA if has_inst else ())

    md = [f"**{args.title}: training losses**", "", table(runs_by_loss, cols)]
    if has_inst:
        for t in args.types:
            md += [f"**{t}**", "", table(runs_by_loss, (("iou", "IoU"), ("bf2", "BF₂"), ("edge_align", "edge align."),
                                                        ("f1_05", "F1@0.5"), ("pq", "PQ"), ("count_err", "count err.")), key=t)]

    # --- paired per-patch differences
    md += ["**Paired per-image differences** (mean, 95 % bootstrap interval, fraction of images where the first is better)", ""]
    base_u = runs_by_loss["bce"].get("unet", {}).get("perimage")
    base_r = runs_by_loss["bce"].get("rw_learned", {}).get("perimage")
    for loss, runs in runs_by_loss.items():
        u = runs.get("unet", {}).get("perimage"); r = runs.get("rw_learned", {}).get("perimage")
        unet_name = "unet logits"
        if u is None and base_u is not None and r is not None:       # a loss dir without its own U-Net: the base U-Net
            u, unet_name = base_u, "unet logits (bce)"
        if u is not None and r is not None:
            md.append(f"- {loss}: rw_learned layer − {unet_name}: " + fmt_paired(paired(sub(r, "layer"), sub(u, "logits"))))
            md.append(f"- {loss}: rw_learned layer − its own logits: " + fmt_paired(paired(sub(r, "layer"), sub(r, "logits"))))
            if "limit__iou" in r:
                lim = sub(r, "limit"); conv = sub(r, "converged")
                li = runs["rw_learned"]["limit_idx"]
                if "idx" in lim:                                  # limit rows stored with their test indices: paired
                    order = lim["idx"].astype(int)
                    md.append(f"- {loss}: PW limit − converged on the {len(order)} limit patches: " +
                              fmt_paired(paired(lim, {k: v[order] for k, v in conv.items()})))
                    if u is not None:
                        md.append(f"- {loss}: PW limit − {unet_name} on the {len(order)} limit patches: " +
                                  fmt_paired(paired(lim, {k: v[order] for k, v in sub(u, "logits").items()})))
                else:                                             # older files: pool order, means only
                    md.append(f"- {loss}: PW limit − converged on the {len(li)} limit patches (means): " +
                              " ".join(f"{k}: {lim[k].mean() - conv[k][li].mean():+.3f}" for k in ("iou", "bf2", "band_acc")))
            if has_inst:
                for mode, per in (("logits", u), ("layer", r)):
                    s = sub(per, mode); ngt = s["inst_n_gt"]
                    bins = [(0, 10), (10, 30), (30, 60), (60, 10 ** 6)]
                    parts = []
                    for lo, hi in bins:
                        sel = (ngt >= lo) & (ngt < hi)
                        parts.append(f"{lo}–{hi if hi < 10 ** 6 else '∞'} nuclei (n={sel.sum()}): "
                                     f"IoU {s['iou'][sel].mean():.3f}, count err {np.mean(np.abs(s['inst_n_pred'][sel] - ngt[sel]) / np.maximum(ngt[sel], 1)):.3f}")
                    md.append(f"- {loss}: {'unet logits' if mode == 'logits' else 'rw_learned layer'} by crowding: " + "; ".join(parts))
        if loss != "bce":
            if u is not None and base_u is not None:
                md.append(f"- unet {loss} − unet bce: " + fmt_paired(paired(sub(u, "logits"), sub(base_u, "logits"))))
            if r is not None and base_r is not None:
                md.append(f"- rw_learned layer {loss} − rw_learned layer bce: " + fmt_paired(paired(sub(r, "layer"), sub(base_r, "layer"))))
    md.append("")
    text = "\n".join(md)
    open(os.path.join(args.outdir, "summary.md"), "w").write(text)
    print(text)

    # --- dot chart: one panel per metric, x = loss, series = method (fixed colours), ceiling dashed
    metrics = [("iou", "IoU", 1), ("bf2", "BF₂", 1), ("band_acc", "band accuracy", 1)]
    if has_inst:
        metrics += [("f1_05", "instance F1@0.5", 1), ("pq", "PQ", 1), ("count_err", "count error (lower is better)", -1)]
    losses = list(runs_by_loss)
    fig, axs = plt.subplots(1, len(metrics), figsize=(3.0 * len(metrics), 3.9))
    xs = np.arange(len(losses))
    for ax, (m, name, _) in zip(axs, metrics):
        for k, (v, mode, lab, col, mk) in enumerate(SERIES):
            ys = [runs_by_loss[l][v]["test"][mode][m] if v in runs_by_loss[l] and mode in runs_by_loss[l][v]["test"] else np.nan
                  for l in losses]
            ax.plot(xs + (k - 1) * 0.12, ys, mk, color=col, ms=7, label=lab, mew=0)
            for x, y in zip(xs + (k - 1) * 0.12, ys):
                if not np.isnan(y):
                    ax.annotate(f"{y:.3f}" if m != "count_err" else f"{y:.2f}", (x, y), textcoords="offset points",
                                xytext=(0, 6 if k != 2 else -11), ha="center", fontsize=6.5, color="#444")
        if has_inst and m in ("f1_05", "pq", "count_err"):
            name += f"\n(binary-mask ceiling {any_run['test']['gt_binary'][m]:.3f})"
        ax.set_xticks(xs); ax.set_xticklabels(losses); ax.set_title(name, fontsize=9)
        ax.grid(axis="y", alpha=0.25); ax.spines[["top", "right"]].set_visible(False)
        ax.margins(x=0.25, y=0.2)
    axs[0].legend(fontsize=7, frameon=False, loc="lower left")
    fig.suptitle(f"{args.title}: training loss vs method (PW limit on its subset)", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(args.outdir, "losses.png"), dpi=130); plt.close(fig)


if __name__ == "__main__":
    main()
