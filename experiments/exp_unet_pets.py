#!/usr/bin/env python3
"""
Experiment 2 (trained end to end): a U-Net with the RW/PW layer as its last layer,
on Oxford-IIIT Pet (binary pet / background from the trimap), 128 x 128.

Variants
  unet        plain U-Net, BCE on the logits
  rw_img      U-Net logits -> unary costs (-log s, -log(1-s)); edge costs from the
              image gradient; RW layer (K unrolled Jacobi-PCG steps, fp32) with p
              annealed upward; BCE on the layer output (+ 0.5 BCE on the logits)
  rw_learned  as rw_img, but the edge costs come from a second U-Net head

Evaluation on the test split: IoU, boundary F-score at 1 and 2 px, accuracy in a
3-px band around the true boundary, softness (fraction of pixels in (0.1,0.9)).
For the RW variants the output is evaluated three ways: the K-step layer as
trained, the converged solve at the final p, and the exact PW limit (p = inf) on a
subset of test images.

usage: exp_unet_pets.py --variant rw_learned --epochs 15 --outdir results_pets
"""
import argparse, json, os, time
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy import ndimage
from pw_layer import RWLayer, unary_costs_from_prob, pw_limit_numpy, boundary_fscore, iou, softness


# ----------------------------------------------------------------------------
# data
# ----------------------------------------------------------------------------
def prepare(root, res, cache):
    if os.path.exists(cache):
        d = np.load(cache)
        return {k: d[k] for k in d.files}
    import torchvision
    from PIL import Image
    out = {}
    for split in ("trainval", "test"):
        ds = torchvision.datasets.OxfordIIITPet(root, split=split, target_types="segmentation", download=False)
        X = np.zeros((len(ds), 3, res, res), np.uint8); Y = np.zeros((len(ds), res, res), np.uint8)
        for i in range(len(ds)):
            im, tm = ds[i]
            X[i] = np.asarray(im.convert("RGB").resize((res, res), Image.BILINEAR)).transpose(2, 0, 1)
            Y[i] = np.asarray(tm.resize((res, res), Image.NEAREST))
            if i % 500 == 0:
                print(f"  {split} {i}/{len(ds)}", flush=True)
        out[f"X_{split}"], out[f"Y_{split}"] = X, Y
    np.savez_compressed(cache, **out)
    return out


def to_target(Y):
    """trimap: 1 pet, 2 background, 3 border (counted as pet)."""
    return (Y != 2).astype(np.float32)


def image_edge_costs(x):
    """x (B,3,H,W) in [0,1] -> squared colour-difference costs on edges, in [0,1]."""
    ch = ((x[:, :, :, 1:] - x[:, :, :, :-1]) ** 2).mean(1, keepdim=True)
    cv = ((x[:, :, 1:, :] - x[:, :, :-1, :]) ** 2).mean(1, keepdim=True)
    return ch, cv


# ----------------------------------------------------------------------------
# model
# ----------------------------------------------------------------------------
def block(i, o):
    return nn.Sequential(nn.Conv2d(i, o, 3, padding=1), nn.BatchNorm2d(o), nn.ReLU(inplace=True),
                         nn.Conv2d(o, o, 3, padding=1), nn.BatchNorm2d(o), nn.ReLU(inplace=True))


class UNet(nn.Module):
    def __init__(self, out_ch, ch=(32, 64, 128, 256)):
        super().__init__()
        self.enc = nn.ModuleList([block(3 if i == 0 else ch[i - 1], ch[i]) for i in range(len(ch))])
        self.up = nn.ModuleList([nn.ConvTranspose2d(ch[i], ch[i - 1], 2, stride=2) for i in range(len(ch) - 1, 0, -1)])
        self.dec = nn.ModuleList([block(2 * ch[i - 1], ch[i - 1]) for i in range(len(ch) - 1, 0, -1)])
        self.head = nn.Conv2d(ch[0], out_ch, 1)

    def forward(self, x):
        skips = []
        for i, e in enumerate(self.enc):
            x = e(x)
            if i < len(self.enc) - 1:
                skips.append(x); x = F.max_pool2d(x, 2)
        for up, dec in zip(self.up, self.dec):
            x = dec(torch.cat([up(x), skips.pop()], 1))
        return self.head(x)


