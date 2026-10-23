#!/usr/bin/env python3
"""
U-Net with the RW/PW layer as its last layer, trained end to end: dataset-agnostic
version of exp_unet_pets.py (whose model, layer and loss it reuses).

Datasets
  pets      Oxford-IIIT Pet, binary pet / background (see exp_unet_pets.py)
  pannuke   PanNuke, binary nucleus / background at native 256 px; train on one fold,
            test on another (data/pannuke_fold{k}.npz from convert_pannuke.py)

Variants: unet / rw_img / rw_learned, as in exp_unet_pets.py, plus
  unet_edge  the fair baseline for the edge-target layer (section 10.1): a plain U-Net with
             3 output channels like rw_learned but no RW layer; channel 0 is the
             segmentation logit, channels 1-2 a per-pixel contour head trained with the same
             edge target (--w-edge).  Evaluated as the thresholded logits and after two
             classical post-processings (postprocess_edge): the segmentation with the
             predicted contour (mean of the two directions > 0.5) removed, and a marker
             watershed on the contour map inside the segmentation, seeded by the maxima of
             the distance transform of the thresholded segmentation (pp_ws) or of the
             contour-removed segmentation (pp_wsc), with the watershed lines set to
             background like the seams of the gap target.  The marker spacing is chosen on
             a held-out fold (--pp-tune-fold, PQ), never on the test fold.

Losses (--loss), applied to the final output of every variant (and, weighted by --aux,
to the logits of the RW variants) so that the comparison between variants stays fair:
  bce       per-pixel BCE (the default, as in exp_unet_pets.py)
  boundary  BCE with the pixels within 3 px of the true boundary weighted x(1+--w-band),
            plus --w-bf times a differentiable boundary-F surrogate at --bf-tol px
            (soft morphological-gradient boundaries, precision / recall through
            max-pooled tolerance regions; Bokhovkin & Burnaev 2019)
  instance  PanNuke only: the target leaves the interfaces between touching nuclei
            (the 2-px seam the instance masks give) as background, and the seam plus
            a 1-px flank is weighted x(1+--w-int); BCE otherwise.  Rewards separating
            neighbouring nuclei, which the plain binary target does not.
  boundary_dice  the band-weighted BCE of `boundary` plus --w-dice times (1 - soft Dice
            restricted to the band): pays for filling the band correctly, with no
            boundary-map surrogate, so a dotted contour earns nothing.

Edge target (--w-edge > 0, rw_learned on PanNuke): the cost head is supervised directly.
Every grid edge whose two pixels carry different instance ids (nucleus / background
boundaries and the seams between touching nuclei) is a positive, weighted --edge-pos;
seam edges (both ids > 0) get --edge-seam times more; BCE on the edge probability
sigma(h) averaged onto the edge (the cost divided by its scale), weight --w-edge.

Target (--gap, PanNuke only): the binary nucleus mask with the touching-interface
pixels (the 2-px seam between touching nuclei, 'touch' in the npz) set to background,
used identically for training, validation and test by every variant.  Separating
touching nuclei is then rewarded; the instance metrics are unchanged (against the
instance masks) and the "ground truth" ceiling row becomes the gap mask itself.

Edge costs of rw_learned (--edge-param): sigmoid (in [0, 1], the default of
exp_unet_pets.py), scaled (edge-cmax * sigmoid, optionally with a learnable scale,
--edge-learn-scale) or exp (exp of the head output, clamped at edge-cmax), so that a
contour can be a large cost at a low p: the layer cuts rather than smooths.

Evaluation (test split): IoU, boundary F at 1 / 2 / 3 px, accuracy in a 3-px band
around the true boundary, fraction of soft pixels; when instance masks exist,
instance metrics on the 4-connected components of the thresholded output (count
error, F1 at IoU 0.5, PQ, AJI) with the ground-truth binary mask as the ceiling any
binary method can reach; and a label-free edge-alignment score (fraction of
predicted boundary pixels within 1 px of the top-10 % colour-gradient pixels).
Everything is also aggregated per tissue type.  RW variants are evaluated as the
K-step layer, the converged solve at the final p, and the exact PW limit on a
subset (which always includes the patches with the most touching nuclei).

usage: exp_unet_seg.py --dataset pannuke --variant rw_learned --epochs 30 --outdir results_pannuke
"""
import argparse, json, os, time
from multiprocessing import get_context
import numpy as np
import torch
import torch.nn.functional as F
from scipy import ndimage
from pw_layer import RWLayer, pw_limit_numpy, boundary_fscore, iou, softness
from exp_unet_pets import Segmenter, UNet, prepare as prepare_pets, to_target as pets_target
from pw_layer import unary_costs_from_prob
from seg_metrics import instance_metrics, aggregate_instance, edge_alignment, strong_edges, FOUR

PP_MODES = ("pp_contour", "pp_ws", "pp_wsc")                    # post-processed outputs of unet_edge


