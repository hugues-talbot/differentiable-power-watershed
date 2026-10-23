#!/usr/bin/env python3
"""
The instances are the labels: a multi-marker Random Walker / Power Watershed layer for
nucleus instance segmentation on PanNuke (section 11).

Model: the U-Net of exp_unet_seg.py with four output channels: channel 0 the foreground
logit (its sigmoid s gives the background attachment c0 = -log(1-s) and the marker
attachment c1 = -log s), channels 1-2 the edge-cost head (scale * sigmoid, learnable
scale, section 6.1's parametrisation, supervised with section 10's edge target), channel
3 the marker head: --mk-head bce (section 11) a marker-map logit trained with BCE against
the eroded ground-truth instances; --mk-head dist (section 11.1, HoVer-Net-style) the
normalised distance transform of every instance (Chebyshev distance to the instance
boundary, capped at --mk-rmax, divided by the instance's maximum, so every nucleus has 1 at
its centre and 0 at its border), sigmoid output trained with --mk-loss mse|bce; --w-peak adds
a per-nucleus detection term (section 11.3): the maximum of the predicted map over every
ground-truth instance should reach the target's, loss = mean over instances of
(max target - max prediction)_+^2, so a small or faint nucleus weighs as much as a large one (under
the pixel MSE it hardly weighs at all).  With --peak-pool 1 (the raw maximum) the gradient goes to a
single pixel per nucleus and the map grows needle peaks (hundreds of regional maxima per patch);
--peak-pool k takes both maxima on the k x k mean-pooled maps, so a nucleus must carry a plateau.
Section 11.4 adds the counterweights the peak loss lacked: --w-neg, hard negatives (the mean of
the --neg-k largest values of the pooled prediction over the background pixels of every image,
squared: spurious maxima in background cost directly), and --w-grad, HoVer-Net's gradient term
(MSE of the finite differences of prediction and target over all pixels: a nucleus should carry
one smooth peak, the background none).
Section 11.5 (--mk-sched E0 E1) trains the solve from the model's own markers for part of the
schedule: from epoch E0 on every training image draws, with a probability rising from 0 at E0 to 1
at E1 ((ep - E0 + 1) / (E1 - E0 + 1)), the markers predicted_markers() extracts from the current
marker head (no gradient through the extraction; thresholds --mk-train-thr / --mk-train-min-area /
--mk-train-h, the fold-3 choice of section 11.1 by default) instead of the eroded ground truth.
The cross-entropy stays against the true instance map: the target of a predicted label is the
ground-truth nucleus holding the majority of its marker pixels (marker_quality's owner), so a
marker in background has no pixel to win and is penalised wherever its label wins; a nucleus with
several markers keeps all of them (the probability of the target is their sum, the loss does not
force a split); the pixels of a nucleus without a marker cannot be right under any label and get
zero weight (--mk-unmarked ignore; --mk-unmarked bg makes the background label their target
instead).  The per-epoch log carries the schedule probability, the share of images on predicted
markers, their marker quality on the training batches and the share of unreachable pixels.

Layer (pw_layer.MultiRWLayer): one label per marker plus the background; the K_b + 1
systems of every image share the matrix L(w) + diag(sum_k a_k) and are stacked along the
batch axis, so the cost is affine in the number of labels and K is free per image.
Training markers: the ground-truth instances eroded by 2-3 px (radius drawn per step),
each keeping its core; loss = per-pixel cross-entropy of the label probabilities against
the instance map (seam pixels and their 1-px flank weighted 1 + --w-seam), + --aux BCE on
the foreground logit, + --w-mk BCE on the marker logit, + --w-edge edge target; p annealed
--p0 -> --p1 (5 -> 20 by default).

Test markers: bce head: 4-connected components of the thresholded marker map (components
below --mk-min-area dropped); dist head: the regional maxima of the predicted distance map
with prominence at least --mk-h (h-maxima), grown by a watershed of the map down to
--mk-thr, basins below --mk-min-area dropped.  --tune-fold F chooses --mk-thr, --mk-min-area
(and --mk-h) by the PQ of the layer's output on --tune-n evenly spaced patches of fold F
(neither the training nor the test fold; the table goes to the json as mk_tune); optionally (--fallback) foreground components of s > 0.5 of at
least --fb-min-area px that contain no marker get one at their distance-transform
maximum.  Marker quality: for every ground-truth nucleus the number of predicted markers
whose majority lies in it (exactly one / none / several), and the markers in background.

Outputs evaluated on fold 2 (label maps, argmax over the labels; instance metrics on the
labels themselves, pixel metrics on the foreground = label > 0):
  logits      s > 0.5, 4-connected components (the plain U-Net pipeline of this model)
  layer       converged multi-marker solve at p1, predicted markers
  layer_fb    the same with the fallback markers
  layer_gtmk  the same with the ground-truth markers (eroded by 2 px): the oracle on markers
  layer_img   converged solve with image-gradient edge costs instead of the learned ones
  ws          classical marker watershed (skimage) of the learned contour map inside s > 0.5
              from the same predicted markers
  limit       exact K-label Power Watershed of the learned costs (subset, --limit-n)
  limit_img   exact Power Watershed with image-gradient edge costs (the marker-controlled
              watershed with the U-Net's background as soft seed), same subset
plus the ground-truth binary mask as the components ceiling, per tissue type, inference
timings (solve time, PCG iterations, K) and the limit's time per patch.

usage: exp_instance_pannuke.py --epochs 30 --outdir results_pannuke_instances
       exp_instance_pannuke.py --mk-head dist --tune-fold 3 --outdir results_pannuke_instances/dist
       exp_instance_pannuke.py --maxit 300 --outdir results_pannuke_instances/maxit300
       exp_instance_pannuke.py --eval-only --load results_pannuke_instances/instances.pt --tune-fold 3 \
                               --outdir results_pannuke_instances/bce_tuned
"""
import argparse, json, os, time
from multiprocessing import get_context
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy import ndimage
from pw_layer import (MultiRWLayer, label_systems, split_labels, multi_cross_entropy, eroded_markers,
                      label_core_distance, pw_limit_multi_numpy, unary_costs_from_prob)
from exp_unet_pets import UNet
from exp_unet_seg import (load_dataset, augment, pixel_edge_probs, edge_loss, summarise, flatten_per_image,
                          maxpool, pixel_metrics)
from seg_metrics import instance_metrics, aggregate_instance, edge_alignment, strong_edges, FOUR

MODES = ("logits", "layer", "layer_fb", "layer_gtmk", "layer_img", "ws", "limit", "limit_img")


# ----------------------------------------------------------------------------
# model
# ----------------------------------------------------------------------------
class InstanceSegmenter(nn.Module):
    def __init__(self, cmax=8.0, edge_cmax=8.0, learn_scale=True):
        super().__init__()
        self.unet = UNet(4)
        self.cmax = cmax
        self.edge_cmax = edge_cmax
        self.log_scale = nn.Parameter(torch.tensor(float(np.log(edge_cmax)))) if learn_scale else None

    def edge_scale(self):
        return self.log_scale.exp() if self.log_scale is not None else torch.tensor(self.edge_cmax)

    def forward(self, img):
        out = self.unet(img)
        logit, h, mlogit = out[:, :1], out[:, 1:3], out[:, 3:4]
        s = torch.sigmoid(logit)
        c1, c0 = unary_costs_from_prob(s, cmax=self.cmax)
        eprob = torch.sigmoid(h)
        e = self.edge_scale() * eprob
        ch = 0.5 * (e[:, :1, :, 1:] + e[:, :1, :, :-1])
        cv = 0.5 * (e[:, 1:2, 1:, :] + e[:, 1:2, :-1, :])
        return dict(logit=logit, s=s, mlogit=mlogit, ch=ch, cv=cv, c0=c0, c1=c1, eprob=eprob)


