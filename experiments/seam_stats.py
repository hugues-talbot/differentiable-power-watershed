#!/usr/bin/env python3
"""Does the output cut at the interfaces between touching nuclei?  For trained
exp_unet_seg.py models: fraction of touching-interface pixels ('touch') predicted as
background by the thresholded logits / layer / converged output, over a whole test fold,
plus the fraction of true seams (connected components of 'touch') that are completely
background in the prediction.  Writes <outdir>/seam_stats.json.

usage: seam_stats.py --outdir results_pannuke_gap --runs unet_gap rw_learned_gap_p50 ...
"""
import argparse, json, os
import numpy as np
import torch
from scipy import ndimage
from exp_unet_seg import SegmenterX, load_dataset, PP_MODES, postprocess_edge, contour_map
from pw_layer import RWLayer


def seam_cut(pred, touch):
    """pred: bool (H,W) foreground; touch: bool.  Returns (#touch px, #touch px background,
    #seams, #seams fully background)."""
    lab, n = ndimage.label(touch, structure=np.ones((3, 3)))
    bg = ~pred
    full = 0
    if n:
        mn = ndimage.minimum(bg.astype(np.uint8), lab, index=np.arange(1, n + 1))
        full = int(np.sum(mn == 1))
    return int(touch.sum()), int((touch & bg).sum()), int(n), full


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default="results_pannuke_gap")
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--data", default="data")
    ap.add_argument("--batch", type=int, default=16)
    args = ap.parse_args()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    out = {}
    d = None
    for run in args.runs:
        r = json.load(open(os.path.join(args.outdir, run + ".json")))
        a = argparse.Namespace(**r["args"])
        if d is None:
            d = load_dataset(a)                                  # same test fold for every run; gap only changes Y
        model = SegmenterX(a.variant, a.K, a.cmax, getattr(a, "edge_param", "sigmoid"), getattr(a, "edge_cmax", 8.0),
                           getattr(a, "edge_learn_scale", False)).to(device)
        model.load_state_dict(torch.load(os.path.join(args.outdir, run + ".pt"), map_location=device))
        model.eval()
        conv = RWLayer("implicit", tol=1e-5, maxit=1000)
        acc = {}
        with torch.no_grad():
            for i in range(0, len(d["X_test"]), args.batch):
                img = torch.from_numpy(d["X_test"][i:i + args.batch]).to(device).float() / 255
                logit, x, costs = model(img, a.p1)
                outs = {"logits": torch.sigmoid(logit).cpu().numpy()[:, 0]}
                if a.variant == "unet_edge":                     # the post-processed outputs, as 0/1 arrays
                    c = contour_map(costs)
                    pps = [postprocess_edge(outs["logits"][j], c[j], **a.pp_md) for j in range(len(img))]
                    outs.update({m: np.stack([pp[m] for pp in pps]).astype(np.float32) for m in PP_MODES})
                if x is not None:
                    outs["layer"] = x.cpu().numpy()[:, 0]
                    outs["converged"] = conv(*costs, float(a.p1)).cpu().numpy()[:, 0]
                for j in range(len(img)):
                    touch = d["touch_test"][i + j].astype(bool)
                    for k, v in outs.items():
                        acc[k] = acc.get(k, np.zeros(4, int)) + np.array(seam_cut(v[j] > 0.5, touch))
        out[run] = {k: dict(touch_px=int(v[0]), touch_bg_frac=float(v[1] / max(v[0], 1)), seams=int(v[2]),
                            seams_cut_frac=float(v[3] / max(v[2], 1))) for k, v in acc.items()}
        print(run, json.dumps(out[run]), flush=True)
    json.dump(out, open(os.path.join(args.outdir, "seam_stats.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
