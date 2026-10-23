#!/bin/bash
# Train the three variants on Oxford-IIIT Pet, sequentially.  Launch with
#   setsid nohup ./run_pets.sh > run_pets.log 2>&1 < /dev/null &
set -e
cd "$(dirname "$0")"
source .venv/bin/activate
export TORCH_DISABLE_NATIVE_JIT=1
EPOCHS=${EPOCHS:-15}
for v in unet rw_img rw_learned; do
  [ -f results_pets/$v.json ] && { echo "skip $v (done)"; continue; }
  python exp_unet_pets.py --variant $v --epochs $EPOCHS --outdir results_pets
done
echo ALL DONE
