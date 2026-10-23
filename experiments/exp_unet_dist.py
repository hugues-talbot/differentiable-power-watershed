#!/usr/bin/env python3
"""
The fair baseline for the multi-marker layer of sections 11 / 11.1 (section 11.2): a plain
U-Net with no layer, three heads and a HoVer-Net-style post-processing.

Model: the U-Net of exp_unet_seg.py with four output channels and no RW/PW layer:
  channel 0   the foreground logit, BCE against the binary nucleus mask (--gap: the gap mask);
  channels 1-2 the contour head, trained with section 10's edge target exactly as
              --variant unet_edge of exp_unet_seg.py (edge_loss, --w-edge, --edge-pos, --edge-seam);
  channel 3   the distance head of exp_instance_pannuke.py --mk-head dist: sigmoid output against
              dist_target (normalised Chebyshev distance to the instance boundary, capped at
              --mk-rmax px, 1 at every nucleus' centre), MSE weighted --w-mk.
Same recipe as the layer runs: fold 1 -> fold 2, --epochs 30, batch 16, d4 augmentation, Adam
1e-3 with cosine annealing, one seed.

Post-processing (HoVer-Net style, `hover_labels`): markers = the h-maxima of the predicted
distance map grown by a watershed of the map down to thr (markers_from_dist of
exp_instance_pannuke.py, basins below min_area px dropped), then a marker watershed inside the
thresholded foreground (s > 0.5) of one of three reliefs (--relief): the contour map c (mean of
the two directions of the contour head), the negative distance map -d, or their sum c - d.
Foreground components that contain no marker get no label (as the layer gives unmarked nuclei
to the background); `ws_fb` keeps them as instances when they have at least --fb-min-area px.
--tune-fold F chooses thr, min_area, h and the relief by the PQ of the result on --tune-n evenly
spaced patches of fold F (never the test fold); the whole table goes to the json as pp_tune.

Outputs evaluated on fold 2 (label maps; instance metrics on the labels, pixel metrics on
label > 0, the same rows as exp_instance_pannuke.py):
  logits       s > 0.5, 4-connected components (the plain U-Net pipeline of this model)
  ws           the tuned post-processing (markers of the distance head, chosen relief)
  ws_contour / ws_dist / ws_both   the same markers with each relief
  ws_fb        ws + the unmarked foreground components kept
  ws_gtmk      the chosen relief from the ground-truth markers (instances eroded by 2 px): the
               oracle on markers, the counterpart of the layer's layer_gtmk
  gt_inst      the ground-truth instances
and, with --layer-dir (the section 11.1 distance-head layer run, its .pt and json), the 2 x 2
of markers x final assignment on the same test patches:
  layer        the layer's own markers through the layer's converged solve (reproduces the run)
  lmk_ws       the layer's markers through this model's watershed (this model's foreground and relief)
  lmk_ws_own   the layer's markers through a watershed of the layer's own contour / distance map
               inside the layer's own output foreground (its solve's label > 0): the solve replaced
               by a watershed with everything else held fixed
  bmk_layer    this model's markers through the layer's converged solve
Marker quality (one / none / several markers per nucleus, background markers per patch) for
this model's markers (markers__*) and the layer's (lmarkers__*).

usage: exp_unet_dist.py --tune-fold 3 --layer-dir results_pannuke_instances/dist --outdir results_pannuke_instances/unet_dist
       exp_unet_dist.py --eval-only --tune-fold 3 --outdir results_pannuke_instances/unet_dist
"""
import argparse, json, os, time
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy import ndimage
from exp_unet_pets import UNet
from exp_unet_seg import load_dataset, augment, pixel_edge_probs, edge_loss, summarise, flatten_per_image
from exp_instance_pannuke import (tb_writer, tb_log, choose_examples, examples_subset, markers_from_dist, dist_target, peak_loss, neg_loss, grad_loss, marker_quality, label_metrics, argmax_labels,
                                  add_fallback_markers, InstanceSegmenter)
from pw_layer import MultiRWLayer, label_systems, split_labels, eroded_markers
from seg_metrics import instance_metrics, aggregate_instance, strong_edges, FOUR

RELIEFS = ("contour", "dist", "both")
MODES = ("logits", "ws", "ws_contour", "ws_dist", "ws_both", "ws_fb", "ws_gtmk", "layer", "lmk_ws", "lmk_ws_own", "bmk_layer")


