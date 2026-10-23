#!/usr/bin/env python3
"""Gap-target runs (exp_unet_seg.py --gap) against the section-6 baseline: one table,
paired per-patch differences with bootstrap intervals, per-tissue table.

usage: compare_gap.py --base results/pannuke --gap results/pannuke/gap \
           --runs "unet (gap)=unet_gap" "rw p 5→50 (gap)=rw_learned_gap_p50" ... --out results/pannuke/gap/compare.md
Per-image npz files are needed for the paired statistics (test patches are in the same
order in every run; limit rows are matched through limit__idx when present).
"""
import argparse, json, os
import numpy as np

MODE_NAME = dict(logits="sigmoid, thresholded at 0.5", layer="layer, 20 steps", converged="converged", limit="PW limit")
COLS = (("iou", "IoU"), ("bf1", "BF₁"), ("bf2", "BF₂"), ("bf3", "BF₃"), ("band_acc", "band acc."), ("soft_frac", "soft px"),
        ("edge_align", "edge align."), ("f1_05", "F1@0.5"), ("pq", "PQ"), ("aji", "AJI"), ("count_err", "count err."))
TCOLS = (("iou", "IoU"), ("bf2", "BF₂"), ("f1_05", "F1@0.5"), ("pq", "PQ"), ("count_err", "count err."))


def fmt(v, k):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "–"
    if k == "soft_frac":
        return "0" if v == 0 else f"{100 * v:.1f} %"
    return f"{v:.3f}"


def load(prefix):
    r = json.load(open(prefix + ".json"))
    f = prefix + "_perimage.npz"
    r["perimage"] = dict(np.load(f)) if os.path.exists(f) else None
    return r


def rows(label, r, modes, key=None):
    out = []
    for mode in modes:
        if mode not in r["test"]:
            continue
        t = r["test"][mode] if key is None else r["test"][mode].get("per_type", {}).get(key)
        if t is None:
            continue
        name = MODE_NAME[mode] + (f" ({t['n']})" if mode == "limit" else "")
        out.append((label, name, t))
    return out


def table(entries, cols):
    lines = ["| run | output | " + " | ".join(c[1] for c in cols) + " |", "|---|---|" + "---|" * len(cols)]
    for label, name, t in entries:
        lines.append(f"| {label} | {name} | " + " | ".join(fmt(t.get(c[0]), c[0]) for c in cols) + " |")
    return "\n".join(lines) + "\n"


