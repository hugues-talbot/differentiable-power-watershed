# Instances as labels: multi-marker layer on PanNuke (fold 1 → fold 2)

Run `results_pannuke_instances/dist_s2/instances`: p 5.0 → 20.0, erosion [2, 3], edge target ×1.0, seam weight 5.0, 30 epochs, seed 2, training solve tol 0.0001 / maxit 100; marker head `dist` (mse, rmax 12; markers = h-maxima h 0.2 grown to thr 0.2, min area 16 px), chosen by PQ on 300 patches of fold 3; learned edge scale 2.01.

## Marker post-processing chosen on fold 3 (300 patches): {'mk_thr': 0.2, 'mk_min_area': 16, 'mk_h': 0.2}

| setting | PQ | F1@0.5 | AJI | count err. | n_pred | one | none | several | bg / patch |
|---|---|---|---|---|---|---|---|---|---|
| thr=0.2/min_area=16/h=0.2 | 0.646 | 0.789 | 0.656 | 0.203 | 25.3 | 84.7 % | 13.8 % | 1.5 % | 4.14 |
| thr=0.2/min_area=9/h=0.2 | 0.645 | 0.788 | 0.656 | 0.218 | 25.8 | 85.6 % | 12.9 % | 1.5 % | 4.42 |
| thr=0.2/min_area=4/h=0.2 | 0.643 | 0.786 | 0.656 | 0.236 | 26.1 | 86.0 % | 12.5 % | 1.5 % | 4.65 |
| thr=0.2/min_area=1/h=0.2 | 0.642 | 0.785 | 0.655 | 0.242 | 26.2 | 86.3 % | 12.2 % | 1.5 % | 4.90 |
| thr=0.3/min_area=16/h=0.2 | 0.641 | 0.789 | 0.657 | 0.162 | 23.6 | 82.1 % | 16.5 % | 1.4 % | 3.07 |
| thr=0.3/min_area=9/h=0.2 | 0.641 | 0.789 | 0.658 | 0.166 | 24.1 | 83.3 % | 15.2 % | 1.4 % | 3.30 |
| thr=0.3/min_area=4/h=0.2 | 0.640 | 0.788 | 0.658 | 0.177 | 24.5 | 84.2 % | 14.4 % | 1.5 % | 3.55 |
| thr=0.3/min_area=1/h=0.2 | 0.638 | 0.787 | 0.658 | 0.184 | 24.9 | 85.3 % | 13.1 % | 1.5 % | 4.04 |
| thr=0.5/min_area=1/h=0.1 (untuned default) | 0.576 | 0.732 | 0.608 | 0.177 | 21.5 | 76.8 % | 20.5 % | 2.7 % | 2.12 |

(top 8 of 72 settings by PQ)

## All of fold 2

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6, binary target), s > 0.5, components | 2523 | 0.719 | 0.652 | 0.769 | 0.807 | 0.577 | 0.656 | 0.531 | 0.494 | 0.275 | 23.0 |
| U-Net + contour head (sec. 10.1, gap target), logits | 2523 | 0.719 | 0.658 | 0.774 | 0.809 | 0.574 | 0.682 | 0.556 | 0.571 | 0.303 | 25.2 |
| U-Net + contour head, tuned marker watershed (b) | 2523 | 0.718 | 0.658 | 0.774 | 0.809 | 0.568 | 0.715 | 0.583 | 0.657 | 0.344 | 27.2 |
| sec. 11.1 dist run: layer, converged (predicted markers) | 2523 | 0.707 | 0.647 | 0.762 | 0.811 | 0.580 | 0.791 | 0.641 | 0.653 | 0.239 | 24.3 |
| this model: s > 0.5, components | 2523 | 0.591 | 0.389 | 0.557 | 0.714 | 0.383 | 0.032 | 0.023 | 0.166 | 40.761 | 560.2 |
| this model: layer, converged (predicted markers) | 2523 | 0.707 | 0.648 | 0.763 | 0.814 | 0.575 | 0.789 | 0.642 | 0.654 | 0.247 | 24.7 |
| this model: layer + fallback markers | 2523 | 0.705 | 0.648 | 0.762 | 0.815 | 0.576 | 0.780 | 0.633 | 0.653 | 0.311 | 25.8 |
| this model: layer, ground-truth markers (oracle) | 2523 | 0.861 | 0.801 | 0.925 | 0.861 | 0.588 | 0.960 | 0.808 | 0.860 | 0.020 | 23.3 |
| this model: layer, image-gradient costs | 2523 | 0.560 | 0.285 | 0.467 | 0.655 | 0.308 | 0.626 | 0.403 | 0.530 | 0.248 | 24.7 |
| this model: marker watershed on the contour map | 2523 | 0.629 | 0.432 | 0.606 | 0.711 | 0.411 | 0.717 | 0.507 | 0.566 | 0.248 | 24.7 |
| this model: PW limit, learned costs | 307 | 0.688 | 0.605 | 0.731 | 0.792 | 0.566 | 0.760 | 0.602 | 0.611 | 0.248 | 25.6 |
| this model: PW limit, image-gradient costs | 307 | 0.557 | 0.287 | 0.463 | 0.653 | 0.300 | 0.605 | 0.388 | 0.512 | 0.248 | 25.6 |
| this model: ground truth instances | 2523 | 1.000 | 1.000 | 1.000 | 1.000 | 0.559 | 1.000 | 1.000 | 1.000 | 0.000 | 23.7 |