# ----------------------------------------------------------------------------
# model
# ----------------------------------------------------------------------------
class DistSegmenter(nn.Module):
    """U-Net with the foreground logit, the two-channel contour head and the distance head."""

    def __init__(self):
        super().__init__()
        self.unet = UNet(4)

    def forward(self, img):
        out = self.unet(img)
        return dict(logit=out[:, :1], s=torch.sigmoid(out[:, :1]), eprob=torch.sigmoid(out[:, 1:3]),
                    dm=torch.sigmoid(out[:, 3:4]))


# ----------------------------------------------------------------------------
# post-processing
# ----------------------------------------------------------------------------
def relief_map(c, dm, relief):
    if relief == "contour":
        return c
    if relief == "dist":
        return -dm
    if relief == "both":
        return c - dm
    raise ValueError(relief)


def hover_labels(lab, fg, rel):
    """Marker label map lab (H,W), foreground mask fg (bool), relief rel -> label map of the
    marker watershed of rel inside fg (components with no marker stay 0)."""
    from skimage.segmentation import watershed
    if lab.max() == 0 or not fg.any():
        return np.zeros(lab.shape, np.int32)
    return watershed(rel, lab, mask=fg, connectivity=1).astype(np.int32)


def gt_markers(inst_np, device, r=2):
    """Ground-truth instances (B,H,W) int -> marker label maps (B,H,W) int32: each instance
    eroded by r px keeping its core (the layer's oracle markers)."""
    inst_t = torch.from_numpy(inst_np.astype(np.int64)).to(device)[:, None]
    core = eroded_markers(inst_t, r)
    return (inst_t * core)[:, 0].cpu().numpy().astype(np.int32)


# ----------------------------------------------------------------------------
# the section 11.1 layer, for the marker swap
# ----------------------------------------------------------------------------
def load_layer(layer_dir, device, name="instances"):
    """The distance-head layer run: its model, its args (marker settings as chosen on fold 3)
    and a converged MultiRWLayer."""
    R = json.load(open(os.path.join(layer_dir, f"{name}.json")))
    A = argparse.Namespace(**R["args"])
    model = InstanceSegmenter(A.cmax, A.edge_cmax, A.learn_scale).to(device)
    model.load_state_dict(torch.load(os.path.join(layer_dir, f"{name}.pt"), map_location=device))
    model.eval()
    layer = MultiRWLayer(tol=A.eval_tol, maxit=A.eval_maxit)
    print(f"  layer loaded from {layer_dir}: head {A.mk_head}, markers thr {A.mk_thr} / min area {A.mk_min_area} / h {A.mk_h}, p {A.p1}", flush=True)
    return model, A, layer


def layer_solve(lmodel, layer, out, labs, p, device):
    """Converged multi-marker solve of the layer's costs from the marker label maps labs
    (list of (H,W) int) -> list of (labels, confidence)."""
    sysd = label_systems(torch.from_numpy(np.stack(labs)).to(device)[:, None].long())
    xs = split_labels(layer(out["ch"], out["cv"], out["c0"], out["c1"], sysd, float(p)), sysd)
    return [argmax_labels(x) for x in xs]


