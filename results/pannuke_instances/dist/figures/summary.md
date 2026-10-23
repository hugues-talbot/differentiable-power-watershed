# Instances as labels: multi-marker layer on PanNuke (fold 1 → fold 2)

Run `results_pannuke_instances/dist/instances`: p 5.0 → 20.0, erosion [2, 3], edge target ×1.0, seam weight 5.0, 30 epochs, seed 0, training solve tol 0.0001 / maxit 100; marker head `dist` (mse, rmax 12; markers = h-maxima h 0.2 grown to thr 0.2, min area 16 px), chosen by PQ on 300 patches of fold 3; learned edge scale 2.14.

## Marker post-processing chosen on fold 3 (300 patches): {'mk_thr': 0.2, 'mk_min_area': 16, 'mk_h': 0.2}

| setting | PQ | F1@0.5 | AJI | count err. | n_pred | one | none | several | bg / patch |
|---|---|---|---|---|---|---|---|---|---|
| thr=0.2/min_area=16/h=0.2 | 0.646 | 0.791 | 0.655 | 0.191 | 24.8 | 84.2 % | 14.5 % | 1.4 % | 3.80 |
| thr=0.2/min_area=9/h=0.2 | 0.645 | 0.791 | 0.655 | 0.199 | 25.2 | 85.0 % | 13.6 % | 1.4 % | 4.01 |
| thr=0.2/min_area=4/h=0.2 | 0.644 | 0.790 | 0.654 | 0.206 | 25.4 | 85.3 % | 13.4 % | 1.4 % | 4.16 |
| thr=0.2/min_area=1/h=0.2 | 0.640 | 0.786 | 0.653 | 0.222 | 25.8 | 85.8 % | 12.9 % | 1.4 % | 4.58 |
| thr=0.3/min_area=16/h=0.2 | 0.638 | 0.787 | 0.654 | 0.168 | 23.3 | 81.7 % | 17.0 % | 1.3 % | 2.95 |
| thr=0.3/min_area=9/h=0.2 | 0.638 | 0.787 | 0.654 | 0.169 | 23.7 | 82.7 % | 16.0 % | 1.3 % | 3.13 |
| thr=0.3/min_area=4/h=0.2 | 0.637 | 0.787 | 0.654 | 0.177 | 24.1 | 83.5 % | 15.2 % | 1.4 % | 3.33 |
| thr=0.3/min_area=1/h=0.2 | 0.633 | 0.783 | 0.653 | 0.191 | 24.8 | 84.9 % | 13.7 % | 1.4 % | 3.90 |
| thr=0.5/min_area=1/h=0.1 (untuned default) | 0.570 | 0.722 | 0.603 | 0.185 | 21.1 | 75.2 % | 22.1 % | 2.7 % | 1.94 |

(top 8 of 72 settings by PQ)

## All of fold 2

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6, binary target), s > 0.5, components | 2523 | 0.719 | 0.652 | 0.769 | 0.807 | 0.577 | 0.656 | 0.531 | 0.494 | 0.275 | 23.0 |
| U-Net + contour head (sec. 10.1, gap target), logits | 2523 | 0.719 | 0.658 | 0.774 | 0.809 | 0.574 | 0.682 | 0.556 | 0.571 | 0.303 | 25.2 |
| U-Net + contour head, tuned marker watershed (b) | 2523 | 0.718 | 0.658 | 0.774 | 0.809 | 0.568 | 0.715 | 0.583 | 0.657 | 0.344 | 27.2 |
| sec. 11 run: layer, converged (predicted markers) | 2523 | 0.706 | 0.643 | 0.759 | 0.795 | 0.585 | 0.681 | 0.554 | 0.652 | 0.460 | 28.6 |
| this model: s > 0.5, components | 2523 | 0.585 | 0.395 | 0.567 | 0.701 | 0.395 | 0.032 | 0.022 | 0.164 | 40.548 | 559.7 |
| this model: layer, converged (predicted markers) | 2523 | 0.707 | 0.647 | 0.762 | 0.811 | 0.580 | 0.791 | 0.641 | 0.653 | 0.239 | 24.3 |
| this model: layer + fallback markers | 2523 | 0.704 | 0.645 | 0.760 | 0.812 | 0.582 | 0.776 | 0.629 | 0.652 | 0.311 | 25.7 |
| this model: layer, ground-truth markers (oracle) | 2523 | 0.859 | 0.796 | 0.922 | 0.858 | 0.591 | 0.959 | 0.805 | 0.857 | 0.020 | 23.3 |
| this model: layer, image-gradient costs | 2523 | 0.547 | 0.266 | 0.446 | 0.643 | 0.299 | 0.613 | 0.387 | 0.518 | 0.241 | 24.3 |
| this model: marker watershed on the contour map | 2523 | 0.620 | 0.436 | 0.614 | 0.698 | 0.422 | 0.709 | 0.496 | 0.556 | 0.241 | 24.3 |
| this model: PW limit, learned costs | 307 | 0.683 | 0.607 | 0.728 | 0.790 | 0.574 | 0.758 | 0.603 | 0.611 | 0.255 | 25.0 |
| this model: PW limit, image-gradient costs | 307 | 0.538 | 0.264 | 0.436 | 0.639 | 0.289 | 0.588 | 0.370 | 0.499 | 0.256 | 25.0 |
| this model: ground truth instances | 2523 | 1.000 | 1.000 | 1.000 | 1.000 | 0.559 | 1.000 | 1.000 | 1.000 | 0.000 | 23.7 |