## Marker quality (predicted markers against the ground-truth nuclei)

- 59872 nuclei in fold 2 (23.7 per patch); predicted markers 24.7 per patch.
- exactly one marker: 84.3 %; none: 13.9 %; several: 1.7 %; markers in background: 3.84 per patch.
- with fallback markers: one 85.7 %, none 12.2 %, several 2.0 %, background 5.10 per patch, 26.4 markers per patch.
- sec. 11.1 dist run: one 83.9 %, none 14.5 %, several 1.6 %, background 3.58 per patch, 24.3 markers per patch.

## Inference cost

- U-Net forward: 0.9 ms per image; converged multi-marker solve (tol 1e-05): 61.7 ms per image at K = 24.7 markers per image (64839 systems in 158 batches of 16; 179 PCG iterations per batch).
- exact K-label PW limit (one CPU core): 0.7 s per patch with the learned costs, 0.7 s with image-gradient costs, K = 25.6; 7022 ambiguous plateaus solved over 307 patches.

## Per tissue type

**Breast**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 749 | 0.722 | 0.596 | 0.756 | 0.780 | 0.585 | 0.690 | 0.547 | 0.550 | 0.198 | 21.2 |
| U-Net + contour head, watershed (b) | 749 | 0.722 | 0.601 | 0.761 | 0.782 | 0.576 | 0.757 | 0.605 | 0.671 | 0.242 | 24.5 |
| sec. 11.1 dist run: layer | 749 | 0.708 | 0.585 | 0.743 | 0.782 | 0.587 | 0.817 | 0.647 | 0.661 | 0.187 | 22.9 |
| s > 0.5, components | 749 | 0.611 | 0.370 | 0.546 | 0.685 | 0.375 | 0.032 | 0.022 | 0.178 | 34.092 | 515.9 |
| layer, converged (predicted markers) | 749 | 0.709 | 0.588 | 0.747 | 0.786 | 0.584 | 0.815 | 0.648 | 0.662 | 0.193 | 23.4 |
| layer + fallback markers | 749 | 0.708 | 0.589 | 0.747 | 0.787 | 0.584 | 0.807 | 0.641 | 0.662 | 0.236 | 24.2 |
| layer, ground-truth markers (oracle) | 749 | 0.856 | 0.751 | 0.913 | 0.840 | 0.593 | 0.968 | 0.809 | 0.855 | 0.014 | 21.4 |
| layer, image-gradient costs | 749 | 0.574 | 0.273 | 0.441 | 0.640 | 0.285 | 0.661 | 0.427 | 0.549 | 0.193 | 23.4 |
| marker watershed on the contour map | 749 | 0.630 | 0.392 | 0.575 | 0.683 | 0.400 | 0.748 | 0.515 | 0.577 | 0.193 | 23.4 |
| PW limit, learned costs | 89 | 0.702 | 0.545 | 0.714 | 0.763 | 0.576 | 0.795 | 0.616 | 0.635 | 0.153 | 24.1 |
| PW limit, image-gradient costs | 89 | 0.588 | 0.282 | 0.449 | 0.641 | 0.276 | 0.655 | 0.422 | 0.546 | 0.154 | 24.1 |
| ground truth instances | 749 | 1.000 | 1.000 | 1.000 | 1.000 | 0.553 | 1.000 | 1.000 | 1.000 | 0.000 | 21.7 |

