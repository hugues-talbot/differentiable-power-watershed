# Instances as labels: multi-marker layer on PanNuke (fold 2 → fold 3)

Run `results_pannuke_instances/dist_f23/instances`: p 5.0 → 20.0, erosion [2, 3], edge target ×1.0, seam weight 5.0, 30 epochs, seed 0, training solve tol 0.0001 / maxit 100; marker head `dist` (mse, rmax 12; markers = h-maxima h 0.2 grown to thr 0.2, min area 16 px), chosen by PQ on 300 patches of fold 1; learned edge scale 2.26.

## Marker post-processing chosen on fold 1 (300 patches): {'mk_thr': 0.2, 'mk_min_area': 16, 'mk_h': 0.2}

| setting | PQ | F1@0.5 | AJI | count err. | n_pred | one | none | several | bg / patch |
|---|---|---|---|---|---|---|---|---|---|
| thr=0.2/min_area=16/h=0.2 | 0.647 | 0.795 | 0.666 | 0.234 | 26.1 | 86.0 % | 11.7 % | 2.3 % | 4.18 |
| thr=0.2/min_area=9/h=0.2 | 0.646 | 0.794 | 0.666 | 0.257 | 26.5 | 86.7 % | 11.1 % | 2.3 % | 4.47 |
| thr=0.2/min_area=4/h=0.2 | 0.644 | 0.791 | 0.665 | 0.264 | 26.8 | 87.0 % | 10.7 % | 2.3 % | 4.73 |
| thr=0.2/min_area=1/h=0.2 | 0.642 | 0.789 | 0.665 | 0.278 | 27.0 | 87.3 % | 10.5 % | 2.3 % | 5.03 |
| thr=0.3/min_area=16/h=0.2 | 0.638 | 0.791 | 0.663 | 0.174 | 24.4 | 83.8 % | 14.1 % | 2.1 % | 3.13 |
| thr=0.3/min_area=9/h=0.2 | 0.637 | 0.790 | 0.664 | 0.191 | 25.1 | 85.0 % | 12.8 % | 2.2 % | 3.46 |
| thr=0.3/min_area=4/h=0.2 | 0.635 | 0.788 | 0.663 | 0.205 | 25.4 | 85.7 % | 12.1 % | 2.2 % | 3.71 |
| thr=0.3/min_area=1/h=0.2 | 0.632 | 0.785 | 0.663 | 0.226 | 26.0 | 86.7 % | 11.0 % | 2.3 % | 4.25 |
| thr=0.5/min_area=1/h=0.1 (untuned default) | 0.568 | 0.722 | 0.610 | 0.154 | 22.8 | 79.0 % | 17.4 % | 3.6 % | 2.24 |

(top 8 of 72 settings by PQ)

## All of fold 3

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| this model: s > 0.5, components | 2722 | 0.583 | 0.395 | 0.567 | 0.697 | 0.389 | 0.027 | 0.019 | 0.137 | 40.536 | 643.7 |
| this model: layer, converged (predicted markers) | 2722 | 0.711 | 0.651 | 0.767 | 0.814 | 0.563 | 0.787 | 0.640 | 0.653 | 0.225 | 26.0 |
| this model: layer + fallback markers | 2722 | 0.707 | 0.648 | 0.763 | 0.814 | 0.564 | 0.772 | 0.627 | 0.652 | 0.292 | 27.4 |
| this model: layer, ground-truth markers (oracle) | 2722 | 0.864 | 0.801 | 0.927 | 0.861 | 0.577 | 0.962 | 0.811 | 0.862 | 0.018 | 24.1 |
| this model: layer, image-gradient costs | 2722 | 0.554 | 0.271 | 0.451 | 0.641 | 0.290 | 0.627 | 0.395 | 0.517 | 0.227 | 26.0 |
| this model: marker watershed on the contour map | 2722 | 0.620 | 0.439 | 0.618 | 0.695 | 0.416 | 0.710 | 0.495 | 0.552 | 0.227 | 26.0 |
| this model: PW limit, learned costs | 307 | 0.700 | 0.628 | 0.751 | 0.802 | 0.550 | 0.773 | 0.618 | 0.625 | 0.197 | 26.9 |
| this model: PW limit, image-gradient costs | 307 | 0.558 | 0.270 | 0.446 | 0.640 | 0.274 | 0.628 | 0.395 | 0.508 | 0.201 | 26.9 |
| this model: ground truth instances | 2722 | 1.000 | 1.000 | 1.000 | 1.000 | 0.548 | 1.000 | 1.000 | 1.000 | 0.000 | 24.5 |

