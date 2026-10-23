#!/bin/bash
# Cost-transform comparison (sq vs abs vs dense rank) on a few 512^2 cases.
# Waits for run_jacobian.sh to finish first.  Launch with
#   setsid nohup ./run_transforms.sh > run_transforms.log 2>&1 < /dev/null &
set -e
cd "$(dirname "$0")"
source .venv/bin/activate
export TORCH_DISABLE_NATIVE_JIT=1
until grep -q "ALL DONE" run.log; do sleep 60; done
CASES=s0.05_r5,s0.1_r5,s0.05_scribble,camera512_r5
rm -f results/conditioning_512_abs.jsonl results/conditioning_512_rank.jsonl
PS=1,2,5,10,20,50,100,200,500,1000
python pw_conditioning.py --res 512 --cases $CASES --ps $PS --cost-transform abs  --outdir results
python pw_conditioning.py --res 512 --cases $CASES --ps $PS --cost-transform rank --outdir results
python - <<'PY'
import json
want = ("s0.05_r5", "s0.1_r5", "s0.05_scribble", "camera512_r5")
with open("results/conditioning_512_sq_subset.jsonl", "w") as out:
    for l in open("results/conditioning_512.jsonl"):
        if any(w in json.loads(l)["case"] for w in want):
            out.write(l)
PY
python plot_results.py results/conditioning_512_sq_subset.jsonl results/conditioning_512_abs.jsonl results/conditioning_512_rank.jsonl --outdir figures_transforms
echo ALL DONE