def boot_ci(x, n=2000, seed=0):
    rng = np.random.default_rng(seed)
    m = x[rng.integers(0, len(x), (n, len(x)))].mean(1)
    return float(x.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def arr(r, mode, metric):
    return r["perimage"][f"{mode}__{metric}"]


def paired_line(name, a, b, metrics=("iou", "bf2")):
    parts = []
    for m in metrics:
        d = a[m] - b[m]; d = d[~np.isnan(d)]
        mean, lo, hi = boot_ci(d)
        parts.append(f"{m.upper().replace('BF2', 'BF₂')} {mean:+.3f} [{lo:+.3f}, {hi:+.3f}], better on {100 * (d > 0).mean():.0f} %")
    return f"- {name} (n = {len(d)}): " + "; ".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="results/pannuke")
    ap.add_argument("--gap", default="results/pannuke/gap")
    ap.add_argument("--runs", nargs="+", required=True, help="label=file prefix (in --gap)")
    ap.add_argument("--types", nargs="+", default=("Breast", "Colon", "HeadNeck"))
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    base = {v: load(os.path.join(args.base, v)) for v in ("unet", "rw_learned")}
    gap = {}
    for spec in args.runs:
        label, prefix = spec.split("=", 1)
        gap[label] = load(os.path.join(args.gap, prefix))

    md = "**All of fold 2** (2523 patches).  The first four rows are section 6 (binary target); the rest use the gap target.\n\n"
    entries = rows("unet (sec. 6)", base["unet"], ("logits",)) + rows("rw_learned p 5→50 (sec. 6)", base["rw_learned"], ("layer", "converged", "limit"))
    for label, r in gap.items():
        entries += rows(label, r, ("logits",) if r["args"]["variant"] == "unet" else ("layer", "converged", "limit"))
    unet_gap = next((r for r in gap.values() if r["args"]["variant"] == "unet"), None)
    t = (unet_gap or base["unet"])["test"]["gt_binary"]
    entries.append(("ground truth", "gap mask" if unet_gap else "binary mask", t))
    entries.insert(4, ("ground truth", "binary mask", base["unet"]["test"]["gt_binary"]))
    md += table(entries, COLS)

    # paired statistics
    md += "\n**Paired per-patch differences** (bootstrap 95 % intervals):\n\n"
    lines = []
    if unet_gap is not None and unet_gap["perimage"] is not None:
        A = {m: arr(unet_gap, "logits", m) for m in ("iou", "bf2")}
        B = {m: arr(base["unet"], "logits", m) for m in ("iou", "bf2")}
        lines.append(paired_line("unet (gap) − unet (sec. 6)", A, B))
        for label, r in gap.items():
            if r["args"]["variant"] == "unet" or r["perimage"] is None:
                continue
            L = {m: arr(r, "layer", m) for m in ("iou", "bf2")}
            lines.append(paired_line(f"{label} layer − unet (gap)", L, A))
            Bl = {m: arr(base["rw_learned"], "layer", m) for m in ("iou", "bf2")}
            lines.append(paired_line(f"{label} layer − rw_learned layer (sec. 6)", L, Bl))
            if "limit__idx" in r["perimage"]:
                idx = r["perimage"]["limit__idx"]
                Li = {m: arr(r, "limit", m) for m in ("iou", "bf2")}
                C = {m: arr(r, "converged", m)[idx] for m in ("iou", "bf2")}
                lines.append(paired_line(f"{label} limit − converged", Li, C))
                U = {m: arr(unet_gap, "logits", m)[idx] for m in ("iou", "bf2")}
                lines.append(paired_line(f"{label} limit − unet (gap)", Li, U))
    md += "\n".join(lines) + "\n"

    # crowding
    if unet_gap is not None and unet_gap["perimage"] is not None:
        ngt = unet_gap["perimage"]["logits__inst_n_gt"]
        md += "\n**IoU gap by crowding** (layer − unet (gap), mean paired difference):\n\n| run | < 10 nuclei | 10–50 | > 50 |\n|---|---|---|---|\n"
        for label, r in gap.items():
            if r["args"]["variant"] == "unet" or r["perimage"] is None:
                continue
            d = arr(r, "layer", "iou") - arr(unet_gap, "logits", "iou")
            md += f"| {label} | " + " | ".join(f"{d[s].mean():+.3f} (n={s.sum()})" for s in (ngt < 10, (ngt >= 10) & (ngt <= 50), ngt > 50)) + " |\n"

    # per tissue
    for tt in args.types:
        md += f"\n**{tt}**\n\n"
        entries = rows("unet (sec. 6)", base["unet"], ("logits",), tt) + rows("rw_learned p 5→50 (sec. 6)", base["rw_learned"], ("layer", "limit"), tt)
        for label, r in gap.items():
            entries += rows(label, r, ("logits",) if r["args"]["variant"] == "unet" else ("layer", "limit"), tt)
        if unet_gap:
            entries.append(("ground truth", "gap mask", unet_gap["test"]["gt_binary"]["per_type"][tt]))
        md += table(entries, TCOLS)

    scales = {label: r["test"].get("_edge_scale") for label, r in gap.items() if r["test"].get("_edge_scale")}
    if scales:
        md += "\nLearned edge-cost scales: " + ", ".join(f"{k}: {v:.2f}" for k, v in scales.items()) + "\n"
    print(md)
    if args.out:
        open(args.out, "w").write(md)


if __name__ == "__main__":
    main()