# ----------------------------------------------------------------------------
# data
# ----------------------------------------------------------------------------
def load_dataset(args):
    """Returns dict with X_train (N,3,H,W) uint8, Y_train (N,H,W) float32 in {0,1},
    X_test, Y_test, and optionally inst_test (int16), touch_test (bool), types_test (str)."""
    if args.dataset == "pets":
        d = prepare_pets(args.data, args.res, os.path.join(args.data, f"pets{args.res}.npz"))
        return dict(X_train=d["X_trainval"], Y_train=pets_target(d["Y_trainval"]),
                    X_test=d["X_test"], Y_test=pets_target(d["Y_test"]), aug="hflip")
    tr = np.load(os.path.join(args.data, f"pannuke_fold{args.train_fold}.npz"))
    te = np.load(os.path.join(args.data, f"pannuke_fold{args.test_fold}.npz"))
    out = dict(X_train=np.ascontiguousarray(tr["images"].transpose(0, 3, 1, 2)),
               Y_train=tr["binary"].astype(np.float32), touch_train=tr["touch"],
               X_test=np.ascontiguousarray(te["images"].transpose(0, 3, 1, 2)),
               Y_test=te["binary"].astype(np.float32),
               inst_test=te["inst"], touch_test=te["touch"], types_test=te["types"].astype(str), aug="d4")
    if getattr(args, "gap", False):                               # the seam between touching nuclei is background
        out["Y_train"] = out["Y_train"] * (1 - tr["touch"].astype(np.float32))
        out["Y_test"] = out["Y_test"] * (1 - te["touch"].astype(np.float32))
    if args.test_n and args.test_n < len(out["X_test"]):
        sel = np.linspace(0, len(out["X_test"]) - 1, args.test_n).astype(int)
        for k in ("X_test", "Y_test", "inst_test", "touch_test", "types_test"):
            out[k] = out[k][sel]
    return out


def augment(img, y, aug):
    """img (B,3,H,W), y (B,C,H,W): the same flips / rotations applied to both (y may
    carry the touching-interface mask as a second channel)."""
    if aug == "hflip":
        if np.random.rand() < 0.5:
            img, y = img.flip(3), y.flip(3)
        return img, y
    if np.random.rand() < 0.5:
        img, y = img.flip(3), y.flip(3)
    if np.random.rand() < 0.5:
        img, y = img.flip(2), y.flip(2)
    k = np.random.randint(4)
    return img.rot90(k, (2, 3)), y.rot90(k, (2, 3))


# ----------------------------------------------------------------------------
# model: Segmenter of exp_unet_pets.py with a choice of edge-cost parametrisation
# ----------------------------------------------------------------------------
class SegmenterX(Segmenter):
    """edge_param: sigmoid  -> e = sigmoid(h) in [0, 1]           (exp_unet_pets.py)
                   scaled   -> e = scale * sigmoid(h), scale = edge_cmax (or learnable, init edge_cmax)
                   exp      -> e = min(exp(h), edge_cmax)
    The edge cost of a grid edge is the mean of e at its two pixels, as before."""

    def __init__(self, variant, K, cmax, edge_param="sigmoid", edge_cmax=8.0, learn_scale=False):
        super().__init__(variant, K, cmax)
        if variant == "unet_edge":                                # segmentation logit + 2-channel contour head
            self.unet = UNet(3)
        self.edge_param, self.edge_cmax = edge_param, edge_cmax
        self.log_scale = torch.nn.Parameter(torch.tensor(float(np.log(edge_cmax)))) if learn_scale else None

    def forward(self, img, p, layer=None):
        """unet_edge: (logit, None, e) with e = sigmoid of the contour head, (B,2,H,W) per-pixel
        edge probabilities (horizontal, vertical); the other variants as Segmenter."""
        if self.variant != "unet_edge":
            return super().forward(img, p, layer)
        out = self.unet(img)
        return out[:, :1], None, torch.sigmoid(out[:, 1:3])

    def edge_scale(self):
        return float(self.log_scale.exp()) if self.log_scale is not None else self.edge_cmax

    def edge_prob(self, ch, cv):
        """Edge costs -> edge probabilities in [0, 1] (sigmoid: the cost itself; scaled: cost / scale)."""
        if self.edge_param == "sigmoid":
            return ch, cv
        if self.edge_param == "scaled":
            scale = self.log_scale.exp() if self.log_scale is not None else self.edge_cmax
            return ch / scale, cv / scale
        raise ValueError("edge target needs the sigmoid or scaled edge parametrisation")

    def costs(self, img, out):
        if self.variant != "rw_learned" or self.edge_param == "sigmoid":
            return super().costs(img, out)
        logit = out[:, :1]
        c1, c0 = unary_costs_from_prob(torch.sigmoid(logit), cmax=self.cmax)
        h = out[:, 1:3]
        if self.edge_param == "scaled":
            scale = self.log_scale.exp() if self.log_scale is not None else self.edge_cmax
            e = scale * torch.sigmoid(h)
        elif self.edge_param == "exp":
            e = torch.exp(h.clamp_max(np.log(self.edge_cmax) + 2.0)).clamp_max(self.edge_cmax)
        else:
            raise ValueError(self.edge_param)
        ch = 0.5 * (e[:, :1, :, 1:] + e[:, :1, :, :-1])
        cv = 0.5 * (e[:, 1:2, 1:, :] + e[:, 1:2, :-1, :])
        return logit, ch, cv, c1, c0


