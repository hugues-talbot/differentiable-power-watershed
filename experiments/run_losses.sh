#!/bin/bash
# Boundary / instance losses: plain U-Net vs rw_learned, same loss on both.  Launch with
#   LOSS=boundary setsid nohup ./run_losses.sh > run_losses_boundary.log 2>&1 < /dev/null &
#   LOSS=instance setsid nohup ./run_losses.sh > run_losses_instance.log 2>&1 < /dev/null &
#   DATASET=pets RES=128 LOSS=boundary setsid nohup ./run_losses.sh > run_losses_pets.log 2>&1 < /dev/null &
set -e
cd "$(dirname "$0")"
source .venv/bin/activate
export TORCH_DISABLE_NATIVE_JIT=1
DATASET=${DATASET:-pannuke}
LOSS=${LOSS:-boundary}
EPOCHS=${EPOCHS:-30}
RES=${RES:-256}
OUT=${OUT:-results_${DATASET}_losses/$LOSS}
for v in unet rw_learned; do
  [ -f $OUT/$v.json ] && { echo "skip $v (done)"; continue; }
  python exp_unet_seg.py --dataset $DATASET --res $RES --loss $LOSS --variant $v --epochs $EPOCHS --outdir $OUT "$@"
done
echo ALL DONE
