"""Write image + seed PGMs of three 512^2 cases for the released executable (built on jacobian), and the
wrapper's released-mode outputs on the Mac for comparison."""
import os, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pwref_compare import load_pw, make_multi_cases, write_pgm
pc, _ = load_pw(os.environ.get("ELLZERO", "../../.."))
rng = np.random.default_rng(0)
for c in pc.make_cases(512, ["camera512_r5", "synth512_s0.1_r30"], rng):
    s8 = np.full(c["img8"].shape, 128, np.uint8); s8[c["seed_mask"] & (c["seed_val"] > 0.5)] = 255; s8[c["seed_mask"] & (c["seed_val"] < 0.5)] = 0
    write_pgm(f"pgm_cases/{c['name']}.pgm", c["img8"]); write_pgm(f"pgm_cases/{c['name']}_seeds.pgm", s8)
    subprocess.run(["./pwref_wrap", f"pgm_cases/{c['name']}.pgm", f"pgm_cases/{c['name']}_seeds.pgm", "prog", f"pgm_cases/mac_{c['name']}", "two", "stoch"], check=True)
rng = np.random.default_rng(0)
for name, img8, lab in make_multi_cases(pc, 512, rng):
    if "astronaut" not in name:
        continue
    labs = np.unique(lab[lab > 0]); remap = np.zeros(lab.max() + 1, int); remap[labs] = np.arange(1, labs.size + 1); lab = remap[lab]
    write_pgm(f"pgm_cases/{name}.pgm", img8); write_pgm(f"pgm_cases/{name}_seeds.pgm", lab.astype(np.uint8))
    subprocess.run(["./pwref_wrap", f"pgm_cases/{name}.pgm", f"pgm_cases/{name}_seeds.pgm", "prog", f"pgm_cases/mac_{name}", "multi", "stoch"], check=True)