# ----------------------------------------------------------------------------
# losses
# ----------------------------------------------------------------------------
def maxpool(x, r):
    return F.max_pool2d(x, 2 * r + 1, stride=1, padding=r) if r > 0 else x


def minpool(x, r):
    return -maxpool(-x, r)


def pixel_bce(out, y, from_logits, eps=1e-6):
    """Per-pixel BCE, (B,1,H,W)."""
    if from_logits:
        return F.binary_cross_entropy_with_logits(out, y, reduction="none")
    x = out.clamp(eps, 1 - eps)
    return -(y * torch.log(x) + (1 - y) * torch.log(1 - x))


def soft_boundary_f(x, y, tol=2, eps=1e-6):
    """1 - differentiable boundary F-score (Bokhovkin & Burnaev 2019).  Boundaries are
    the soft inner morphological gradient x - minpool(x) (1 px); a predicted boundary
    pixel counts as correct when within tol px of a true one and vice versa."""
    bp = x - minpool(x, 1)
    bg = y - minpool(y, 1)
    prec = (bp * maxpool(bg, tol)).sum((1, 2, 3)) / (bp.sum((1, 2, 3)) + eps)
    rec = (bg * maxpool(bp, tol)).sum((1, 2, 3)) / (bg.sum((1, 2, 3)) + eps)
    f = 2 * prec * rec / (prec + rec + eps)
    return (1 - f).mean()


def seg_loss(out, y, touch, args, from_logits):
    """out: logits (from_logits) or probabilities; y: target (B,1,H,W) in {0,1};
    touch: touching-interface mask (B,1,H,W) in {0,1} or None."""
    if args.loss == "bce":
        return pixel_bce(out, y, from_logits).mean()
    if args.loss == "boundary":
        band = (maxpool(y, args.band_px) - minpool(y, args.band_px))   # within band_px of the true boundary
        w = 1 + args.w_band * band
        loss = (w * pixel_bce(out, y, from_logits)).mean()
        if args.w_bf > 0:
            x = torch.sigmoid(out) if from_logits else out.clamp(0, 1)
            loss = loss + args.w_bf * soft_boundary_f(x, y, args.bf_tol)
        return loss
    if args.loss == "boundary_dice":
        band = (maxpool(y, args.band_px) - minpool(y, args.band_px))
        w = 1 + args.w_band * band
        loss = (w * pixel_bce(out, y, from_logits)).mean()
        x = torch.sigmoid(out) if from_logits else out.clamp(0, 1)
        inter = (band * x * y).sum((1, 2, 3))
        dice = 2 * inter / ((band * x).sum((1, 2, 3)) + (band * y).sum((1, 2, 3)) + 1e-6)
        return loss + args.w_dice * (1 - dice).mean()
    if args.loss == "instance":
        if touch is None:
            raise ValueError("--loss instance needs the touching-interface masks (PanNuke)")
        y_sep = y * (1 - touch)                                           # the seam is background
        w = 1 + args.w_int * maxpool(touch, 1)                            # seam + 1-px flank
        return (w * pixel_bce(out, y_sep, from_logits)).mean()
    raise ValueError(args.loss)


def pixel_edge_probs(e):
    """Per-pixel edge probabilities (B,2,H,W) -> probabilities on the grid edges, (B,1,H,W-1)
    and (B,1,H-1,W), the mean of the two pixels of each edge (as the cost head of rw_learned)."""
    ph = 0.5 * (e[:, :1, :, 1:] + e[:, :1, :, :-1])
    pv = 0.5 * (e[:, 1:2, 1:, :] + e[:, 1:2, :-1, :])
    return ph, pv


def edge_targets(inst):
    """inst (B,1,H,W) float instance ids (0 = background) -> (t_h, seam_h, t_v, seam_v):
    1 where the two pixels of a grid edge differ, and where both are nuclei."""
    a, b = inst[:, :, :, 1:], inst[:, :, :, :-1]
    t_h = (a != b).float(); seam_h = t_h * ((a > 0) & (b > 0)).float()
    a, b = inst[:, :, 1:, :], inst[:, :, :-1, :]
    t_v = (a != b).float(); seam_v = t_v * ((a > 0) & (b > 0)).float()
    return t_h, seam_h, t_v, seam_v


