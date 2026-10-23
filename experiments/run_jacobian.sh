#!/bin/bash
# Full conditioning study on jacobian (RTX 6000 Ada). Launch with
#   setsid nohup ./run_jacobian.sh > run.log 2>&1 < /dev/null &
set -e
cd "$(dirname "$0")"
source .venv/bin/activate
export TORCH_DISABLE_NATIVE_JIT=1
rm -f results/conditioning_512.jsonl results/conditioning_1024.jsonl
python pw_conditioning.py --res 512 --outdir results
python pw_conditioning.py --res 1024 --cases s0.05_r5,s0.05_r30,s0.1_r5 --ps 1,2,5,10,20,50,100,200,500,1000 --outdir results
python plot_results.py results/conditioning_512.jsonl --outdir figures512
python plot_results.py results/conditioning_1024.jsonl --outdir figures1024
echo ALL DONE