## Marker quality (predicted markers against the ground-truth nuclei)

- 59872 nuclei in fold 2 (23.7 per patch); predicted markers 24.3 per patch.
- exactly one marker: 83.9 %; none: 14.5 %; several: 1.6 %; markers in background: 3.58 per patch.
- with fallback markers: one 85.4 %, none 12.6 %, several 2.0 %, background 4.96 per patch, 26.2 markers per patch.
- sec. 11 run: one 73.2 %, none 17.4 %, several 9.5 %, background 5.88 per patch, 30.5 markers per patch.

## Inference cost

- U-Net forward: 0.8 ms per image; converged multi-marker solve (tol 1e-05): 94.3 ms per image at K = 24.3 markers per image (63768 systems in 158 batches of 16; 177 PCG iterations per batch).
- exact K-label PW limit (one CPU core): 0.7 s per patch with the learned costs, 0.8 s with image-gradient costs, K = 25.0; 6894 ambiguous plateaus solved over 307 patches.

## Per tissue type

**Breast**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 749 | 0.722 | 0.596 | 0.756 | 0.780 | 0.585 | 0.690 | 0.547 | 0.550 | 0.198 | 21.2 |
| U-Net + contour head, watershed (b) | 749 | 0.722 | 0.601 | 0.761 | 0.782 | 0.576 | 0.757 | 0.605 | 0.671 | 0.242 | 24.5 |
| sec. 11 run: layer | 749 | 0.710 | 0.587 | 0.745 | 0.772 | 0.593 | 0.716 | 0.569 | 0.661 | 0.372 | 26.9 |
| s > 0.5, components | 749 | 0.601 | 0.375 | 0.555 | 0.673 | 0.387 | 0.031 | 0.021 | 0.171 | 34.803 | 531.2 |
| layer, converged (predicted markers) | 749 | 0.708 | 0.585 | 0.743 | 0.782 | 0.587 | 0.817 | 0.647 | 0.661 | 0.187 | 22.9 |
| layer + fallback markers | 749 | 0.707 | 0.586 | 0.743 | 0.782 | 0.587 | 0.805 | 0.637 | 0.661 | 0.237 | 23.9 |
| layer, ground-truth markers (oracle) | 749 | 0.853 | 0.743 | 0.909 | 0.838 | 0.595 | 0.967 | 0.806 | 0.852 | 0.015 | 21.4 |
| layer, image-gradient costs | 749 | 0.560 | 0.256 | 0.421 | 0.627 | 0.274 | 0.650 | 0.413 | 0.536 | 0.188 | 22.9 |
| marker watershed on the contour map | 749 | 0.621 | 0.398 | 0.585 | 0.671 | 0.410 | 0.740 | 0.504 | 0.567 | 0.188 | 22.9 |
| PW limit, learned costs | 89 | 0.702 | 0.554 | 0.715 | 0.763 | 0.580 | 0.802 | 0.622 | 0.635 | 0.142 | 23.5 |
| PW limit, image-gradient costs | 89 | 0.573 | 0.264 | 0.426 | 0.627 | 0.258 | 0.637 | 0.403 | 0.531 | 0.143 | 23.5 |
| ground truth instances | 749 | 1.000 | 1.000 | 1.000 | 1.000 | 0.553 | 1.000 | 1.000 | 1.000 | 0.000 | 21.7 |