**Colon**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 468 | 0.698 | 0.617 | 0.738 | 0.788 | 0.558 | 0.547 | 0.431 | 0.349 | 0.274 | 21.1 |
| U-Net + contour head, watershed (b) | 468 | 0.691 | 0.621 | 0.742 | 0.788 | 0.550 | 0.630 | 0.497 | 0.574 | 0.340 | 27.7 |
| sec. 11.1 dist run: layer | 468 | 0.683 | 0.605 | 0.726 | 0.791 | 0.569 | 0.709 | 0.558 | 0.579 | 0.238 | 23.8 |
| s > 0.5, components | 468 | 0.556 | 0.353 | 0.508 | 0.703 | 0.385 | 0.019 | 0.013 | 0.088 | 43.134 | 658.7 |
| layer, converged (predicted markers) | 468 | 0.685 | 0.608 | 0.728 | 0.795 | 0.561 | 0.711 | 0.559 | 0.579 | 0.248 | 24.8 |
| layer + fallback markers | 468 | 0.684 | 0.608 | 0.728 | 0.795 | 0.561 | 0.702 | 0.552 | 0.579 | 0.290 | 25.9 |
| layer, ground-truth markers (oracle) | 468 | 0.853 | 0.776 | 0.910 | 0.853 | 0.565 | 0.942 | 0.774 | 0.844 | 0.024 | 24.9 |
| layer, image-gradient costs | 468 | 0.559 | 0.332 | 0.475 | 0.661 | 0.330 | 0.557 | 0.352 | 0.476 | 0.251 | 24.8 |
| marker watershed on the contour map | 468 | 0.614 | 0.414 | 0.575 | 0.701 | 0.415 | 0.609 | 0.420 | 0.493 | 0.251 | 24.8 |
| PW limit, learned costs | 62 | 0.660 | 0.567 | 0.697 | 0.768 | 0.524 | 0.649 | 0.495 | 0.503 | 0.216 | 30.4 |
| PW limit, image-gradient costs | 62 | 0.537 | 0.331 | 0.469 | 0.652 | 0.298 | 0.504 | 0.318 | 0.432 | 0.216 | 30.4 |
| ground truth instances | 468 | 1.000 | 1.000 | 1.000 | 1.000 | 0.539 | 1.000 | 1.000 | 1.000 | 0.000 | 25.4 |

**HeadNeck**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 169 | 0.672 | 0.658 | 0.744 | 0.835 | 0.648 | 0.640 | 0.519 | 0.556 | 0.424 | 20.2 |
| U-Net + contour head, watershed (b) | 169 | 0.682 | 0.675 | 0.756 | 0.839 | 0.638 | 0.688 | 0.565 | 0.660 | 0.474 | 23.6 |
| sec. 11.1 dist run: layer | 169 | 0.701 | 0.711 | 0.782 | 0.846 | 0.631 | 0.784 | 0.647 | 0.651 | 0.203 | 19.8 |
| s > 0.5, components | 169 | 0.484 | 0.354 | 0.490 | 0.771 | 0.458 | 0.031 | 0.022 | 0.214 | 45.503 | 511.7 |
| layer, converged (predicted markers) | 169 | 0.688 | 0.696 | 0.768 | 0.848 | 0.625 | 0.780 | 0.645 | 0.648 | 0.257 | 20.4 |
| layer + fallback markers | 169 | 0.677 | 0.684 | 0.757 | 0.851 | 0.635 | 0.760 | 0.627 | 0.647 | 0.410 | 21.9 |
| layer, ground-truth markers (oracle) | 169 | 0.859 | 0.853 | 0.937 | 0.886 | 0.643 | 0.968 | 0.822 | 0.863 | 0.031 | 18.2 |
| layer, image-gradient costs | 169 | 0.540 | 0.331 | 0.509 | 0.697 | 0.405 | 0.572 | 0.357 | 0.506 | 0.257 | 20.4 |
| marker watershed on the contour map | 169 | 0.620 | 0.495 | 0.637 | 0.766 | 0.476 | 0.720 | 0.519 | 0.567 | 0.257 | 20.4 |
| ground truth instances | 169 | 1.000 | 1.000 | 1.000 | 1.000 | 0.629 | 1.000 | 1.000 | 1.000 | 0.000 | 18.5 |

