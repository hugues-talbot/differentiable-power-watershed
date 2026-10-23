#!/bin/bash
# Section 11.1: better markers for the multi-marker layer.  Three runs, same recipe as section 11
# (p 5 -> 20, erosion 2-3 px, edge target, 30 epochs, fold 1 -> fold 2):
#   dist      HoVer-Net-style marker head (normalised distance transform, h-maxima markers), marker
#             threshold / min area / prominence chosen by PQ on 300 patches of fold 3;
#   maxit300  section 11's BCE marker head with the training PCG cap raised 100 -> 300;
#   bce_tuned section 11's trained model re-evaluated with its marker threshold / min area chosen on fold 3
#             (eval only, needs results_pannuke_instances/instances.pt).
# Launch with   RUNS="dist maxit300" setsid nohup ./run_instances_11_1.sh > run_instances_11_1.log 2>&1 < /dev/null &
set -e
cd "$(dirname "$0")"
source .venv/bin/activate
export TORCH_DISABLE_NATIVE_JIT=1
EPOCHS=${EPOCHS:-30}
BASE=${BASE:-results_pannuke_instances}
RUNS=${RUNS:-"dist maxit300 bce_tuned"}
for r in $RUNS; do
  OUT=$BASE/$r
  if [ -f $OUT/instances.json ]; then echo "$r done already"; continue; fi
  mkdir -p $OUT
  case $r in
    dist)      python exp_instance_pannuke.py --epochs $EPOCHS --mk-head dist --w-mk 2 --tune-fold 3 --outdir $OUT ;;
    dist_maxit300) python exp_instance_pannuke.py --epochs $EPOCHS --mk-head dist --w-mk 2 --tune-fold 3 --maxit 300 --outdir $OUT ;;
    maxit300)  python exp_instance_pannuke.py --epochs $EPOCHS --maxit 300 --outdir $OUT ;;
    bce_tuned) python exp_instance_pannuke.py --eval-only --load $BASE/instances.pt --tune-fold 3 --outdir $OUT ;;
    *) echo "unknown run $r"; exit 1 ;;
  esac
  python plot_instances.py --res $OUT --ref $BASE > $OUT/plot.log 2>&1 || echo "plot failed for $r"
done
echo ALL DONE
