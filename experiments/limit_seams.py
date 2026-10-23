#!/usr/bin/env python3
"""Seam statistics (seam_stats.py) of the exact PW limit, on the limit patches of a
trained rw_learned run, with the layer and converged outputs on the same patches for
comparison.  Writes <dir>/limit_seams.json.

usage: limit_seams.py results_pannuke_leads/edge_bce [more dirs...]
"""
import argparse, json, os
from multiprocessing import get_context
import numpy as np
import torch
from exp_unet_seg import SegmenterX, load_dataset
from pw_layer import RWLayer, pw_limit_numpy
from seam_stats import seam_cut


def _worker(job):
    g, ch, cv, c1, c0 = job
    return g, pw_limit_numpy(ch, cv, c1, c0)[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--name", default="rw_learned")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    d = None
    for dd in args.dirs:
        r = json.load(open(os.path.join(dd, args.name + ".json")))
        a = argparse.Namespace(**r["args"])
        if d is None:
            d = load_dataset(a)
        idx = sorted(r["limit_idx"])
        model = SegmenterX(a.variant, a.K, a.cmax, getattr(a, "edge_param", "sigmoid"), getattr(a, "edge_cmax", 8.0),
                           getattr(a, "edge_learn_scale", False)).to(device)
        model.load_state_dict(torch.load(os.path.join(dd, args.name + ".pt"), map_location=device)); model.eval()
        conv = RWLayer("implicit", tol=1e-5, maxit=1000)
        acc = {k: np.zeros(4, int) for k in ("logits", "layer", "converged", "limit")}
        jobs = []
        with torch.no_grad():
            for i in range(0, len(idx), 16):
                sel = idx[i:i + 16]
                img = torch.from_numpy(d["X_test"][sel]).to(device).float() / 255
                logit, x, costs = model(img, a.p1)
                outs = dict(logits=torch.sigmoid(logit).cpu().numpy()[:, 0], layer=x.cpu().numpy()[:, 0],
                            converged=conv(*costs, float(a.p1)).cpu().numpy()[:, 0])
                for j, g in enumerate(sel):
                    touch = d["touch_test"][g].astype(bool)
                    for k, v in outs.items():
                        acc[k] += np.array(seam_cut(v[j] > 0.5, touch))
                    jobs.append((g,) + tuple(c[j, 0].double().cpu().numpy() for c in costs))
        with get_context("fork").Pool(args.workers) as pool:
            for g, xinf in pool.imap_unordered(_worker, jobs, chunksize=2):
                acc["limit"] += np.array(seam_cut(xinf > 0.5, d["touch_test"][g].astype(bool)))
        out = {k: dict(n_patches=len(idx), touch_px=int(v[0]), touch_bg_frac=float(v[1] / max(v[0], 1)), seams=int(v[2]),
                       seams_cut_frac=float(v[3] / max(v[2], 1))) for k, v in acc.items()}
        print(dd, json.dumps({k: (round(v["touch_bg_frac"], 3), round(v["seams_cut_frac"], 3)) for k, v in out.items()}), flush=True)
        json.dump(out, open(os.path.join(dd, "limit_seams.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
