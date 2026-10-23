#!/bin/bash
# Section 10 leads on PanNuke: a band-Dice boundary loss (no boundary-map surrogate) for
# both variants, and the edge target on the cost head of rw_learned (binary target at
# p 5 -> 50, with BCE and with the band-Dice loss; gap target at p 2 -> 10 with sharp
# edges, the best finite-p configuration of section 6.1).  Launch the chains with
#   CHAIN=dice setsid nohup ./run_leads.sh > run_leads_dice.log 2>&1 < /dev/null &
#   CHAIN=edge setsid nohup ./run_leads.sh > run_leads_edge.log 2>&1 < /dev/null &
#   CHAIN=edge_gap setsid nohup ./run_leads.sh > run_leads_edge_gap.log 2>&1 < /dev/null &
set -e
cd "$(dirname "$0")"
source .venv/bin/activate
export TORCH_DISABLE_NATIVE_JIT=1
EPOCHS=${EPOCHS:-30}
OUT=${OUT:-results_pannuke_leads}
run() {  # subdir variant args...
  local sub=$1 v=$2; shift 2
  [ -f $OUT/$sub/$v.json ] && { echo "skip $sub/$v (done)"; return; }
  python exp_unet_seg.py --dataset pannuke --variant $v --epochs $EPOCHS --outdir $OUT/$sub "$@"
}
case ${CHAIN:-dice} in
  dice)
    run dice unet --loss boundary_dice
    run dice rw_learned --loss boundary_dice ;;
  edge)
    run edge_bce rw_learned --loss bce --w-edge 1
    run edge_dice rw_learned --loss boundary_dice --w-edge 1 ;;
  edge_gap)
    run edge_gap_p10 rw_learned --gap --p0 2 --p1 10 --edge-param scaled --edge-cmax 8 --edge-learn-scale --w-edge 1 ;;
esac
echo ALL DONE
