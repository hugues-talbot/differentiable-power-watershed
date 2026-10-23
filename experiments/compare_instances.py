#!/usr/bin/env python3
"""Section 11.1: cross-run tables for the multi-marker layer runs of exp_instance_pannuke.py
(numpy only, runs on the Mac from the results folders): training cost and PCG iterations per
epoch, the validation curves (first --val-n test patches, every 5 epochs), the headline test
rows with the marker-quality counts, and paired per-patch bootstrap differences between the
runs' layer outputs (and their oracles and limits).

usage: compare_instances.py --runs sec11=../results/pannuke_instances dist=../results/pannuke_instances/dist ...
       --out ../results/pannuke_instances/compare_11_1.md
A run is label=dir (name instances) or label=dir:name; name unet_dist (exp_unet_dist.py) is read with
its post-processing row `ws` in place of `layer`, `ws_gtmk` as the oracle, no limit.  Paired
differences are only made between runs with the same test fold.
"""
import argparse, json, os
import numpy as np

COLS = (("iou", "IoU"), ("bf1", "BF₁"), ("bf2", "BF₂"), ("band_acc", "band acc."), ("edge_align", "edge align."),
        ("f1_05", "F1@0.5"), ("pq", "PQ"), ("aji", "AJI"), ("count_err", "count err."), ("n_pred_mean", "n_pred"))


def fmt(v, k=None):                                   # the helpers of plot_instances.py (which needs matplotlib)
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "–"
    return f"{v:.1f}" if k == "n_pred_mean" else f"{v:.3f}"


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
        ii = idx if idx.shape[1] == d.size else boot_idx(d.size, idx.shape[0])
        means = d[ii].mean(1)
        cells.append(f"{d.mean():+.3f} [{np.percentile(means, 2.5):+.3f}, {np.percentile(means, 97.5):+.3f}]")
    for m in inst:
        full = inst_agg(a)[m] - inst_agg(b)[m]
        diffs = np.array([inst_agg(a, i)[m] - inst_agg(b, i)[m] for i in idx[:400]])
        cells.append(f"{full:+.3f} [{np.percentile(diffs, 2.5):+.3f}, {np.percentile(diffs, 97.5):+.3f}]")
    return cells


MAIN = dict(instances=("layer", "layer_gtmk", "limit"), unet_dist=("ws", "ws_gtmk", None))


