#!/usr/bin/env python3
"""Diagnostic: instance metrics of trained models on PanNuke fold 2 after removing
connected components smaller than a minimum area (are the spurious components of a
loss speckle that trivial post-processing removes, or real fragmentation?).

usage: inst_minarea.py --runs bce=results_pannuke boundary=results_pannuke_losses/boundary ... --out results_pannuke_losses/minarea.json
"""
import argparse, json, os
import numpy as np
import torch
from scipy import ndimage
from exp_unet_seg import SegmenterX, PP_MODES, postprocess_edge, contour_map
from seg_metrics import instance_metrics, aggregate_instance, FOUR
from pw_layer import iou, pw_limit_numpy
from multiprocessing import get_context


def _limit_worker(job):
    g, ch, cv, c1, c0 = job
    return g, pw_limit_numpy(ch, cv, c1, c0)[0]


def remove_small(pred, min_area):
    if min_area <= 1:
        return pred
    lab, n = ndimage.label(pred, structure=FOUR)
    if n == 0:
        return pred
    area = np.bincount(lab.ravel())
    keep = area >= min_area; keep[0] = False
    return keep[lab]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True, help="label=dir pairs (dir holds unet.pt, rw_learned.pt)")
    ap.add_argument("--areas", nargs="+", type=int, default=(1, 8, 32))
    ap.add_argument("--data", default="data")
    ap.add_argument("--test-fold", type=int, default=2)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", action="store_true", help="also the exact PW limit on the limit_idx of each rw_learned.json")
    ap.add_argument("--limit-workers", type=int, default=4)
    args = ap.parse_args()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    te = np.load(os.path.join(args.data, f"pannuke_fold{args.test_fold}.npz"))
    X = np.ascontiguousarray(te["images"].transpose(0, 3, 1, 2)); Y = te["binary"]; inst = te["inst"]
    out = {}
    per_image = {}
    for s in args.runs:
        lab, d = s.split("=", 1)
        for v in ("unet", "rw_learned", "unet_edge"):
            f = os.path.join(d, f"{v}.pt")
            if not os.path.exists(f):
                continue
            a = argparse.Namespace(**json.load(open(os.path.join(d, f"{v}.json")))["args"])
            model = SegmenterX(v, a.K, a.cmax, getattr(a, "edge_param", "sigmoid"), getattr(a, "edge_cmax", 8.0),
                               getattr(a, "edge_learn_scale", False)).to(device)
            model.load_state_dict(torch.load(f, map_location=device)); model.eval()
            p_eval = float(a.p1)
            if v == "unet":
                modes = ("logits",)
            elif v == "unet_edge":
                modes = ("logits",) + PP_MODES
            else:
                modes = ("logits", "layer", "limit") if args.limit else ("logits", "layer")
            rows = {(mode, a): [] for mode in modes for a in args.areas}
            ious = {k: [] for k in rows}
            limit_idx = set(json.load(open(os.path.join(d, f"{v}.json")))["limit_idx"]) if "limit" in modes else set()
            pp_md = getattr(a, "pp_md", None)                   # (the loop below rebinds `a` to the areas)
            jobs = []
            with torch.no_grad():
                for i in range(0, len(X), args.batch):
                    img = torch.from_numpy(X[i:i + args.batch]).to(device).float() / 255
                    logit, x, costs = model(img, p_eval)
                    outs = {"logits": torch.sigmoid(logit).cpu().numpy()[:, 0]}
                    if v == "unet_edge":                         # the post-processed outputs, as 0/1 arrays
                        c = contour_map(costs)
                        pps = [postprocess_edge(outs["logits"][j], c[j], **pp_md) for j in range(len(img))]
                        outs.update({m: np.stack([pp[m] for pp in pps]).astype(np.float32) for m in PP_MODES})
                    if x is not None:
                        outs["layer"] = x.cpu().numpy()[:, 0]
                        for j in range(len(img)):
                            if i + j in limit_idx:
                                jobs.append((i + j,) + tuple(c[j, 0].double().cpu().numpy() for c in costs))
                    outs = {m: arr for m, arr in outs.items() if m != "limit"}
                    for j in range(len(img)):
                        for mode, arr in outs.items():
                            for a in args.areas:
                                pred = remove_small(arr[j] > 0.5, a)
                                rows[(mode, a)].append(instance_metrics(pred, inst[i + j]))
                                ious[(mode, a)].append(float(iou(pred, Y[i + j])))
            if jobs:
                with get_context("fork").Pool(args.limit_workers) as pool:
                    for g, xinf in pool.imap_unordered(_limit_worker, jobs, chunksize=2):
                        for a in args.areas:
                            pred = remove_small(xinf > 0.5, a)
                            rows[("limit", a)].append(instance_metrics(pred, inst[g]))
                            ious[("limit", a)].append(float(iou(pred, Y[g])))
            for (mode, a), rs in rows.items():
                if not rs:
                    continue
                agg = aggregate_instance(rs); agg["iou"] = float(np.mean(ious[(mode, a)]))
                for k in ("n_pred", "n_gt", "tp", "fp", "fn", "iou_sum"):
                    per_image[f"{lab}/{v}/{mode}/min_area={a}/{k}"] = np.array([r[k] for r in rs])
                per_image[f"{lab}/{v}/{mode}/min_area={a}/iou"] = np.array(ious[(mode, a)])
                out[f"{lab}/{v}/{mode}/min_area={a}"] = agg
                print(f"{lab:9s} {v:11s} {mode:7s} min_area={a:3d}  IoU {agg['iou']:.3f}  F1 {agg['f1_05']:.3f}  PQ {agg['pq']:.3f}  "
                      f"count err {agg['count_err']:.3f}  n_pred {agg['n_pred_mean']:.1f}", flush=True)
    json.dump(out, open(args.out, "w"), indent=1)
    np.savez_compressed(args.out.replace(".json", "_perimage.npz"), **per_image)   # per-image counts, for paired bootstraps


if __name__ == "__main__":
    main()
