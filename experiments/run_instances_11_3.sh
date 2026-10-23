#!/bin/bash
# Sections 11.3-11.5: a per-nucleus peak loss on the distance head, seeds and fold pairs (11.3), the marker-head
# losses of 11.4, and the solve trained from the predicted markers (11.5, dist_sched10 / dist_sched20), for the layer
# (exp_instance_pannuke.py --mk-head dist, section 11.1 recipe) and its fair baseline
# (exp_unet_dist.py, section 11.2); every baseline run loads the matching layer run (--layer-dir)
# for the markers x assignment 2 x 2.  Marker post-processing of both is chosen on the tuning fold.
# Launch with   setsid nohup ./run_instances_11_3.sh > run_instances_11_3.log 2>&1 < /dev/null &
set -e
cd "$(dirname "$0")"
source .venv/bin/activate
export TORCH_DISABLE_NATIVE_JIT=1
EPOCHS=${EPOCHS:-30}
BASE=${BASE:-results_pannuke_instances}
RUNS=${RUNS:-"dist_peak unet_dist_peak dist_s1 unet_dist_s1 dist_s2 unet_dist_s2 dist_f23 unet_dist_f23 dist_f31 unet_dist_f31"}  # dist_peak (raw max) grows needle peaks: see dist_peak5
LAYER="python exp_instance_pannuke.py --epochs $EPOCHS --mk-head dist --w-mk 2 --tb"
UNET="python exp_unet_dist.py --epochs $EPOCHS --tb"
for r in $RUNS; do
  OUT=$BASE/$r
  case $r in unet_*) J=$OUT/unet_dist.json ;; *) J=$OUT/instances.json ;; esac
  if [ -f $J ]; then echo "$r done already"; continue; fi
  mkdir -p $OUT
  case $r in
    dist_peak)      $LAYER --w-peak 1 --tune-fold 3 --outdir $OUT 2>&1 | tee $OUT/run.log ;;
    unet_dist_peak) $UNET --w-peak 1 --tune-fold 3 --layer-dir $BASE/dist_peak --outdir $OUT 2>&1 | tee $OUT/run.log ;;
    dist_peak5)     $LAYER --w-peak 1 --peak-pool 5 --tune-fold 3 --outdir $OUT 2>&1 | tee $OUT/run.log ;;
    unet_dist_peak5) $UNET --w-peak 1 --peak-pool 5 --tune-fold 3 --layer-dir $BASE/dist_peak5 --outdir $OUT 2>&1 | tee $OUT/run.log ;;
    dist_grad) $LAYER --w-grad 2 --tune-fold 3 --outdir $OUT 2>&1 | tee $OUT/run.log ;;
    unet_dist_grad) $UNET --w-grad 2 --tune-fold 3 --layer-dir $BASE/dist_grad --outdir $OUT 2>&1 | tee $OUT/run.log ;;
    dist_peakneg) $LAYER --w-peak 1 --peak-pool 5 --w-neg 1 --tune-fold 3 --outdir $OUT 2>&1 | tee $OUT/run.log ;;
    unet_dist_peakneg) $UNET --w-peak 1 --peak-pool 5 --w-neg 1 --tune-fold 3 --layer-dir $BASE/dist_peakneg --outdir $OUT 2>&1 | tee $OUT/run.log ;;
    dist_peakgrad) $LAYER --w-peak 1 --peak-pool 5 --w-grad 2 --tune-fold 3 --outdir $OUT 2>&1 | tee $OUT/run.log ;;
    unet_dist_peakgrad) $UNET --w-peak 1 --peak-pool 5 --w-grad 2 --tune-fold 3 --layer-dir $BASE/dist_peakgrad --outdir $OUT 2>&1 | tee $OUT/run.log ;;
    dist_det) $LAYER --w-peak 1 --peak-pool 5 --w-neg 1 --w-grad 2 --tune-fold 3 --outdir $OUT 2>&1 | tee $OUT/run.log ;;
    unet_dist_det) $UNET --w-peak 1 --peak-pool 5 --w-neg 1 --w-grad 2 --tune-fold 3 --layer-dir $BASE/dist_det --outdir $OUT 2>&1 | tee $OUT/run.log ;;
    dist_sched10)   $LAYER --mk-sched 10 15 --tune-fold 3 --outdir $OUT 2>&1 | tee $OUT/run.log ;;   # section 11.5: solve trained from the predicted markers
    dist_sched20)   $LAYER --mk-sched 20 25 --tune-fold 3 --outdir $OUT 2>&1 | tee $OUT/run.log ;;
    dist_sched10_bg) $LAYER --mk-sched 10 15 --mk-unmarked bg --tune-fold 3 --outdir $OUT 2>&1 | tee $OUT/run.log ;;
    dist_bg_s1) $LAYER --mk-sched 10 15 --mk-unmarked bg --seed 1 --tune-fold 3 --outdir $OUT 2>&1 | tee $OUT/run.log ;;
    dist_bg_s2) $LAYER --mk-sched 10 15 --mk-unmarked bg --seed 2 --tune-fold 3 --outdir $OUT 2>&1 | tee $OUT/run.log ;;
    dist_bg_f23) $LAYER --mk-sched 10 15 --mk-unmarked bg --train-fold 2 --test-fold 3 --tune-fold 1 --outdir $OUT 2>&1 | tee $OUT/run.log ;;
    dist_bg_f31) $LAYER --mk-sched 10 15 --mk-unmarked bg --train-fold 3 --test-fold 1 --tune-fold 2 --outdir $OUT 2>&1 | tee $OUT/run.log ;;
    dist_s1)        $LAYER --seed 1 --tune-fold 3 --outdir $OUT 2>&1 | tee $OUT/run.log ;;
    unet_dist_s1)   $UNET --seed 1 --tune-fold 3 --layer-dir $BASE/dist_s1 --outdir $OUT 2>&1 | tee $OUT/run.log ;;
    dist_s2)        $LAYER --seed 2 --tune-fold 3 --outdir $OUT 2>&1 | tee $OUT/run.log ;;
    unet_dist_s2)   $UNET --seed 2 --tune-fold 3 --layer-dir $BASE/dist_s2 --outdir $OUT 2>&1 | tee $OUT/run.log ;;
    dist_f23)       $LAYER --train-fold 2 --test-fold 3 --tune-fold 1 --outdir $OUT 2>&1 | tee $OUT/run.log ;;
    unet_dist_f23)  $UNET --train-fold 2 --test-fold 3 --tune-fold 1 --layer-dir $BASE/dist_f23 --outdir $OUT 2>&1 | tee $OUT/run.log ;;
    dist_f31)       $LAYER --train-fold 3 --test-fold 1 --tune-fold 2 --outdir $OUT 2>&1 | tee $OUT/run.log ;;
    unet_dist_f31)  $UNET --train-fold 3 --test-fold 1 --tune-fold 2 --layer-dir $BASE/dist_f31 --outdir $OUT 2>&1 | tee $OUT/run.log ;;
    *) echo "unknown run $r"; exit 1 ;;
  esac
  case $r in
    unet_dist_f*)  echo "no per-run plot for $r (other test fold; compare_instances.py)" ;;
    unet_dist_*)   python plot_unet_dist.py --res $OUT --dist $BASE/${r#unet_} --bce $BASE/bce_tuned > $OUT/plot.log 2>&1 || echo "plot failed for $r" ;;
    dist_f*)       python plot_instances.py --res $OUT --unet "" --ue "" > $OUT/plot.log 2>&1 || echo "plot failed for $r" ;;
    dist_*)        python plot_instances.py --res $OUT --ref $BASE/dist --ref-label "sec. 11.1 dist run" > $OUT/plot.log 2>&1 || echo "plot failed for $r" ;;
  esac
done
echo ALL DONE
