# Instances as labels: multi-marker layer on PanNuke (fold 1 → fold 2)

Run `results_pannuke_instances/dist_peakneg/instances`: p 5.0 → 20.0, erosion [2, 3], edge target ×1.0, seam weight 5.0, 30 epochs, seed 0, training solve tol 0.0001 / maxit 100, peak loss ×1.0; marker head `dist` (mse, rmax 12; markers = h-maxima h 0.2 grown to thr 0.7, min area 9 px), chosen by PQ on 300 patches of fold 3; learned edge scale 2.01.

## Marker post-processing chosen on fold 3 (300 patches): {'mk_thr': 0.7, 'mk_min_area': 9, 'mk_h': 0.2}

| setting | PQ | F1@0.5 | AJI | count err. | n_pred | one | none | several | bg / patch |
|---|---|---|---|---|---|---|---|---|---|
| thr=0.7/min_area=9/h=0.2 | 0.537 | 0.684 | 0.562 | 0.205 | 20.8 | 70.3 % | 25.3 % | 4.4 % | 1.65 |
| thr=0.6/min_area=9/h=0.2 | 0.535 | 0.682 | 0.565 | 0.190 | 21.7 | 71.0 % | 23.6 % | 5.4 % | 1.80 |
| thr=0.5/min_area=16/h=0.2 | 0.533 | 0.677 | 0.553 | 0.226 | 19.6 | 67.4 % | 28.6 % | 4.0 % | 1.35 |
| thr=0.6/min_area=16/h=0.2 | 0.533 | 0.676 | 0.552 | 0.233 | 19.3 | 67.1 % | 29.4 % | 3.5 % | 1.30 |
| thr=0.5/min_area=9/h=0.2 | 0.531 | 0.678 | 0.565 | 0.185 | 22.2 | 71.1 % | 22.6 % | 6.3 % | 1.89 |
| thr=0.4/min_area=16/h=0.2 | 0.530 | 0.673 | 0.553 | 0.217 | 20.0 | 67.3 % | 28.1 % | 4.6 % | 1.38 |
| thr=0.7/min_area=16/h=0.2 | 0.528 | 0.670 | 0.545 | 0.253 | 18.4 | 65.6 % | 31.6 % | 2.8 % | 1.16 |
| thr=0.4/min_area=9/h=0.2 | 0.524 | 0.669 | 0.563 | 0.186 | 22.9 | 70.6 % | 21.9 % | 7.6 % | 1.99 |
| thr=0.5/min_area=1/h=0.1 (untuned default) | 0.285 | 0.374 | 0.515 | 1.419 | 56.4 | 48.4 % | 5.1 % | 46.4 % | 31.95 |

(top 8 of 72 settings by PQ)

## All of fold 2

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6, binary target), s > 0.5, components | 2523 | 0.719 | 0.652 | 0.769 | 0.807 | 0.577 | 0.656 | 0.531 | 0.494 | 0.275 | 23.0 |
| U-Net + contour head (sec. 10.1, gap target), logits | 2523 | 0.719 | 0.658 | 0.774 | 0.809 | 0.574 | 0.682 | 0.556 | 0.571 | 0.303 | 25.2 |
| U-Net + contour head, tuned marker watershed (b) | 2523 | 0.718 | 0.658 | 0.774 | 0.809 | 0.568 | 0.715 | 0.583 | 0.657 | 0.344 | 27.2 |
| sec. 11.1 dist run: layer, converged (predicted markers) | 2523 | 0.707 | 0.647 | 0.762 | 0.811 | 0.580 | 0.791 | 0.641 | 0.653 | 0.239 | 24.3 |
| this model: s > 0.5, components | 2523 | 0.610 | 0.434 | 0.592 | 0.724 | 0.406 | 0.036 | 0.026 | 0.162 | 34.511 | 503.7 |
| this model: layer, converged (predicted markers) | 2523 | 0.600 | 0.542 | 0.650 | 0.717 | 0.578 | 0.674 | 0.527 | 0.553 | 0.221 | 20.4 |
| this model: layer + fallback markers | 2523 | 0.599 | 0.546 | 0.656 | 0.725 | 0.572 | 0.644 | 0.502 | 0.556 | 0.277 | 24.5 |
| this model: layer, ground-truth markers (oracle) | 2523 | 0.855 | 0.792 | 0.918 | 0.856 | 0.591 | 0.956 | 0.800 | 0.854 | 0.020 | 23.3 |
| this model: layer, image-gradient costs | 2523 | 0.264 | 0.108 | 0.191 | 0.523 | 0.262 | 0.091 | 0.052 | 0.233 | 0.221 | 20.4 |
| this model: marker watershed on the contour map | 2523 | 0.636 | 0.475 | 0.634 | 0.704 | 0.451 | 0.679 | 0.490 | 0.514 | 0.221 | 20.4 |
| this model: PW limit, learned costs | 307 | 0.605 | 0.538 | 0.654 | 0.715 | 0.583 | 0.666 | 0.513 | 0.540 | 0.204 | 21.0 |
| this model: PW limit, image-gradient costs | 307 | 0.235 | 0.107 | 0.177 | 0.518 | 0.274 | 0.071 | 0.041 | 0.196 | 0.204 | 21.0 |
| this model: ground truth instances | 2523 | 1.000 | 1.000 | 1.000 | 1.000 | 0.559 | 1.000 | 1.000 | 1.000 | 0.000 | 23.7 |