**Adrenal_gland**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 148 | 0.716 | 0.676 | 0.774 | 0.808 | 0.554 | 0.694 | 0.582 | 0.655 | 0.378 | 18.4 |
| U-Net + contour head, watershed (b) | 148 | 0.719 | 0.689 | 0.783 | 0.811 | 0.551 | 0.712 | 0.605 | 0.713 | 0.444 | 20.1 |
| sec. 11.1 dist run: layer | 148 | 0.709 | 0.688 | 0.779 | 0.824 | 0.562 | 0.823 | 0.696 | 0.696 | 0.260 | 17.1 |
| s > 0.5, components | 148 | 0.614 | 0.412 | 0.570 | 0.730 | 0.351 | 0.031 | 0.023 | 0.477 | 60.847 | 632.3 |
| layer, converged (predicted markers) | 148 | 0.715 | 0.691 | 0.783 | 0.826 | 0.558 | 0.815 | 0.691 | 0.693 | 0.265 | 17.1 |
| layer + fallback markers | 148 | 0.714 | 0.690 | 0.783 | 0.827 | 0.558 | 0.799 | 0.676 | 0.693 | 0.323 | 18.2 |
| layer, ground-truth markers (oracle) | 148 | 0.871 | 0.832 | 0.936 | 0.869 | 0.579 | 0.963 | 0.836 | 0.876 | 0.020 | 15.7 |
| layer, image-gradient costs | 148 | 0.530 | 0.205 | 0.397 | 0.620 | 0.280 | 0.633 | 0.407 | 0.533 | 0.265 | 17.1 |
| marker watershed on the contour map | 148 | 0.639 | 0.448 | 0.613 | 0.725 | 0.394 | 0.769 | 0.580 | 0.621 | 0.265 | 17.1 |
| ground truth instances | 148 | 1.000 | 1.000 | 1.000 | 1.000 | 0.557 | 1.000 | 1.000 | 1.000 | 0.000 | 16.0 |

## Paired per-patch differences (2523 patches; bootstrap 95 % intervals; F1 / PQ / AJI dataset-level, bootstrapped over patches)

