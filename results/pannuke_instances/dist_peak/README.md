# dist_peak: distance head + raw per-nucleus peak loss (section 11.3) — abandoned after training

Trained 21–22 Oct 2026 on jacobian (30 epochs, `--mk-head dist --w-mk 2 --w-peak 1`, peak loss =
mean over nuclei of (1 − max of the predicted map over the nucleus)²; final losses ce 0.0875 /
aux 0.1649 / mk 0.0097 / edge 0.2412 / peak 0.0020).  The fold-3 tuning was stopped after its first
batch (1516 s for 72 settings, against ~130 s for the `dist` model): the loss, whose gradient reaches
one pixel per nucleus per step, grew needle-shaped maxima all over the map.  Regional maxima per
patch (h-maxima grown to thr, 16 fold-3 patches with 22.7 nuclei each), `dist` vs `dist_peak`:

| h | thr | dist | dist_peak |
|---|---|---|---|
| 0.05 | 0.2 | 36.0 | 298.2 |
| 0.10 | 0.2 | 27.1 | 258.9 |
| 0.20 | 0.2 | 24.0 | 200.4 |
| 0.30 | 0.2 | 21.6 | 144.1 |
| 0.30 | 0.4 | 20.9 | 138.2 |

The mean map and its area above 0.2 are the same as `dist`'s (0.066 vs 0.064; 10.9 % vs 11.1 %):
the needles sit on top of an otherwise similar map.  Replaced by `dist_peak5` (`--peak-pool 5`: both
maxima taken on the 5 × 5 mean-pooled prediction and target, so a nucleus must carry a plateau).
The .pt stays on jacobian; `run.log` is the training log.
