#!/usr/bin/env python3
"""
Instance-level and label-free metrics for binary nucleus segmentation.

* instance_metrics(pred_bool, inst_gt): connected components of the thresholded
  prediction (4-connectivity, the adjacency of the grid graph the layer works on)
  against the ground-truth instance map: object counts, matches at IoU >= 0.5
  (tp / fp / fn, to be summed over the dataset for F1 and PQ), the summed IoU of
  the matches (for the segmentation quality), and the AJI numerator / denominator
  (Kumar et al. 2017), again to be summed over the dataset.
* edge_alignment(pred_bool, img_uint8, q=0.9, tol=1): fraction of predicted
  boundary pixels within `tol` px of a strong image edge, where strong = top
  (1-q) of the colour-gradient magnitude of the patch.  Needs no labels.
"""
import numpy as np
from scipy import ndimage

FOUR = ndimage.generate_binary_structure(2, 1)


def components(pred):
    lab, n = ndimage.label(pred, structure=FOUR)
    return lab, n


def overlap_matrix(a, na, b, nb):
    """Pixel-count overlap matrix between label maps a (ids 1..na) and b (1..nb)."""
    idx = a.astype(np.int64) * (nb + 1) + b.astype(np.int64)
    cnt = np.bincount(idx.ravel(), minlength=(na + 1) * (nb + 1)).reshape(na + 1, nb + 1)
    return cnt


def instance_metrics(pred, inst_gt, lab=None):
    """pred: bool (H,W); inst_gt: int (H,W) with 0 background.  Returns per-image
    counts to be aggregated over the dataset.  With `lab` (int (H,W), 0 background) the
    predicted instances are the labels of that map instead of the components of pred
    (multi-label outputs); its ids need not be contiguous."""
    if lab is None:
        lab, npred = components(pred)
    else:
        ids, lab = np.unique(lab, return_inverse=True)
        lab = lab.reshape(inst_gt.shape)
        if ids[0] != 0:
            lab = lab + 1
        npred = int(lab.max())
    inst_gt = inst_gt.astype(np.int64)
    ngt = int(inst_gt.max())
    out = dict(n_pred=npred, n_gt=ngt, tp=0, fp=npred, fn=ngt, iou_sum=0.0, aji_num=0.0, aji_den=0.0)
    if ngt == 0 and npred == 0:
        return out
    cnt = overlap_matrix(inst_gt, ngt, lab, npred)
    area_gt = cnt.sum(1)                                     # (ngt+1,)
    area_pred = cnt.sum(0)                                   # (npred+1,)
    inter = cnt[1:, 1:].astype(np.float64)                   # (ngt, npred)
    union = area_gt[1:, None] + area_pred[None, 1:] - inter
    iou = np.where(union > 0, inter / np.maximum(union, 1), 0.0)
    if ngt and npred:
        matched = iou >= 0.5                                 # at most one match per row and column
        tp = int(matched.sum())
        out.update(tp=tp, fp=npred - tp, fn=ngt - tp, iou_sum=float(iou[matched].sum()))
        # AJI: each GT instance takes its best-IoU prediction; unused predictions go to the denominator
        best = iou.argmax(1)
        used = np.zeros(npred, bool)
        num = den = 0.0
        for g in range(ngt):
            j = best[g]
            if iou[g, j] > 0:
                num += inter[g, j]; den += union[g, j]; used[j] = True
            else:
                den += area_gt[g + 1]
        den += area_pred[1:][~used].sum()
        out.update(aji_num=float(num), aji_den=float(den))
    else:
        out.update(aji_num=0.0, aji_den=float(area_gt[1:].sum() + area_pred[1:].sum()))
    return out


def aggregate_instance(rows):
    """Dataset-level F1 at IoU 0.5, PQ = SQ * DQ, AJI, count errors."""
    tp = sum(r["tp"] for r in rows); fp = sum(r["fp"] for r in rows); fn = sum(r["fn"] for r in rows)
    iou_sum = sum(r["iou_sum"] for r in rows)
    f1 = 2 * tp / max(2 * tp + fp + fn, 1)
    sq = iou_sum / max(tp, 1)
    pq = iou_sum / max(tp + 0.5 * fp + 0.5 * fn, 1e-9)
    aji = sum(r["aji_num"] for r in rows) / max(sum(r["aji_den"] for r in rows), 1e-9)
    npred = np.array([r["n_pred"] for r in rows], float); ngt = np.array([r["n_gt"] for r in rows], float)
    rel = np.abs(npred - ngt) / np.maximum(ngt, 1)
    return dict(f1_05=f1, pq=pq, sq=sq, dq=2 * tp / max(2 * tp + fp + fn, 1), aji=aji,
                count_err=float(rel.mean()), count_bias=float((npred - ngt).mean()),
                n_pred_mean=float(npred.mean()), n_gt_mean=float(ngt.mean()), tp=tp, fp=fp, fn=fn)


def colour_gradient(img, sigma=1.0):
    """img (H,W,3) uint8 -> gradient magnitude (L2 over channels) after Gaussian smoothing."""
    g2 = np.zeros(img.shape[:2])
    for c in range(img.shape[2]):
        f = ndimage.gaussian_filter(img[..., c].astype(np.float64), sigma)
        g2 += ndimage.sobel(f, 0) ** 2 + ndimage.sobel(f, 1) ** 2
    return np.sqrt(g2)


def strong_edges(img, q=0.9, sigma=1.0):
    g = colour_gradient(img, sigma)
    return g >= np.quantile(g, q)


def contour(m):
    return m ^ ndimage.binary_erosion(m, border_value=0)


def edge_alignment(pred, img=None, q=0.9, tol=1, strong=None):
    """Fraction of predicted boundary pixels within tol px of a strong colour edge."""
    if strong is None:
        strong = strong_edges(img, q)
    near = ndimage.binary_dilation(strong, iterations=tol) if tol > 0 else strong
    b = contour(pred)
    return float(near[b].mean()) if b.any() else float("nan")


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    inst = np.zeros((64, 64), np.int16)
    inst[5:20, 5:20] = 1; inst[30:50, 30:50] = 2; inst[5:15, 40:60] = 3
    pred = inst > 0
    pred[30:50, 30:50] = False; pred[32:48, 32:48] = True      # shrunk second object
    pred[55:60, 2:6] = True                                      # a false positive
    r = instance_metrics(pred, inst); print(r)
    print(aggregate_instance([r]))
    img = (rng.random((64, 64, 3)) * 255).astype(np.uint8); img[inst > 0] = 40
    print("edge alignment pred", edge_alignment(pred, img), "gt", edge_alignment(inst > 0, img))
