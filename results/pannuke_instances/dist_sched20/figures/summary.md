# Instances as labels: multi-marker layer on PanNuke (fold 1 → fold 2)

Run `results_pannuke_instances/dist_sched20/instances`: p 5.0 → 20.0, erosion [2, 3], edge target ×1.0, seam weight 5.0, 30 epochs, seed 0, training solve tol 0.0001 / maxit 100, training markers predicted from epoch 20 (all from 25; thr 0.2 / min area 16 / h 0.2, unmarked nuclei: ignore); marker head `dist` (mse, rmax 12; markers = h-maxima h 0.2 grown to thr 0.2, min area 1 px), chosen by PQ on 300 patches of fold 3; learned edge scale 1.99.

## Marker post-processing chosen on fold 3 (300 patches): {'mk_thr': 0.2, 'mk_min_area': 1, 'mk_h': 0.2}

| setting | PQ | F1@0.5 | AJI | count err. | n_pred | one | none | several | bg / patch |
|---|---|---|---|---|---|---|---|---|---|
| thr=0.2/min_area=1/h=0.2 | 0.650 | 0.793 | 0.668 | 0.159 | 23.7 | 85.8 % | 12.8 % | 1.4 % | 4.44 |
| thr=0.2/min_area=4/h=0.2 | 0.650 | 0.793 | 0.668 | 0.160 | 23.7 | 85.5 % | 13.2 % | 1.4 % | 4.21 |
| thr=0.2/min_area=9/h=0.2 | 0.650 | 0.792 | 0.668 | 0.159 | 23.6 | 85.0 % | 13.7 % | 1.4 % | 4.00 |
| thr=0.2/min_area=16/h=0.2 | 0.650 | 0.791 | 0.668 | 0.159 | 23.3 | 83.9 % | 14.7 % | 1.3 % | 3.72 |
| thr=0.3/min_area=1/h=0.2 | 0.646 | 0.785 | 0.661 | 0.169 | 21.8 | 84.5 % | 14.1 % | 1.4 % | 3.63 |
| thr=0.3/min_area=4/h=0.2 | 0.645 | 0.784 | 0.661 | 0.170 | 21.7 | 83.1 % | 15.6 % | 1.3 % | 3.20 |
| thr=0.3/min_area=9/h=0.2 | 0.645 | 0.783 | 0.661 | 0.171 | 21.6 | 82.3 % | 16.4 % | 1.3 % | 3.01 |
| thr=0.3/min_area=16/h=0.2 | 0.644 | 0.782 | 0.661 | 0.172 | 21.5 | 81.2 % | 17.5 % | 1.3 % | 2.75 |
| thr=0.5/min_area=1/h=0.1 (untuned default) | 0.586 | 0.711 | 0.602 | 0.267 | 17.5 | 73.7 % | 23.8 % | 2.6 % | 1.78 |

(top 8 of 72 settings by PQ)

## All of fold 2

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6, binary target), s > 0.5, components | 2523 | 0.719 | 0.652 | 0.769 | 0.807 | 0.577 | 0.656 | 0.531 | 0.494 | 0.275 | 23.0 |
| U-Net + contour head (sec. 10.1, gap target), logits | 2523 | 0.719 | 0.658 | 0.774 | 0.809 | 0.574 | 0.682 | 0.556 | 0.571 | 0.303 | 25.2 |
| U-Net + contour head, tuned marker watershed (b) | 2523 | 0.718 | 0.658 | 0.774 | 0.809 | 0.568 | 0.715 | 0.583 | 0.657 | 0.344 | 27.2 |
| sec. 11.1 dist run: layer, converged (predicted markers) | 2523 | 0.707 | 0.647 | 0.762 | 0.811 | 0.580 | 0.791 | 0.641 | 0.653 | 0.239 | 24.3 |
| this model: s > 0.5, components | 2523 | 0.607 | 0.445 | 0.608 | 0.709 | 0.401 | 0.046 | 0.032 | 0.227 | 27.715 | 420.5 |
| this model: layer, converged (predicted markers) | 2523 | 0.714 | 0.656 | 0.774 | 0.806 | 0.589 | 0.792 | 0.645 | 0.663 | 0.197 | 23.4 |
| this model: layer + fallback markers | 2523 | 0.714 | 0.656 | 0.774 | 0.806 | 0.589 | 0.790 | 0.643 | 0.663 | 0.203 | 23.6 |
| this model: layer, ground-truth markers (oracle) | 2523 | 0.801 | 0.728 | 0.852 | 0.820 | 0.597 | 0.902 | 0.745 | 0.795 | 0.103 | 21.3 |
| this model: layer, image-gradient costs | 2523 | 0.515 | 0.232 | 0.403 | 0.625 | 0.278 | 0.529 | 0.326 | 0.495 | 0.294 | 25.5 |
| this model: marker watershed on the contour map | 2523 | 0.617 | 0.459 | 0.621 | 0.705 | 0.420 | 0.687 | 0.479 | 0.571 | 0.294 | 25.5 |
| this model: PW limit, learned costs | 307 | 0.646 | 0.589 | 0.703 | 0.750 | 0.602 | 0.719 | 0.576 | 0.575 | 0.227 | 20.8 |
| this model: PW limit, image-gradient costs | 307 | 0.515 | 0.244 | 0.408 | 0.624 | 0.270 | 0.504 | 0.310 | 0.479 | 0.318 | 26.2 |
| this model: ground truth instances | 2523 | 1.000 | 1.000 | 1.000 | 1.000 | 0.559 | 1.000 | 1.000 | 1.000 | 0.000 | 23.7 |

