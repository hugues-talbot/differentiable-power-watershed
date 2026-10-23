# Instances as labels: multi-marker layer on PanNuke (fold 1 → fold 2)

Run `results_pannuke_instances/dist_sched10/instances`: p 5.0 → 20.0, erosion [2, 3], edge target ×1.0, seam weight 5.0, 30 epochs, seed 0, training solve tol 0.0001 / maxit 100, training markers predicted from epoch 10 (all from 15; thr 0.2 / min area 16 / h 0.2, unmarked nuclei: ignore); marker head `dist` (mse, rmax 12; markers = h-maxima h 0.2 grown to thr 0.2, min area 1 px), chosen by PQ on 300 patches of fold 3; learned edge scale 1.84.

## Marker post-processing chosen on fold 3 (300 patches): {'mk_thr': 0.2, 'mk_min_area': 1, 'mk_h': 0.2}

| setting | PQ | F1@0.5 | AJI | count err. | n_pred | one | none | several | bg / patch |
|---|---|---|---|---|---|---|---|---|---|
| thr=0.2/min_area=1/h=0.2 | 0.651 | 0.793 | 0.670 | 0.159 | 23.3 | 85.5 % | 13.2 % | 1.3 % | 4.37 |
| thr=0.2/min_area=4/h=0.2 | 0.651 | 0.793 | 0.670 | 0.159 | 23.3 | 85.3 % | 13.4 % | 1.3 % | 4.26 |
| thr=0.2/min_area=9/h=0.2 | 0.651 | 0.792 | 0.670 | 0.159 | 23.2 | 85.0 % | 13.8 % | 1.2 % | 4.11 |
| thr=0.2/min_area=16/h=0.2 | 0.651 | 0.792 | 0.670 | 0.160 | 23.1 | 84.2 % | 14.5 % | 1.2 % | 3.85 |
| thr=0.3/min_area=1/h=0.2 | 0.641 | 0.782 | 0.662 | 0.165 | 21.9 | 84.5 % | 14.2 % | 1.2 % | 3.79 |
| thr=0.3/min_area=4/h=0.2 | 0.641 | 0.781 | 0.662 | 0.165 | 21.9 | 83.9 % | 15.0 % | 1.2 % | 3.51 |
| thr=0.3/min_area=9/h=0.2 | 0.641 | 0.781 | 0.662 | 0.166 | 21.9 | 83.1 % | 15.7 % | 1.1 % | 3.30 |
| thr=0.2/min_area=4/h=0.1 | 0.641 | 0.784 | 0.666 | 0.174 | 24.6 | 84.7 % | 11.0 % | 4.3 % | 5.13 |
| thr=0.5/min_area=1/h=0.1 (untuned default) | 0.587 | 0.715 | 0.607 | 0.248 | 17.9 | 76.4 % | 21.0 % | 2.6 % | 2.09 |

(top 8 of 72 settings by PQ)

## All of fold 2

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6, binary target), s > 0.5, components | 2523 | 0.719 | 0.652 | 0.769 | 0.807 | 0.577 | 0.656 | 0.531 | 0.494 | 0.275 | 23.0 |
| U-Net + contour head (sec. 10.1, gap target), logits | 2523 | 0.719 | 0.658 | 0.774 | 0.809 | 0.574 | 0.682 | 0.556 | 0.571 | 0.303 | 25.2 |
| U-Net + contour head, tuned marker watershed (b) | 2523 | 0.718 | 0.658 | 0.774 | 0.809 | 0.568 | 0.715 | 0.583 | 0.657 | 0.344 | 27.2 |
| sec. 11.1 dist run: layer, converged (predicted markers) | 2523 | 0.707 | 0.647 | 0.762 | 0.811 | 0.580 | 0.791 | 0.641 | 0.653 | 0.239 | 24.3 |
| this model: s > 0.5, components | 2523 | 0.622 | 0.465 | 0.623 | 0.717 | 0.416 | 0.140 | 0.097 | 0.232 | 7.252 | 125.2 |
| this model: layer, converged (predicted markers) | 2523 | 0.717 | 0.658 | 0.775 | 0.804 | 0.586 | 0.792 | 0.645 | 0.666 | 0.186 | 23.0 |
| this model: layer + fallback markers | 2523 | 0.717 | 0.658 | 0.775 | 0.804 | 0.586 | 0.790 | 0.644 | 0.666 | 0.189 | 23.1 |
| this model: layer, ground-truth markers (oracle) | 2523 | 0.780 | 0.710 | 0.832 | 0.809 | 0.598 | 0.877 | 0.725 | 0.777 | 0.129 | 20.7 |
| this model: layer, image-gradient costs | 2523 | 0.519 | 0.236 | 0.405 | 0.625 | 0.274 | 0.542 | 0.332 | 0.497 | 0.281 | 25.3 |
| this model: marker watershed on the contour map | 2523 | 0.626 | 0.471 | 0.629 | 0.716 | 0.421 | 0.709 | 0.497 | 0.580 | 0.284 | 25.3 |
| this model: PW limit, learned costs | 307 | 0.635 | 0.585 | 0.698 | 0.740 | 0.614 | 0.694 | 0.558 | 0.560 | 0.240 | 19.2 |
| this model: PW limit, image-gradient costs | 307 | 0.513 | 0.240 | 0.402 | 0.623 | 0.267 | 0.513 | 0.313 | 0.478 | 0.308 | 26.1 |
| this model: ground truth instances | 2523 | 1.000 | 1.000 | 1.000 | 1.000 | 0.559 | 1.000 | 1.000 | 1.000 | 0.000 | 23.7 |

