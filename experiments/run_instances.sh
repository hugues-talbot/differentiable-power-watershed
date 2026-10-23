#!/bin/bash
# Section 11: the instances are the labels.  Multi-marker RW/PW layer on PanNuke, fold 1 -> fold 2,
# p 5 -> 20, edge target on the cost head, markers from a marker head.  Launch with
#   setsid nohup ./run_instances.sh > run_instances.log 2>&1 < /dev/null &
set -e
cd "$(dirname "$0")"
source .venv/bin/activate
export TORCH_DISABLE_NATIVE_JIT=1
EPOCHS=${EPOCHS:-30}
OUT=${OUT:-results_pannuke_instances}
if [ ! -f $OUT/instances.json ]; then
  python exp_instance_pannuke.py --epochs $EPOCHS --outdir $OUT
fi
echo ALL DONE
