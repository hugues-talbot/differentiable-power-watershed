#!/bin/bash
# Gap target (touching-interface pixels = background) on PanNuke: plain U-Net vs the
# learned-cost layer at the section-6 p schedule (5 -> 50), at lower p (5 -> 20, 2 -> 10)
# and with a sharper edge-cost parametrisation (8 * sigmoid, learnable scale).  Launch with
#   setsid nohup ./run_gap.sh > run_gap.log 2>&1 < /dev/null &
set -e
cd "$(dirname "$0")"
source .venv/bin/activate
export TORCH_DISABLE_NATIVE_JIT=1
EPOCHS=${EPOCHS:-30}
OUT=${OUT:-results_pannuke_gap}
run() {  # tag variant args...
  local tag=$1 v=$2; shift 2
  [ -f $OUT/${v}_$tag.json ] && { echo "skip ${v}_$tag (done)"; return; }
  python exp_unet_seg.py --dataset pannuke --gap --variant $v --tag $tag --epochs $EPOCHS --outdir $OUT "$@"
}
run gap            unet
run gap_p50        rw_learned
run gap_p20        rw_learned --p0 5 --p1 20
run gap_p10_sharp  rw_learned --p0 2 --p1 10 --edge-param scaled --edge-cmax 8 --edge-learn-scale
run gap_p20_sharp  rw_learned --p0 5 --p1 20 --edge-param scaled --edge-cmax 8 --edge-learn-scale
echo ALL DONE
