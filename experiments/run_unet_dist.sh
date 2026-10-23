#!/bin/bash
# Section 11.2: the fair baseline for the distance-head layer of section 11.1.  A plain U-Net with
# the foreground logit, the contour head (section 10's edge target) and the distance head of
# exp_instance_pannuke.py --mk-head dist, no layer; HoVer-Net-style post-processing (h-maxima
# markers of the distance map, marker watershed of the contour / negative distance map inside the
# foreground) chosen by PQ on 300 patches of fold 3; the 2 x 2 of markers x assignment against the
# section 11.1 layer (results_pannuke_instances/dist); unet_dist_ext re-tunes the saved model on an extended
# threshold grid (the first choice sat at the grid edge), eval only.  Launch with
#   setsid nohup ./run_unet_dist.sh > run_unet_dist.log 2>&1 < /dev/null &
set -e
cd "$(dirname "$0")"
source .venv/bin/activate
export TORCH_DISABLE_NATIVE_JIT=1
EPOCHS=${EPOCHS:-30}
BASE=${BASE:-results_pannuke_instances}
RUNS=${RUNS:-"unet_dist"}
for r in $RUNS; do
  OUT=$BASE/$r
  if [ -f $OUT/unet_dist.json ]; then echo "$r done already"; continue; fi
  mkdir -p $OUT
  case $r in
    unet_dist)     python exp_unet_dist.py --epochs $EPOCHS --tune-fold 3 --layer-dir $BASE/dist --outdir $OUT 2>&1 | tee $OUT/run.log ;;
    unet_dist_gap) python exp_unet_dist.py --epochs $EPOCHS --gap --tune-fold 3 --layer-dir $BASE/dist --outdir $OUT 2>&1 | tee $OUT/run.log ;;
    unet_dist_ext) python exp_unet_dist.py --eval-only --load $BASE/unet_dist/unet_dist.pt --tune-fold 3 --tune-thr 0.4 0.5 0.6 0.7 \
                     --tune-min-area 4 9 16 --tune-h 0.2 0.3 --outdir $OUT 2>&1 | tee $OUT/run.log ;;
    *) echo "unknown run $r"; exit 1 ;;
  esac
  python plot_unet_dist.py --res $OUT --unet results_pannuke --ue results_pannuke_leads/unet_edge --dist $BASE/dist --bce $BASE/bce_tuned > $OUT/plot.log 2>&1 || echo "plot failed for $r"
done
echo ALL DONE