def edge_loss(ph, pv, inst, args):
    """Weighted BCE of the edge probabilities (B,1,H,W-1), (B,1,H-1,W) in [0,1] against
    the instance-id edge targets."""
    t_h, s_h, t_v, s_v = edge_targets(inst)
    tot, n = 0.0, 0
    for pe, t, sm in ((ph, t_h, s_h), (pv, t_v, s_v)):
        w = 1 + (args.edge_pos - 1) * t + args.edge_pos * (args.edge_seam - 1) * sm
        tot = tot + (w * pixel_bce(pe, t, from_logits=False)).sum(); n += t.numel()
    return tot / n


# ----------------------------------------------------------------------------
# classical post-processing of the unet_edge outputs
# ----------------------------------------------------------------------------
def seam_pixels(lab):
    """Pixels of a label map with a 4-neighbour of a different non-zero label (both sides,
    2 px wide: the definition of the touching-interface mask of convert_pannuke.py)."""
    seam = np.zeros(lab.shape, bool)
    d = (lab[:, 1:] != lab[:, :-1]) & (lab[:, 1:] > 0) & (lab[:, :-1] > 0)
    seam[:, 1:] |= d; seam[:, :-1] |= d
    d = (lab[1:, :] != lab[:-1, :]) & (lab[1:, :] > 0) & (lab[:-1, :] > 0)
    seam[1:, :] |= d; seam[:-1, :] |= d
    return seam


def marker_watershed(seg, mk_mask, c, min_distance):
    """Marker-based watershed of the contour map c inside the mask seg; one marker per
    maximum of the distance transform of mk_mask (maxima at least min_distance apart,
    per connected component).  Returns the label map (0 outside seg)."""
    from skimage.segmentation import watershed
    from skimage.feature import peak_local_max
    if not mk_mask.any():
        return np.zeros(seg.shape, np.int32)
    comp, n = ndimage.label(mk_mask, structure=FOUR)
    dist = ndimage.distance_transform_edt(mk_mask)
    peaks = peak_local_max(dist, min_distance=min_distance, labels=comp, exclude_border=False)
    markers = np.zeros(seg.shape, np.int32)
    markers[tuple(peaks.T)] = np.arange(1, len(peaks) + 1)
    return watershed(c, markers, mask=seg, connectivity=1)


def postprocess_edge(s, c, md_ws=5, md_wsc=5, thr=0.5):
    """s: sigmoid of the segmentation logit (H,W); c: contour probability (H,W), the mean
    of the two directions of the contour head.  Returns bool masks:
      pp_contour  the thresholded segmentation with the predicted contour (c > thr) removed;
      pp_ws       marker watershed on c inside the segmentation, seeded by the distance-transform
                  maxima of the segmentation, with the watershed lines (seam_pixels) removed;
      pp_wsc      the same, seeded by the distance-transform maxima of pp_contour (the contour
                  already separates what it crosses; the watershed closes the rest)."""
    seg = s > 0.5
    out = {"pp_contour": seg & ~(c > thr)}
    for name, mk, md in (("pp_ws", seg, md_ws), ("pp_wsc", out["pp_contour"], md_wsc)):
        lab = marker_watershed(seg, mk, c, md)
        out[name] = seg & ~seam_pixels(lab)
    return out


def contour_map(e):
    """Contour head output (B,2,H,W) -> per-pixel contour probability (B,H,W), numpy."""
    return e.mean(1).cpu().numpy()


def tune_postproc(model, args, device, mds=(2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25)):
    """Choose the marker spacing of pp_ws and pp_wsc by PQ on --pp-tune-n evenly spaced patches
    of fold --pp-tune-fold (neither the training nor the test fold).  Returns
    (dict(md_ws, md_wsc), table of PQ / F1 / count error per spacing)."""
    f = np.load(os.path.join(args.data, f"pannuke_fold{args.pp_tune_fold}.npz"))
    n = len(f["types"])
    sel = np.linspace(0, n - 1, min(args.pp_tune_n, n)).astype(int)
    X = np.ascontiguousarray(f["images"][sel].transpose(0, 3, 1, 2)); inst_all = f["inst"][sel]
    rows = {(name, md): [] for name in ("pp_ws", "pp_wsc") for md in mds}
    model.eval()
    with torch.no_grad():
        for i in range(0, len(X), args.batch):
            img = torch.from_numpy(X[i:i + args.batch]).to(device).float() / 255
            logit, _, e = model(img, args.p1)
            s = torch.sigmoid(logit).cpu().numpy()[:, 0]; c = contour_map(e)
            for j in range(len(s)):
                for md in mds:
                    pp = postprocess_edge(s[j], c[j], md_ws=md, md_wsc=md)
                    for name in ("pp_ws", "pp_wsc"):
                        rows[(name, md)].append(instance_metrics(pp[name], inst_all[i + j]))
    table = {f"{name}/md={md}": {k: aggregate_instance(rs)[k] for k in ("pq", "f1_05", "count_err", "n_pred_mean")}
             for (name, md), rs in rows.items()}
    best = {}
    for name in ("pp_ws", "pp_wsc"):
        best[name] = max(mds, key=lambda md: table[f"{name}/md={md}"]["pq"])
    for k, v in table.items():
        print(f"  tune {k:14s} PQ {v['pq']:.3f}  F1 {v['f1_05']:.3f}  count err {v['count_err']:.3f}  n_pred {v['n_pred_mean']:.1f}", flush=True)
    print(f"  chosen marker spacing: pp_ws {best['pp_ws']}  pp_wsc {best['pp_wsc']}  (fold {args.pp_tune_fold}, {len(sel)} patches)", flush=True)
    return dict(md_ws=int(best["pp_ws"]), md_wsc=int(best["pp_wsc"])), table