def image_costs(img, cmax, q=0.99):
    """img (B,3,H,W) in [0,1] -> edge costs from the colour gradient: the root-mean-square
    colour difference across each grid edge, scaled per image so that its q-quantile is
    cmax (comparable with the unary costs, which are clamped at cmax), clamped at cmax."""
    gh = ((img[:, :, :, 1:] - img[:, :, :, :-1]) ** 2).mean(1, keepdim=True).sqrt()
    gv = ((img[:, :, 1:, :] - img[:, :, :-1, :]) ** 2).mean(1, keepdim=True).sqrt()
    B = img.shape[0]
    allg = torch.cat([gh.reshape(B, -1), gv.reshape(B, -1)], 1)
    ref = torch.quantile(allg, q, dim=1).clamp_min(1e-6).view(B, 1, 1, 1)
    return (cmax * gh / ref).clamp_max(cmax), (cmax * gv / ref).clamp_max(cmax)


# ----------------------------------------------------------------------------
# markers at test time
# ----------------------------------------------------------------------------
def markers_from_map(m, thr=0.5, min_area=1):
    """Marker probability map (H,W) -> label map of its 4-connected components above thr
    (components below min_area px dropped), labels 1..K."""
    lab, n = ndimage.label(m > thr, structure=FOUR)
    if n and min_area > 1:
        area = np.bincount(lab.ravel(), minlength=n + 1)
        keep = area >= min_area; keep[0] = False
        remap = np.zeros(n + 1, lab.dtype); remap[keep] = np.arange(1, keep.sum() + 1)
        lab = remap[lab]
    return lab.astype(np.int32)


def drop_small(lab, min_area):
    """Relabel a marker label map 1..K' after dropping the labels with fewer than min_area px."""
    n = int(lab.max())
    if n == 0 or min_area <= 1:
        return lab.astype(np.int32)
    area = np.bincount(lab.ravel(), minlength=n + 1)
    keep = area >= min_area; keep[0] = False
    remap = np.zeros(n + 1, np.int32); remap[keep] = np.arange(1, keep.sum() + 1)
    return remap[lab]


def markers_from_dist(dm, thr=0.5, min_area=1, h=0.1):
    """Predicted normalised distance map (H,W) in [0,1] -> marker label map: one marker per
    regional maximum of prominence at least h (skimage h_maxima, one seed per plateau), grown
    by a watershed of -dm inside dm > thr (so two touching nuclei whose maxima are separated
    by a valley deeper than h get two markers even when the valley is above thr); basins
    below min_area px dropped.  Labels 1..K."""
    from skimage.morphology import h_maxima
    from skimage.segmentation import watershed
    mask = dm > thr
    if not mask.any():
        return np.zeros(dm.shape, np.int32)
    seeds, n = ndimage.label((h_maxima(dm, h) > 0) & mask, structure=FOUR)
    if n == 0:
        seeds, n = ndimage.label(mask, structure=FOUR)
    lab = watershed(-dm, seeds, mask=mask, connectivity=1)
    return drop_small(lab, min_area)


def predicted_markers(m, args, thr=None, min_area=None, h=None):
    """Marker head output (H,W) -> marker label map, by --mk-head."""
    thr = args.mk_thr if thr is None else thr
    min_area = args.mk_min_area if min_area is None else min_area
    if args.mk_head == "dist":
        return markers_from_dist(m, thr, min_area, args.mk_h if h is None else h)
    return markers_from_map(m, thr, min_area)


def dist_target(inst, rmax):
    """inst (B,1,H,W) int -> normalised Chebyshev distance to the instance boundary (B,1,H,W)
    float in [0,1]: d / max_instance(d) with d capped at rmax; the pixels at an instance's
    maximum are 1 (so a 1-px-thin nucleus still has a marker), background 0."""
    d, dmax = label_core_distance(inst, rmax=rmax)
    fg = inst > 0
    t = d / dmax.clamp_min(1.0)
    return torch.where(fg & (d == dmax), torch.ones_like(t), t) * fg.float()


