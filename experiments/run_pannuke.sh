#!/bin/bash
# Train the three variants on PanNuke (fold 1 -> fold 2), sequentially.  Launch with
#   setsid nohup ./run_pannuke.sh > run_pannuke.log 2>&1 < /dev/null &
set -e
cd "$(dirname "$0")"
source .venv/bin/activate
export TORCH_DISABLE_NATIVE_JIT=1
EPOCHS=${EPOCHS:-30}
OUT=${OUT:-results_pannuke}
for v in unet rw_img rw_learned; do
  [ -f $OUT/$v.json ] && { echo "skip $v (done)"; continue; }
  python exp_unet_seg.py --dataset pannuke --variant $v --epochs $EPOCHS --outdir $OUT "$@"
done
echo ALL DONE