## Marker quality (predicted markers against the ground-truth nuclei)

- 59872 nuclei in fold 2 (23.7 per patch); predicted markers 20.4 per patch.
- exactly one marker: 70.1 %; none: 25.4 %; several: 4.6 %; markers in background: 1.52 per patch.
- with fallback markers: one 79.1 %, none 15.7 %, several 5.2 %, background 4.37 per patch, 25.7 markers per patch.
- sec. 11.1 dist run: one 83.9 %, none 14.5 %, several 1.6 %, background 3.58 per patch, 24.3 markers per patch.

## Inference cost

- U-Net forward: 2.5 ms per image; converged multi-marker solve (tol 1e-05): 125.9 ms per image at K = 20.4 markers per image (54090 systems in 158 batches of 16; 256 PCG iterations per batch).
- exact K-label PW limit (one CPU core): 0.7 s per patch with the learned costs, 0.7 s with image-gradient costs, K = 21.0; 4949 ambiguous plateaus solved over 307 patches.

## Per tissue type

**Breast**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 749 | 0.722 | 0.596 | 0.756 | 0.780 | 0.585 | 0.690 | 0.547 | 0.550 | 0.198 | 21.2 |
| U-Net + contour head, watershed (b) | 749 | 0.722 | 0.601 | 0.761 | 0.782 | 0.576 | 0.757 | 0.605 | 0.671 | 0.242 | 24.5 |
| sec. 11.1 dist run: layer | 749 | 0.708 | 0.585 | 0.743 | 0.782 | 0.587 | 0.817 | 0.647 | 0.661 | 0.187 | 22.9 |
| s > 0.5, components | 749 | 0.625 | 0.417 | 0.586 | 0.697 | 0.405 | 0.036 | 0.025 | 0.190 | 31.350 | 491.0 |
| layer, converged (predicted markers) | 749 | 0.599 | 0.476 | 0.624 | 0.690 | 0.564 | 0.704 | 0.533 | 0.557 | 0.179 | 19.6 |
| layer + fallback markers | 749 | 0.598 | 0.480 | 0.629 | 0.695 | 0.561 | 0.668 | 0.505 | 0.558 | 0.223 | 22.9 |
| layer, ground-truth markers (oracle) | 749 | 0.850 | 0.741 | 0.905 | 0.835 | 0.596 | 0.966 | 0.802 | 0.849 | 0.015 | 21.4 |
| layer, image-gradient costs | 749 | 0.274 | 0.093 | 0.174 | 0.507 | 0.220 | 0.106 | 0.060 | 0.255 | 0.179 | 19.6 |
| marker watershed on the contour map | 749 | 0.639 | 0.446 | 0.616 | 0.680 | 0.445 | 0.725 | 0.511 | 0.534 | 0.179 | 19.6 |
| PW limit, learned costs | 89 | 0.621 | 0.473 | 0.633 | 0.689 | 0.572 | 0.719 | 0.537 | 0.565 | 0.176 | 20.2 |
| PW limit, image-gradient costs | 89 | 0.246 | 0.087 | 0.157 | 0.500 | 0.213 | 0.092 | 0.052 | 0.225 | 0.176 | 20.2 |
| ground truth instances | 749 | 1.000 | 1.000 | 1.000 | 1.000 | 0.553 | 1.000 | 1.000 | 1.000 | 0.000 | 21.7 |