**Colon**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 468 | 0.698 | 0.617 | 0.738 | 0.788 | 0.558 | 0.547 | 0.431 | 0.349 | 0.274 | 21.1 |
| U-Net + contour head, watershed (b) | 468 | 0.691 | 0.621 | 0.742 | 0.788 | 0.550 | 0.630 | 0.497 | 0.574 | 0.340 | 27.7 |
| sec. 11 run: layer | 468 | 0.681 | 0.602 | 0.724 | 0.773 | 0.572 | 0.570 | 0.451 | 0.584 | 0.698 | 32.9 |
| s > 0.5, components | 468 | 0.553 | 0.363 | 0.523 | 0.691 | 0.402 | 0.019 | 0.013 | 0.090 | 43.640 | 669.7 |
| layer, converged (predicted markers) | 468 | 0.683 | 0.605 | 0.726 | 0.791 | 0.569 | 0.709 | 0.558 | 0.579 | 0.238 | 23.8 |
| layer + fallback markers | 468 | 0.681 | 0.603 | 0.725 | 0.791 | 0.572 | 0.695 | 0.547 | 0.580 | 0.300 | 25.2 |
| layer, ground-truth markers (oracle) | 468 | 0.850 | 0.771 | 0.905 | 0.850 | 0.569 | 0.939 | 0.771 | 0.841 | 0.025 | 24.8 |
| layer, image-gradient costs | 468 | 0.549 | 0.319 | 0.463 | 0.652 | 0.330 | 0.545 | 0.341 | 0.471 | 0.239 | 23.8 |
| marker watershed on the contour map | 468 | 0.604 | 0.419 | 0.585 | 0.688 | 0.429 | 0.598 | 0.409 | 0.484 | 0.239 | 23.8 |
| PW limit, learned costs | 62 | 0.653 | 0.572 | 0.696 | 0.763 | 0.541 | 0.630 | 0.484 | 0.503 | 0.221 | 29.1 |
| PW limit, image-gradient costs | 62 | 0.518 | 0.312 | 0.449 | 0.639 | 0.303 | 0.480 | 0.299 | 0.422 | 0.221 | 29.1 |
| ground truth instances | 468 | 1.000 | 1.000 | 1.000 | 1.000 | 0.539 | 1.000 | 1.000 | 1.000 | 0.000 | 25.4 |

**HeadNeck**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 169 | 0.672 | 0.658 | 0.744 | 0.835 | 0.648 | 0.640 | 0.519 | 0.556 | 0.424 | 20.2 |
| U-Net + contour head, watershed (b) | 169 | 0.682 | 0.675 | 0.756 | 0.839 | 0.638 | 0.688 | 0.565 | 0.660 | 0.474 | 23.6 |
| sec. 11 run: layer | 169 | 0.688 | 0.687 | 0.759 | 0.816 | 0.636 | 0.664 | 0.547 | 0.641 | 0.354 | 22.1 |
| s > 0.5, components | 169 | 0.495 | 0.376 | 0.515 | 0.762 | 0.472 | 0.032 | 0.023 | 0.238 | 45.463 | 485.3 |
| layer, converged (predicted markers) | 169 | 0.701 | 0.711 | 0.782 | 0.846 | 0.631 | 0.784 | 0.647 | 0.651 | 0.203 | 19.8 |
| layer + fallback markers | 169 | 0.670 | 0.679 | 0.751 | 0.849 | 0.647 | 0.758 | 0.625 | 0.650 | 0.371 | 21.5 |
| layer, ground-truth markers (oracle) | 169 | 0.864 | 0.858 | 0.946 | 0.888 | 0.651 | 0.964 | 0.819 | 0.862 | 0.026 | 18.2 |
| layer, image-gradient costs | 169 | 0.540 | 0.326 | 0.501 | 0.685 | 0.405 | 0.553 | 0.339 | 0.493 | 0.206 | 19.8 |
| marker watershed on the contour map | 169 | 0.628 | 0.512 | 0.658 | 0.756 | 0.488 | 0.713 | 0.510 | 0.560 | 0.206 | 19.8 |
| ground truth instances | 169 | 1.000 | 1.000 | 1.000 | 1.000 | 0.629 | 1.000 | 1.000 | 1.000 | 0.000 | 18.5 |

