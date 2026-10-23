#!/bin/bash
# Submit the seed and fold-pair runs of section 11.3 on ruche: every layer run as one job, its fair
# baseline as a dependent job (it loads the layer's .pt for the markers x assignment 2 x 2).
#   ./ruche_submit.sh            # s1 s2 f23 f31
#   CFGS="peak" ./ruche_submit.sh
cd ~/Claude/pw-unrolling
mkdir -p logs
for cfg in ${CFGS:-s1 s2 f23 f31}; do
  j=$(sbatch --parsable -J dist_$cfg ruche_run.sh dist_$cfg)
  k=$(sbatch --parsable -J unet_dist_$cfg --time=4:00:00 --dependency=afterok:$j ruche_run.sh unet_dist_$cfg)
  echo "dist_$cfg job $j, unet_dist_$cfg job $k (after $j)"
done
squeue -u $USER -o "%.10i %.14j %.9P %.2t %.10M %.6D %R"