**Colon**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 468 | 0.698 | 0.617 | 0.738 | 0.788 | 0.558 | 0.547 | 0.431 | 0.349 | 0.274 | 21.1 |
| U-Net + contour head, watershed (b) | 468 | 0.691 | 0.621 | 0.742 | 0.788 | 0.550 | 0.630 | 0.497 | 0.574 | 0.340 | 27.7 |
| sec. 11.1 dist run: layer | 468 | 0.683 | 0.605 | 0.726 | 0.791 | 0.569 | 0.709 | 0.558 | 0.579 | 0.238 | 23.8 |
| s > 0.5, components | 468 | 0.587 | 0.409 | 0.559 | 0.712 | 0.401 | 0.022 | 0.015 | 0.082 | 34.958 | 581.0 |
| layer, converged (predicted markers) | 468 | 0.538 | 0.474 | 0.579 | 0.680 | 0.566 | 0.552 | 0.419 | 0.459 | 0.239 | 20.2 |
| layer + fallback markers | 468 | 0.538 | 0.481 | 0.588 | 0.687 | 0.559 | 0.529 | 0.400 | 0.462 | 0.260 | 24.1 |
| layer, ground-truth markers (oracle) | 468 | 0.846 | 0.767 | 0.900 | 0.848 | 0.570 | 0.933 | 0.763 | 0.837 | 0.023 | 24.9 |
| layer, image-gradient costs | 468 | 0.283 | 0.162 | 0.231 | 0.539 | 0.280 | 0.072 | 0.041 | 0.214 | 0.239 | 20.2 |
| marker watershed on the contour map | 468 | 0.619 | 0.452 | 0.602 | 0.693 | 0.439 | 0.550 | 0.388 | 0.428 | 0.239 | 20.2 |
| PW limit, learned costs | 62 | 0.512 | 0.460 | 0.568 | 0.668 | 0.553 | 0.512 | 0.378 | 0.414 | 0.264 | 24.3 |
| PW limit, image-gradient costs | 62 | 0.232 | 0.144 | 0.199 | 0.528 | 0.277 | 0.059 | 0.035 | 0.165 | 0.264 | 24.3 |
| ground truth instances | 468 | 1.000 | 1.000 | 1.000 | 1.000 | 0.539 | 1.000 | 1.000 | 1.000 | 0.000 | 25.4 |

**HeadNeck**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 169 | 0.672 | 0.658 | 0.744 | 0.835 | 0.648 | 0.640 | 0.519 | 0.556 | 0.424 | 20.2 |
| U-Net + contour head, watershed (b) | 169 | 0.682 | 0.675 | 0.756 | 0.839 | 0.638 | 0.688 | 0.565 | 0.660 | 0.474 | 23.6 |
| sec. 11.1 dist run: layer | 169 | 0.701 | 0.711 | 0.782 | 0.846 | 0.631 | 0.784 | 0.647 | 0.651 | 0.203 | 19.8 |
| s > 0.5, components | 169 | 0.511 | 0.396 | 0.526 | 0.772 | 0.470 | 0.035 | 0.025 | 0.192 | 35.305 | 443.2 |
| layer, converged (predicted markers) | 169 | 0.601 | 0.602 | 0.672 | 0.753 | 0.647 | 0.645 | 0.508 | 0.538 | 0.219 | 16.2 |
| layer + fallback markers | 169 | 0.584 | 0.591 | 0.665 | 0.768 | 0.659 | 0.603 | 0.474 | 0.542 | 0.308 | 20.4 |
| layer, ground-truth markers (oracle) | 169 | 0.855 | 0.848 | 0.935 | 0.883 | 0.646 | 0.961 | 0.814 | 0.859 | 0.032 | 18.2 |
| layer, image-gradient costs | 169 | 0.299 | 0.188 | 0.265 | 0.584 | 0.372 | 0.030 | 0.016 | 0.185 | 0.219 | 16.2 |
| marker watershed on the contour map | 169 | 0.626 | 0.523 | 0.651 | 0.743 | 0.498 | 0.676 | 0.493 | 0.513 | 0.219 | 16.2 |
| ground truth instances | 169 | 1.000 | 1.000 | 1.000 | 1.000 | 0.629 | 1.000 | 1.000 | 1.000 | 0.000 | 18.5 |