**Adrenal_gland**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 148 | 0.716 | 0.676 | 0.774 | 0.808 | 0.554 | 0.694 | 0.582 | 0.655 | 0.378 | 18.4 |
| U-Net + contour head, watershed (b) | 148 | 0.719 | 0.689 | 0.783 | 0.811 | 0.551 | 0.712 | 0.605 | 0.713 | 0.444 | 20.1 |
| sec. 11 run: layer | 148 | 0.714 | 0.688 | 0.780 | 0.809 | 0.571 | 0.726 | 0.615 | 0.695 | 0.394 | 19.1 |
| s > 0.5, components | 148 | 0.604 | 0.413 | 0.576 | 0.715 | 0.362 | 0.032 | 0.024 | 0.458 | 60.639 | 605.9 |
| layer, converged (predicted markers) | 148 | 0.709 | 0.688 | 0.779 | 0.824 | 0.562 | 0.823 | 0.696 | 0.696 | 0.260 | 17.1 |
| layer + fallback markers | 148 | 0.708 | 0.686 | 0.778 | 0.825 | 0.562 | 0.800 | 0.675 | 0.695 | 0.343 | 18.4 |
| layer, ground-truth markers (oracle) | 148 | 0.866 | 0.826 | 0.930 | 0.866 | 0.583 | 0.961 | 0.833 | 0.870 | 0.026 | 15.6 |
| layer, image-gradient costs | 148 | 0.516 | 0.184 | 0.365 | 0.607 | 0.266 | 0.631 | 0.395 | 0.519 | 0.264 | 17.1 |
| marker watershed on the contour map | 148 | 0.627 | 0.447 | 0.617 | 0.711 | 0.402 | 0.767 | 0.572 | 0.613 | 0.264 | 17.1 |
| ground truth instances | 148 | 1.000 | 1.000 | 1.000 | 1.000 | 0.557 | 1.000 | 1.000 | 1.000 | 0.000 | 16.0 |

## Paired per-patch differences (2523 patches; bootstrap 95 % intervals; F1 / PQ / AJI dataset-level, bootstrapped over patches)

