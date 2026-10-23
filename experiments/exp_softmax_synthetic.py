#!/usr/bin/env python3
"""
Experiment 1 (no training): the RW/PW layer as a tunable, spatially coupled softmax.

A simulated U-Net output s (ground truth, elastically displaced by a few pixels,
blurred, soft) is passed through the prior-augmented RW layer with edge costs
from the image and unary costs alpha * (-log s, -log(1-s)), everything raised
to p.  alpha sets the strength of the unaries relative to the edges (Grady's
gamma).  For a ladder of p, and for the exact PW limit, we measure against the
ground truth: IoU, boundary F-score at 1 and 2 px, and how soft the output is.
Truncated solvers (K Jacobi-PCG / Jacobi steps) are evaluated at a few p.  A
control set has the image edge displaced from the true boundary, which is the
layer's failure mode.

usage: exp_softmax_synthetic.py --outdir results_softmax [--res 256] [--n 4]
"""
import argparse, json, os, time
import numpy as np
import torch
from scipy import ndimage
from pw_layer import RWLayer, unary_costs_from_prob, pw_limit_numpy, boundary_fscore, iou, softness
from pw_conditioning import disc

PS = (1, 2, 5, 10, 20, 50, 100, 200, 500)
KS = (5, 10, 20, 50)
P_TRUNC = (20, 50, 100)
P_SHOW = (5, 20, 100, 500)


def make_scene(res, rng):
    H = W = res
    gt = disc(H, W, 0.45 * H, 0.38 * W, 0.24 * res)
    yy, xx = np.mgrid[:H, :W]
    gt |= (yy > 0.58 * H) & (yy < 0.88 * H) & (xx > 0.52 * W) & (xx < 0.92 * W)
    gt |= disc(H, W, 0.22 * H, 0.76 * W, 0.09 * res)
    # a thin protrusion: the kind of detail a soft prediction rounds off
    gt |= (np.abs(yy - 0.45 * H) < 0.012 * res) & (xx > 0.38 * W) & (xx < 0.72 * W)
    return gt


def render(gt, sigma, rng, edge_shift=0):
    """8-bit image whose intensity edge is the GT boundary (or shifted by edge_shift px)."""
    H, W = gt.shape
    region = ndimage.binary_dilation(gt, iterations=edge_shift) if edge_shift > 0 else gt
    illum = 0.08 * np.linspace(-1, 1, W)[None, :] + 0.05 * np.linspace(-1, 1, H)[:, None]
    img = np.where(region, 0.65, 0.35) + illum + sigma * rng.standard_normal((H, W))
    return np.clip(np.round(img * 255), 0, 255).astype(np.uint8)


def soft_prediction(gt, rng, blur=4.0, amp=3.0, logit_scale=2.5, noise=0.5):
    """Simulated U-Net output: elastic displacement, blur, soft logits."""
    H, W = gt.shape
    yy, xx = np.mgrid[:H, :W].astype(np.float64)
    dy = ndimage.gaussian_filter(rng.standard_normal((H, W)), 12); dy *= amp / (np.abs(dy).max() + 1e-9)
    dx = ndimage.gaussian_filter(rng.standard_normal((H, W)), 12); dx *= amp / (np.abs(dx).max() + 1e-9)
    warped = ndimage.map_coordinates(gt.astype(np.float64), [yy + dy, xx + dx], order=1, mode="nearest")
    f = ndimage.gaussian_filter(2 * warped - 1, blur)
    logit = logit_scale * f + noise * ndimage.gaussian_filter(rng.standard_normal((H, W)), 3) * 4
    return 1 / (1 + np.exp(-logit))


def edge_costs(img8):
    I = img8.astype(np.float64) / 255.0
    return (I[:, 1:] - I[:, :-1]) ** 2, (I[1:, :] - I[:-1, :]) ** 2


def metrics(x, gt):
    pred = x > 0.5
    frac, ent = softness(x)
    return dict(iou=float(iou(pred, gt)), bf1=float(boundary_fscore(pred, gt, 1)),
                bf2=float(boundary_fscore(pred, gt, 2)), soft_frac=frac, entropy=ent)