## Marker quality (predicted markers against the ground-truth nuclei)

- 59872 nuclei in fold 2 (23.7 per patch); predicted markers 25.4 per patch.
- exactly one marker: 85.6 %; none: 12.8 %; several: 1.6 %; markers in background: 4.26 per patch.
- with fallback markers: one 86.0 %, none 12.0 %, several 2.0 %, background 5.08 per patch, 26.5 markers per patch.
- sec. 11.1 dist run: one 83.9 %, none 14.5 %, several 1.6 %, background 3.58 per patch, 24.3 markers per patch.

## Inference cost

- U-Net forward: 2.5 ms per image; converged multi-marker solve (tol 1e-05): 157.7 ms per image at K = 25.4 markers per image (66498 systems in 158 batches of 16; 263 PCG iterations per batch).
- exact K-label PW limit (one CPU core): 0.7 s per patch with the learned costs, 0.6 s with image-gradient costs, K = 26.2; 10845 ambiguous plateaus solved over 307 patches.

## Per tissue type

**Breast**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 749 | 0.722 | 0.596 | 0.756 | 0.780 | 0.585 | 0.690 | 0.547 | 0.550 | 0.198 | 21.2 |
| U-Net + contour head, watershed (b) | 749 | 0.722 | 0.601 | 0.761 | 0.782 | 0.576 | 0.757 | 0.605 | 0.671 | 0.242 | 24.5 |
| sec. 11.1 dist run: layer | 749 | 0.708 | 0.585 | 0.743 | 0.782 | 0.587 | 0.817 | 0.647 | 0.661 | 0.187 | 22.9 |
| s > 0.5, components | 749 | 0.630 | 0.435 | 0.603 | 0.691 | 0.403 | 0.141 | 0.096 | 0.263 | 6.429 | 118.8 |
| layer, converged (predicted markers) | 749 | 0.716 | 0.597 | 0.757 | 0.777 | 0.596 | 0.820 | 0.654 | 0.675 | 0.141 | 21.6 |
| layer + fallback markers | 749 | 0.716 | 0.597 | 0.757 | 0.777 | 0.596 | 0.820 | 0.654 | 0.675 | 0.144 | 21.7 |
| layer, ground-truth markers (oracle) | 749 | 0.776 | 0.649 | 0.815 | 0.786 | 0.606 | 0.902 | 0.731 | 0.774 | 0.106 | 19.5 |
| layer, image-gradient costs | 749 | 0.533 | 0.229 | 0.384 | 0.607 | 0.245 | 0.577 | 0.357 | 0.515 | 0.206 | 23.6 |
| marker watershed on the contour map | 749 | 0.632 | 0.437 | 0.606 | 0.690 | 0.409 | 0.738 | 0.508 | 0.591 | 0.206 | 23.6 |
| PW limit, learned costs | 89 | 0.645 | 0.523 | 0.675 | 0.711 | 0.627 | 0.748 | 0.586 | 0.597 | 0.226 | 18.0 |
| PW limit, image-gradient costs | 89 | 0.544 | 0.240 | 0.391 | 0.608 | 0.229 | 0.567 | 0.349 | 0.510 | 0.165 | 24.1 |
| ground truth instances | 749 | 1.000 | 1.000 | 1.000 | 1.000 | 0.553 | 1.000 | 1.000 | 1.000 | 0.000 | 21.7 |