## Marker quality (predicted markers against the ground-truth nuclei)

- 59872 nuclei in fold 2 (23.7 per patch); predicted markers 25.5 per patch.
- exactly one marker: 85.7 %; none: 12.6 %; several: 1.7 %; markers in background: 4.32 per patch.
- with fallback markers: one 85.8 %, none 12.1 %, several 2.1 %, background 4.77 per patch, 26.2 markers per patch.
- sec. 11.1 dist run: one 83.9 %, none 14.5 %, several 1.6 %, background 3.58 per patch, 24.3 markers per patch.

## Inference cost

- U-Net forward: 2.5 ms per image; converged multi-marker solve (tol 1e-05): 188.8 ms per image at K = 25.5 markers per image (66830 systems in 158 batches of 16; 300 PCG iterations per batch).
- exact K-label PW limit (one CPU core): 0.6 s per patch with the learned costs, 0.6 s with image-gradient costs, K = 26.3; 10321 ambiguous plateaus solved over 307 patches.

## Per tissue type

**Breast**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 749 | 0.722 | 0.596 | 0.756 | 0.780 | 0.585 | 0.690 | 0.547 | 0.550 | 0.198 | 21.2 |
| U-Net + contour head, watershed (b) | 749 | 0.722 | 0.601 | 0.761 | 0.782 | 0.576 | 0.757 | 0.605 | 0.671 | 0.242 | 24.5 |
| sec. 11.1 dist run: layer | 749 | 0.708 | 0.585 | 0.743 | 0.782 | 0.587 | 0.817 | 0.647 | 0.661 | 0.187 | 22.9 |
| s > 0.5, components | 749 | 0.615 | 0.415 | 0.588 | 0.682 | 0.387 | 0.047 | 0.032 | 0.251 | 23.836 | 386.8 |
| layer, converged (predicted markers) | 749 | 0.717 | 0.596 | 0.758 | 0.778 | 0.597 | 0.817 | 0.650 | 0.673 | 0.150 | 21.9 |
| layer + fallback markers | 749 | 0.717 | 0.597 | 0.758 | 0.778 | 0.597 | 0.816 | 0.650 | 0.673 | 0.157 | 22.0 |
| layer, ground-truth markers (oracle) | 749 | 0.796 | 0.666 | 0.834 | 0.796 | 0.604 | 0.916 | 0.744 | 0.792 | 0.082 | 20.0 |
| layer, image-gradient costs | 749 | 0.530 | 0.225 | 0.380 | 0.607 | 0.244 | 0.564 | 0.350 | 0.513 | 0.210 | 23.6 |
| marker watershed on the contour map | 749 | 0.621 | 0.424 | 0.596 | 0.679 | 0.402 | 0.717 | 0.489 | 0.580 | 0.210 | 23.6 |
| PW limit, learned costs | 89 | 0.647 | 0.521 | 0.673 | 0.717 | 0.615 | 0.756 | 0.591 | 0.597 | 0.197 | 18.9 |
| PW limit, image-gradient costs | 89 | 0.543 | 0.240 | 0.391 | 0.608 | 0.233 | 0.554 | 0.343 | 0.510 | 0.158 | 24.2 |
| ground truth instances | 749 | 1.000 | 1.000 | 1.000 | 1.000 | 0.553 | 1.000 | 1.000 | 1.000 | 0.000 | 21.7 |