## Marker quality (predicted markers against the ground-truth nuclei)

- 66654 nuclei in fold 2 (24.5 per patch); predicted markers 26.0 per patch.
- exactly one marker: 84.6 %; none: 13.3 %; several: 2.0 %; markers in background: 4.23 per patch.
- with fallback markers: one 85.8 %, none 11.8 %, several 2.4 %, background 5.61 per patch, 27.8 markers per patch.

## Inference cost

- U-Net forward: 1.1 ms per image; converged multi-marker solve (tol 1e-05): 62.6 ms per image at K = 26.0 markers per image (73451 systems in 171 batches of 16; 171 PCG iterations per batch).
- exact K-label PW limit (one CPU core): 0.7 s per patch with the learned costs, 0.8 s with image-gradient costs, K = 26.9; 7237 ambiguous plateaus solved over 307 patches.

## Per tissue type

**Breast**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| s > 0.5, components | 775 | 0.595 | 0.370 | 0.549 | 0.669 | 0.390 | 0.027 | 0.019 | 0.142 | 36.992 | 564.9 |
| layer, converged (predicted markers) | 775 | 0.706 | 0.584 | 0.742 | 0.783 | 0.579 | 0.811 | 0.643 | 0.657 | 0.200 | 22.9 |
| layer + fallback markers | 775 | 0.702 | 0.582 | 0.739 | 0.783 | 0.580 | 0.798 | 0.632 | 0.657 | 0.252 | 23.8 |
| layer, ground-truth markers (oracle) | 775 | 0.855 | 0.745 | 0.911 | 0.838 | 0.591 | 0.965 | 0.806 | 0.853 | 0.018 | 20.8 |
| layer, image-gradient costs | 775 | 0.562 | 0.257 | 0.423 | 0.624 | 0.282 | 0.657 | 0.417 | 0.533 | 0.202 | 22.9 |
| marker watershed on the contour map | 775 | 0.617 | 0.397 | 0.584 | 0.667 | 0.415 | 0.740 | 0.504 | 0.562 | 0.202 | 22.9 |
| PW limit, learned costs | 85 | 0.694 | 0.568 | 0.725 | 0.775 | 0.566 | 0.798 | 0.621 | 0.627 | 0.178 | 22.4 |
| PW limit, image-gradient costs | 85 | 0.579 | 0.276 | 0.435 | 0.632 | 0.264 | 0.662 | 0.419 | 0.528 | 0.180 | 22.4 |
| ground truth instances | 775 | 1.000 | 1.000 | 1.000 | 1.000 | 0.549 | 1.000 | 1.000 | 1.000 | 0.000 | 21.2 |