| comparison | IoU | BF₂ | edge align. | F1@0.5 | PQ | AJI |
|---|---|---|---|---|---|---|
| layer − U-Net (sec. 6) logits | -0.012 [-0.016, -0.009] | -0.007 [-0.011, -0.004] | +0.003 [+0.002, +0.005] | +0.134 [+0.129, +0.139] | +0.111 [+0.107, +0.114] | +0.158 [+0.143, +0.172] |
| layer − contour-head U-Net, watershed (b) | -0.011 [-0.014, -0.008] | -0.012 [-0.015, -0.009] | +0.012 [+0.010, +0.014] | +0.076 [+0.072, +0.079] | +0.058 [+0.056, +0.061] | -0.005 [-0.007, -0.002] |
| layer − sec. 11 run layer | +0.001 [-0.003, +0.004] | +0.003 [-0.000, +0.007] | -0.006 [-0.007, -0.005] | +0.110 [+0.105, +0.115] | +0.087 [+0.083, +0.091] | +0.001 [-0.002, +0.003] |
| layer, ground-truth markers − sec. 11 run layer, ground-truth markers | -0.000 [-0.001, +0.001] | +0.000 [-0.001, +0.001] | +0.000 [-0.000, +0.001] | -0.000 [-0.002, +0.001] | -0.000 [-0.001, +0.001] | -0.000 [-0.001, +0.000] |
| layer − this model's own logits | +0.122 [+0.117, +0.128] | +0.195 [+0.189, +0.200] | +0.190 [+0.188, +0.193] | +0.759 [+0.753, +0.763] | +0.619 [+0.614, +0.624] | +0.489 [+0.475, +0.503] |
| layer − marker watershed, same markers | +0.086 [+0.085, +0.088] | +0.148 [+0.145, +0.150] | +0.159 [+0.157, +0.161] | +0.081 [+0.078, +0.085] | +0.145 [+0.143, +0.148] | +0.096 [+0.095, +0.098] |
| layer − layer with image costs | +0.159 [+0.156, +0.162] | +0.316 [+0.311, +0.321] | +0.281 [+0.278, +0.285] | +0.178 [+0.172, +0.184] | +0.254 [+0.250, +0.259] | +0.135 [+0.132, +0.137] |
| layer + fallback − U-Net (sec. 6) logits | -0.015 [-0.017, -0.012] | -0.009 [-0.012, -0.006] | +0.004 [+0.003, +0.006] | +0.120 [+0.115, +0.125] | +0.098 [+0.094, +0.102] | +0.158 [+0.143, +0.172] |
| layer + fallback − contour-head U-Net, watershed (b) | -0.014 [-0.017, -0.011] | -0.014 [-0.017, -0.011] | +0.013 [+0.011, +0.015] | +0.061 [+0.058, +0.064] | +0.046 [+0.043, +0.048] | -0.005 [-0.007, -0.003] |
| layer + fallback − layer | -0.002 [-0.005, -0.001] | -0.002 [-0.004, +0.000] | +0.000 [-0.000, +0.001] | -0.014 [-0.015, -0.014] | -0.013 [-0.013, -0.012] | -0.000 [-0.000, -0.000] |
| layer, ground-truth markers − layer | +0.152 [+0.147, +0.158] | +0.160 [+0.155, +0.166] | +0.012 [+0.010, +0.014] | +0.168 [+0.164, +0.173] | +0.163 [+0.160, +0.167] | +0.205 [+0.201, +0.209] |
| on the 307 limit patches: PW limit (learned) − layer | -0.014 [-0.016, -0.012] | -0.020 [-0.023, -0.017] | -0.000 [-0.002, +0.001] | -0.008 [-0.010, -0.005] | -0.016 [-0.018, -0.014] | -0.018 [-0.020, -0.016] |
| on the 307 limit patches: PW limit (learned) − PW limit (image costs) | +0.145 [+0.136, +0.155] | +0.293 [+0.276, +0.309] | +0.285 [+0.274, +0.296] | +0.170 [+0.156, +0.187] | +0.233 [+0.221, +0.246] | +0.112 [+0.105, +0.120] |
| on the 307 limit patches: PW limit (learned) − U-Net (sec. 6) logits | -0.030 [-0.040, -0.021] | -0.035 [-0.046, -0.025] | +0.005 [-0.002, +0.011] | +0.125 [+0.109, +0.140] | +0.094 [+0.081, +0.106] | +0.186 [+0.132, +0.229] |

## By crowding (F1@0.5 / PQ / count error)

| patches | n | U-Net (sec. 6) | contour-head U-Net, watershed (b) | layer | layer + fallback | marker watershed, same markers | PW limit (learned, subset) |
|---|---|---|---|---|---|---|---|
| < 10 nuclei | 486 | 0.608 / 0.485 / 0.68 | 0.596 / 0.479 / 0.81 | 0.689 / 0.553 / 0.64 | 0.646 / 0.517 / 0.90 | 0.622 / 0.431 / 0.65 | 0.628 / 0.482 / 0.69 |
| 10–30 | 1383 | 0.691 / 0.563 / 0.18 | 0.719 / 0.591 / 0.27 | 0.802 / 0.655 / 0.16 | 0.784 / 0.640 / 0.20 | 0.737 / 0.521 / 0.16 | 0.793 / 0.635 / 0.16 |
| 30–60 | 525 | 0.650 / 0.524 / 0.15 | 0.733 / 0.596 / 0.15 | 0.801 / 0.648 / 0.10 | 0.791 / 0.638 / 0.11 | 0.715 / 0.499 / 0.10 | 0.769 / 0.611 / 0.10 |
| > 60 | 129 | 0.588 / 0.469 / 0.24 | 0.700 / 0.562 / 0.13 | 0.763 / 0.615 / 0.15 | 0.759 / 0.610 / 0.13 | 0.644 / 0.442 / 0.15 | 0.695 / 0.547 / 0.19 |

## Marker quality by crowding (nuclei with one / none / several markers; background markers per patch)

| patches | one | none | several | bg markers / patch |
|---|---|---|---|---|
| < 10 nuclei | 83.3 % | 14.3 % | 2.3 % | 1.81 |
| 10–30 | 86.7 % | 11.4 % | 1.9 % | 3.48 |
| 30–60 | 84.1 % | 14.3 % | 1.6 % | 4.73 |
| > 60 | 77.1 % | 22.2 % | 0.7 % | 6.62 |