def load(spec):
    d, _, name = spec.partition(":"); name = name or "instances"
    R = json.load(open(os.path.join(d, f"{name}.json")))
    per = dict(np.load(os.path.join(d, f"{name}_perimage.npz")))
    main, oracle, limit = MAIN[name]
    R["_main"], R["_oracle"], R["_limit"], R["_name"] = main, oracle, limit, name
    return R, per


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True, help="label=dir")
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    runs = [(lab, *load(d)) for lab, d in (r.split("=", 1) for r in args.runs)]
    def fold(R):
        return (R["args"].get("train_fold", 1), R["args"].get("test_fold", 2))
    L = []
    # --- training
    L += ["## Training", "", "| run | model | folds (train → test, tune) | seed | marker head | peak loss | training markers | train maxit | s / epoch | PCG it. / batch, epochs 0-9 / 10-19 / 20-29 | epochs at the cap | final edge scale | final loss (ce / aux / mk / edge / peak) |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for lab, R, per in runs:
        A, log = R["args"], R["log"]
        folds = f"{A.get('train_fold', 1)} → {A.get('test_fold', 2)}, {A.get('tune_fold', 0) or '–'}"
        if R["_name"] == "unet_dist":
            f = log[-1] if log else {}
            L.append(f"| {lab} | U-Net + watershed | {folds} | {A.get('seed', 0)} | dist | {A.get('w_peak', 0)} | – | – | {np.mean([e['time'] for e in log]) if log else float('nan'):.0f} | – | – | – | "
                     f"– / {f.get('loss_fg', float('nan')):.4f} / {f.get('loss_mk', float('nan')):.4f} / {f.get('loss_edge', float('nan')):.4f} / {f.get('loss_peak', 0):.4f} |")
            continue
        sched = A.get("mk_sched")
        trmk = "ground truth" if not sched else f"predicted from ep. {sched[0]} (all from {sched[1]})"
        if not log:
            L.append(f"| {lab} | layer | {folds} | {A.get('seed', 0)} | {A.get('mk_head', 'bce')} | {A.get('w_peak', 0)} | {trmk} | {A['maxit']} | – | – | – | {R['test'].get('_edge_scale', float('nan')):.2f} | – |"); continue
        it = np.array([e["iters"] for e in log]); t = np.mean([e["time"] for e in log])
        thirds = " / ".join(f"{it[a:b].mean():.0f}" for a, b in ((0, 10), (10, 20), (20, 30)) if len(it) > a)
        cap = int((it >= A["maxit"] - 0.5).sum())
        f = log[-1]
        L.append(f"| {lab} | layer | {folds} | {A.get('seed', 0)} | {A.get('mk_head', 'bce')} | {A.get('w_peak', 0)} | {trmk} | {A['maxit']} | {t:.0f} | {thirds} | {cap}/{len(log)} | {f['edge_scale']:.2f} | "
                 f"{f['loss_ce']:.4f} / {f['loss_aux']:.4f} / {f['loss_mk']:.4f} / {f['loss_edge']:.4f} / {f.get('loss_peak', 0):.4f} |")
    L.append("")
    # --- validation curves
    eps = sorted({e["epoch"] for _, R, _ in runs for e in R["log"] if "val" in e})
    if eps:
        L += ["## Validation during training (own markers, untuned thresholds; first 200 test patches)", "",
              "| epoch | p | " + " | ".join(f"{lab}: IoU / F1 / PQ / one-marker" for lab, _, _ in runs) + " |", "|---|---|" + "---|" * len(runs)]
        for ep in eps:
            cells = []; p = float("nan")
            for lab, R, per in runs:
                e = next((e for e in R["log"] if e["epoch"] == ep and "val" in e), None)
                if e is None:
                    cells.append("–"); continue
                p = e.get("p", p); v = e["val"][R["_main"]]; m = e["val"]["markers"]
                cells.append(f"{v['iou']:.3f} / {v['f1_05']:.3f} / {v['pq']:.3f} / {100 * m['frac_one']:.0f} %")
            L.append(f"| {ep} | {p:.1f} | " + " | ".join(cells) + " |")
        L.append("")
    # --- test headline
    L += ["## Test (all of the test fold; limits on the subset)", "", "| run | test fold | output | n | " + " | ".join(c[1] for c in COLS) + " |", "|---|---|---|---|" + "---|" * len(COLS)]
    for lab, R, per in runs:
        T = R["test"]
        rows_ = ((R["_main"], "predicted markers"), (R["_oracle"], "GT markers (oracle)")) + (((R["_limit"], "PW limit, learned costs"),) if R["_limit"] else ())
        for m, nm in rows_:
            if m in T:
                L.append(f"| {lab} | {fold(R)[1]} | {nm} | {T[m]['n']} | " + " | ".join(fmt(T[m].get(c[0]), c[0]) for c in COLS) + " |")
    L.append("")
    L += ["## Marker quality on the test fold", "", "| run | test fold | markers | one | none | several | bg / patch | markers / patch |", "|---|---|---|---|---|---|---|---|"]
    for lab, R, per in runs:
        M = R["test"]["markers"]; A = R["args"]
        mk = f"{A.get('mk_head', 'dist' if R['_name'] == 'unet_dist' else 'bce')}: thr {A['mk_thr']}, min area {A['mk_min_area']}" + (f", h {A['mk_h']}" if A.get("mk_head", "dist") == "dist" else "")
        tn = R.get("mk_tune") or R.get("pp_tune")
        if tn:
            mk += f" (fold {tn['fold']})"
        L.append(f"| {lab} | {fold(R)[1]} | {mk} | {100 * M['frac_one']:.1f} % | {100 * M['frac_zero']:.1f} % | {100 * M['frac_multi']:.1f} % | {M['bg_per_patch']:.2f} | {M['mk_per_patch']:.1f} |")
    L.append("")
    # --- paired differences between runs
    L += [f"## Paired per-patch differences between runs on the same test fold (bootstrap 95 % intervals)", "",
          "| comparison | test fold | IoU | BF₂ | edge align. | F1@0.5 | PQ | AJI |", "|---|---|---|---|---|---|---|---|"]
    for i in range(len(runs)):
        for j in range(i + 1, len(runs)):
            la, Ra, pa = runs[i]; lb, Rb, pb = runs[j]
            if fold(Ra)[1] != fold(Rb)[1]:
                continue
            n = len(pa[Ra["_main"] + "__iou"]); idx = boot_idx(n)
            for key, nm in (("_main", "main output"), ("_oracle", "oracle"), ("_limit", "limit")):
                ma, mb = Ra[key], Rb[key]
                if ma is None or mb is None or f"{ma}__iou" not in pa or f"{mb}__iou" not in pb:
                    continue
                a, b = sub(pa, ma), sub(pb, mb)
                if key == "_limit":
                    if not np.array_equal(pa["limit__idx"], pb["limit__idx"]):
                        oa = np.argsort(pa["limit__idx"]); ob = np.argsort(pb["limit__idx"])
                        a = {k: v[oa] for k, v in a.items()}; b = {k: v[ob] for k, v in b.items()}
                    ii = boot_idx(len(a["iou"]))
                else:
                    ii = idx
                L.append(f"| {la} − {lb}, {nm} | {fold(Ra)[1]} | " + " | ".join(paired(a, b, ii)) + " |")
    L.append("")
    txt = "\n".join(L)
    print(txt)
    if args.out:
        open(args.out, "w").write(txt)


if __name__ == "__main__":
    main()