class Segmenter(nn.Module):
    def __init__(self, variant, K, cmax):
        super().__init__()
        self.variant, self.cmax = variant, cmax
        self.unet = UNet(1 if variant != "rw_learned" else 3)
        self.layer = RWLayer("unrolled", K=K)

    def costs(self, img, out):
        logit = out[:, :1]
        s = torch.sigmoid(logit)
        c1, c0 = unary_costs_from_prob(s, cmax=self.cmax)
        if self.variant == "rw_learned":
            e = torch.sigmoid(out[:, 1:3])                      # learned edge costs in [0,1]
            ch = 0.5 * (e[:, :1, :, 1:] + e[:, :1, :, :-1])
            cv = 0.5 * (e[:, 1:2, 1:, :] + e[:, 1:2, :-1, :])
        else:
            ch, cv = image_edge_costs(img)
        return logit, ch, cv, c1, c0

    def forward(self, img, p, layer=None):
        out = self.unet(img)
        if self.variant == "unet":
            return out[:, :1], None, None
        logit, ch, cv, c1, c0 = self.costs(img, out)
        x = (layer or self.layer)(ch, cv, c1, c0, p)
        return logit, x, (ch, cv, c1, c0)


def bce_prob(x, y, eps=1e-6):
    x = x.clamp(eps, 1 - eps)
    return -(y * torch.log(x) + (1 - y) * torch.log(1 - x)).mean()


# ----------------------------------------------------------------------------
# evaluation
# ----------------------------------------------------------------------------
def eval_metrics(prob, y, band_px=3):
    pred = prob > 0.5; gt = y > 0.5
    contour = gt ^ ndimage.binary_erosion(gt, border_value=0)
    band = ndimage.binary_dilation(contour, iterations=band_px)
    frac, ent = softness(prob)
    return dict(iou=float(iou(pred, gt)), bf1=float(boundary_fscore(pred, gt, 1)),
                bf2=float(boundary_fscore(pred, gt, 2)),
                band_acc=float((pred[band] == gt[band]).mean()) if band.any() else 1.0,
                soft_frac=frac, entropy=ent)


def evaluate(model, X, Y, p, device, args, limit_n=0):
    model.eval()
    res = {"layer": [], "converged": [], "limit": [], "logits": []}
    conv_layer = RWLayer("implicit", tol=1e-5, maxit=1000)
    examples = []
    with torch.no_grad():
        for i in range(0, len(X), args.batch):
            img = torch.from_numpy(X[i:i + args.batch]).to(device).float() / 255
            y = to_target(Y[i:i + args.batch])
            logit, x, costs = model(img, p)
            s = torch.sigmoid(logit).cpu().numpy()[:, 0]
            for j in range(len(y)):
                res["logits"].append(eval_metrics(s[j], y[j]))
            if x is not None:
                xk = x.cpu().numpy()[:, 0]
                xc = conv_layer(*costs, float(p)).cpu().numpy()[:, 0]
                for j in range(len(y)):
                    res["layer"].append(eval_metrics(xk[j], y[j]))
                    res["converged"].append(eval_metrics(xc[j], y[j]))
                    if i + j < limit_n:
                        ch, cv, c1, c0 = (c[j, 0].double().cpu().numpy() for c in costs)
                        xinf, _ = pw_limit_numpy(ch, cv, c1, c0)
                        res["limit"].append(eval_metrics(xinf, y[j]))
                        if len(examples) < 6:
                            examples.append(dict(img=X[i + j], y=y[j], s=s[j], xk=xk[j], xc=xc[j], xinf=xinf,
                                                 ch=ch, cv=cv))
            elif len(examples) < 6:
                for j in range(min(6 - len(examples), len(y))):
                    examples.append(dict(img=X[i + j], y=y[j], s=s[j]))
    summary = {k: {m: float(np.mean([r[m] for r in v])) for m in v[0]} for k, v in res.items() if v}
    for k in summary:
        summary[k]["n"] = len(res[k])
    return summary, examples