def peak_loss(pred, inst, target=None, pool=1):
    """pred (B,1,H,W) in [0,1], inst (B,1,H,W) int, target (B,1,H,W) the distance target (None =
    1): mean over the ground-truth instances of (max target - max pred)_+^2 over the instance,
    both maxima on the pool x pool mean-pooled maps (differentiable through the arg-max pixels)."""
    B = inst.shape[0]; n = int(inst.max()) + 1
    if n <= 1:
        return pred.sum() * 0
    if pool > 1:
        pred = F.avg_pool2d(pred, pool, 1, pool // 2)
        target = F.avg_pool2d(target, pool, 1, pool // 2) if target is not None else None
    flat = (inst.long() + torch.arange(B, device=inst.device)[:, None, None, None] * n).reshape(-1)
    def imax(x):
        t = torch.full((B * n,), -1.0, device=x.device, dtype=x.dtype)
        return t.scatter_reduce(0, flat, x.reshape(-1), "amax", include_self=True)
    pm = imax(pred)
    tm = imax(target) if target is not None else torch.ones_like(pm)
    valid = (torch.arange(B * n, device=inst.device) % n > 0) & (pm >= 0)
    return (F.relu(tm[valid] - pm[valid]) ** 2).mean()


def neg_loss(pred, inst, k=256, pool=1):
    """Hard negatives: per image, the mean of the k largest values of the (pool x pool mean-pooled)
    prediction over the background pixels (inst == 0), squared; mean over the batch."""
    if pool > 1:
        pred = F.avg_pool2d(pred, pool, 1, pool // 2)
    bg = (inst == 0).reshape(pred.shape[0], -1)
    v = pred.reshape(pred.shape[0], -1).masked_fill(~bg, -1.0)
    top = v.topk(min(k, v.shape[1]), dim=1).values.clamp_min(0.0)
    return (top ** 2).mean()


def grad_loss(pred, target):
    """HoVer-Net's gradient term on the distance map: MSE of the horizontal and vertical finite
    differences of prediction and target over all pixels."""
    dxp, dyp = pred[..., :, 1:] - pred[..., :, :-1], pred[..., 1:, :] - pred[..., :-1, :]
    dxt, dyt = target[..., :, 1:] - target[..., :, :-1], target[..., 1:, :] - target[..., :-1, :]
    return F.mse_loss(dxp, dxt) + F.mse_loss(dyp, dyt)


def marker_loss(mlogit, inst, core, args):
    if args.mk_head == "dist":
        t = dist_target(inst, args.mk_rmax)
        if args.mk_loss == "bce":
            return F.binary_cross_entropy_with_logits(mlogit, t)
        return F.mse_loss(torch.sigmoid(mlogit), t)
    return F.binary_cross_entropy_with_logits(mlogit, core.float())


def add_fallback_markers(lab, s, min_area=16, thr=0.5):
    """Foreground components (s > thr, 4-connected) of at least min_area px with no marker
    pixel get a marker: the 3x3 neighbourhood of their distance-transform maximum."""
    lab = lab.copy()
    fg, n = ndimage.label(s > thr, structure=FOUR)
    if n == 0:
        return lab
    has = np.zeros(n + 1, bool); has[np.unique(fg[lab > 0])] = True
    area = np.bincount(fg.ravel(), minlength=n + 1)
    cand = np.flatnonzero(~has & (area >= min_area)); cand = cand[cand > 0]
    if cand.size == 0:
        return lab
    dist = ndimage.distance_transform_edt(fg > 0)
    nxt = int(lab.max()) + 1
    for c in cand:
        d = np.where(fg == c, dist, -1.0)
        i, j = np.unravel_index(int(d.argmax()), d.shape)
        sl = (slice(max(i - 1, 0), i + 2), slice(max(j - 1, 0), j + 2))
        patch = lab[sl]
        patch[(fg[sl] == c) & (patch == 0)] = nxt
        nxt += 1
    return lab


def marker_quality(lab, inst):
    """How many predicted markers does each ground-truth nucleus get?  A marker belongs to
    the GT id of the majority of its pixels.  Returns counts: n_gt, one, zero, multi (GT
    nuclei with exactly one / no / several markers), n_mk, bg_mk (markers in background)."""
    inst = inst.astype(np.int64); ngt = int(inst.max()); nmk = int(lab.max())
    out = dict(n_gt=ngt, one=0, zero=ngt, multi=0, n_mk=nmk, bg_mk=0)
    if nmk == 0:
        return out
    cnt = np.bincount(lab.ravel().astype(np.int64) * (ngt + 1) + inst.ravel(), minlength=(nmk + 1) * (ngt + 1)).reshape(nmk + 1, ngt + 1)
    owner = cnt[1:].argmax(1)                                   # GT id (0 = background) of every marker
    out["bg_mk"] = int((owner == 0).sum())
    per_gt = np.bincount(owner[owner > 0], minlength=ngt + 1)[1:]
    out.update(one=int((per_gt == 1).sum()), zero=int((per_gt == 0).sum()), multi=int((per_gt > 1).sum()))
    return out


def sched_prob(ep, sched):
    """--mk-sched E0 E1 -> the probability that a training image uses the predicted markers at
    epoch ep: 0 before E0, (ep - E0 + 1) / (E1 - E0 + 1) from E0 to E1 (the first scheduled epoch
    already draws some), 1 after E1 (E1 = E0: all of them from E0 on)."""
    if sched is None or ep < sched[0]:
        return 0.0
    e0, e1 = sched
    return min(1.0, (ep - e0 + 1) / max(e1 - e0 + 1, 1))


def marker_target_map(mk, inst):
    """Predicted marker labels (H,W) long 0..K and ground-truth ids (H,W) long 0..G (both
    consecutive) -> (M, owner): M (G+1, K+1) float, row g marks the predicted labels whose target
    is nucleus g (the nucleus holding the majority of the marker's pixels, as in marker_quality);
    row 0 holds the background label alone, so a marker in background has no pixel to win and a
    nucleus with several markers keeps all of them; owner (K,) long the ground-truth id of every
    marker (0 = background)."""
    K, G = int(mk.max()), int(inst.max())
    M = torch.zeros(G + 1, K + 1, device=mk.device)
    M[0, 0] = 1.0
    if K == 0:
        return M, torch.zeros(0, dtype=torch.long, device=mk.device)
    cnt = torch.bincount(mk.reshape(-1) * (G + 1) + inst.reshape(-1), minlength=(K + 1) * (G + 1)).reshape(K + 1, G + 1)
    owner = cnt[1:].argmax(1)
    k = torch.arange(1, K + 1, device=mk.device)
    M[owner[owner > 0], k[owner > 0]] = 1.0
    return M, owner


def mixed_label_systems(inst, core, mk_labs, unmarked="ignore"):
    """Training systems of a batch where some images use the eroded ground-truth markers and the
    others the model's own predicted markers (--mk-sched).  inst (B,1,H,W) long ground-truth ids,
    core (B,1,H,W) bool the erosion; mk_labs: list over images of a predicted marker label map
    (H,W) int (labels 1..K), or None for the ground-truth markers.  Returns sysd as label_systems
    (mk, group, is_bg, offsets, K; target = the ground-truth ids relabelled 0..G_b for every image)
    plus tmap, per image None (the targets are the labels themselves) or the (G_b+1, K_b+1) map of
    marker_target_map, and the counts of the predicted markers over the batch (marker_quality's
    one / zero / multi / bg_mk, images and nuclei, unreachable pixels).  unmarked: the pixels of a
    nucleus with no marker are 'ignore' (no label can be right there: zero weight in the loss) or
    'bg' (the background label is their target)."""
    B, _, H, W = inst.shape
    mks, groups, is_bg, offsets, Ks, targets, tmaps = [], [], [], [], [], [], []
    stats = dict(n_pred=0, n_gt=0, one=0, zero=0, multi=0, n_mk=0, bg_mk=0, unreach=0, px=0)
    off = 0
    for b in range(B):
        lb = inst[b, 0].long()
        uniq, inv = torch.unique(lb, return_inverse=True)
        if uniq[0] != 0:
            inv = inv + 1
        G = int(inv.max())
        if mk_labs[b] is None:
            sd = label_systems(inst[b:b + 1], core[b:b + 1])
            oh, K, tmap = sd["mk"], sd["K"][0], None
        else:
            mk = torch.from_numpy(np.ascontiguousarray(mk_labs[b])).to(inst.device).long()
            K = int(mk.max())
            oh = F.one_hot(mk, K + 1).permute(2, 0, 1).to(torch.float32)[:, None]
            oh[0] = 1.0
            tmap, owner = marker_target_map(mk, inv)
            reach = tmap.sum(1) > 0
            if unmarked == "bg":
                tmap[~reach, 0] = 1.0
            per_gt = torch.bincount(owner[owner > 0], minlength=G + 1)[1:]
            stats["n_pred"] += 1; stats["n_gt"] += G; stats["n_mk"] += K; stats["bg_mk"] += int((owner == 0).sum())
            stats["one"] += int((per_gt == 1).sum()); stats["zero"] += int((per_gt == 0).sum()); stats["multi"] += int((per_gt > 1).sum())
            stats["unreach"] += int((~reach[inv]).sum()); stats["px"] += H * W
        mks.append(oh); groups.append(torch.full((K + 1,), b, dtype=torch.long, device=inst.device))
        flag = torch.zeros(K + 1, dtype=torch.bool, device=inst.device); flag[0] = True
        is_bg.append(flag); offsets.append(off); Ks.append(K); targets.append(inv); tmaps.append(tmap)
        off += K + 1
    return dict(mk=torch.cat(mks), group=torch.cat(groups), is_bg=torch.cat(is_bg), offsets=offsets, K=Ks,
                target=torch.stack(targets), tmap=tmaps), stats


def mapped_cross_entropy(x, sysd, weight=None, eps=1e-6):
    """multi_cross_entropy for the systems of mixed_label_systems: on an image with predicted
    markers the probability of the target is the sum over the labels mapped to the pixel's nucleus
    (tmap), and the pixels of a nucleus no label is mapped to get zero weight (they stay in the
    denominator, so the value is comparable with the ground-truth-marker epochs)."""
    tot, n = 0.0, 0
    tmaps = sysd.get("tmap")
    for b, xb in enumerate(split_labels(x, sysd)):
        tgt = sysd["target"][b][None]
        M = tmaps[b] if tmaps is not None else None
        if M is None:
            l = -torch.log(xb.gather(0, tgt)[0].clamp_min(eps))
        else:
            pt = torch.einsum("gk,khw->ghw", M, xb).gather(0, tgt)[0]
            l = -torch.log(pt.clamp_min(eps)) * (M.sum(1) > 0).float()[tgt[0]]
        if weight is not None:
            l = l * weight[b]
        tot = tot + l.sum(); n += l.numel()
    return tot / n


def _marker_worker(job):
    """Pool worker of the training-time marker extraction (--mk-sched): map -> label map."""
    m, head, thr, ma, h = job
    return markers_from_dist(m, thr, ma, h) if head == "dist" else markers_from_map(m, thr, ma)


def ws_labels(cmean, lab, s, thr=0.5):
    """Classical marker watershed of the contour map inside s > thr from the marker label map."""
    from skimage.segmentation import watershed
    if lab.max() == 0:
        return np.zeros_like(lab)
    return watershed(cmean, lab, mask=s > thr, connectivity=1).astype(np.int32)


# ----------------------------------------------------------------------------
# metrics on a label map
# ----------------------------------------------------------------------------
def label_metrics(L, conf, y, inst, strong):
    """L (H,W) int label map (0 background); conf (H,W) the probability of the chosen label
    (for the softness) or None; y the binary target; inst the GT instances."""
    fg = (L > 0).astype(np.float32)
    m = pixel_metrics(fg, y)
    if conf is not None:
        m["soft_frac"] = float(((conf > 0.1) & (conf < 0.9)).mean())
    if strong is not None:
        m["edge_align"] = edge_alignment(fg > 0.5, strong=strong)
    m["inst"] = instance_metrics(fg > 0.5, inst, lab=L)
    return m


def argmax_labels(xb):
    """(K+1,H,W) label probabilities (torch) -> (labels (H,W) int32, confidence (H,W))."""
    conf, L = xb.max(0)
    return L.cpu().numpy().astype(np.int32), conf.cpu().numpy()


# ----------------------------------------------------------------------------
# evaluation
# ----------------------------------------------------------------------------
def _limit_worker(job):
    g, ch, cv, c0, c1, chi, cvi, lab = job
    t0 = time.time(); L, st = pw_limit_multi_numpy(ch, cv, c0, c1, lab); t1 = time.time()
    Li, sti = pw_limit_multi_numpy(chi, cvi, c0, c1, lab); t2 = time.time()
    return g, L.astype(np.int32), Li.astype(np.int32), t1 - t0, t2 - t1, int(lab.max()), st["solved_plateaus"]


def evaluate(model, d, p, device, args, limit_idx=(), example_idx=(), quick=False):
    """quick: validation during training (layer with predicted markers and logits only)."""
    model.eval()
    X, Y, inst_all, types = d["X_test"], d["Y_test"], d["inst_test"], d.get("types_test")
    limit_idx, example_idx = set(limit_idx), set(example_idx)
    layer = MultiRWLayer(tol=args.eval_tol, maxit=args.eval_maxit)
    res = {k: [] for k in MODES}; res_types = {k: [] for k in MODES}
    mq = []; ref = []; examples = []
    timing = dict(solve_s=0.0, solve_n=0, iters=0, K_sum=0, systems=0, batches=0, unet_s=0.0)
    limit_jobs, limit_ctx = [], {}
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
            s = out["s"].cpu().numpy()[:, 0]; mprob = torch.sigmoid(out["mlogit"]).cpu().numpy()[:, 0]
            cmean = out["eprob"].mean(1).cpu().numpy()
            # markers
            labs = [predicted_markers(mprob[j], args) for j in range(len(y))]
            labs_fb = [add_fallback_markers(labs[j], s[j], args.fb_min_area) for j in range(len(y))] if args.fallback and not quick else None
            lab_t = torch.from_numpy(np.stack(labs)).to(device)[:, None].long()
            sysd = label_systems(lab_t)
            st = {}
            if device == "cuda":
                torch.cuda.synchronize()
            t0 = time.time()
            x = layer(out["ch"], out["cv"], out["c0"], out["c1"], sysd, float(p), stats=st)
            if device == "cuda":
                torch.cuda.synchronize()
            timing["solve_s"] += time.time() - t0; timing["solve_n"] += len(y); timing["iters"] += st.get("last_iters", 0)
            timing["K_sum"] += sum(sysd["K"]); timing["systems"] += x.shape[0]; timing["batches"] += 1
            xs = split_labels(x, sysd)
            xs_fb = xs_gt = xs_img = None
            if not quick:
                if labs_fb is not None:
                    sysd_fb = label_systems(torch.from_numpy(np.stack(labs_fb)).to(device)[:, None].long())
                    xs_fb = split_labels(layer(out["ch"], out["cv"], out["c0"], out["c1"], sysd_fb, float(p)), sysd_fb)
                inst_t = torch.from_numpy(inst_all[i:i + args.batch].astype(np.int64)).to(device)[:, None]
                core = eroded_markers(inst_t, 2)
                sysd_gt = label_systems(inst_t, core)
                xs_gt = split_labels(layer(out["ch"], out["cv"], out["c0"], out["c1"], sysd_gt, float(p)), sysd_gt)
                chi, cvi = image_costs(img, args.cmax)
                xs_img = split_labels(layer(chi, cvi, out["c0"], out["c1"], sysd, float(p)), sysd)
            for j in range(len(y)):
                g = i + j
                inst = inst_all[g]
                strong = strong_edges(X[g].transpose(1, 2, 0)) if args.edge_align and not quick else None
                tt = types[g] if types is not None else None
                mq.append(dict(marker_quality(labs[j], inst), **{"fb_" + k: v for k, v in (marker_quality(labs_fb[j], inst).items() if labs_fb is not None else {}.items())}))
                res["logits"].append(label_metrics(ndimage.label(s[j] > 0.5, structure=FOUR)[0], s[j], y[j], inst, strong)); res_types["logits"].append(tt)
                L, conf = argmax_labels(xs[j])
                res["layer"].append(label_metrics(L, conf, y[j], inst, strong)); res_types["layer"].append(tt)
                ex = None
                if g in example_idx:
                    ex = dict(idx=g, img=X[g], y=y[j], inst=inst, s=s[j], m=mprob[j], c=cmean[j], lab=labs[j], L_layer=L, conf=conf,
                              ch=out["ch"][j, 0].cpu().numpy(), cv=out["cv"][j, 0].cpu().numpy())
                    if tt is not None:
                        ex["type"] = tt
                if quick:
                    continue
                ref.append(label_metrics(inst.astype(np.int32), None, y[j], inst, strong))
                if xs_fb is not None:
                    Lf, cf = argmax_labels(xs_fb[j])
                    res["layer_fb"].append(label_metrics(Lf, cf, y[j], inst, strong)); res_types["layer_fb"].append(tt)
                    if ex is not None:
                        ex.update(lab_fb=labs_fb[j], L_layer_fb=Lf)
                Lg, cg = argmax_labels(xs_gt[j])
                res["layer_gtmk"].append(label_metrics(Lg, cg, y[j], inst, strong)); res_types["layer_gtmk"].append(tt)
                Li, ci = argmax_labels(xs_img[j])
                res["layer_img"].append(label_metrics(Li, ci, y[j], inst, strong)); res_types["layer_img"].append(tt)
                Lw = ws_labels(cmean[j], labs[j], s[j])
                res["ws"].append(label_metrics(Lw, None, y[j], inst, strong)); res_types["ws"].append(tt)
                if ex is not None:
                    ex.update(L_gtmk=Lg, L_img=Li, L_ws=Lw)
                    examples.append(ex)
                if g in limit_idx:
                    limit_jobs.append((g,) + tuple(t[j, 0].double().cpu().numpy() for t in (out["ch"], out["cv"], out["c0"], out["c1"], chi, cvi)) + (labs[j],))
                    limit_ctx[g] = (y[j], inst, strong, tt)
            if (i // args.batch) % 20 == 0:
                print(f"    eval {i}/{len(X)}  solve {timing['solve_s'] / max(timing['batches'], 1):.2f}s/batch", flush=True)
    t_limit = dict(learned=0.0, img=0.0, n=0, K=0, solved_plateaus=0)
    limit_order = []
    if limit_jobs:
        t0 = time.time()
        with get_context("fork").Pool(max(1, args.limit_workers)) as pool:
            for g, L, Li, tl, ti, K, sp in pool.imap_unordered(_limit_worker, limit_jobs, chunksize=1):
                yy, inst, strong, tt = limit_ctx[g]
                res["limit"].append(label_metrics(L, None, yy, inst, strong)); res_types["limit"].append(tt)
                res["limit_img"].append(label_metrics(Li, None, yy, inst, strong)); res_types["limit_img"].append(tt)
                limit_order.append(g)
                t_limit["learned"] += tl; t_limit["img"] += ti; t_limit["n"] += 1; t_limit["K"] += K; t_limit["solved_plateaus"] += sp
                for ex in examples:
                    if ex["idx"] == g:
                        ex.update(L_limit=L, L_limit_img=Li)
                if len(limit_order) % 50 == 0:
                    print(f"    limit {len(limit_order)}/{len(limit_jobs)}  {time.time() - t0:.0f}s", flush=True)
        t_limit["wall"] = time.time() - t0
    summary = {k: summarise(v, res_types[k] if types is not None else None) for k, v in res.items() if v}
    if ref:
        summary["gt_inst"] = summarise(ref, list(types) if types is not None else None)
    if mq:
        agg = {k: int(sum(r[k] for r in mq)) for k in mq[0]}
        ngt = max(agg["n_gt"], 1)
        summary["markers"] = dict(agg, frac_one=agg["one"] / ngt, frac_zero=agg["zero"] / ngt, frac_multi=agg["multi"] / ngt,
                                  bg_per_patch=agg["bg_mk"] / len(mq), mk_per_patch=agg["n_mk"] / len(mq), n_gt_per_patch=agg["n_gt"] / len(mq))
        if "fb_n_gt" in agg:
            summary["markers"].update(fb_frac_one=agg["fb_one"] / ngt, fb_frac_zero=agg["fb_zero"] / ngt, fb_frac_multi=agg["fb_multi"] / ngt,
                                      fb_bg_per_patch=agg["fb_bg_mk"] / len(mq), fb_mk_per_patch=agg["fb_n_mk"] / len(mq))
    summary["_timing"] = dict(timing, solve_s_per_image=timing["solve_s"] / max(timing["solve_n"], 1),
                              unet_s_per_image=timing["unet_s"] / max(timing["solve_n"], 1),
                              iters_per_batch=timing["iters"] / max(timing["batches"], 1),
                              K_per_image=timing["K_sum"] / max(timing["solve_n"], 1),
                              limit=dict(t_limit, learned_per_patch=t_limit["learned"] / max(t_limit["n"], 1),
                                         img_per_patch=t_limit["img"] / max(t_limit["n"], 1),
                                         K_per_patch=t_limit["K"] / max(t_limit["n"], 1)))
    per_image = {k: v for k, v in res.items() if v}
    per_image["markers"] = mq
    if limit_order:
        per_image["limit_idx"] = limit_order
    return summary, examples, per_image


def choose_examples(d, mode="touch", n=8):
    """Test indices of the example patches.  touch: the n patches with the most touching-interface
    pixels (section 11: all dense Colon).  diverse: one patch per tissue type for the n most
    frequent types, the patch whose nucleus count is closest to the type's median among the
    patches of the type with at least the type's median number of touching pixels."""
    touch = d["touch_test"].reshape(len(d["touch_test"]), -1).sum(1)
    if mode == "touch":
        return [int(i) for i in np.argsort(-touch)[:n]]
    types = np.asarray(d["types_test"]); counts = np.array([int(i.max()) for i in d["inst_test"]])
    order = sorted(set(types.tolist()), key=lambda t: (-(types == t).sum(), t))[:n]
    out = []
    for t in order:
        sel = np.flatnonzero(types == t)
        cand = sel[touch[sel] >= np.median(touch[sel])]
        med = np.median(counts[sel])
        out.append(int(cand[np.argmin(np.abs(counts[cand] - med) + 1e-3 * np.arange(len(cand)))]))
    return out


def examples_subset(d, idx):
    return {k: (v[idx] if isinstance(v, np.ndarray) and len(v) == len(d["X_test"]) else v) for k, v in d.items()}


def tb_writer(args, name):
    """--tb: a TensorBoard SummaryWriter under <outdir>/tb (view with
    `tensorboard --logdir <results dir>` on the machine and an ssh tunnel, see the README of
    the results folder); None when off."""
    if not getattr(args, "tb", False):
        return None
    from torch.utils.tensorboard import SummaryWriter
    return SummaryWriter(os.path.join(args.outdir, "tb"), comment=name)


def log_from_tb(tbdir):
    """Rebuild the per-epoch training log from the TensorBoard events of tb_log (every float of the
    epoch entry as train/<key>, the validation dicts as val/<k>/<m>): for a run whose job died
    after the training (the .pt saved, no json), so that --eval-only keeps the training curves."""
    from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
    import glob
    train, val = {}, {}
    for f in sorted(glob.glob(os.path.join(tbdir, "events.out.tfevents.*"))):
        acc = EventAccumulator(f, size_guidance={"scalars": 0}); acc.Reload()
        for tag in acc.Tags()["scalars"]:
            for e in acc.Scalars(tag):
                if tag.startswith("train/"):
                    train.setdefault(e.step, {})[tag[6:]] = float(e.value)
                elif tag.startswith("val/"):
                    _, k, m = tag.split("/", 2)
                    val.setdefault(e.step, {}).setdefault(k, {})[m] = float(e.value)
    log = []
    for ep in sorted(train):
        entry = dict(epoch=int(ep), **train[ep])
        if ep in val:
            entry["val"] = val[ep]
        log.append(entry)
    return log


def tb_log(tb, entry, ep):
    """Every float of the epoch entry as train/<key>, the nested validation dicts as val/<...>."""
    if tb is None:
        return
    for k, v in entry.items():
        if isinstance(v, (int, float)) and k != "epoch":
            tb.add_scalar(f"train/{k}", v, ep)
    for k, v in entry.get("val", {}).items():
        for m, x in v.items():
            tb.add_scalar(f"val/{k}/{m}", x, ep)
    tb.flush()


# ----------------------------------------------------------------------------
# marker post-processing chosen on a held-out fold
# ----------------------------------------------------------------------------
def tune_markers(model, args, device, p):
    """Choose --mk-thr, --mk-min-area (and --mk-h for the dist head) by the PQ of the layer's
    output (converged multi-marker solve at p from the predicted markers) on --tune-n evenly
    spaced patches of fold --tune-fold.  Returns (dict of the chosen values, table)."""
    f = np.load(os.path.join(args.data, f"pannuke_fold{args.tune_fold}.npz"))
    n = len(f["types"])
    sel = np.linspace(0, n - 1, min(args.tune_n, n)).astype(int)
    X = np.ascontiguousarray(f["images"][sel].transpose(0, 3, 1, 2)); inst_all = f["inst"][sel]
    hs = tuple(args.tune_h) if args.mk_head == "dist" else (None,)
    grid = [(thr, ma, h) for thr in args.tune_thr for ma in args.tune_min_area for h in hs]
    layer = MultiRWLayer(tol=args.eval_tol, maxit=args.eval_maxit)
    rows = {g: [] for g in grid}; mq = {g: [] for g in grid}
    model.eval(); t0 = time.time()
    with torch.no_grad():
        for i in range(0, len(X), args.batch):
            img = torch.from_numpy(X[i:i + args.batch]).to(device).float() / 255
            out = model(img)
            mprob = torch.sigmoid(out["mlogit"]).cpu().numpy()[:, 0]
            for g in grid:
                thr, ma, h = g
                labs = [predicted_markers(mprob[j], args, thr, ma, h) for j in range(len(mprob))]
                sysd = label_systems(torch.from_numpy(np.stack(labs)).to(device)[:, None].long())
                xs = split_labels(layer(out["ch"], out["cv"], out["c0"], out["c1"], sysd, float(p)), sysd)
                for j in range(len(mprob)):
                    L, _ = argmax_labels(xs[j])
                    rows[g].append(instance_metrics(L > 0, inst_all[i + j], lab=L))
                    mq[g].append(marker_quality(labs[j], inst_all[i + j]))
            if (i // args.batch) % 5 == 0:
                print(f"    tune {i}/{len(X)}  {time.time() - t0:.0f}s", flush=True)
    def key(g):
        return f"thr={g[0]}/min_area={g[1]}" + (f"/h={g[2]}" if g[2] is not None else "")
    table = {}
    for g in grid:
        a = aggregate_instance(rows[g]); ngt = max(sum(r["n_gt"] for r in mq[g]), 1)
        table[key(g)] = dict(pq=a["pq"], f1_05=a["f1_05"], aji=a["aji"], count_err=a["count_err"], n_pred=a["n_pred_mean"],
                             frac_one=sum(r["one"] for r in mq[g]) / ngt, frac_zero=sum(r["zero"] for r in mq[g]) / ngt,
                             frac_multi=sum(r["multi"] for r in mq[g]) / ngt, bg_per_patch=sum(r["bg_mk"] for r in mq[g]) / len(mq[g]))
    best = max(grid, key=lambda g: table[key(g)]["pq"])
    for g in grid:
        v = table[key(g)]
        print(f"  tune {key(g):32s} PQ {v['pq']:.3f}  F1 {v['f1_05']:.3f}  AJI {v['aji']:.3f}  count err {v['count_err']:.3f}  "
              f"n_pred {v['n_pred']:.1f}  one/zero/multi {v['frac_one']:.2f}/{v['frac_zero']:.2f}/{v['frac_multi']:.2f}  bg {v['bg_per_patch']:.1f}", flush=True)
    chosen = dict(mk_thr=float(best[0]), mk_min_area=int(best[1]))
    if best[2] is not None:
        chosen["mk_h"] = float(best[2])
    print(f"  chosen markers: {chosen}  (fold {args.tune_fold}, {len(sel)} patches, {time.time() - t0:.0f}s)", flush=True)
    return chosen, dict(fold=int(args.tune_fold), n=int(len(sel)), chosen=chosen, table=table)


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
    ap.add_argument("--p0", type=float, default=5.0)
    ap.add_argument("--p1", type=float, default=20.0)
    ap.add_argument("--cmax", type=float, default=8.0)
    ap.add_argument("--edge-cmax", type=float, default=8.0)
    ap.add_argument("--no-learn-scale", dest="learn_scale", action="store_false")
    ap.add_argument("--tol", type=float, default=1e-4, help="training solve tolerance")
    ap.add_argument("--maxit", type=int, default=100)
    ap.add_argument("--eval-tol", type=float, default=1e-5)
    ap.add_argument("--eval-maxit", type=int, default=1000)
    ap.add_argument("--erode", type=int, nargs="+", default=(2, 3), help="training marker erosion radii (drawn per step)")
    ap.add_argument("--aux", type=float, default=0.5, help="BCE on the foreground logit")
    ap.add_argument("--w-mk", type=float, default=1.0, help="BCE on the marker logit")
    ap.add_argument("--w-peak", type=float, default=0.0, help="per-nucleus peak loss on the marker head (0 = off)")
    ap.add_argument("--peak-pool", type=int, default=1, help="peak loss on the k x k mean-pooled maps (1 = raw maximum)")
    ap.add_argument("--w-neg", type=float, default=0.0, help="hard-negative loss on the marker head (0 = off)")
    ap.add_argument("--neg-k", type=int, default=256, help="hard negatives: number of largest background values per image")
    ap.add_argument("--w-grad", type=float, default=0.0, help="gradient (finite-difference MSE) loss on the distance head (0 = off)")
    ap.add_argument("--w-seam", type=float, default=5.0, help="extra weight of the seam (+1 px) pixels in the cross-entropy")
    ap.add_argument("--w-edge", type=float, default=1.0, help="edge target on the cost head (0 = off)")
    ap.add_argument("--edge-pos", type=float, default=10.0)
    ap.add_argument("--edge-seam", type=float, default=5.0)
    ap.add_argument("--mk-head", choices=("bce", "dist"), default="bce",
                    help="marker head: bce = eroded-mask logit (section 11); dist = normalised distance transform")
    ap.add_argument("--mk-loss", choices=("mse", "bce"), default="mse", help="dist head loss")
    ap.add_argument("--mk-rmax", type=int, default=12, help="dist head: cap of the Chebyshev distance (px)")
    ap.add_argument("--mk-sched", type=int, nargs=2, default=None, metavar=("E0", "E1"),
                    help="section 11.5: train the solve from the model's own predicted markers: from epoch E0 on, every training "
                         "image draws them with probability rising from 0 at E0 to 1 at E1 (instead of the eroded ground truth)")
    ap.add_argument("--mk-train-thr", type=float, default=0.2, help="--mk-sched: marker threshold at training time")
    ap.add_argument("--mk-train-min-area", type=int, default=16, help="--mk-sched: minimum marker area at training time")
    ap.add_argument("--mk-train-h", type=float, default=0.2, help="--mk-sched: prominence of the maxima at training time (dist head)")
    ap.add_argument("--mk-unmarked", choices=("ignore", "bg"), default="ignore",
                    help="--mk-sched: the pixels of a nucleus without a marker: ignore (zero weight) or bg (background is their target)")
    ap.add_argument("--mk-thr", type=float, default=0.5)
    ap.add_argument("--mk-min-area", type=int, default=1)
    ap.add_argument("--mk-h", type=float, default=0.1, help="dist head: prominence of the regional maxima")
    ap.add_argument("--tune-fold", type=int, default=0, help="choose mk-thr / mk-min-area (/ mk-h) by PQ on this fold (0 = off)")
    ap.add_argument("--tune-n", type=int, default=300)
    ap.add_argument("--tune-thr", type=float, nargs="+", default=(0.2, 0.3, 0.4, 0.5, 0.6, 0.7))
    ap.add_argument("--tune-min-area", type=int, nargs="+", default=(1, 4, 9, 16))
    ap.add_argument("--tune-h", type=float, nargs="+", default=(0.05, 0.1, 0.2))
    ap.add_argument("--no-fallback", dest="fallback", action="store_false")
    ap.add_argument("--fb-min-area", type=int, default=16)
    ap.add_argument("--limit-n", type=int, default=300)
    ap.add_argument("--limit-workers", type=int, default=4)
    ap.add_argument("--val-n", type=int, default=200)
    ap.add_argument("--val-every", type=int, default=5)
    ap.add_argument("--n-examples", type=int, default=8)
    ap.add_argument("--examples", choices=("touch", "diverse"), default="touch", help="how the example patches are chosen")
    ap.add_argument("--examples-only", action="store_true",
                    help="with --eval-only: run the saved model on the example patches only and write <name>_examples_<mode>.npz "
                         "(marker settings taken from the json next to the .pt)")
    ap.add_argument("--no-edge-align", dest="edge_align", action="store_false")
    ap.add_argument("--data", default="data")
    ap.add_argument("--outdir", default="results_pannuke_instances")
    ap.add_argument("--tag", default="")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--eval-only", action="store_true")
    ap.add_argument("--load", default="", help="eval only: the .pt to load (default <outdir>/<name>.pt)")
    ap.add_argument("--tb", action="store_true", help="write TensorBoard scalars to <outdir>/tb")
    args = ap.parse_args()
    args.dataset = "pannuke"; args.gap = False
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    os.makedirs(args.outdir, exist_ok=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    d = load_dataset(args)
    tr = np.load(os.path.join(args.data, f"pannuke_fold{args.train_fold}.npz"))
    Xtr, Ytr, Itr, Ttr = d["X_train"], d["Y_train"], tr["inst"], d["touch_train"]
    if args.train_n:
        Xtr, Ytr, Itr, Ttr = Xtr[:args.train_n], Ytr[:args.train_n], Itr[:args.train_n], Ttr[:args.train_n]
    N_te = len(d["X_test"])
    name = "instances" + (f"_{args.tag}" if args.tag else "")
    print(f"pannuke instances / p {args.p0} -> {args.p1} / erode {args.erode} / edge target x{args.w_edge} / "
          f"marker head {args.mk_head} (peak loss x{args.w_peak}, pool {args.peak_pool}; neg x{args.w_neg} k {args.neg_k}; grad x{args.w_grad}) / "
          f"training markers {'ground truth' if args.mk_sched is None else f'predicted from epoch {args.mk_sched[0]} (all from {args.mk_sched[1]}; thr {args.mk_train_thr} / min area {args.mk_train_min_area} / h {args.mk_train_h}; unmarked nuclei: {args.mk_unmarked})'} / "
          f"train solve tol {args.tol} maxit {args.maxit} / "
          f"folds train {args.train_fold} test {args.test_fold} tune {args.tune_fold} / seed {args.seed}: "
          f"train {len(Xtr)} test {N_te} device {device}", flush=True)
    limit_idx = list(np.linspace(0, N_te - 1, min(args.limit_n, N_te)).astype(int)) if args.limit_n else []
    touch_px = d["touch_test"].reshape(N_te, -1).sum(1)
    example_idx = choose_examples(d, args.examples, args.n_examples) if args.n_examples else []
    limit_idx = sorted(set(limit_idx) | set(example_idx))

    model = InstanceSegmenter(args.cmax, args.edge_cmax, args.learn_scale).to(device)
    layer = MultiRWLayer(tol=args.tol, maxit=args.maxit)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, args.epochs)
    val = dict(X_test=d["X_test"][:args.val_n], Y_test=d["Y_test"][:args.val_n], inst_test=d["inst_test"][:args.val_n])
    log = []
    if args.eval_only:
        pt = args.load or os.path.join(args.outdir, f"{name}.pt")
        model.load_state_dict(torch.load(pt, map_location=device))
        prev = pt[:-3] + ".json"
        log = json.load(open(prev))["log"] if os.path.exists(prev) else []
        if not log and os.path.isdir(os.path.join(os.path.dirname(pt), "tb")):
            log = log_from_tb(os.path.join(os.path.dirname(pt), "tb"))
            print(f"  training log rebuilt from TensorBoard: {len(log)} epochs", flush=True)
        print(f"  eval only: loaded {pt}", flush=True)
        if args.examples_only:
            prev = os.path.join(args.outdir, f"{name}.json") if os.path.exists(os.path.join(args.outdir, f"{name}.json")) else prev
            if os.path.exists(prev):
                for k, v in json.load(open(prev))["args"].items():
                    if k in ("mk_thr", "mk_min_area", "mk_h", "mk_head", "fallback", "fb_min_area"):
                        setattr(args, k, v)
            sub = examples_subset(d, example_idx)
            print(f"  examples only ({args.examples}): test patches {example_idx}, types {list(sub['types_test'])}, markers thr {args.mk_thr} / "
                  f"min area {args.mk_min_area} / h {args.mk_h}", flush=True)
            _, examples, _ = evaluate(model, sub, args.p1, device, args, limit_idx=range(len(example_idx)), example_idx=range(len(example_idx)))
            for e in examples:
                e["idx"] = example_idx[e["idx"]]
            np.savez_compressed(os.path.join(args.outdir, f"{name}_examples_{args.examples}.npz"),
                                **{f"{i}__{k}": np.asarray(v) for i, e in enumerate(examples) for k, v in e.items()})
            print("DONE", flush=True)
            return
    tb = tb_writer(args, name)
    mk_pool = None                                            # --mk-sched: the training-time marker extraction runs in a process pool
    for ep in range(0 if args.eval_only else args.epochs):
        model.train()
        p = args.p0 * (args.p1 / args.p0) ** (ep / max(args.epochs - 1, 1))
        q = sched_prob(ep, args.mk_sched)
        if q > 0 and mk_pool is None:
            mk_pool = get_context("fork").Pool(max(1, args.limit_workers))
        perm = np.random.permutation(len(Xtr))
        t0 = time.time(); tot = np.zeros(8); nb = 0; iters = 0; n_img = 0
        sched_tot = dict(n_pred=0, n_gt=0, one=0, zero=0, multi=0, n_mk=0, bg_mk=0, unreach=0, px=0); t_mk = 0.0
        for i in range(0, len(perm), args.batch):
            idx = perm[i:i + args.batch]
            img = torch.from_numpy(Xtr[idx]).to(device).float() / 255
            y = torch.cat([torch.from_numpy(Ytr[idx]).to(device)[:, None],
                           torch.from_numpy(Itr[idx].astype(np.float32)).to(device)[:, None],
                           torch.from_numpy(Ttr[idx]).to(device)[:, None].float()], 1)
            img, y = augment(img, y, d["aug"])
            ybin, inst, touch = y[:, :1], y[:, 1:2].long(), y[:, 2:3]
            out = model(img)
            r = int(np.random.choice(args.erode))
            core = eroded_markers(inst, r)
            use = np.random.rand(len(idx)) < q
            if use.any():
                t1 = time.time()
                mprob_np = torch.sigmoid(out["mlogit"]).detach().cpu().numpy()[:, 0]
                jobs = [(mprob_np[j], args.mk_head, args.mk_train_thr, args.mk_train_min_area, args.mk_train_h) for j in np.flatnonzero(use)]
                maps = iter(mk_pool.map(_marker_worker, jobs, chunksize=1))
                sysd, mst = mixed_label_systems(inst, core, [next(maps) if u else None for u in use], args.mk_unmarked)
                for k in sched_tot:
                    sched_tot[k] += mst[k]
                t_mk += time.time() - t1
            else:
                sysd = label_systems(inst, core)
            n_img += len(idx)
            st = {}
            x = layer(out["ch"], out["cv"], out["c0"], out["c1"], sysd, p, stats=st)
            w = (1 + args.w_seam * maxpool(touch, 1))[:, 0]
            l_ce = mapped_cross_entropy(x, sysd, weight=w)
            l_aux = F.binary_cross_entropy_with_logits(out["logit"], ybin)
            l_mk = marker_loss(out["mlogit"], inst, core, args)
            l_edge = edge_loss(*pixel_edge_probs(out["eprob"]), inst.float(), args) if args.w_edge > 0 else torch.zeros((), device=device)
            mprob = torch.sigmoid(out["mlogit"]); dt = dist_target(inst, args.mk_rmax) if args.mk_head == "dist" else None
            l_peak = peak_loss(mprob, inst, dt, args.peak_pool) if args.w_peak > 0 else torch.zeros((), device=device)
            l_neg = neg_loss(mprob, inst, args.neg_k, args.peak_pool) if args.w_neg > 0 else torch.zeros((), device=device)
            l_grad = grad_loss(mprob, dt if dt is not None else core.float()) if args.w_grad > 0 else torch.zeros((), device=device)
            loss = (l_ce + args.aux * l_aux + args.w_mk * l_mk + args.w_edge * l_edge + args.w_peak * l_peak
                    + args.w_neg * l_neg + args.w_grad * l_grad)
            opt.zero_grad(); loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            opt.step()
            tot += np.array([loss.item(), l_ce.item(), l_aux.item(), l_mk.item(), l_edge.item(), l_peak.item(), l_neg.item(), l_grad.item()]); nb += 1; iters += st.get("last_iters", 0)
        sched.step()
        tot /= nb
        entry = dict(epoch=ep, p=p, loss=tot[0], loss_ce=tot[1], loss_aux=tot[2], loss_mk=tot[3], loss_edge=tot[4], loss_peak=tot[5],
                     loss_neg=tot[6], loss_grad=tot[7], time=time.time() - t0, iters=iters / nb, edge_scale=float(model.edge_scale()))
        msg = (f"  ep {ep} p={p:.1f} loss={tot[0]:.4f} (ce {tot[1]:.4f} aux {tot[2]:.4f} mk {tot[3]:.4f} edge {tot[4]:.4f} peak {tot[5]:.4f} neg {tot[6]:.4f} grad {tot[7]:.4f}) "
               f"iters {iters / nb:.0f} scale {entry['edge_scale']:.2f} [{entry['time']:.0f}s]")
        if args.mk_sched is not None:
            entry.update(sched_q=q, sched_pred_frac=sched_tot["n_pred"] / max(n_img, 1), sched_marker_s=t_mk)
            if sched_tot["n_pred"]:
                ngt = max(sched_tot["n_gt"], 1)
                entry.update(train_mk_one=sched_tot["one"] / ngt, train_mk_zero=sched_tot["zero"] / ngt, train_mk_multi=sched_tot["multi"] / ngt,
                             train_mk_bg=sched_tot["bg_mk"] / sched_tot["n_pred"], train_mk_per_image=sched_tot["n_mk"] / sched_tot["n_pred"],
                             train_unreach=sched_tot["unreach"] / max(sched_tot["px"], 1))
                msg += (f" | pred markers q={q:.2f} on {100 * entry['sched_pred_frac']:.0f} % of images ({t_mk:.0f}s): one={entry['train_mk_one']:.2f} "
                        f"zero={entry['train_mk_zero']:.2f} multi={entry['train_mk_multi']:.2f} bg={entry['train_mk_bg']:.1f} unreachable px {100 * entry['train_unreach']:.1f} %")
            else:
                msg += f" | pred markers q={q:.2f}"
        if ep % args.val_every == args.val_every - 1 or ep == args.epochs - 1:
            summ, _, _ = evaluate(model, val, p, device, args, quick=True)
            entry["val"] = {k: {m: summ[k][m] for m in ("iou", "bf2", "f1_05", "pq", "count_err")} for k in ("logits", "layer")}
            entry["val"]["markers"] = {m: summ["markers"][m] for m in ("frac_one", "frac_zero", "frac_multi", "bg_per_patch")}
            msg += " | " + " ".join(f"{k}: iou={v['iou']:.3f} f1={v['f1_05']:.3f} pq={v['pq']:.3f}" for k, v in entry["val"].items() if k != "markers")
            msg += f" | markers one={summ['markers']['frac_one']:.2f} zero={summ['markers']['frac_zero']:.2f} multi={summ['markers']['frac_multi']:.2f}"
        print(msg, flush=True)
        log.append(entry)
        tb_log(tb, entry, ep)
    if tb is not None:
        tb.close()
    if mk_pool is not None:
        mk_pool.close()
    if not args.eval_only:
        torch.save(model.state_dict(), os.path.join(args.outdir, f"{name}.pt"))
        with open(os.path.join(args.outdir, f"{name}.json"), "w") as f:      # args + log now; the test results replace it below
            json.dump(dict(args=vars(args), log=log), f, indent=1, default=float)

    mk_tune = None
    if args.tune_fold:
        chosen, mk_tune = tune_markers(model, args, device, args.p1)
        for k, v in chosen.items():
            setattr(args, k, v)
    t0 = time.time()
    summ, examples, per_image = evaluate(model, d, args.p1, device, args, limit_idx=limit_idx, example_idx=example_idx)
    summ["_eval_seconds"] = time.time() - t0
    summ["_edge_scale"] = float(model.edge_scale())
    print("TEST", json.dumps({k: ({m: v for m, v in s.items() if m != "per_type"} if isinstance(s, dict) else s)
                              for k, s in summ.items()}, indent=1, default=float), flush=True)
    with open(os.path.join(args.outdir, f"{name}.json"), "w") as f:
        json.dump(dict(args=vars(args), log=log, test=summ, limit_idx=[int(i) for i in limit_idx], mk_tune=mk_tune), f, indent=1, default=float)
    mq = per_image.pop("markers")
    flat = flatten_per_image(per_image, d.get("types_test"))
    for k in mq[0]:
        flat[f"markers__{k}"] = np.array([r[k] for r in mq])
    np.savez_compressed(os.path.join(args.outdir, f"{name}_perimage.npz"), **flat)
    np.savez_compressed(os.path.join(args.outdir, f"{name}_examples.npz"),
                        **{f"{i}__{k}": np.asarray(v) for i, e in enumerate(examples) for k, v in e.items()})
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
