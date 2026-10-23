#!/usr/bin/env python3
"""
One-time conversion of the raw PanNuke folds (float64 .npy, 4 + 8 GB per fold) to a
compact per-fold .npz:

    images   (N,256,256,3) uint8
    inst     (N,256,256)   int16   instance ids, 0 = background, relabelled 1..n per image
                                   (max over the five nucleus channels, which never overlap)
    nuc_type (N,256,256)   uint8   nucleus type per pixel: 0 background, 1..5 = channel + 1
    binary   (N,256,256)   bool    any nucleus
    touch    (N,256,256)   bool    pixels with a 4-neighbour belonging to a different nucleus
                                   (the interfaces between touching nuclei)
    types    (N,)          str     tissue type per patch

The raw arrays are memory-mapped and processed in chunks; the raw data is never
written to.

usage: convert_pannuke.py --raw /path/PanNuke_raw --out data --folds 1 2 3
"""
import argparse, os, time
import numpy as np


def relabel_chunk(m):
    """m (n,H,W,6) float -> inst int16, nuc_type uint8, touch bool."""
    nuc = m[..., :5]
    present = nuc > 0
    ntype = (present.argmax(-1) + 1).astype(np.uint8) * present.any(-1)
    # unique ids across channels: offset channel c by the running max of channels < c
    ids = nuc.astype(np.int64)
    offs = np.zeros(5, np.int64)
    for c in range(1, 5):
        offs[c] = offs[c - 1] + int(ids[..., c - 1].max())
    comb = (ids + offs * present).max(-1)                     # one id per pixel (channels never overlap)
    inst = np.zeros(comb.shape, np.int16)
    for i in range(comb.shape[0]):
        u, inv = np.unique(comb[i], return_inverse=True)      # u[0] == 0 if any background
        lab = inv.reshape(comb.shape[1:])
        if u[0] != 0:
            lab = lab + 1
        assert lab.max() < 32767
        inst[i] = lab
    touch = np.zeros(inst.shape, bool)
    a, b = inst[:, :, 1:], inst[:, :, :-1]
    d = (a != b) & (a > 0) & (b > 0)
    touch[:, :, 1:] |= d; touch[:, :, :-1] |= d
    a, b = inst[:, 1:, :], inst[:, :-1, :]
    d = (a != b) & (a > 0) & (b > 0)
    touch[:, 1:, :] |= d; touch[:, :-1, :] |= d
    return inst, ntype, touch


def convert(raw, out, k, chunk=128):
    im = np.load(f"{raw}/Fold{k}/images/fold{k}/images.npy", mmap_mode="r")
    ms = np.load(f"{raw}/Fold{k}/masks/fold{k}/masks.npy", mmap_mode="r")
    types = np.load(f"{raw}/Fold{k}/images/fold{k}/types.npy", allow_pickle=True).astype(str)
    N = im.shape[0]
    assert ms.shape[0] == N == len(types)
    images = np.zeros(im.shape, np.uint8)
    inst = np.zeros(ms.shape[:3], np.int16)
    ntype = np.zeros(ms.shape[:3], np.uint8)
    touch = np.zeros(ms.shape[:3], bool)
    t0 = time.time()
    for s in range(0, N, chunk):
        e = min(s + chunk, N)
        images[s:e] = np.clip(np.rint(np.asarray(im[s:e])), 0, 255).astype(np.uint8)
        inst[s:e], ntype[s:e], touch[s:e] = relabel_chunk(np.asarray(ms[s:e]))
        print(f"  fold {k}: {e}/{N}  {time.time() - t0:.0f}s", flush=True)
    binary = inst > 0
    ninst = np.array([int(x.max()) for x in inst])
    print(f"fold {k}: {N} patches, nuclei/patch mean {ninst.mean():.1f} max {ninst.max()}, "
          f"nucleus pixels {binary.mean():.3f}, touching-interface pixels {touch.mean():.4f}", flush=True)
    path = os.path.join(out, f"pannuke_fold{k}.npz")
    np.savez(path, images=images, inst=inst, nuc_type=ntype, binary=binary, touch=touch, types=types)
    print(f"wrote {path} ({os.path.getsize(path) / 1e9:.2f} GB)", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="/atlantic/AIpool/home/galia/data/PanNuke_raw")
    ap.add_argument("--out", default="data")
    ap.add_argument("--folds", type=int, nargs="+", default=[1, 2, 3])
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for k in a.folds:
        convert(a.raw, a.out, k)