# ----------------------------------------------------------------------------
# evaluation
# ----------------------------------------------------------------------------
def pixel_metrics(prob, y, band_px=3):
    pred = prob > 0.5; gt = y > 0.5
    contour = gt ^ ndimage.binary_erosion(gt, border_value=0)
    band = ndimage.binary_dilation(contour, iterations=band_px)
    frac, ent = softness(prob)
    return dict(iou=float(iou(pred, gt)), bf1=float(boundary_fscore(pred, gt, 1)),
                bf2=float(boundary_fscore(pred, gt, 2)), bf3=float(boundary_fscore(pred, gt, 3)),
                band_acc=float((pred[band] == gt[band]).mean()) if band.any() else 1.0,
                soft_frac=frac, entropy=ent)


def full_metrics(prob, y, inst=None, strong=None):
    m = pixel_metrics(prob, y)
    pred = prob > 0.5
    if strong is not None:
        m["edge_align"] = edge_alignment(pred, strong=strong)
    if inst is not None:
        m["inst"] = instance_metrics(pred, inst)
    return m


def summarise(rows, types=None, min_type_n=50):
    """rows: list of per-image metric dicts (with optional 'inst').  Mean of the pixel
    metrics, dataset-level instance aggregates; the same per tissue type."""
    def agg(rs):
        s = {k: float(np.nanmean([r[k] for r in rs])) for k in rs[0] if k != "inst"}
        if "inst" in rs[0]:
            s.update(aggregate_instance([r["inst"] for r in rs]))
        s["n"] = len(rs)
        return s
    out = agg(rows)
    if types is not None:
        out["per_type"] = {}
        for t in sorted(set(types)):
            sel = [r for r, tt in zip(rows, types) if tt == t]
            if len(sel) >= min_type_n:
                out["per_type"][t] = agg(sel)
    return out


def _limit_worker(job):
    g, ch, cv, c1, c0 = job
    xinf, _ = pw_limit_numpy(ch, cv, c1, c0)
    return g, xinf