**Colon**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 468 | 0.698 | 0.617 | 0.738 | 0.788 | 0.558 | 0.547 | 0.431 | 0.349 | 0.274 | 21.1 |
| U-Net + contour head, watershed (b) | 468 | 0.691 | 0.621 | 0.742 | 0.788 | 0.550 | 0.630 | 0.497 | 0.574 | 0.340 | 27.7 |
| sec. 11.1 dist run: layer | 468 | 0.683 | 0.605 | 0.726 | 0.791 | 0.569 | 0.709 | 0.558 | 0.579 | 0.238 | 23.8 |
| s > 0.5, components | 468 | 0.588 | 0.432 | 0.585 | 0.700 | 0.406 | 0.025 | 0.017 | 0.130 | 33.723 | 566.9 |
| layer, converged (predicted markers) | 468 | 0.691 | 0.619 | 0.742 | 0.784 | 0.578 | 0.715 | 0.564 | 0.587 | 0.211 | 22.8 |
| layer + fallback markers | 468 | 0.691 | 0.619 | 0.742 | 0.784 | 0.578 | 0.712 | 0.562 | 0.587 | 0.210 | 23.0 |
| layer, ground-truth markers (oracle) | 468 | 0.771 | 0.683 | 0.812 | 0.800 | 0.582 | 0.851 | 0.686 | 0.749 | 0.138 | 21.7 |
| layer, image-gradient costs | 468 | 0.505 | 0.281 | 0.417 | 0.630 | 0.307 | 0.446 | 0.269 | 0.442 | 0.265 | 24.9 |
| marker watershed on the contour map | 468 | 0.596 | 0.444 | 0.595 | 0.696 | 0.430 | 0.582 | 0.396 | 0.501 | 0.266 | 24.9 |
| PW limit, learned costs | 62 | 0.582 | 0.523 | 0.637 | 0.711 | 0.566 | 0.593 | 0.457 | 0.459 | 0.291 | 24.2 |
| PW limit, image-gradient costs | 62 | 0.477 | 0.282 | 0.412 | 0.619 | 0.278 | 0.384 | 0.232 | 0.397 | 0.213 | 30.5 |
| ground truth instances | 468 | 1.000 | 1.000 | 1.000 | 1.000 | 0.539 | 1.000 | 1.000 | 1.000 | 0.000 | 25.4 |

**HeadNeck**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 169 | 0.672 | 0.658 | 0.744 | 0.835 | 0.648 | 0.640 | 0.519 | 0.556 | 0.424 | 20.2 |
| U-Net + contour head, watershed (b) | 169 | 0.682 | 0.675 | 0.756 | 0.839 | 0.638 | 0.688 | 0.565 | 0.660 | 0.474 | 23.6 |
| sec. 11.1 dist run: layer | 169 | 0.701 | 0.711 | 0.782 | 0.846 | 0.631 | 0.784 | 0.647 | 0.651 | 0.203 | 19.8 |
| s > 0.5, components | 169 | 0.554 | 0.456 | 0.594 | 0.763 | 0.505 | 0.048 | 0.033 | 0.294 | 24.231 | 343.3 |
| layer, converged (predicted markers) | 169 | 0.690 | 0.694 | 0.774 | 0.837 | 0.646 | 0.786 | 0.647 | 0.659 | 0.218 | 19.2 |
| layer + fallback markers | 169 | 0.690 | 0.694 | 0.774 | 0.837 | 0.646 | 0.782 | 0.644 | 0.659 | 0.224 | 19.4 |
| layer, ground-truth markers (oracle) | 169 | 0.796 | 0.782 | 0.869 | 0.848 | 0.651 | 0.912 | 0.760 | 0.800 | 0.114 | 16.9 |
| layer, image-gradient costs | 169 | 0.477 | 0.261 | 0.430 | 0.673 | 0.406 | 0.458 | 0.275 | 0.472 | 0.414 | 21.4 |
| marker watershed on the contour map | 169 | 0.588 | 0.492 | 0.626 | 0.759 | 0.511 | 0.688 | 0.486 | 0.572 | 0.414 | 21.4 |
| ground truth instances | 169 | 1.000 | 1.000 | 1.000 | 1.000 | 0.629 | 1.000 | 1.000 | 1.000 | 0.000 | 18.5 |