**Colon**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| s > 0.5, components | 494 | 0.559 | 0.369 | 0.524 | 0.689 | 0.403 | 0.014 | 0.010 | 0.089 | 46.626 | 785.0 |
| layer, converged (predicted markers) | 494 | 0.684 | 0.602 | 0.725 | 0.791 | 0.566 | 0.702 | 0.549 | 0.573 | 0.246 | 24.3 |
| layer + fallback markers | 494 | 0.684 | 0.603 | 0.725 | 0.792 | 0.567 | 0.687 | 0.536 | 0.573 | 0.309 | 25.8 |
| layer, ground-truth markers (oracle) | 494 | 0.855 | 0.776 | 0.912 | 0.854 | 0.576 | 0.947 | 0.778 | 0.847 | 0.019 | 23.5 |
| layer, image-gradient costs | 494 | 0.565 | 0.341 | 0.485 | 0.662 | 0.342 | 0.575 | 0.361 | 0.474 | 0.246 | 24.4 |
| marker watershed on the contour map | 494 | 0.603 | 0.419 | 0.585 | 0.687 | 0.435 | 0.589 | 0.397 | 0.476 | 0.246 | 24.4 |
| PW limit, learned costs | 61 | 0.649 | 0.559 | 0.692 | 0.764 | 0.544 | 0.663 | 0.504 | 0.518 | 0.271 | 30.8 |
| PW limit, image-gradient costs | 61 | 0.540 | 0.313 | 0.472 | 0.642 | 0.306 | 0.565 | 0.357 | 0.448 | 0.273 | 30.8 |
| ground truth instances | 494 | 1.000 | 1.000 | 1.000 | 1.000 | 0.544 | 1.000 | 1.000 | 1.000 | 0.000 | 23.9 |

**HeadNeck**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| s > 0.5, components | 145 | 0.523 | 0.396 | 0.546 | 0.744 | 0.466 | 0.026 | 0.018 | 0.189 | 44.028 | 651.6 |
| layer, converged (predicted markers) | 145 | 0.694 | 0.701 | 0.775 | 0.840 | 0.619 | 0.794 | 0.658 | 0.676 | 0.247 | 24.7 |
| layer + fallback markers | 145 | 0.686 | 0.692 | 0.766 | 0.842 | 0.622 | 0.771 | 0.639 | 0.674 | 0.378 | 26.6 |
| layer, ground-truth markers (oracle) | 145 | 0.863 | 0.853 | 0.940 | 0.884 | 0.627 | 0.966 | 0.826 | 0.870 | 0.022 | 22.5 |
| layer, image-gradient costs | 145 | 0.531 | 0.309 | 0.492 | 0.674 | 0.392 | 0.595 | 0.369 | 0.512 | 0.247 | 24.7 |
| marker watershed on the contour map | 145 | 0.613 | 0.496 | 0.651 | 0.737 | 0.483 | 0.728 | 0.518 | 0.577 | 0.247 | 24.7 |
| ground truth instances | 145 | 1.000 | 1.000 | 1.000 | 1.000 | 0.613 | 1.000 | 1.000 | 1.000 | 0.000 | 22.9 |

**Adrenal_gland**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| s > 0.5, components | 155 | 0.606 | 0.417 | 0.584 | 0.718 | 0.384 | 0.030 | 0.022 | 0.448 | 62.164 | 633.6 |
| layer, converged (predicted markers) | 155 | 0.730 | 0.707 | 0.797 | 0.839 | 0.586 | 0.814 | 0.691 | 0.691 | 0.239 | 16.7 |
| layer + fallback markers | 155 | 0.729 | 0.706 | 0.796 | 0.840 | 0.585 | 0.791 | 0.671 | 0.691 | 0.338 | 17.8 |
| layer, ground-truth markers (oracle) | 155 | 0.878 | 0.840 | 0.941 | 0.874 | 0.610 | 0.969 | 0.843 | 0.877 | 0.018 | 14.9 |
| layer, image-gradient costs | 155 | 0.539 | 0.192 | 0.378 | 0.610 | 0.265 | 0.644 | 0.403 | 0.522 | 0.245 | 16.7 |
| marker watershed on the contour map | 155 | 0.640 | 0.461 | 0.637 | 0.715 | 0.425 | 0.766 | 0.570 | 0.603 | 0.245 | 16.7 |
| ground truth instances | 155 | 1.000 | 1.000 | 1.000 | 1.000 | 0.590 | 1.000 | 1.000 | 1.000 | 0.000 | 15.1 |

## Paired per-patch differences (2722 patches; bootstrap 95 % intervals; F1 / PQ / AJI dataset-level, bootstrapped over patches)