# ----------------------------------------------------------------------------
# post-processing chosen on a held-out fold
# ----------------------------------------------------------------------------
def tune_postproc(model, args, device):
    """Grid over thr x min_area x h x relief; the setting with the best PQ on --tune-n evenly
    spaced patches of fold --tune-fold.  Returns (chosen dict, table)."""
    f = np.load(os.path.join(args.data, f"pannuke_fold{args.tune_fold}.npz"))
    n = len(f["types"])
    sel = np.linspace(0, n - 1, min(args.tune_n, n)).astype(int)
    X = np.ascontiguousarray(f["images"][sel].transpose(0, 3, 1, 2)); inst_all = f["inst"][sel]
    mgrid = [(thr, ma, h) for thr in args.tune_thr for ma in args.tune_min_area for h in args.tune_h]
    rows = {(g, r): [] for g in mgrid for r in RELIEFS}; mq = {g: [] for g in mgrid}
    model.eval(); t0 = time.time()
    with torch.no_grad():
        for i in range(0, len(X), args.batch):
            img = torch.from_numpy(X[i:i + args.batch]).to(device).float() / 255
            out = model(img)
            s = out["s"].cpu().numpy()[:, 0]; dm = out["dm"].cpu().numpy()[:, 0]; c = out["eprob"].mean(1).cpu().numpy()
            for j in range(len(s)):
                fg = s[j] > 0.5; inst = inst_all[i + j]
                rels = {r: relief_map(c[j], dm[j], r) for r in RELIEFS}
                for g in mgrid:
                    lab = markers_from_dist(dm[j], *g)
                    mq[g].append(marker_quality(lab, inst))
                    for r in RELIEFS:
                        L = hover_labels(lab, fg, rels[r])
                        rows[(g, r)].append(instance_metrics(L > 0, inst, lab=L))
            if (i // args.batch) % 5 == 0:
                print(f"    tune {i}/{len(X)}  {time.time() - t0:.0f}s", flush=True)

    def key(g, r):
        return f"thr={g[0]}/min_area={g[1]}/h={g[2]}/{r}"
    table = {}
    for g in mgrid:
        ngt = max(sum(q["n_gt"] for q in mq[g]), 1)
        mkq = dict(frac_one=sum(q["one"] for q in mq[g]) / ngt, frac_zero=sum(q["zero"] for q in mq[g]) / ngt,
                   frac_multi=sum(q["multi"] for q in mq[g]) / ngt, bg_per_patch=sum(q["bg_mk"] for q in mq[g]) / len(mq[g]))
        for r in RELIEFS:
            a = aggregate_instance(rows[(g, r)])
            table[key(g, r)] = dict(pq=a["pq"], f1_05=a["f1_05"], aji=a["aji"], count_err=a["count_err"], n_pred=a["n_pred_mean"], **mkq)
    best = max(table, key=lambda k: table[k]["pq"])
    for k, v in table.items():
        print(f"  tune {k:40s} PQ {v['pq']:.3f}  F1 {v['f1_05']:.3f}  AJI {v['aji']:.3f}  count err {v['count_err']:.3f}  "
              f"n_pred {v['n_pred']:.1f}  one/zero/multi {v['frac_one']:.2f}/{v['frac_zero']:.2f}/{v['frac_multi']:.2f}  bg {v['bg_per_patch']:.1f}", flush=True)
    bg, br = next((g, r) for g in mgrid for r in RELIEFS if key(g, r) == best)
    chosen = dict(mk_thr=float(bg[0]), mk_min_area=int(bg[1]), mk_h=float(bg[2]), relief=br)
    print(f"  chosen post-processing: {chosen}  (fold {args.tune_fold}, {len(sel)} patches, {time.time() - t0:.0f}s)", flush=True)
    return chosen, dict(fold=int(args.tune_fold), n=int(len(sel)), chosen=chosen, table=table)


# ----------------------------------------------------------------------------
# evaluation
# ----------------------------------------------------------------------------
def evaluate(model, d, device, args, lay=None, example_idx=(), quick=False):
    """lay: (layer model, its args, its MultiRWLayer) or None.  quick: validation during
    training (logits and ws only)."""
    model.eval()
    X, Y, inst_all, types = d["X_test"], d["Y_test"], d["inst_test"], d.get("types_test")
    example_idx = set(example_idx)
    res = {k: [] for k in MODES}; res_types = {k: [] for k in MODES}
    mq, lmq, ref, examples = [], [], [], []
    timing = dict(unet_s=0.0, post_s=0.0, n=0, solve_s=0.0, solve_n=0)
    with torch.no_grad():
        for i in range(0, len(X), args.batch):
            img = torch.from_numpy(X[i:i + args.batch]).to(device).float() / 255
            y = Y[i:i + args.batch]
            if device == "cuda":
                torch.cuda.synchronize()
            t0 = time.time()
            out = model(img)
            if device == "cuda":
                torch.cuda.synchronize()
            timing["unet_s"] += time.time() - t0
            s = out["s"].cpu().numpy()[:, 0]; dm = out["dm"].cpu().numpy()[:, 0]; c = out["eprob"].mean(1).cpu().numpy()
            gmk = gt_markers(inst_all[i:i + args.batch], device) if not quick else None
            # the layer: its own markers, its solve from its own and from this model's markers
            lab_l = L_l = L_bl = None
            if lay is not None and not quick:
                lmodel, LA, layer = lay
                lout = lmodel(img)
                s_l = lout["s"].cpu().numpy()[:, 0]; dm_l = torch.sigmoid(lout["mlogit"]).cpu().numpy()[:, 0]; c_l = lout["eprob"].mean(1).cpu().numpy()
                lab_l = [markers_from_dist(dm_l[j], LA.mk_thr, LA.mk_min_area, LA.mk_h) for j in range(len(y))]
                lab_b = [markers_from_dist(dm[j], args.mk_thr, args.mk_min_area, args.mk_h) for j in range(len(y))]
                if device == "cuda":
                    torch.cuda.synchronize()
                t0 = time.time()
                L_l = layer_solve(lmodel, layer, lout, lab_l, LA.p1, device)
                L_bl = layer_solve(lmodel, layer, lout, lab_b, LA.p1, device)
                if device == "cuda":
                    torch.cuda.synchronize()
                timing["solve_s"] += time.time() - t0; timing["solve_n"] += 2 * len(y)
            for j in range(len(y)):
                g = i + j
                inst = inst_all[g]
                strong = strong_edges(X[g].transpose(1, 2, 0)) if args.edge_align and not quick else None
                tt = types[g] if types is not None else None
                t0 = time.time()
                fg = s[j] > 0.5
                lab = markers_from_dist(dm[j], args.mk_thr, args.mk_min_area, args.mk_h)
                rels = {r: relief_map(c[j], dm[j], r) for r in RELIEFS}
                Lw = {r: hover_labels(lab, fg, rels[r]) for r in (RELIEFS if not quick else (args.relief,))}
                timing["post_s"] += time.time() - t0; timing["n"] += 1
                mq.append(marker_quality(lab, inst))
                res["logits"].append(label_metrics(ndimage.label(fg, structure=FOUR)[0], s[j], y[j], inst, strong)); res_types["logits"].append(tt)
                res["ws"].append(label_metrics(Lw[args.relief], None, y[j], inst, strong)); res_types["ws"].append(tt)
                if quick:
                    continue
                for r in RELIEFS:
                    res[f"ws_{r}"].append(label_metrics(Lw[r], None, y[j], inst, strong)); res_types[f"ws_{r}"].append(tt)
                lab_fb = add_fallback_markers(lab, s[j], args.fb_min_area)
                Lfb = hover_labels(lab_fb, fg, rels[args.relief])
                res["ws_fb"].append(label_metrics(Lfb, None, y[j], inst, strong)); res_types["ws_fb"].append(tt)
                Lg = hover_labels(gmk[j], fg, rels[args.relief])
                res["ws_gtmk"].append(label_metrics(Lg, None, y[j], inst, strong)); res_types["ws_gtmk"].append(tt)
                ref.append(label_metrics(inst.astype(np.int32), None, y[j], inst, strong))
                ex = None
                if g in example_idx:
                    ex = dict(idx=g, img=X[g], y=y[j], inst=inst, s=s[j], m=dm[j], c=c[j], lab=lab, L_ws=Lw[args.relief],
                              L_ws_contour=Lw["contour"], L_ws_dist=Lw["dist"], L_ws_fb=Lfb, L_gtmk=Lg)
                    if tt is not None:
                        ex["type"] = tt
                if lab_l is not None:
                    lmq.append(marker_quality(lab_l[j], inst))
                    Ll, cl = L_l[j]
                    res["layer"].append(label_metrics(Ll, cl, y[j], inst, strong)); res_types["layer"].append(tt)
                    Lx = hover_labels(lab_l[j], fg, rels[args.relief])
                    res["lmk_ws"].append(label_metrics(Lx, None, y[j], inst, strong)); res_types["lmk_ws"].append(tt)
                    Lo = hover_labels(lab_l[j], Ll > 0, relief_map(c_l[j], dm_l[j], args.relief))
                    res["lmk_ws_own"].append(label_metrics(Lo, None, y[j], inst, strong)); res_types["lmk_ws_own"].append(tt)
                    Lb, cb = L_bl[j]
                    res["bmk_layer"].append(label_metrics(Lb, cb, y[j], inst, strong)); res_types["bmk_layer"].append(tt)
                    if ex is not None:
                        ex.update(lab_layer=lab_l[j], L_layer=Ll, L_lmk_ws=Lx, L_lmk_ws_own=Lo, L_bmk_layer=Lb, m_layer=dm_l[j], c_layer=c_l[j])
                if ex is not None:
                    examples.append(ex)
            if (i // args.batch) % 20 == 0:
                print(f"    eval {i}/{len(X)}  post {1000 * timing['post_s'] / max(timing['n'], 1):.0f} ms/patch", flush=True)
    summary = {k: summarise(v, res_types[k] if types is not None else None) for k, v in res.items() if v}
    if ref:
        summary["gt_inst"] = summarise(ref, list(types) if types is not None else None)

    def mk_summary(q):
        agg = {k: int(sum(r[k] for r in q)) for k in q[0]}; ngt = max(agg["n_gt"], 1)
        return dict(agg, frac_one=agg["one"] / ngt, frac_zero=agg["zero"] / ngt, frac_multi=agg["multi"] / ngt,
                    bg_per_patch=agg["bg_mk"] / len(q), mk_per_patch=agg["n_mk"] / len(q), n_gt_per_patch=agg["n_gt"] / len(q))
    if mq:
        summary["markers"] = mk_summary(mq)
    if lmq:
        summary["lmarkers"] = mk_summary(lmq)
    summary["_timing"] = dict(timing, unet_s_per_image=timing["unet_s"] / max(timing["n"], 1), post_s_per_image=timing["post_s"] / max(timing["n"], 1),
                              solve_s_per_image=timing["solve_s"] / max(timing["solve_n"], 1))
    per_image = {k: v for k, v in res.items() if v}
    per_image["markers"] = mq
    if lmq:
        per_image["lmarkers"] = lmq
    return summary, examples, per_image


# ----------------------------------------------------------------------------
# training
# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--train-fold", type=int, default=1)
    ap.add_argument("--test-fold", type=int, default=2)
    ap.add_argument("--test-n", type=int, default=0)
    ap.add_argument("--train-n", type=int, default=0)
    ap.add_argument("--gap", action="store_true", help="foreground target = the gap mask (seams background), as section 10.1")
    ap.add_argument("--w-edge", type=float, default=1.0, help="edge target on the contour head")
    ap.add_argument("--edge-pos", type=float, default=10.0)
    ap.add_argument("--edge-seam", type=float, default=5.0)
    ap.add_argument("--w-mk", type=float, default=2.0, help="MSE on the distance head")
    ap.add_argument("--w-peak", type=float, default=0.0, help="per-nucleus peak loss on the distance head (exp_instance_pannuke.peak_loss; 0 = off)")
    ap.add_argument("--peak-pool", type=int, default=1, help="peak loss on the k x k mean-pooled maps (1 = raw maximum)")
    ap.add_argument("--w-neg", type=float, default=0.0, help="hard-negative loss on the distance head (exp_instance_pannuke.neg_loss; 0 = off)")
    ap.add_argument("--neg-k", type=int, default=256)
    ap.add_argument("--w-grad", type=float, default=0.0, help="gradient loss on the distance head (exp_instance_pannuke.grad_loss; 0 = off)")
    ap.add_argument("--mk-rmax", type=int, default=12)
    ap.add_argument("--mk-thr", type=float, default=0.2)
    ap.add_argument("--mk-min-area", type=int, default=16)
    ap.add_argument("--mk-h", type=float, default=0.2)
    ap.add_argument("--relief", choices=RELIEFS, default="contour")
    ap.add_argument("--tune-fold", type=int, default=0, help="choose thr / min area / h / relief by PQ on this fold (0 = off)")
    ap.add_argument("--tune-n", type=int, default=300)
    ap.add_argument("--tune-thr", type=float, nargs="+", default=(0.1, 0.2, 0.3, 0.4, 0.5))
    ap.add_argument("--tune-min-area", type=int, nargs="+", default=(4, 9, 16))
    ap.add_argument("--tune-h", type=float, nargs="+", default=(0.1, 0.2, 0.3))
    ap.add_argument("--fb-min-area", type=int, default=16)
    ap.add_argument("--layer-dir", default="", help="the section 11.1 distance-head layer run (instances.pt + instances.json) for the marker swap")
    ap.add_argument("--val-n", type=int, default=200)
    ap.add_argument("--val-every", type=int, default=5)
    ap.add_argument("--n-examples", type=int, default=8)
    ap.add_argument("--examples", choices=("touch", "diverse"), default="touch", help="how the example patches are chosen")
    ap.add_argument("--examples-only", action="store_true",
                    help="with --eval-only: run the saved model on the example patches only and write <name>_examples_<mode>.npz "
                         "(post-processing settings taken from the json next to the .pt)")
    ap.add_argument("--no-edge-align", dest="edge_align", action="store_false")
    ap.add_argument("--data", default="data")
    ap.add_argument("--outdir", default="results_pannuke_instances/unet_dist")
    ap.add_argument("--tag", default="")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--eval-only", action="store_true")
    ap.add_argument("--load", default="", help="eval only: the .pt to load (default <outdir>/<name>.pt)")
    ap.add_argument("--tb", action="store_true", help="write TensorBoard scalars to <outdir>/tb")
    args = ap.parse_args()
    args.dataset = "pannuke"
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    os.makedirs(args.outdir, exist_ok=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    d = load_dataset(args)
    tr = np.load(os.path.join(args.data, f"pannuke_fold{args.train_fold}.npz"))
    Xtr, Ytr, Itr = d["X_train"], d["Y_train"], tr["inst"]
    if args.train_n:
        Xtr, Ytr, Itr = Xtr[:args.train_n], Ytr[:args.train_n], Itr[:args.train_n]
    N_te = len(d["X_test"])
    name = "unet_dist" + (f"_{args.tag}" if args.tag else "")
    print(f"pannuke unet_dist{' / gap target' if args.gap else ''} / edge target x{args.w_edge} / distance head x{args.w_mk} (rmax {args.mk_rmax}, peak loss x{args.w_peak} pool {args.peak_pool}, neg x{args.w_neg} k {args.neg_k}, grad x{args.w_grad}) / "
          f"folds train {args.train_fold} test {args.test_fold} tune {args.tune_fold} / seed {args.seed}: "
          f"train {len(Xtr)} test {N_te} device {device}", flush=True)
    touch_px = d["touch_test"].reshape(N_te, -1).sum(1)
    example_idx = choose_examples(d, args.examples, args.n_examples) if args.n_examples else []

    model = DistSegmenter().to(device)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, args.epochs)
    val = dict(X_test=d["X_test"][:args.val_n], Y_test=d["Y_test"][:args.val_n], inst_test=d["inst_test"][:args.val_n])
    log = []
    if args.eval_only:
        pt = args.load or os.path.join(args.outdir, f"{name}.pt")
        model.load_state_dict(torch.load(pt, map_location=device))
        prev = pt[:-3] + ".json"
        log = json.load(open(prev))["log"] if os.path.exists(prev) else []
        print(f"  eval only: loaded {pt}", flush=True)
        if args.examples_only:
            prev = os.path.join(args.outdir, f"{name}.json") if os.path.exists(os.path.join(args.outdir, f"{name}.json")) else prev
            if os.path.exists(prev):
                for k, v in json.load(open(prev))["args"].items():
                    if k in ("mk_thr", "mk_min_area", "mk_h", "relief", "fb_min_area", "layer_dir"):
                        setattr(args, k, v)
            lay = load_layer(args.layer_dir, device) if args.layer_dir else None
            sub = examples_subset(d, example_idx)
            print(f"  examples only ({args.examples}): test patches {example_idx}, types {list(sub['types_test'])}, post-processing thr {args.mk_thr} / "
                  f"min area {args.mk_min_area} / h {args.mk_h} / relief {args.relief}", flush=True)
            _, examples, _ = evaluate(model, sub, device, args, lay=lay, example_idx=range(len(example_idx)))
            for e in examples:
                e["idx"] = example_idx[e["idx"]]
            np.savez_compressed(os.path.join(args.outdir, f"{name}_examples_{args.examples}.npz"),
                                **{f"{i}__{k}": np.asarray(v) for i, e in enumerate(examples) for k, v in e.items()})
            print("DONE", flush=True)
            return
    tb = tb_writer(args, name)
    for ep in range(0 if args.eval_only else args.epochs):
        model.train()
        perm = np.random.permutation(len(Xtr))
        t0 = time.time(); tot = np.zeros(7); nb = 0
        for i in range(0, len(perm), args.batch):
            idx = perm[i:i + args.batch]
            img = torch.from_numpy(Xtr[idx]).to(device).float() / 255
            y = torch.cat([torch.from_numpy(Ytr[idx]).to(device)[:, None],
                           torch.from_numpy(Itr[idx].astype(np.float32)).to(device)[:, None]], 1)
            img, y = augment(img, y, d["aug"])
            ybin, inst = y[:, :1], y[:, 1:2].long()
            out = model(img)
            l_fg = F.binary_cross_entropy_with_logits(out["logit"], ybin)
            l_edge = edge_loss(*pixel_edge_probs(out["eprob"]), inst.float(), args) if args.w_edge > 0 else torch.zeros((), device=device)
            dt = dist_target(inst, args.mk_rmax)
            l_mk = F.mse_loss(out["dm"], dt)
            l_peak = peak_loss(out["dm"], inst, dt, args.peak_pool) if args.w_peak > 0 else torch.zeros((), device=device)
            l_neg = neg_loss(out["dm"], inst, args.neg_k, args.peak_pool) if args.w_neg > 0 else torch.zeros((), device=device)
            l_grad = grad_loss(out["dm"], dt) if args.w_grad > 0 else torch.zeros((), device=device)
            loss = l_fg + args.w_edge * l_edge + args.w_mk * l_mk + args.w_peak * l_peak + args.w_neg * l_neg + args.w_grad * l_grad
            opt.zero_grad(); loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            opt.step()
            tot += np.array([loss.item(), l_fg.item(), l_edge.item(), l_mk.item(), l_peak.item(), l_neg.item(), l_grad.item()]); nb += 1
        sched.step()
        tot /= nb
        entry = dict(epoch=ep, loss=tot[0], loss_fg=tot[1], loss_edge=tot[2], loss_mk=tot[3], loss_peak=tot[4], loss_neg=tot[5], loss_grad=tot[6], time=time.time() - t0)
        msg = f"  ep {ep} loss={tot[0]:.4f} (fg {tot[1]:.4f} edge {tot[2]:.4f} mk {tot[3]:.4f} peak {tot[4]:.4f} neg {tot[5]:.4f} grad {tot[6]:.4f}) [{entry['time']:.0f}s]"
        if ep % args.val_every == args.val_every - 1 or ep == args.epochs - 1:
            summ, _, _ = evaluate(model, val, device, args, quick=True)
            entry["val"] = {k: {m: summ[k][m] for m in ("iou", "bf2", "f1_05", "pq", "count_err")} for k in ("logits", "ws")}
            entry["val"]["markers"] = {m: summ["markers"][m] for m in ("frac_one", "frac_zero", "frac_multi", "bg_per_patch")}
            msg += " | " + " ".join(f"{k}: iou={v['iou']:.3f} f1={v['f1_05']:.3f} pq={v['pq']:.3f}" for k, v in entry["val"].items() if k != "markers")
            msg += f" | markers one={summ['markers']['frac_one']:.2f} zero={summ['markers']['frac_zero']:.2f} multi={summ['markers']['frac_multi']:.2f}"
        print(msg, flush=True)
        log.append(entry)
        tb_log(tb, entry, ep)
    if tb is not None:
        tb.close()
    if not args.eval_only:
        torch.save(model.state_dict(), os.path.join(args.outdir, f"{name}.pt"))

    pp_tune = None
    if args.tune_fold:
        chosen, pp_tune = tune_postproc(model, args, device)
        for k, v in chosen.items():
            setattr(args, k, v)
    lay = load_layer(args.layer_dir, device) if args.layer_dir else None
    t0 = time.time()
    summ, examples, per_image = evaluate(model, d, device, args, lay=lay, example_idx=example_idx)
    summ["_eval_seconds"] = time.time() - t0
    print("TEST", json.dumps({k: ({m: v for m, v in s.items() if m != "per_type"} if isinstance(s, dict) else s)
                              for k, s in summ.items()}, indent=1, default=float), flush=True)
    with open(os.path.join(args.outdir, f"{name}.json"), "w") as f:
        json.dump(dict(args=vars(args), log=log, test=summ, pp_tune=pp_tune), f, indent=1, default=float)
    flat = {}
    for key in ("markers", "lmarkers"):
        q = per_image.pop(key, None)
        if q:
            for k in q[0]:
                flat[f"{key}__{k}"] = np.array([r[k] for r in q])
    flat.update(flatten_per_image(per_image, d.get("types_test")))
    np.savez_compressed(os.path.join(args.outdir, f"{name}_perimage.npz"), **flat)
    np.savez_compressed(os.path.join(args.outdir, f"{name}_examples.npz"),
                        **{f"{i}__{k}": np.asarray(v) for i, e in enumerate(examples) for k, v in e.items()})
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