# ----------------------------------------------------------------------------
# training
# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", choices=("unet", "rw_img", "rw_learned"), required=True)
    ap.add_argument("--epochs", type=int, default=15)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--res", type=int, default=128)
    ap.add_argument("--K", type=int, default=20)
    ap.add_argument("--p0", type=float, default=5.0)
    ap.add_argument("--p1", type=float, default=50.0)
    ap.add_argument("--cmax", type=float, default=8.0)
    ap.add_argument("--aux", type=float, default=0.5, help="weight of the BCE on the logits for RW variants")
    ap.add_argument("--limit-n", type=int, default=300, help="test images on which the exact PW limit is evaluated")
    ap.add_argument("--data", default="data")
    ap.add_argument("--outdir", default="results_pets")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    os.makedirs(args.outdir, exist_ok=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    d = prepare(args.data, args.res, os.path.join(args.data, f"pets{args.res}.npz"))
    Xtr, Ytr, Xte, Yte = d["X_trainval"], d["Y_trainval"], d["X_test"], d["Y_test"]
    print(f"{args.variant}: train {len(Xtr)} test {len(Xte)} device {device}", flush=True)

    model = Segmenter(args.variant, args.K, args.cmax).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, args.epochs)
    log = []
    for ep in range(args.epochs):
        model.train()
        p = args.p0 * (args.p1 / args.p0) ** (ep / max(args.epochs - 1, 1))
        perm = np.random.permutation(len(Xtr))
        t0 = time.time(); tot = 0.0; nb = 0; gcost = 0.0
        for i in range(0, len(perm), args.batch):
            idx = perm[i:i + args.batch]
            img = torch.from_numpy(Xtr[idx]).to(device).float() / 255
            y = torch.from_numpy(to_target(Ytr[idx])).to(device)[:, None]
            if np.random.rand() < 0.5:                       # horizontal flip
                img, y = img.flip(3), y.flip(3)
            logit, x, costs = model(img, p)
            if x is None:
                loss = F.binary_cross_entropy_with_logits(logit, y)
            else:
                loss = bce_prob(x, y) + args.aux * F.binary_cross_entropy_with_logits(logit, y)
            opt.zero_grad(); loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            opt.step()
            tot += loss.item(); nb += 1
        sched.step()
        entry = dict(epoch=ep, p=p, loss=tot / nb, time=time.time() - t0)
        if ep % 5 == 4 or ep == args.epochs - 1:
            summ, _ = evaluate(model, Xte[:400], Yte[:400], p, device, args, limit_n=0)
            entry["val"] = summ
            print(f"  ep {ep} p={p:.1f} loss={tot / nb:.4f} " +
                  " ".join(f"{k}: iou={v['iou']:.3f} bf2={v['bf2']:.3f} soft={v['soft_frac']:.3f}" for k, v in summ.items()),
                  flush=True)
        else:
            print(f"  ep {ep} p={p:.1f} loss={tot / nb:.4f} [{entry['time']:.0f}s]", flush=True)
        log.append(entry)

    summ, examples = evaluate(model, Xte, Yte, args.p1, device, args, limit_n=args.limit_n)
    print("TEST", json.dumps(summ, indent=1), flush=True)
    with open(os.path.join(args.outdir, f"{args.variant}.json"), "w") as f:
        json.dump(dict(args=vars(args), log=log, test=summ), f, indent=1)
    np.savez_compressed(os.path.join(args.outdir, f"{args.variant}_examples.npz"),
                        **{f"{i}__{k}": v for i, e in enumerate(examples) for k, v in e.items()})
    torch.save(model.state_dict(), os.path.join(args.outdir, f"{args.variant}.pt"))


if __name__ == "__main__":
    main()
