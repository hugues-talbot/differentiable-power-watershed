#!/usr/bin/env python3
"""
Experiment 4: p-annealing versus fixed-point reweighting, on the synthetic scenes of
exp_softmax_synthetic.py (simulated soft prediction + image edge costs, alpha = 0.1).

Two ways to sharpen the Random Walker output:
  * annealed:   weights exp(-p c), p raised (the one-parameter family of the note);
  * reweighted: weights exp(-p0 c) at a benign p0, then `outer` fixed-point steps
                w <- w0 * rho(jump of the current solution; eps), rho = Cauchy
                (eps^2/(eps^2+d^2), the smoothed-l0 half-quadratic weight) or
                smoothed-l1 (1/(1+|d|/eps)).
For each we record, against the ground truth: IoU, boundary F at 1 and 2 px, softness;
and as cost / trainability measures: inner PCG iterations (to 1e-9) of the last and of
all solves, the smallest edge weight, and the gradient of 1/2 ||x - gt||^2 with respect
to the edge costs (autograd through the whole layer): its norm and the number of edges
carrying 90 % of its mass.

usage: exp_reweighted_synthetic.py --outdir results_reweighted [--res 256] [--n 3]
"""
import argparse, json, os, time
import numpy as np
import torch
from pw_layer import RWLayer, unary_costs_from_prob, hdiff, vdiff
from exp_softmax_synthetic import make_scene, render, soft_prediction, edge_costs, metrics

PS = (10, 20, 50, 100, 200, 500)
EPS = (0.1, 0.03, 0.01)
KINDS = ("cauchy", "l1")
OUTER = 5
P0S = (10.0, 50.0, 100.0)
ALPHA = 0.1


def _support(g):
    ag = torch.cat([g[0].abs().flatten(), g[1].abs().flatten()])
    tot = float(ag.sum())
    if tot == 0:
        return 0.0, 0, 0
    srt = torch.sort(ag, descending=True).values
    cum = torch.cumsum(srt, 0) / tot
    return float(torch.sqrt((ag * ag).sum())), int(torch.searchsorted(cum, 0.9)) + 1, int(torch.searchsorted(cum, 0.99)) + 1


def grad_stats(x, gt_t, ch, cv):
    """Gradient w.r.t. the edge costs of (a) the squared loss to the ground truth, whose
    support shrinks trivially as the loss is minimised, and (b) a fixed random linear
    functional sum_i r_i x_i, r_i = +-1, which measures through how many edges the
    output can be influenced at all (the sensitivity support)."""
    loss = 0.5 * ((x - gt_t) ** 2).sum()
    g = torch.autograd.grad(loss, (ch, cv), retain_graph=True)
    l2, n90, n99 = _support(g)
    gen = torch.Generator(device="cpu").manual_seed(1234)
    r = (torch.randint(0, 2, x.shape, generator=gen).to(x) * 2 - 1)
    g2 = torch.autograd.grad((x * r).sum(), (ch, cv))
    l2r, n90r, n99r = _support(g2)
    return dict(grad_l2=l2, n90=n90, n99=n99, loss=float(loss), grad_rand_l2=l2r, n90_rand=n90r, n99_rand=n99r)


def run(args):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dt = torch.float64
    rng = np.random.default_rng(args.seed)
    os.makedirs(args.outdir, exist_ok=True)
    out = open(os.path.join(args.outdir, "reweighted_synthetic.jsonl"), "w")
    examples = {}
    T = lambda a: torch.from_numpy(np.ascontiguousarray(a)).to(dt).to(device)[None, None]
    for sigma in (0.05, 0.1):
        for shift in (0, 4):
            for k in range(args.n):
                gt = make_scene(args.res, rng)
                img8 = render(gt, sigma, rng, edge_shift=shift)
                s = soft_prediction(gt, rng)
                ch_np, cv_np = edge_costs(img8)
                tag = f"s{sigma:g}_shift{shift}_{k}"
                base = dict(case=tag, sigma=sigma, edge_shift=shift, k=k, res=args.res, unary_scale=ALPHA)
                gt_t = T(gt.astype(np.float64))
                c1, c0 = unary_costs_from_prob(T(s), cmax=8.0)
                c1, c0 = ALPHA * c1, ALPHA * c0
                ex = dict(img=img8, gt=gt, s=s)
                out.write(json.dumps(dict(base, family="soft", **metrics(s, gt))) + "\n")
                # --- annealed family
                for p in PS:
                    ch, cv = T(ch_np).requires_grad_(True), T(cv_np).requires_grad_(True)
                    st = {}; t0 = time.time()
                    x = RWLayer("implicit", tol=1e-9, maxit=5000)(ch, cv, c1, c0, float(p), stats=st)
                    gs = grad_stats(x, gt_t, ch, cv)
                    xn = x.detach().cpu().numpy()[0, 0]
                    rec = dict(base, family="annealed", p=p, iters_last=st["last_iters"], iters_cum=st["iters"],
                               wmin=float(np.exp(-p * max(ch_np.max(), cv_np.max()))), t=time.time() - t0,
                               **metrics(xn, gt), **gs)
                    out.write(json.dumps(rec) + "\n")
                    if p in (100, 500):
                        ex[f"ann_p{p}"] = xn
                # --- reweighted family
                for kind, eps, P0 in [(kd, e, q) for kd in KINDS for e in EPS for q in P0S if kd == "cauchy" or q == 10.0]:
                        ch, cv = T(ch_np).requires_grad_(True), T(cv_np).requires_grad_(True)
                        st = {}; rec_x = []; t0 = time.time()
                        layer = RWLayer("reweighted", tol=1e-9, maxit=5000, outer=OUTER, eps=eps, kind=kind)
                        x = layer(ch, cv, c1, c0, P0, stats=st, record=rec_x)
                        gs = grad_stats(x, gt_t, ch, cv)
                        per = st["per_solve"]
                        for step, xs in enumerate(rec_x):
                            xn = xs.detach().cpu().numpy()[0, 0]
                            rec = dict(base, family="reweighted", kind=kind, eps=eps, p0=P0, step=step,
                                       iters_last=per[step], iters_cum=int(sum(per[:step + 1])), **metrics(xn, gt))
                            if step == OUTER:
                                rec.update(gs); rec["wmin"] = st.get("wmin"); rec["t"] = time.time() - t0
                            out.write(json.dumps(rec) + "\n")
                            if kind == "cauchy" and eps == 0.03 and step in (1, 5):
                                ex[f"rw_p{P0:g}_e{eps:g}_k{step}"] = xn
                out.flush()
                last = [json.loads(l) for l in open(os.path.join(args.outdir, "reweighted_synthetic.jsonl"))][-1]
                print(f"{tag}: soft bf2={metrics(s, gt)['bf2']:.3f} | annealed p100 bf2={metrics(ex['ann_p100'], gt)['bf2']:.3f} "
                      f"p500={metrics(ex['ann_p500'], gt)['bf2']:.3f} | cauchy e0.03 k5: "
                      + " ".join(f"p0={q:g}:{metrics(ex[f'rw_p{q:g}_e0.03_k5'], gt)['bf2']:.3f}" for q in P0S)
                      + f" soft={metrics(ex['rw_p100_e0.03_k5'], gt)['soft_frac']:.3f}",
                      flush=True)
                if k == 0:
                    examples[tag] = ex
    out.close()
    np.savez_compressed(os.path.join(args.outdir, "examples.npz"),
                        **{f"{t}__{kk}": v for t, d in examples.items() for kk, v in d.items()})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", type=int, default=256)
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--outdir", default="results_reweighted")
    run(ap.parse_args())