**Adrenal_gland**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 148 | 0.716 | 0.676 | 0.774 | 0.808 | 0.554 | 0.694 | 0.582 | 0.655 | 0.378 | 18.4 |
| U-Net + contour head, watershed (b) | 148 | 0.719 | 0.689 | 0.783 | 0.811 | 0.551 | 0.712 | 0.605 | 0.713 | 0.444 | 20.1 |
| sec. 11.1 dist run: layer | 148 | 0.709 | 0.688 | 0.779 | 0.824 | 0.562 | 0.823 | 0.696 | 0.696 | 0.260 | 17.1 |
| s > 0.5, components | 148 | 0.625 | 0.453 | 0.599 | 0.737 | 0.380 | 0.035 | 0.027 | 0.477 | 52.018 | 562.6 |
| layer, converged (predicted markers) | 148 | 0.620 | 0.591 | 0.681 | 0.733 | 0.578 | 0.728 | 0.595 | 0.613 | 0.265 | 13.8 |
| layer + fallback markers | 148 | 0.624 | 0.600 | 0.692 | 0.743 | 0.563 | 0.681 | 0.553 | 0.619 | 0.324 | 17.6 |
| layer, ground-truth markers (oracle) | 148 | 0.860 | 0.817 | 0.926 | 0.861 | 0.582 | 0.955 | 0.825 | 0.867 | 0.023 | 15.7 |
| layer, image-gradient costs | 148 | 0.194 | 0.034 | 0.094 | 0.484 | 0.289 | 0.029 | 0.017 | 0.196 | 0.265 | 13.8 |
| marker watershed on the contour map | 148 | 0.630 | 0.491 | 0.639 | 0.708 | 0.456 | 0.753 | 0.581 | 0.593 | 0.265 | 13.8 |
| ground truth instances | 148 | 1.000 | 1.000 | 1.000 | 1.000 | 0.557 | 1.000 | 1.000 | 1.000 | 0.000 | 16.0 |

## Paired per-patch differences (2523 patches; bootstrap 95 % intervals; F1 / PQ / AJI dataset-level, bootstrapped over patches)