| comparison | IoU | BF₂ | edge align. | F1@0.5 | PQ | AJI |
|---|---|---|---|---|---|---|
| layer − U-Net (sec. 6) logits | -0.012 [-0.015, -0.009] | -0.006 [-0.009, -0.003] | -0.002 [-0.003, -0.000] | +0.133 [+0.128, +0.138] | +0.111 [+0.108, +0.115] | +0.159 [+0.145, +0.173] |
| layer − contour-head U-Net, watershed (b) | -0.011 [-0.014, -0.008] | -0.011 [-0.014, -0.008] | +0.007 [+0.006, +0.009] | +0.074 [+0.072, +0.077] | +0.059 [+0.057, +0.061] | -0.004 [-0.006, -0.001] |
| layer − sec. 11.1 dist run layer | +0.000 [-0.002, +0.003] | +0.001 [-0.001, +0.004] | -0.005 [-0.006, -0.004] | -0.001 [-0.003, +0.001] | +0.001 [-0.001, +0.002] | +0.001 [-0.001, +0.003] |
| layer, ground-truth markers − sec. 11.1 dist run layer, ground-truth markers | +0.002 [+0.001, +0.003] | +0.003 [+0.001, +0.004] | -0.003 [-0.004, -0.002] | +0.001 [+0.000, +0.002] | +0.003 [+0.002, +0.004] | +0.002 [+0.002, +0.003] |
| layer − this model's own logits | +0.116 [+0.110, +0.121] | +0.206 [+0.201, +0.212] | +0.197 [+0.195, +0.200] | +0.757 [+0.752, +0.761] | +0.619 [+0.614, +0.624] | +0.488 [+0.474, +0.502] |
| layer − marker watershed, same markers | +0.078 [+0.077, +0.080] | +0.158 [+0.155, +0.160] | +0.164 [+0.162, +0.166] | +0.073 [+0.069, +0.077] | +0.135 [+0.133, +0.138] | +0.087 [+0.086, +0.089] |
| layer − layer with image costs | +0.147 [+0.144, +0.150] | +0.297 [+0.292, +0.302] | +0.268 [+0.265, +0.271] | +0.164 [+0.159, +0.169] | +0.239 [+0.235, +0.243] | +0.124 [+0.121, +0.127] |
| layer + fallback − U-Net (sec. 6) logits | -0.013 [-0.016, -0.011] | -0.007 [-0.010, -0.004] | -0.001 [-0.002, +0.000] | +0.123 [+0.118, +0.128] | +0.102 [+0.099, +0.107] | +0.159 [+0.144, +0.172] |
| layer + fallback − contour-head U-Net, watershed (b) | -0.013 [-0.016, -0.010] | -0.012 [-0.014, -0.009] | +0.008 [+0.006, +0.010] | +0.064 [+0.062, +0.068] | +0.050 [+0.048, +0.052] | -0.004 [-0.007, -0.001] |
| layer + fallback − layer | -0.002 [-0.004, -0.000] | -0.001 [-0.003, +0.001] | +0.001 [+0.000, +0.001] | -0.010 [-0.011, -0.009] | -0.009 [-0.010, -0.008] | -0.000 [-0.001, -0.000] |
| layer, ground-truth markers − layer | +0.154 [+0.149, +0.159] | +0.161 [+0.156, +0.166] | +0.014 [+0.012, +0.016] | +0.171 [+0.166, +0.174] | +0.165 [+0.162, +0.169] | +0.206 [+0.202, +0.210] |
| on the 307 limit patches: PW limit (learned) − layer | -0.017 [-0.019, -0.015] | -0.026 [-0.029, -0.023] | -0.000 [-0.002, +0.001] | -0.010 [-0.013, -0.007] | -0.019 [-0.021, -0.017] | -0.020 [-0.022, -0.018] |
| on the 307 limit patches: PW limit (learned) − PW limit (image costs) | +0.131 [+0.123, +0.141] | +0.268 [+0.253, +0.283] | +0.266 [+0.257, +0.276] | +0.155 [+0.142, +0.166] | +0.215 [+0.204, +0.227] | +0.098 [+0.090, +0.106] |
| on the 307 limit patches: PW limit (learned) − U-Net (sec. 6) logits | -0.025 [-0.032, -0.018] | -0.032 [-0.039, -0.025] | -0.002 [-0.008, +0.004] | +0.126 [+0.112, +0.142] | +0.093 [+0.082, +0.108] | +0.185 [+0.135, +0.234] |

## By crowding (F1@0.5 / PQ / count error)

| patches | n | U-Net (sec. 6) | contour-head U-Net, watershed (b) | layer | layer + fallback | marker watershed, same markers | PW limit (learned, subset) |
|---|---|---|---|---|---|---|---|
| < 10 nuclei | 486 | 0.608 / 0.485 / 0.68 | 0.596 / 0.479 / 0.81 | 0.683 / 0.548 / 0.65 | 0.651 / 0.522 / 0.88 | 0.616 / 0.433 / 0.66 | 0.640 / 0.492 / 0.61 |
| 10–30 | 1383 | 0.691 / 0.563 / 0.18 | 0.719 / 0.591 / 0.27 | 0.798 / 0.654 / 0.17 | 0.785 / 0.643 / 0.20 | 0.741 / 0.530 / 0.17 | 0.789 / 0.631 / 0.18 |
| 30–60 | 525 | 0.650 / 0.524 / 0.15 | 0.733 / 0.596 / 0.15 | 0.802 / 0.650 / 0.10 | 0.795 / 0.644 / 0.12 | 0.727 / 0.512 / 0.10 | 0.771 / 0.610 / 0.11 |
| > 60 | 129 | 0.588 / 0.469 / 0.24 | 0.700 / 0.562 / 0.13 | 0.767 / 0.618 / 0.14 | 0.765 / 0.615 / 0.13 | 0.657 / 0.455 / 0.14 | 0.705 / 0.552 / 0.18 |

## Marker quality by crowding (nuclei with one / none / several markers; background markers per patch)

| patches | one | none | several | bg markers / patch |
|---|---|---|---|---|
| < 10 nuclei | 82.9 % | 14.1 % | 3.0 % | 1.94 |
| 10–30 | 86.9 % | 11.1 % | 2.0 % | 3.73 |
| 30–60 | 84.8 % | 13.5 % | 1.7 % | 5.14 |
| > 60 | 77.8 % | 21.3 % | 0.9 % | 6.98 |