| comparison | IoU | BF₂ | edge align. | F1@0.5 | PQ | AJI |
|---|---|---|---|---|---|---|
| layer − this model's own logits | +0.128 [+0.123, +0.133] | +0.200 [+0.195, +0.206] | +0.178 [+0.176, +0.181] | +0.760 [+0.756, +0.765] | +0.621 [+0.616, +0.626] | +0.515 [+0.506, +0.524] |
| layer − marker watershed, same markers | +0.091 [+0.089, +0.092] | +0.148 [+0.146, +0.151] | +0.146 [+0.145, +0.148] | +0.077 [+0.074, +0.080] | +0.145 [+0.142, +0.147] | +0.101 [+0.099, +0.103] |
| layer − layer with image costs | +0.157 [+0.154, +0.160] | +0.316 [+0.310, +0.321] | +0.272 [+0.269, +0.276] | +0.160 [+0.155, +0.166] | +0.245 [+0.241, +0.249] | +0.136 [+0.133, +0.138] |
| layer + fallback − layer | -0.004 [-0.006, -0.002] | -0.003 [-0.005, -0.001] | +0.000 [+0.000, +0.001] | -0.015 [-0.016, -0.015] | -0.013 [-0.014, -0.012] | -0.000 [-0.001, -0.000] |
| layer, ground-truth markers − layer | +0.153 [+0.149, +0.158] | +0.160 [+0.156, +0.165] | +0.016 [+0.014, +0.018] | +0.175 [+0.170, +0.179] | +0.171 [+0.168, +0.175] | +0.209 [+0.205, +0.214] |
| on the 307 limit patches: PW limit (learned) − layer | -0.016 [-0.018, -0.014] | -0.020 [-0.022, -0.017] | +0.000 [-0.001, +0.002] | -0.008 [-0.011, -0.005] | -0.016 [-0.018, -0.014] | -0.018 [-0.020, -0.016] |
| on the 307 limit patches: PW limit (learned) − PW limit (image costs) | +0.142 [+0.133, +0.151] | +0.305 [+0.288, +0.322] | +0.276 [+0.266, +0.285] | +0.144 [+0.130, +0.162] | +0.223 [+0.211, +0.238] | +0.117 [+0.109, +0.125] |

## By crowding (F1@0.5 / PQ / count error)

| patches | n | U-Net (sec. 6) | contour-head U-Net, watershed (b) | layer | layer + fallback | marker watershed, same markers | PW limit (learned, subset) |
|---|---|---|---|---|---|---|---|
| < 10 nuclei | 520 | – | – | 0.706 / 0.569 / 0.51 | 0.669 / 0.539 / 0.70 | 0.641 / 0.446 / 0.53 | 0.688 / 0.545 / 0.37 |
| 10–30 | 1427 | – | – | 0.791 / 0.645 / 0.18 | 0.772 / 0.629 / 0.23 | 0.730 / 0.514 / 0.18 | 0.787 / 0.636 / 0.18 |
| 30–60 | 630 | – | – | 0.802 / 0.653 / 0.11 | 0.789 / 0.642 / 0.13 | 0.725 / 0.506 / 0.11 | 0.795 / 0.636 / 0.13 |
| > 60 | 145 | – | – | 0.767 / 0.616 / 0.12 | 0.759 / 0.609 / 0.11 | 0.648 / 0.440 / 0.12 | 0.728 / 0.572 / 0.15 |

## Marker quality by crowding (nuclei with one / none / several markers; background markers per patch)

| patches | one | none | several | bg markers / patch |
|---|---|---|---|---|
| < 10 nuclei | 84.9 % | 12.1 % | 3.1 % | 1.88 |
| 10–30 | 86.8 % | 10.9 % | 2.4 % | 3.99 |
| 30–60 | 85.1 % | 12.8 % | 2.1 % | 5.79 |
| > 60 | 79.1 % | 19.9 % | 1.1 % | 8.32 |
