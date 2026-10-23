#!/usr/bin/env python3
"""The practitioner's baseline, done properly: threshold the soft output at several
levels instead of only 0.5, for a trained model on the PanNuke test fold.

usage: threshold_sweep.py --ckpt results_pannuke/unet.pt --variant unet --out results_pannuke/threshold_sweep_unet.json
"""
import argparse, json, os, time
from multiprocessing import Pool
import numpy as np
import torch
from exp_unet_seg import load_dataset, pixel_metrics
from exp_unet_pets import Segmenter
from seg_metrics import instance_metrics, strong_edges, edge_alignment

THRESHOLDS = (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8)


def _one(job):
    prob, y, inst, img = job
    strong = strong_edges(img.transpose(1, 2, 0))
    out = {}
    for t in THRESHOLDS:
        pred = (prob > t)
        m = pixel_metrics(pred.astype(np.float32), y)
        m.pop("soft_frac", None); m.pop("entropy", None)
        m["edge_align"] = edge_alignment(pred, strong=strong)
        m.update({f"inst_{k}": v for k, v in instance_metrics(pred, inst).items() if isinstance(v, (int, float))})
        out[t] = m
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--variant", choices=("unet", "rw_learned"), default="unet")
    ap.add_argument("--p", type=float, default=50.0)
    ap.add_argument("--K", type=int, default=20)
    ap.add_argument("--cmax", type=float, default=8.0)
    ap.add_argument("--dataset", default="pannuke")
    ap.add_argument("--data", default="data")
    ap.add_argument("--train-fold", type=int, default=1)
    ap.add_argument("--test-fold", type=int, default=2)
    ap.add_argument("--test-n", type=int, default=0)
    ap.add_argument("--res", type=int, default=256)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    d = load_dataset(args)
    model = Segmenter(args.variant, args.K, args.cmax).to(device)
    model.load_state_dict(torch.load(args.ckpt, map_location=device))
    model.eval()
    X, Y, inst = d["X_test"], d["Y_test"], d["inst_test"]
    probs_logit, probs_layer = [], []
    t0 = time.time()
    with torch.no_grad():
        for i in range(0, len(X), args.batch):
            img = torch.from_numpy(X[i:i + args.batch]).to(device).float() / 255
            logit, x, _ = model(img, args.p)
            probs_logit.append(torch.sigmoid(logit).cpu().numpy()[:, 0])
            if x is not None:
                probs_layer.append(x.cpu().numpy()[:, 0])
    print(f"inference {time.time() - t0:.0f}s", flush=True)
    result = {}
    for name, probs in (("logits", probs_logit), ("layer", probs_layer)):
        if not probs:
            continue
        P = np.concatenate(probs)
        with Pool(args.workers) as pool:
            rows = pool.map(_one, [(P[g], Y[g], inst[g], X[g]) for g in range(len(P))], chunksize=16)
        agg = {}
        for t in THRESHOLDS:
            keys = rows[0][t].keys()
            agg[str(t)] = {k: float(np.mean([r[t][k] for r in rows])) for k in keys}
        result[name] = agg
        print(name, flush=True)
        for t in THRESHOLDS:
            a = agg[str(t)]
            print(f"  t={t:.1f}  iou={a['iou']:.4f} bf1={a['bf1']:.4f} bf2={a['bf2']:.4f} band={a['band_acc']:.4f} "
                  f"edge={a['edge_align']:.3f} " + " ".join(f"{k[5:]}={v:.3f}" for k, v in a.items() if k.startswith("inst_")),
                  flush=True)
    with open(args.out, "w") as f:
        json.dump(dict(args=vars(args), thresholds=THRESHOLDS, n=len(Y), result=result), f, indent=1)


if __name__ == "__main__":
    main()