**Colon**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 468 | 0.698 | 0.617 | 0.738 | 0.788 | 0.558 | 0.547 | 0.431 | 0.349 | 0.274 | 21.1 |
| U-Net + contour head, watershed (b) | 468 | 0.691 | 0.621 | 0.742 | 0.788 | 0.550 | 0.630 | 0.497 | 0.574 | 0.340 | 27.7 |
| sec. 11.1 dist run: layer | 468 | 0.683 | 0.605 | 0.726 | 0.791 | 0.569 | 0.709 | 0.558 | 0.579 | 0.238 | 23.8 |
| s > 0.5, components | 468 | 0.603 | 0.450 | 0.597 | 0.710 | 0.420 | 0.087 | 0.059 | 0.131 | 8.105 | 154.0 |
| layer, converged (predicted markers) | 468 | 0.692 | 0.619 | 0.740 | 0.784 | 0.570 | 0.712 | 0.563 | 0.590 | 0.205 | 22.7 |
| layer + fallback markers | 468 | 0.692 | 0.619 | 0.739 | 0.784 | 0.571 | 0.710 | 0.561 | 0.590 | 0.210 | 22.9 |
| layer, ground-truth markers (oracle) | 468 | 0.751 | 0.667 | 0.793 | 0.790 | 0.580 | 0.823 | 0.662 | 0.726 | 0.150 | 21.3 |
| layer, image-gradient costs | 468 | 0.518 | 0.292 | 0.430 | 0.634 | 0.301 | 0.470 | 0.284 | 0.449 | 0.264 | 24.8 |
| marker watershed on the contour map | 468 | 0.611 | 0.459 | 0.606 | 0.708 | 0.422 | 0.607 | 0.416 | 0.511 | 0.267 | 24.8 |
| PW limit, learned costs | 62 | 0.551 | 0.507 | 0.620 | 0.694 | 0.590 | 0.535 | 0.415 | 0.423 | 0.307 | 22.8 |
| PW limit, image-gradient costs | 62 | 0.484 | 0.284 | 0.415 | 0.620 | 0.272 | 0.392 | 0.237 | 0.399 | 0.231 | 30.5 |
| ground truth instances | 468 | 1.000 | 1.000 | 1.000 | 1.000 | 0.539 | 1.000 | 1.000 | 1.000 | 0.000 | 25.4 |

**HeadNeck**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 169 | 0.672 | 0.658 | 0.744 | 0.835 | 0.648 | 0.640 | 0.519 | 0.556 | 0.424 | 20.2 |
| U-Net + contour head, watershed (b) | 169 | 0.682 | 0.675 | 0.756 | 0.839 | 0.638 | 0.688 | 0.565 | 0.660 | 0.474 | 23.6 |
| sec. 11.1 dist run: layer | 169 | 0.701 | 0.711 | 0.782 | 0.846 | 0.631 | 0.784 | 0.647 | 0.651 | 0.203 | 19.8 |
| s > 0.5, components | 169 | 0.591 | 0.496 | 0.626 | 0.770 | 0.511 | 0.143 | 0.100 | 0.309 | 6.163 | 105.8 |
| layer, converged (predicted markers) | 169 | 0.708 | 0.707 | 0.787 | 0.833 | 0.642 | 0.786 | 0.648 | 0.669 | 0.197 | 18.7 |
| layer + fallback markers | 169 | 0.709 | 0.708 | 0.787 | 0.833 | 0.642 | 0.784 | 0.646 | 0.669 | 0.204 | 18.9 |
| layer, ground-truth markers (oracle) | 169 | 0.773 | 0.764 | 0.847 | 0.836 | 0.652 | 0.878 | 0.733 | 0.779 | 0.142 | 16.3 |
| layer, image-gradient costs | 169 | 0.494 | 0.273 | 0.445 | 0.674 | 0.403 | 0.472 | 0.282 | 0.476 | 0.363 | 21.2 |
| marker watershed on the contour map | 169 | 0.607 | 0.513 | 0.643 | 0.769 | 0.512 | 0.709 | 0.506 | 0.586 | 0.364 | 21.2 |
| ground truth instances | 169 | 1.000 | 1.000 | 1.000 | 1.000 | 0.629 | 1.000 | 1.000 | 1.000 | 0.000 | 18.5 |