| comparison | IoU | BF₂ | edge align. | F1@0.5 | PQ | AJI |
|---|---|---|---|---|---|---|
| layer − U-Net (sec. 6) logits | -0.118 [-0.124, -0.113] | -0.119 [-0.124, -0.114] | +0.002 [-0.000, +0.004] | +0.017 [+0.011, +0.024] | -0.004 [-0.010, +0.002] | +0.058 [+0.042, +0.072] |
| layer − contour-head U-Net, watershed (b) | -0.118 [-0.123, -0.113] | -0.124 [-0.129, -0.119] | +0.012 [+0.009, +0.014] | -0.041 [-0.046, -0.036] | -0.056 [-0.061, -0.052] | -0.105 [-0.109, -0.100] |
| layer − sec. 11.1 dist run layer | -0.106 [-0.112, -0.101] | -0.112 [-0.117, -0.106] | -0.001 [-0.004, +0.001] | -0.117 [-0.122, -0.111] | -0.115 [-0.119, -0.110] | -0.100 [-0.105, -0.096] |
| layer, ground-truth markers − sec. 11.1 dist run layer, ground-truth markers | -0.004 [-0.005, -0.003] | -0.004 [-0.006, -0.003] | -0.001 [-0.001, -0.000] | -0.003 [-0.004, -0.002] | -0.005 [-0.006, -0.004] | -0.003 [-0.004, -0.002] |
| layer − this model's own logits | -0.010 [-0.017, -0.003] | +0.058 [+0.050, +0.065] | +0.178 [+0.175, +0.181] | +0.637 [+0.631, +0.644] | +0.501 [+0.494, +0.507] | +0.390 [+0.375, +0.405] |
| layer − marker watershed, same markers | -0.036 [-0.039, -0.033] | +0.016 [+0.013, +0.019] | +0.127 [+0.125, +0.129] | -0.005 [-0.010, +0.001] | +0.037 [+0.032, +0.042] | +0.038 [+0.034, +0.043] |
| layer − layer with image costs | +0.336 [+0.331, +0.341] | +0.459 [+0.452, +0.465] | +0.316 [+0.310, +0.321] | +0.583 [+0.576, +0.591] | +0.475 [+0.469, +0.480] | +0.319 [+0.315, +0.323] |
| layer + fallback − U-Net (sec. 6) logits | -0.120 [-0.124, -0.116] | -0.113 [-0.117, -0.109] | -0.005 [-0.007, -0.003] | -0.013 [-0.020, -0.005] | -0.029 [-0.035, -0.023] | +0.061 [+0.045, +0.076] |
| layer + fallback − contour-head U-Net, watershed (b) | -0.119 [-0.123, -0.115] | -0.118 [-0.122, -0.114] | +0.004 [+0.002, +0.006] | -0.071 [-0.076, -0.066] | -0.081 [-0.086, -0.077] | -0.102 [-0.106, -0.097] |
| layer + fallback − layer | -0.001 [-0.005, +0.002] | +0.006 [+0.002, +0.010] | -0.008 [-0.009, -0.007] | -0.030 [-0.032, -0.028] | -0.025 [-0.026, -0.024] | +0.003 [+0.003, +0.004] |
| layer, ground-truth markers − layer | +0.255 [+0.249, +0.260] | +0.268 [+0.262, +0.274] | +0.012 [+0.010, +0.014] | +0.282 [+0.274, +0.288] | +0.273 [+0.266, +0.279] | +0.302 [+0.296, +0.307] |
| on the 307 limit patches: PW limit (learned) − layer | +0.013 [+0.009, +0.016] | +0.011 [+0.006, +0.015] | +0.006 [+0.004, +0.009] | +0.013 [+0.008, +0.018] | +0.004 [-0.000, +0.008] | +0.004 [+0.001, +0.007] |
| on the 307 limit patches: PW limit (learned) − PW limit (image costs) | +0.370 [+0.353, +0.386] | +0.477 [+0.456, +0.496] | +0.310 [+0.293, +0.326] | +0.595 [+0.571, +0.619] | +0.472 [+0.453, +0.494] | +0.344 [+0.331, +0.359] |
| on the 307 limit patches: PW limit (learned) − U-Net (sec. 6) logits | -0.109 [-0.120, -0.096] | -0.109 [-0.121, -0.096] | +0.016 [+0.009, +0.024] | +0.033 [+0.014, +0.051] | +0.004 [-0.012, +0.018] | +0.115 [+0.058, +0.165] |

## By crowding (F1@0.5 / PQ / count error)

| patches | n | U-Net (sec. 6) | contour-head U-Net, watershed (b) | layer | layer + fallback | marker watershed, same markers | PW limit (learned, subset) |
|---|---|---|---|---|---|---|---|
| < 10 nuclei | 486 | 0.608 / 0.485 / 0.68 | 0.596 / 0.479 / 0.81 | 0.568 / 0.437 / 0.41 | 0.491 / 0.376 / 0.74 | 0.630 / 0.455 / 0.41 | 0.545 / 0.411 / 0.27 |
| 10–30 | 1383 | 0.691 / 0.563 / 0.18 | 0.719 / 0.591 / 0.27 | 0.661 / 0.514 / 0.18 | 0.623 / 0.483 / 0.19 | 0.705 / 0.514 / 0.18 | 0.686 / 0.529 / 0.18 |
| 30–60 | 525 | 0.650 / 0.524 / 0.15 | 0.733 / 0.596 / 0.15 | 0.686 / 0.535 / 0.16 | 0.664 / 0.516 / 0.12 | 0.687 / 0.492 / 0.16 | 0.681 / 0.522 / 0.16 |
| > 60 | 129 | 0.588 / 0.469 / 0.24 | 0.700 / 0.562 / 0.13 | 0.705 / 0.564 / 0.26 | 0.697 / 0.556 / 0.16 | 0.607 / 0.431 / 0.26 | 0.625 / 0.484 / 0.29 |

## Marker quality by crowding (nuclei with one / none / several markers; background markers per patch)

| patches | one | none | several | bg markers / patch |
|---|---|---|---|---|
| < 10 nuclei | 62.9 % | 31.4 % | 5.7 % | 0.63 |
| 10–30 | 70.7 % | 23.4 % | 5.9 % | 1.45 |
| 30–60 | 71.5 % | 24.1 % | 4.4 % | 2.18 |
| > 60 | 67.4 % | 31.0 % | 1.6 % | 2.98 |