**Adrenal_gland**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 148 | 0.716 | 0.676 | 0.774 | 0.808 | 0.554 | 0.694 | 0.582 | 0.655 | 0.378 | 18.4 |
| U-Net + contour head, watershed (b) | 148 | 0.719 | 0.689 | 0.783 | 0.811 | 0.551 | 0.712 | 0.605 | 0.713 | 0.444 | 20.1 |
| sec. 11.1 dist run: layer | 148 | 0.709 | 0.688 | 0.779 | 0.824 | 0.562 | 0.823 | 0.696 | 0.696 | 0.260 | 17.1 |
| s > 0.5, components | 148 | 0.620 | 0.449 | 0.607 | 0.720 | 0.378 | 0.044 | 0.033 | 0.498 | 36.411 | 430.2 |
| layer, converged (predicted markers) | 148 | 0.720 | 0.700 | 0.793 | 0.815 | 0.569 | 0.820 | 0.696 | 0.708 | 0.203 | 16.1 |
| layer + fallback markers | 148 | 0.720 | 0.700 | 0.793 | 0.815 | 0.569 | 0.817 | 0.693 | 0.708 | 0.203 | 16.2 |
| layer, ground-truth markers (oracle) | 148 | 0.803 | 0.758 | 0.858 | 0.826 | 0.586 | 0.916 | 0.784 | 0.818 | 0.121 | 14.4 |
| layer, image-gradient costs | 148 | 0.500 | 0.166 | 0.341 | 0.595 | 0.257 | 0.551 | 0.340 | 0.502 | 0.331 | 18.3 |
| marker watershed on the contour map | 148 | 0.632 | 0.470 | 0.628 | 0.715 | 0.405 | 0.716 | 0.533 | 0.626 | 0.331 | 18.3 |
| ground truth instances | 148 | 1.000 | 1.000 | 1.000 | 1.000 | 0.557 | 1.000 | 1.000 | 1.000 | 0.000 | 16.0 |

## Paired per-patch differences (2523 patches; bootstrap 95 % intervals; F1 / PQ / AJI dataset-level, bootstrapped over patches)