**Adrenal_gland**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 148 | 0.716 | 0.676 | 0.774 | 0.808 | 0.554 | 0.694 | 0.582 | 0.655 | 0.378 | 18.4 |
| U-Net + contour head, watershed (b) | 148 | 0.719 | 0.689 | 0.783 | 0.811 | 0.551 | 0.712 | 0.605 | 0.713 | 0.444 | 20.1 |
| sec. 11.1 dist run: layer | 148 | 0.709 | 0.688 | 0.779 | 0.824 | 0.562 | 0.823 | 0.696 | 0.696 | 0.260 | 17.1 |
| s > 0.5, components | 148 | 0.630 | 0.462 | 0.615 | 0.728 | 0.393 | 0.147 | 0.108 | 0.514 | 9.510 | 123.9 |
| layer, converged (predicted markers) | 148 | 0.711 | 0.684 | 0.779 | 0.804 | 0.570 | 0.813 | 0.691 | 0.705 | 0.205 | 15.7 |
| layer + fallback markers | 148 | 0.711 | 0.684 | 0.779 | 0.804 | 0.570 | 0.811 | 0.689 | 0.705 | 0.212 | 15.8 |
| layer, ground-truth markers (oracle) | 148 | 0.770 | 0.728 | 0.827 | 0.808 | 0.588 | 0.883 | 0.758 | 0.796 | 0.166 | 13.8 |
| layer, image-gradient costs | 148 | 0.494 | 0.159 | 0.326 | 0.589 | 0.250 | 0.547 | 0.333 | 0.498 | 0.311 | 18.2 |
| marker watershed on the contour map | 148 | 0.636 | 0.470 | 0.623 | 0.726 | 0.401 | 0.743 | 0.552 | 0.629 | 0.312 | 18.2 |
| ground truth instances | 148 | 1.000 | 1.000 | 1.000 | 1.000 | 0.557 | 1.000 | 1.000 | 1.000 | 0.000 | 16.0 |

## Paired per-patch differences (2523 patches; bootstrap 95 % intervals; F1 / PQ / AJI dataset-level, bootstrapped over patches)

