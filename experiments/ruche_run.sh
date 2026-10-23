#!/bin/bash
#SBATCH --job-name=pw
#SBATCH --partition=gpua100
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --tmp=16G
#SBATCH --time=12:00:00
#SBATCH --output=logs/%x-%j.out
# One run of sections 11.3-11.5 (the cases of run_instances_11_3.sh) as a SLURM job on ruche:
#   sbatch -J dist_s1 ruche_run.sh dist_s1
# Project folder ~/Claude/pw-unrolling (code + data/ + results_pannuke_instances/ on GPFS, which is slow:
# the fold files are copied once to the node-local SSD ($TMPDIR = /scratch/$USER-$SLURM_JOB_ID) and the
# scripts load a fold fully into RAM once; only the small result files are written to GPFS).
# Env: conda env ~/Claude/pw-env (python 3.12, torch 2.11 cu128).  A100 partition only: the V100s (sm_70)
# have no kernels in current PyTorch wheels ("no kernel image is available"), and CUDA 13 dropped them too.
set -e
r=$1
cd ~/Claude/pw-unrolling
source ~/miniconda3/etc/profile.d/conda.sh
conda activate ~/Claude/pw-env
export TORCH_DISABLE_NATIVE_JIT=1 OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-8}
STAGE=${TMPDIR:-/scratch/$USER-$SLURM_JOB_ID}
mkdir -p $STAGE/data logs
t0=$(date +%s)
if cp data/pannuke_fold*.npz $STAGE/data/ 2>/dev/null; then
  DATA=$STAGE/data; echo "staged data to $STAGE in $(( $(date +%s) - t0 )) s"
else
  DATA=data; rm -rf $STAGE/data; echo "staging to $STAGE failed (quota?): reading the folds from GPFS (one sequential read per fold)"
fi
echo "node $(hostname), $(nvidia-smi --query-gpu=name --format=csv,noheader), $(df -h $STAGE | tail -1)"
EPOCHS=${EPOCHS:-30}
BASE=results_pannuke_instances
OUT=$BASE/$r
mkdir -p $OUT
LAYER="python exp_instance_pannuke.py --data $DATA --epochs $EPOCHS --mk-head dist --w-mk 2 --limit-workers ${SLURM_CPUS_PER_TASK:-8} --tb"
UNET="python exp_unet_dist.py --data $DATA --epochs $EPOCHS --tb"
case $r in
  smoke)          mkdir -p ${OUT}_unet
                  $LAYER --epochs 1 --train-n 32 --test-n 16 --val-n 8 --limit-n 2 --n-examples 1 --tune-fold 3 --tune-n 16 --tune-thr 0.2 --tune-min-area 16 --tune-h 0.2 --outdir $OUT 2>&1 | tee $OUT/run.log
                  $UNET --epochs 1 --train-n 32 --test-n 16 --val-n 8 --n-examples 1 --tune-fold 3 --tune-n 16 --tune-thr 0.5 --tune-min-area 4 --tune-h 0.2 --layer-dir $OUT --outdir ${OUT}_unet 2>&1 | tee ${OUT}_unet/run.log ;;
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
  dist_sched10)   $LAYER --mk-sched 10 15 --tune-fold 3 --outdir $OUT 2>&1 | tee $OUT/run.log ;;
  dist_sched20)   $LAYER --mk-sched 20 25 --tune-fold 3 --outdir $OUT 2>&1 | tee $OUT/run.log ;;
  dist_sched10_bg) $LAYER --mk-sched 10 15 --mk-unmarked bg --tune-fold 3 --outdir $OUT 2>&1 | tee $OUT/run.log ;;
  dist_bg_s1) $LAYER --mk-sched 10 15 --mk-unmarked bg --seed 1 --tune-fold 3 --outdir $OUT 2>&1 | tee $OUT/run.log ;;
  dist_bg_s2) $LAYER --mk-sched 10 15 --mk-unmarked bg --seed 2 --tune-fold 3 --outdir $OUT 2>&1 | tee $OUT/run.log ;;
  dist_bg_f23) $LAYER --mk-sched 10 15 --mk-unmarked bg --train-fold 2 --test-fold 3 --tune-fold 1 --outdir $OUT 2>&1 | tee $OUT/run.log ;;
  dist_bg_f31) $LAYER --mk-sched 10 15 --mk-unmarked bg --train-fold 3 --test-fold 1 --tune-fold 2 --outdir $OUT 2>&1 | tee $OUT/run.log ;;
  smoke_sched)    $LAYER --epochs 2 --mk-sched 0 1 --train-n 32 --test-n 16 --val-n 8 --limit-n 2 --n-examples 1 --tune-fold 3 --tune-n 16 --tune-thr 0.2 --tune-min-area 16 --tune-h 0.2 --outdir $OUT 2>&1 | tee $OUT/run.log ;;
  eval_*)         # tuning + evaluation only from a saved model (a job that died after the training): sbatch -J eval_<run> ruche_run.sh eval_<run>, EXTRA="<the run's training flags>"
                  SRC=$BASE/${r#eval_}; $LAYER --eval-only --load $SRC/instances.pt --tune-fold 3 $EXTRA --outdir $SRC 2>&1 | tee -a $SRC/run.log ;;
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
rm -rf $STAGE/data
echo "JOB DONE $r"