def run_one(args, out, examples, device, dt, layer, gt, img8, s, tag, base, alpha):
    ch_np, cv_np = edge_costs(img8)
    T = lambda a: torch.from_numpy(np.ascontiguousarray(a)).to(dt).to(device)[None, None]
    ch, cv = T(ch_np), T(cv_np)
    c1, c0 = unary_costs_from_prob(T(s), cmax=args.cmax)
    c1, c0 = alpha * c1, alpha * c0
    ms = metrics(s, gt)
    out.write(json.dumps(dict(base, method="soft_prediction", p=None, **ms)) + "\n")
    xs = {}
    for p in PS:
        t0 = time.time()
        x = layer(ch, cv, c1, c0, float(p)).cpu().numpy()[0, 0]
        xs[p] = x
        out.write(json.dumps(dict(base, method="rw_implicit", p=p, t=time.time() - t0, **metrics(x, gt))) + "\n")
        if p in P_TRUNC:
            for K in KS:
                for mode in ("unrolled", "jacobi"):
                    xk = RWLayer(mode, K=K)(ch, cv, c1, c0, float(p)).cpu().numpy()[0, 0]
                    rec = dict(base, method=f"{mode}_K{K}", p=p, K=K, **metrics(xk, gt))
                    rec["lab_vs_converged"] = float(((xk > 0.5) != (x > 0.5)).mean())
                    out.write(json.dumps(rec) + "\n")
    t0 = time.time()
    xinf, st = pw_limit_numpy(ch_np, cv_np, c1.cpu().numpy()[0, 0], c0.cpu().numpy()[0, 0])
    ml = metrics(xinf, gt)
    out.write(json.dumps(dict(base, method="pw_limit", p=float("inf"), t=time.time() - t0, pw=st, **ml)) + "\n")
    out.flush()
    print(f"{tag} a={alpha:g}: soft iou={ms['iou']:.3f} bf2={ms['bf2']:.3f} | "
          + " ".join(f"p{p}:{metrics(xs[p], gt)['bf2']:.3f}" for p in P_SHOW)
          + f" | limit iou={ml['iou']:.3f} bf2={ml['bf2']:.3f} soft={ml['soft_frac']:.3f}", flush=True)
    if base["k"] == 0:
        examples[f"{tag}_a{alpha:g}"] = dict(img=img8, gt=gt, s=s, xinf=xinf, **{f"x{p}": xs[p] for p in P_SHOW})


def run(args):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dt = torch.float64
    rng = np.random.default_rng(args.seed)
    os.makedirs(args.outdir, exist_ok=True)
    out = open(os.path.join(args.outdir, "softmax_synthetic.jsonl"), "w")
    examples = {}
    layer = RWLayer("implicit", tol=1e-9, maxit=5000)
    for sigma in (0.05, 0.1):
        for shift in (0, 4):
            for k in range(args.n):
                gt = make_scene(args.res, rng)
                img8 = render(gt, sigma, rng, edge_shift=shift)
                s = soft_prediction(gt, rng)
                tag = f"s{sigma:g}_shift{shift}_{k}"
                for alpha in args.unary_scales:
                    base = dict(case=tag, sigma=sigma, edge_shift=shift, k=k, res=args.res, unary_scale=alpha)
                    run_one(args, out, examples, device, dt, layer, gt, img8, s, tag, base, alpha)
    out.close()
    np.savez_compressed(os.path.join(args.outdir, "examples.npz"),
                        **{f"{t}__{k}": v for t, d in examples.items() for k, v in d.items()})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", type=int, default=256)
    ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--unary-scales", type=str, default="0.03,0.1,0.3,1",
                    help="multipliers alpha on the unary costs -log s")
    ap.add_argument("--cmax", type=float, default=8.0, help="clip for the unary costs")
    ap.add_argument("--outdir", default="results_softmax")
    a = ap.parse_args()
    a.unary_scales = [float(x) for x in a.unary_scales.split(",")]
    run(a)