| comparison | IoU | BF₂ | edge align. | F1@0.5 | PQ | AJI |
|---|---|---|---|---|---|---|
| layer − U-Net (sec. 6) logits | -0.002 [-0.005, +0.001] | +0.006 [+0.002, +0.009] | +0.010 [+0.008, +0.011] | +0.136 [+0.131, +0.141] | +0.115 [+0.111, +0.118] | +0.172 [+0.157, +0.185] |
| layer − contour-head U-Net, watershed (b) | -0.001 [-0.004, +0.002] | +0.000 [-0.002, +0.003] | +0.018 [+0.017, +0.020] | +0.077 [+0.074, +0.080] | +0.062 [+0.060, +0.064] | +0.009 [+0.007, +0.011] |
| layer − sec. 11.1 dist run layer | +0.010 [+0.007, +0.013] | +0.013 [+0.009, +0.016] | +0.006 [+0.005, +0.008] | +0.002 [-0.001, +0.004] | +0.004 [+0.002, +0.006] | +0.013 [+0.012, +0.016] |
| layer, ground-truth markers − sec. 11.1 dist run layer, ground-truth markers | -0.079 [-0.083, -0.076] | -0.090 [-0.094, -0.087] | +0.008 [+0.007, +0.009] | -0.081 [-0.085, -0.078] | -0.079 [-0.082, -0.077] | -0.081 [-0.083, -0.078] |
| layer − this model's own logits | +0.094 [+0.091, +0.098] | +0.151 [+0.147, +0.156] | +0.172 [+0.170, +0.175] | +0.652 [+0.646, +0.657] | +0.548 [+0.543, +0.553] | +0.434 [+0.416, +0.449] |
| layer − marker watershed, same markers | +0.090 [+0.087, +0.093] | +0.146 [+0.142, +0.150] | +0.166 [+0.163, +0.168] | +0.083 [+0.080, +0.086] | +0.149 [+0.147, +0.151] | +0.087 [+0.085, +0.088] |
| layer − layer with image costs | +0.198 [+0.194, +0.201] | +0.369 [+0.363, +0.375] | +0.313 [+0.309, +0.317] | +0.250 [+0.245, +0.256] | +0.313 [+0.310, +0.317] | +0.169 [+0.167, +0.172] |
| layer + fallback − U-Net (sec. 6) logits | -0.002 [-0.005, +0.001] | +0.006 [+0.003, +0.009] | +0.010 [+0.008, +0.011] | +0.134 [+0.129, +0.139] | +0.113 [+0.109, +0.117] | +0.172 [+0.157, +0.185] |
| layer + fallback − contour-head U-Net, watershed (b) | -0.001 [-0.004, +0.002] | +0.001 [-0.002, +0.003] | +0.019 [+0.017, +0.020] | +0.075 [+0.072, +0.078] | +0.061 [+0.058, +0.063] | +0.009 [+0.007, +0.011] |
| layer + fallback − layer | -0.000 [-0.000, +0.000] | +0.000 [-0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.002 [-0.002, -0.001] | -0.001 [-0.002, -0.001] | +0.000 [-0.000, +0.000] |
| layer, ground-truth markers − layer | +0.063 [+0.059, +0.068] | +0.057 [+0.053, +0.061] | +0.013 [+0.011, +0.015] | +0.085 [+0.082, +0.089] | +0.080 [+0.077, +0.083] | +0.110 [+0.107, +0.113] |
| on the 307 limit patches: PW limit (learned) − layer | -0.071 [-0.082, -0.057] | -0.066 [-0.076, -0.053] | +0.037 [+0.029, +0.045] | -0.074 [-0.083, -0.064] | -0.062 [-0.069, -0.055] | -0.078 [-0.088, -0.069] |
| on the 307 limit patches: PW limit (learned) − PW limit (image costs) | +0.122 [+0.108, +0.138] | +0.296 [+0.276, +0.316] | +0.348 [+0.334, +0.361] | +0.181 [+0.166, +0.196] | +0.245 [+0.232, +0.259] | +0.082 [+0.068, +0.096] |
| on the 307 limit patches: PW limit (learned) − U-Net (sec. 6) logits | -0.078 [-0.091, -0.064] | -0.066 [-0.078, -0.052] | +0.047 [+0.038, +0.056] | +0.060 [+0.044, +0.077] | +0.049 [+0.036, +0.063] | +0.135 [+0.091, +0.178] |

## By crowding (F1@0.5 / PQ / count error)

| patches | n | U-Net (sec. 6) | contour-head U-Net, watershed (b) | layer | layer + fallback | marker watershed, same markers | PW limit (learned, subset) |
|---|---|---|---|---|---|---|---|
| < 10 nuclei | 486 | 0.608 / 0.485 / 0.68 | 0.596 / 0.479 / 0.81 | 0.704 / 0.568 / 0.44 | 0.701 / 0.565 / 0.46 | 0.587 / 0.408 / 0.79 | 0.623 / 0.491 / 0.29 |
| 10–30 | 1383 | 0.691 / 0.563 / 0.18 | 0.719 / 0.591 / 0.27 | 0.803 / 0.660 / 0.13 | 0.801 / 0.658 / 0.13 | 0.722 / 0.512 / 0.19 | 0.736 / 0.598 / 0.23 |
| 30–60 | 525 | 0.650 / 0.524 / 0.15 | 0.733 / 0.596 / 0.15 | 0.802 / 0.652 / 0.10 | 0.801 / 0.651 / 0.10 | 0.726 / 0.506 / 0.11 | 0.706 / 0.567 / 0.21 |
| > 60 | 129 | 0.588 / 0.469 / 0.24 | 0.700 / 0.562 / 0.13 | 0.765 / 0.614 / 0.15 | 0.763 / 0.612 / 0.15 | 0.674 / 0.458 / 0.13 | 0.611 / 0.484 / 0.30 |

## Marker quality by crowding (nuclei with one / none / several markers; background markers per patch)

| patches | one | none | several | bg markers / patch |
|---|---|---|---|---|
| < 10 nuclei | 85.9 % | 11.6 % | 2.5 % | 2.23 |
| 10–30 | 88.0 % | 10.1 % | 1.9 % | 4.12 |
| 30–60 | 85.6 % | 12.8 % | 1.6 % | 5.48 |
| > 60 | 79.8 % | 19.4 % | 0.8 % | 8.32 |