| comparison | IoU | BF₂ | edge align. | F1@0.5 | PQ | AJI |
|---|---|---|---|---|---|---|
| layer − U-Net (sec. 6) logits | -0.005 [-0.007, -0.002] | +0.005 [+0.002, +0.007] | +0.012 [+0.010, +0.013] | +0.136 [+0.131, +0.141] | +0.114 [+0.111, +0.118] | +0.169 [+0.154, +0.183] |
| layer − contour-head U-Net, watershed (b) | -0.004 [-0.006, -0.001] | -0.000 [-0.003, +0.002] | +0.021 [+0.019, +0.022] | +0.077 [+0.075, +0.081] | +0.062 [+0.060, +0.064] | +0.006 [+0.004, +0.008] |
| layer − sec. 11.1 dist run layer | +0.007 [+0.004, +0.010] | +0.012 [+0.009, +0.015] | +0.009 [+0.007, +0.010] | +0.002 [-0.000, +0.004] | +0.004 [+0.002, +0.005] | +0.011 [+0.009, +0.013] |
| layer, ground-truth markers − sec. 11.1 dist run layer, ground-truth markers | -0.058 [-0.061, -0.056] | -0.070 [-0.074, -0.067] | +0.007 [+0.006, +0.009] | -0.057 [-0.060, -0.054] | -0.060 [-0.062, -0.057] | -0.062 [-0.064, -0.060] |
| layer − this model's own logits | +0.107 [+0.103, +0.111] | +0.166 [+0.161, +0.170] | +0.191 [+0.188, +0.193] | +0.747 [+0.742, +0.751] | +0.613 [+0.608, +0.618] | +0.436 [+0.418, +0.454] |
| layer − marker watershed, same markers | +0.097 [+0.094, +0.100] | +0.152 [+0.149, +0.156] | +0.170 [+0.168, +0.173] | +0.105 [+0.103, +0.109] | +0.166 [+0.164, +0.168] | +0.092 [+0.091, +0.094] |
| layer − layer with image costs | +0.199 [+0.196, +0.203] | +0.371 [+0.365, +0.376] | +0.313 [+0.310, +0.318] | +0.263 [+0.257, +0.269] | +0.319 [+0.315, +0.323] | +0.169 [+0.166, +0.171] |
| layer + fallback − U-Net (sec. 6) logits | -0.005 [-0.007, -0.002] | +0.005 [+0.002, +0.007] | +0.012 [+0.010, +0.013] | +0.134 [+0.129, +0.138] | +0.112 [+0.108, +0.116] | +0.169 [+0.154, +0.183] |
| layer + fallback − contour-head U-Net, watershed (b) | -0.004 [-0.006, -0.001] | -0.000 [-0.003, +0.002] | +0.021 [+0.019, +0.022] | +0.075 [+0.072, +0.078] | +0.060 [+0.058, +0.062] | +0.006 [+0.004, +0.008] |
| layer + fallback − layer | -0.000 [-0.000, +0.000] | +0.000 [-0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.002 [-0.003, -0.002] | -0.002 [-0.002, -0.002] | -0.000 [-0.000, +0.000] |
| layer, ground-truth markers − layer | +0.087 [+0.082, +0.092] | +0.078 [+0.073, +0.083] | +0.011 [+0.009, +0.012] | +0.109 [+0.106, +0.112] | +0.100 [+0.097, +0.102] | +0.132 [+0.129, +0.135] |
| on the 307 limit patches: PW limit (learned) − layer | -0.060 [-0.072, -0.047] | -0.061 [-0.072, -0.049] | +0.024 [+0.020, +0.029] | -0.054 [-0.062, -0.046] | -0.049 [-0.055, -0.043] | -0.065 [-0.073, -0.057] |
| on the 307 limit patches: PW limit (learned) − PW limit (image costs) | +0.131 [+0.118, +0.144] | +0.296 [+0.276, +0.316] | +0.335 [+0.323, +0.347] | +0.214 [+0.198, +0.230] | +0.266 [+0.253, +0.280] | +0.096 [+0.086, +0.106] |
| on the 307 limit patches: PW limit (learned) − U-Net (sec. 6) logits | -0.068 [-0.080, -0.054] | -0.060 [-0.072, -0.047] | +0.035 [+0.028, +0.042] | +0.085 [+0.070, +0.101] | +0.067 [+0.055, +0.080] | +0.150 [+0.100, +0.193] |

## By crowding (F1@0.5 / PQ / count error)

| patches | n | U-Net (sec. 6) | contour-head U-Net, watershed (b) | layer | layer + fallback | marker watershed, same markers | PW limit (learned, subset) |
|---|---|---|---|---|---|---|---|
| < 10 nuclei | 486 | 0.608 / 0.485 / 0.68 | 0.596 / 0.479 / 0.81 | 0.705 / 0.567 / 0.49 | 0.700 / 0.563 / 0.52 | 0.555 / 0.383 / 0.85 | 0.632 / 0.501 / 0.35 |
| 10–30 | 1383 | 0.691 / 0.563 / 0.18 | 0.719 / 0.591 / 0.27 | 0.802 / 0.658 / 0.13 | 0.799 / 0.656 / 0.14 | 0.700 / 0.494 / 0.18 | 0.744 / 0.603 / 0.20 |
| 30–60 | 525 | 0.650 / 0.524 / 0.15 | 0.733 / 0.596 / 0.15 | 0.802 / 0.651 / 0.10 | 0.800 / 0.649 / 0.10 | 0.703 / 0.488 / 0.11 | 0.739 / 0.590 / 0.18 |
| > 60 | 129 | 0.588 / 0.469 / 0.24 | 0.700 / 0.562 / 0.13 | 0.770 / 0.618 / 0.14 | 0.768 / 0.616 / 0.14 | 0.654 / 0.446 / 0.12 | 0.659 / 0.519 / 0.25 |

## Marker quality by crowding (nuclei with one / none / several markers; background markers per patch)

| patches | one | none | several | bg markers / patch |
|---|---|---|---|---|
| < 10 nuclei | 86.4 % | 11.0 % | 2.6 % | 2.33 |
| 10–30 | 88.1 % | 9.9 % | 2.0 % | 4.11 |
| 30–60 | 85.7 % | 12.6 % | 1.7 % | 5.62 |
| > 60 | 80.1 % | 18.9 % | 0.9 % | 8.89 |