def evaluate(model, d, p, device, args, limit_idx=(), n_examples=0, example_idx=()):
    model.eval()
    X, Y = d["X_test"], d["Y_test"]
    inst_all, touch_all, types = d.get("inst_test"), d.get("touch_test"), d.get("types_test")
    limit_idx, example_idx = set(limit_idx), set(example_idx)
    res = {"logits": [], "layer": [], "converged": [], "limit": []}
    res.update({k: [] for k in PP_MODES})
    res_types = {k: [] for k in res}
    pp_md = getattr(args, "pp_md", None) if getattr(args, "postproc", True) else None   # unet_edge post-processing
    ref = []                                                   # ground-truth binary mask as a "method"
    if getattr(args, "layer", "unrolled") == "reweighted":       # "converged" = the full fixed point
        conv_layer = RWLayer("reweighted", tol=1e-5, maxit=args.inner_maxit_eval, outer=args.outer_eval,
                             eps=args.eps, kind=args.kind)
    else:
        conv_layer = RWLayer("implicit", tol=1e-5, maxit=1000)
    examples = []
    t_limit = 0.0
    limit_jobs, limit_ctx, limit_order = [], {}, []
    with torch.no_grad():
        for i in range(0, len(X), args.batch):
            img = torch.from_numpy(X[i:i + args.batch]).to(device).float() / 255
            y = Y[i:i + args.batch]
            logit, x, costs = model(img, p)
            s = torch.sigmoid(logit).cpu().numpy()[:, 0]
            xk = x.cpu().numpy()[:, 0] if x is not None else None
            xc = conv_layer(*costs, float(p)).cpu().numpy()[:, 0] if x is not None else None
            cmap = contour_map(costs) if model.variant == "unet_edge" else None
            for j in range(len(y)):
                g = i + j
                inst = inst_all[g] if inst_all is not None else None
                strong = strong_edges(X[g].transpose(1, 2, 0)) if args.edge_align else None
                tt = types[g] if types is not None else None
                res["logits"].append(full_metrics(s[j], y[j], inst, strong)); res_types["logits"].append(tt)
                if inst is not None:
                    ref.append(full_metrics(y[j], y[j], inst, strong))
                pp = postprocess_edge(s[j], cmap[j], **pp_md) if cmap is not None and pp_md is not None else {}
                for k, m in pp.items():
                    res[k].append(full_metrics(m.astype(np.float32), y[j], inst, strong)); res_types[k].append(tt)
                if xk is not None:
                    res["layer"].append(full_metrics(xk[j], y[j], inst, strong)); res_types["layer"].append(tt)
                    res["converged"].append(full_metrics(xc[j], y[j], inst, strong)); res_types["converged"].append(tt)
                if xk is not None and g in limit_idx:
                    limit_jobs.append((g,) + tuple(c[j, 0].double().cpu().numpy() for c in costs))
                    limit_ctx[g] = (y[j], inst, strong, tt)
                if g in example_idx or len(examples) < n_examples and not example_idx:
                    ex = dict(idx=g, img=X[g], y=y[j], s=s[j])
                    if inst is not None:
                        ex["inst"] = inst
                    if tt is not None:
                        ex["type"] = tt
                    if xk is not None:
                        ex.update(xk=xk[j], xc=xc[j], ch=costs[0][j, 0].cpu().numpy(), cv=costs[1][j, 0].cpu().numpy())
                    if cmap is not None:
                        ex["c"] = cmap[j]
                        ex.update({k: m.astype(np.float32) for k, m in pp.items()})
                    examples.append(ex)
            if (i // args.batch) % 20 == 0:
                print(f"    eval {i}/{len(X)}", flush=True)
    # exact PW limit on the selected patches, in a process pool (CPU, ~2 s per 256^2 patch)
    if limit_jobs:
        t0 = time.time()
        workers = max(1, getattr(args, "limit_workers", 4))
        with get_context("fork").Pool(workers) as pool:
            for g, xinf in pool.imap_unordered(_limit_worker, limit_jobs, chunksize=2):
                yy, inst, strong, tt = limit_ctx[g]
                res["limit"].append(full_metrics(xinf, yy, inst, strong)); res_types["limit"].append(tt); limit_order.append(g)
                for ex in examples:
                    if ex["idx"] == g:
                        ex["xinf"] = xinf
                if len(res["limit"]) % 50 == 0:
                    print(f"    limit {len(res['limit'])}/{len(limit_jobs)}  {time.time() - t0:.0f}s", flush=True)
        t_limit = time.time() - t0
    summary = {k: summarise(v, res_types[k] if types is not None else None) for k, v in res.items() if v}
    if ref:
        summary["gt_binary"] = summarise(ref, list(types) if types is not None else None)
    summary["_limit_seconds"] = t_limit
    per_image = {k: v for k, v in res.items() if v}
    if limit_order:
        per_image["limit_idx"] = limit_order                   # test indices of the limit rows, in their stored order
    return summary, examples, per_image


def flatten_per_image(per_image, types):
    """Per-image metrics as flat float arrays for the npz."""
    out = {}
    for mode, rows in per_image.items():
        if mode == "limit_idx":
            out["limit__idx"] = np.array(rows); continue
        for k in rows[0]:
            if k == "inst":
                for kk in rows[0]["inst"]:
                    out[f"{mode}__inst_{kk}"] = np.array([r["inst"][kk] for r in rows])
            else:
                out[f"{mode}__{k}"] = np.array([r[k] for r in rows])
    if types is not None:
        out["types"] = np.asarray(types)
    return out


# ----------------------------------------------------------------------------
# training
# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", choices=("pets", "pannuke"), default="pannuke")
    ap.add_argument("--variant", choices=("unet", "rw_img", "rw_learned", "unet_edge"), required=True)
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--res", type=int, default=256, help="pets only")
    ap.add_argument("--train-fold", type=int, default=1)
    ap.add_argument("--test-fold", type=int, default=2)
    ap.add_argument("--test-n", type=int, default=0, help="evenly spaced test subset (0 = all)")
    ap.add_argument("--train-n", type=int, default=0, help="training subset (0 = all), for smoke tests")
    ap.add_argument("--K", type=int, default=20)
    ap.add_argument("--p0", type=float, default=5.0)
    ap.add_argument("--p1", type=float, default=50.0)
    ap.add_argument("--cmax", type=float, default=8.0)
    ap.add_argument("--gap", action="store_true",
                    help="PanNuke: target = binary mask with the touching-interface pixels set to background "
                         "(training, validation and test, every variant)")
    ap.add_argument("--edge-param", choices=("sigmoid", "scaled", "exp"), default="sigmoid",
                    help="rw_learned edge costs: sigmoid in [0,1]; edge-cmax * sigmoid; exp clamped at edge-cmax")
    ap.add_argument("--edge-cmax", type=float, default=8.0)
    ap.add_argument("--edge-learn-scale", action="store_true", help="scaled: learn the scale (init edge-cmax)")
    ap.add_argument("--tag", default="", help="suffix of the output file names ({variant}_{tag}.json ...)")
    ap.add_argument("--layer", choices=("unrolled", "reweighted"), default="unrolled",
                    help="unrolled: K Jacobi-PCG steps at exp(-p c); reweighted: implicit solve at exp(-p c) "
                         "then outer-train half-quadratic reweighting steps (eval uses outer-eval steps)")
    ap.add_argument("--eps", type=float, default=0.1, help="reweighted: epsilon of the Cauchy / l1 weight")
    ap.add_argument("--kind", choices=("cauchy", "l1"), default="cauchy")
    ap.add_argument("--outer-train", type=int, default=2)
    ap.add_argument("--outer-eval", type=int, default=5)
    ap.add_argument("--inner-tol", type=float, default=1e-4)
    ap.add_argument("--inner-maxit", type=int, default=150)
    ap.add_argument("--inner-maxit-eval", type=int, default=500)
    ap.add_argument("--aux", type=float, default=0.5, help="weight of the loss on the logits for RW variants")
    ap.add_argument("--loss", choices=("bce", "boundary", "instance", "boundary_dice"), default="bce")
    ap.add_argument("--w-dice", type=float, default=1.0, help="boundary_dice: weight of the band Dice term")
    ap.add_argument("--w-edge", type=float, default=0.0, help="rw_learned / unet_edge: weight of the edge target on the cost / contour head")
    ap.add_argument("--pp-min-distance", type=int, default=0,
                    help="unet_edge: marker spacing of the watershed post-processing (0 = choose by PQ on --pp-tune-fold)")
    ap.add_argument("--pp-tune-fold", type=int, default=3)
    ap.add_argument("--pp-tune-n", type=int, default=300)
    ap.add_argument("--edge-pos", type=float, default=10.0, help="edge target: weight of the positive (boundary) edges")
    ap.add_argument("--edge-seam", type=float, default=5.0, help="edge target: extra factor on seam edges")
    ap.add_argument("--band-px", type=int, default=3, help="boundary loss: half-width of the boundary band")
    ap.add_argument("--w-band", type=float, default=4.0, help="boundary loss: extra weight of band pixels")
    ap.add_argument("--w-bf", type=float, default=1.0, help="boundary loss: weight of the soft boundary-F term")
    ap.add_argument("--bf-tol", type=int, default=2, help="boundary loss: tolerance (px) of the soft boundary F")
    ap.add_argument("--w-int", type=float, default=20.0, help="instance loss: extra weight of the interface pixels")
    ap.add_argument("--limit-n", type=int, default=300, help="test images on which the exact PW limit is evaluated")
    ap.add_argument("--limit-workers", type=int, default=4)
    ap.add_argument("--val-n", type=int, default=400)
    ap.add_argument("--val-every", type=int, default=5)
    ap.add_argument("--n-examples", type=int, default=8)
    ap.add_argument("--no-edge-align", dest="edge_align", action="store_false")
    ap.add_argument("--data", default="data")
    ap.add_argument("--outdir", default="results_pannuke")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--eval-only", action="store_true",
                    help="skip training: load {outdir}/{name}.pt (and the training log of its json), then evaluate")
    args = ap.parse_args()
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    os.makedirs(args.outdir, exist_ok=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    d = load_dataset(args)
    Xtr, Ytr = d["X_train"], d["Y_train"]
    Ttr = d.get("touch_train") if args.loss == "instance" else None
    Itr = None
    if args.w_edge > 0:
        if args.variant not in ("rw_learned", "unet_edge") or args.dataset != "pannuke":
            raise ValueError("--w-edge needs rw_learned or unet_edge on PanNuke")
        Itr = np.load(os.path.join(args.data, f"pannuke_fold{args.train_fold}.npz"))["inst"]
    if args.train_n:
        Xtr, Ytr = Xtr[:args.train_n], Ytr[:args.train_n]
        Ttr = Ttr[:args.train_n] if Ttr is not None else None
        Itr = Itr[:args.train_n] if Itr is not None else None
    N_te = len(d["X_test"])
    print(f"{args.dataset} / {args.variant} / loss {args.loss}{' / gap target' if args.gap else ''} / p {args.p0} -> {args.p1}"
          f" / edges {args.edge_param}{f' / edge target x{args.w_edge}' if args.w_edge > 0 else ''}: "
          f"train {len(Xtr)} test {N_te} device {device}", flush=True)

    # exact-limit subset: evenly spaced, plus the patches with the most touching-nuclei pixels
    limit_idx = list(np.linspace(0, N_te - 1, min(args.limit_n, N_te)).astype(int)) if args.limit_n else []
    example_idx = []
    if "touch_test" in d and args.n_examples:
        touch_px = d["touch_test"].reshape(N_te, -1).sum(1)
        example_idx = list(np.argsort(-touch_px)[:args.n_examples])
        limit_idx = sorted(set(limit_idx) | set(example_idx))
    elif args.n_examples:
        example_idx = limit_idx[:args.n_examples] if limit_idx else list(range(args.n_examples))

    model = SegmenterX(args.variant, args.K, args.cmax, args.edge_param, args.edge_cmax, args.edge_learn_scale).to(device)
    name = args.variant + (f"_{args.tag}" if args.tag else "")
    if args.layer == "reweighted":
        model.layer = RWLayer("reweighted", tol=args.inner_tol, maxit=args.inner_maxit, outer=args.outer_train,
                              eps=args.eps, kind=args.kind)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, args.epochs)
    val = {k: d[k][:args.val_n] for k in ("X_test", "Y_test")}
    log = []
    if args.eval_only:
        model.load_state_dict(torch.load(os.path.join(args.outdir, f"{name}.pt"), map_location=device))
        prev = os.path.join(args.outdir, f"{name}.json")
        log = json.load(open(prev))["log"] if os.path.exists(prev) else []
        print(f"  eval only: loaded {name}.pt", flush=True)
    for ep in range(0 if args.eval_only else args.epochs):
        model.train()
        p = args.p0 * (args.p1 / args.p0) ** (ep / max(args.epochs - 1, 1))
        perm = np.random.permutation(len(Xtr))
        t0 = time.time(); tot = 0.0; nb = 0
        for i in range(0, len(perm), args.batch):
            idx = perm[i:i + args.batch]
            img = torch.from_numpy(Xtr[idx]).to(device).float() / 255
            y = torch.from_numpy(Ytr[idx]).to(device)[:, None]
            extra = [torch.from_numpy(Ttr[idx]).to(device)[:, None].float()] if Ttr is not None else []
            if Itr is not None:
                extra.append(torch.from_numpy(Itr[idx].astype(np.float32)).to(device)[:, None])
            y = torch.cat([y] + extra, 1)
            img, y = augment(img, y, d["aug"])
            touch = y[:, 1:2] if Ttr is not None else None
            inst = y[:, -1:] if Itr is not None else None
            y = y[:, :1]
            logit, x, costs = model(img, p)
            if x is None:
                loss = seg_loss(logit, y, touch, args, from_logits=True)
                if inst is not None and costs is not None:         # unet_edge: the same edge target on the contour head
                    loss = loss + args.w_edge * edge_loss(*pixel_edge_probs(costs), inst, args)
            else:
                loss = seg_loss(x, y, touch, args, from_logits=False) + args.aux * seg_loss(logit, y, touch, args, from_logits=True)
                if inst is not None:
                    loss = loss + args.w_edge * edge_loss(*model.edge_prob(costs[0], costs[1]), inst, args)
            opt.zero_grad(); loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            opt.step()
            tot += loss.item(); nb += 1
        sched.step()
        entry = dict(epoch=ep, p=p, loss=tot / nb, time=time.time() - t0)
        if model.log_scale is not None:
            entry["edge_scale"] = model.edge_scale()
        if ep % args.val_every == args.val_every - 1 or ep == args.epochs - 1:
            summ, _, _ = evaluate(model, dict(val, aug=d["aug"]), p, device,
                                  argparse.Namespace(batch=args.batch, edge_align=False, postproc=False))
            entry["val"] = {k: {m: v[m] for m in ("iou", "bf2", "soft_frac")} for k, v in summ.items() if not k.startswith("_")}
            print(f"  ep {ep} p={p:.1f} loss={tot / nb:.4f} [{entry['time']:.0f}s] " +
                  " ".join(f"{k}: iou={v['iou']:.3f} bf2={v['bf2']:.3f} soft={v['soft_frac']:.3f}"
                           for k, v in entry["val"].items()), flush=True)
        else:
            print(f"  ep {ep} p={p:.1f} loss={tot / nb:.4f} [{entry['time']:.0f}s]", flush=True)
        log.append(entry)
    if not args.eval_only:
        torch.save(model.state_dict(), os.path.join(args.outdir, f"{name}.pt"))

    pp_tune = None
    if args.variant == "unet_edge":                              # marker spacing of the watershed, on a held-out fold
        if args.pp_min_distance > 0:
            args.pp_md = dict(md_ws=args.pp_min_distance, md_wsc=args.pp_min_distance)
        else:
            args.pp_md, pp_tune = tune_postproc(model, args, device)

    t0 = time.time()
    summ, examples, per_image = evaluate(model, d, args.p1, device, args, limit_idx=limit_idx,
                                         n_examples=args.n_examples, example_idx=example_idx)
    summ["_eval_seconds"] = time.time() - t0
    if model.log_scale is not None:
        summ["_edge_scale"] = model.edge_scale()
    print("TEST", json.dumps({k: {m: v for m, v in s.items() if m != "per_type"} if isinstance(s, dict) else s
                              for k, s in summ.items()}, indent=1), flush=True)
    with open(os.path.join(args.outdir, f"{name}.json"), "w") as f:
        json.dump(dict(args=vars(args), log=log, test=summ, limit_idx=[int(i) for i in limit_idx], pp_tune=pp_tune), f, indent=1)
    np.savez_compressed(os.path.join(args.outdir, f"{name}_perimage.npz"),
                        **flatten_per_image(per_image, d.get("types_test")))
    np.savez_compressed(os.path.join(args.outdir, f"{name}_examples.npz"),
                        **{f"{i}__{k}": np.asarray(v) for i, e in enumerate(examples) for k, v in e.items()})
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
