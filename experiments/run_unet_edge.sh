#!/bin/bash
# Section 10.1: the fair baseline for the edge-target layer of section 10.  A plain U-Net with a
# second contour head trained on the same edge target (gap target, --w-edge 1, same weights), its
# thresholded logits and two classical post-processings (contour removed; marker watershed on the
# contour map), against results_pannuke_leads/edge_gap_p10.  Launch with
#   setsid nohup ./run_unet_edge.sh > run_unet_edge.log 2>&1 < /dev/null &
set -e
cd "$(dirname "$0")"
source .venv/bin/activate
export TORCH_DISABLE_NATIVE_JIT=1
EPOCHS=${EPOCHS:-30}
L=${OUT:-results_pannuke_leads}
if [ ! -f $L/unet_edge/unet_edge.json ]; then
  python exp_unet_seg.py --dataset pannuke --gap --variant unet_edge --w-edge 1 --epochs $EPOCHS --outdir $L/unet_edge
fi
# tables, figures, seam statistics, min-area filter
python plot_pannuke.py $L/unet_edge > /dev/null && echo "plotted unet_edge"
python seam_stats.py --outdir $L/unet_edge --runs unet_edge
python inst_minarea.py --runs unet_edge=$L/unet_edge --out $L/unet_edge/minarea.json > $L/unet_edge/minarea.log && echo "min-area done"
echo ALL DONE
