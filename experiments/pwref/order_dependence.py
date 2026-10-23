"""Does the reference's result depend on the order of the stochastic sort?  Same problem, two
seeds of rand(), modes raw (raw weights for the plateaus) and prog (released default)."""
import os, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pwref_compare import write_pgm, random_small_cases
rng = np.random.default_rng(1)
os.makedirs("tmp_order", exist_ok=True)
tot = {"raw": [0, 0], "prog": [0, 0], "geod": [0, 0]}
for name, img8, spec in random_small_cases(rng, 40):
    if spec[0] == "two":
        seeds8 = np.full(img8.shape, 128, np.uint8); seeds8[spec[1] & (spec[2] > 0.5)] = 255; seeds8[spec[1] & (spec[2] < 0.5)] = 0; labels = "two"
    else:
        seeds8 = spec[1].astype(np.uint8); labels = "multi"
    write_pgm("tmp_order/i.pgm", img8); write_pgm("tmp_order/s.pgm", seeds8)
    for mode in tot:
        masks, probas = [], []
        for seed in (1, 2, 3):
            subprocess.run(["./pwref_wrap_seed", "tmp_order/i.pgm", "tmp_order/s.pgm", mode, "tmp_order/o", labels, "stoch", str(seed)], check=True, capture_output=True)
            masks.append(np.fromfile("tmp_order/o.mask.u8", np.uint8)); probas.append(np.fromfile("tmp_order/o.proba.f32", np.float32))
        ld = max(int((masks[0] != m).sum()) for m in masks[1:]); pd = max(float(np.abs(probas[0] - p).max()) for p in probas[1:])
        tot[mode][0] += ld; tot[mode][1] = max(tot[mode][1], pd)
print("label differences between three rand() seeds, summed over 40 random 24x24 cases; max potential difference")
for mode, (ld, pd) in tot.items():
    print(f"  {mode:5s}: {ld:6d} labels, {pd:.2e}")
