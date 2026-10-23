# Instances as labels: multi-marker layer on PanNuke (fold 3 → fold 1)

Run `results_pannuke_instances/dist_f31/instances`: p 5.0 → 20.0, erosion [2, 3], edge target ×1.0, seam weight 5.0, 30 epochs, seed 0, training solve tol 0.0001 / maxit 100; marker head `dist` (mse, rmax 12; markers = h-maxima h 0.2 grown to thr 0.3, min area 16 px), chosen by PQ on 300 patches of fold 2; learned edge scale 1.98.

## Marker post-processing chosen on fold 2 (300 patches): {'mk_thr': 0.3, 'mk_min_area': 16, 'mk_h': 0.2}

| setting | PQ | F1@0.5 | AJI | count err. | n_pred | one | none | several | bg / patch |
|---|---|---|---|---|---|---|---|---|---|
| thr=0.3/min_area=16/h=0.2 | 0.629 | 0.779 | 0.644 | 0.223 | 23.5 | 82.2 % | 15.6 % | 2.2 % | 3.34 |
| thr=0.2/min_area=16/h=0.2 | 0.628 | 0.775 | 0.639 | 0.289 | 25.2 | 84.6 % | 13.2 % | 2.2 % | 4.46 |
| thr=0.3/min_area=9/h=0.2 | 0.627 | 0.777 | 0.644 | 0.236 | 24.0 | 83.3 % | 14.5 % | 2.3 % | 3.69 |
| thr=0.2/min_area=9/h=0.2 | 0.626 | 0.772 | 0.639 | 0.317 | 25.6 | 85.2 % | 12.6 % | 2.2 % | 4.76 |
| thr=0.3/min_area=4/h=0.2 | 0.625 | 0.776 | 0.644 | 0.249 | 24.3 | 83.9 % | 13.8 % | 2.3 % | 3.91 |
| thr=0.2/min_area=4/h=0.2 | 0.625 | 0.772 | 0.639 | 0.327 | 25.7 | 85.7 % | 12.1 % | 2.2 % | 4.93 |
| thr=0.2/min_area=1/h=0.2 | 0.625 | 0.771 | 0.639 | 0.328 | 25.8 | 86.0 % | 11.8 % | 2.2 % | 5.14 |
| thr=0.3/min_area=1/h=0.2 | 0.624 | 0.775 | 0.644 | 0.253 | 24.4 | 84.8 % | 12.9 % | 2.3 % | 4.36 |
| thr=0.5/min_area=1/h=0.1 (untuned default) | 0.573 | 0.724 | 0.606 | 0.197 | 21.4 | 78.0 % | 18.4 % | 3.6 % | 2.52 |

(top 8 of 72 settings by PQ)

## All of fold 1

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| this model: s > 0.5, components | 2656 | 0.592 | 0.402 | 0.568 | 0.709 | 0.386 | 0.024 | 0.017 | 0.161 | 51.438 | 743.7 |
| this model: layer, converged (predicted markers) | 2656 | 0.709 | 0.634 | 0.751 | 0.797 | 0.559 | 0.787 | 0.636 | 0.655 | 0.204 | 24.0 |
| this model: layer + fallback markers | 2656 | 0.700 | 0.627 | 0.744 | 0.799 | 0.559 | 0.758 | 0.612 | 0.654 | 0.318 | 26.5 |
| this model: layer, ground-truth markers (oracle) | 2656 | 0.866 | 0.799 | 0.925 | 0.861 | 0.576 | 0.962 | 0.811 | 0.862 | 0.017 | 23.4 |
| this model: layer, image-gradient costs | 2656 | 0.502 | 0.218 | 0.367 | 0.597 | 0.276 | 0.515 | 0.308 | 0.472 | 0.208 | 24.1 |
| this model: marker watershed on the contour map | 2656 | 0.634 | 0.453 | 0.627 | 0.705 | 0.421 | 0.723 | 0.512 | 0.560 | 0.209 | 24.1 |
| this model: PW limit, learned costs | 307 | 0.708 | 0.626 | 0.751 | 0.788 | 0.551 | 0.771 | 0.616 | 0.637 | 0.184 | 25.7 |
| this model: PW limit, image-gradient costs | 307 | 0.499 | 0.211 | 0.357 | 0.587 | 0.264 | 0.489 | 0.290 | 0.462 | 0.185 | 25.8 |
| this model: ground truth instances | 2656 | 1.000 | 1.000 | 1.000 | 1.000 | 0.547 | 1.000 | 1.000 | 1.000 | 0.000 | 23.8 |

## Marker quality (predicted markers against the ground-truth nuclei)

- 63218 nuclei in fold 2 (23.8 per patch); predicted markers 24.1 per patch.
- exactly one marker: 82.9 %; none: 15.1 %; several: 2.1 %; markers in background: 3.35 per patch.
- with fallback markers: one 85.5 %, none 11.9 %, several 2.6 %, background 5.63 per patch, 27.3 markers per patch.

## Inference cost

- U-Net forward: 0.9 ms per image; converged multi-marker solve (tol 1e-05): 63.6 ms per image at K = 24.1 markers per image (66641 systems in 166 batches of 16; 188 PCG iterations per batch).
- exact K-label PW limit (one CPU core): 0.8 s per patch with the learned costs, 0.8 s with image-gradient costs, K = 25.8; 6766 ambiguous plateaus solved over 307 patches.

## Per tissue type

**Breast**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| s > 0.5, components | 827 | 0.602 | 0.377 | 0.551 | 0.677 | 0.372 | 0.022 | 0.015 | 0.176 | 48.411 | 793.9 |
| layer, converged (predicted markers) | 827 | 0.703 | 0.566 | 0.721 | 0.763 | 0.553 | 0.808 | 0.635 | 0.656 | 0.142 | 23.0 |
| layer + fallback markers | 827 | 0.699 | 0.564 | 0.719 | 0.764 | 0.553 | 0.782 | 0.614 | 0.655 | 0.216 | 24.9 |
| layer, ground-truth markers (oracle) | 827 | 0.858 | 0.746 | 0.910 | 0.839 | 0.579 | 0.966 | 0.809 | 0.856 | 0.015 | 21.9 |
| layer, image-gradient costs | 827 | 0.510 | 0.210 | 0.349 | 0.581 | 0.248 | 0.540 | 0.325 | 0.486 | 0.145 | 23.1 |
| marker watershed on the contour map | 827 | 0.632 | 0.414 | 0.597 | 0.674 | 0.408 | 0.753 | 0.518 | 0.569 | 0.145 | 23.1 |
| PW limit, learned costs | 92 | 0.707 | 0.559 | 0.718 | 0.759 | 0.559 | 0.811 | 0.629 | 0.644 | 0.137 | 22.4 |
| PW limit, image-gradient costs | 92 | 0.517 | 0.208 | 0.341 | 0.579 | 0.239 | 0.526 | 0.313 | 0.482 | 0.139 | 22.5 |
| ground truth instances | 827 | 1.000 | 1.000 | 1.000 | 1.000 | 0.539 | 1.000 | 1.000 | 1.000 | 0.000 | 22.3 |

**Colon**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| s > 0.5, components | 478 | 0.564 | 0.366 | 0.519 | 0.701 | 0.393 | 0.013 | 0.009 | 0.091 | 57.705 | 915.9 |
| layer, converged (predicted markers) | 478 | 0.675 | 0.580 | 0.703 | 0.775 | 0.547 | 0.705 | 0.550 | 0.574 | 0.217 | 24.7 |
| layer + fallback markers | 478 | 0.664 | 0.571 | 0.694 | 0.776 | 0.551 | 0.680 | 0.530 | 0.573 | 0.325 | 27.2 |
| layer, ground-truth markers (oracle) | 478 | 0.862 | 0.780 | 0.914 | 0.856 | 0.560 | 0.949 | 0.783 | 0.851 | 0.020 | 24.7 |
| layer, image-gradient costs | 478 | 0.502 | 0.263 | 0.387 | 0.610 | 0.303 | 0.447 | 0.267 | 0.431 | 0.218 | 24.8 |
| marker watershed on the contour map | 478 | 0.612 | 0.419 | 0.582 | 0.698 | 0.425 | 0.602 | 0.413 | 0.480 | 0.218 | 24.8 |
| PW limit, learned costs | 60 | 0.657 | 0.554 | 0.686 | 0.751 | 0.531 | 0.651 | 0.500 | 0.536 | 0.277 | 31.5 |
| PW limit, image-gradient costs | 60 | 0.470 | 0.222 | 0.356 | 0.584 | 0.299 | 0.399 | 0.239 | 0.406 | 0.277 | 31.5 |
| ground truth instances | 478 | 1.000 | 1.000 | 1.000 | 1.000 | 0.529 | 1.000 | 1.000 | 1.000 | 0.000 | 25.1 |

**HeadNeck**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| s > 0.5, components | 70 | 0.492 | 0.391 | 0.522 | 0.779 | 0.463 | 0.019 | 0.014 | 0.224 | 153.161 | 798.8 |
| layer, converged (predicted markers) | 70 | 0.669 | 0.683 | 0.748 | 0.849 | 0.615 | 0.801 | 0.659 | 0.663 | 0.429 | 19.3 |
| layer + fallback markers | 70 | 0.641 | 0.656 | 0.723 | 0.851 | 0.624 | 0.759 | 0.623 | 0.661 | 0.715 | 22.3 |
| layer, ground-truth markers (oracle) | 70 | 0.876 | 0.871 | 0.948 | 0.897 | 0.611 | 0.964 | 0.819 | 0.853 | 0.022 | 18.8 |
| layer, image-gradient costs | 70 | 0.470 | 0.276 | 0.422 | 0.677 | 0.404 | 0.430 | 0.249 | 0.442 | 0.427 | 19.3 |
| marker watershed on the contour map | 70 | 0.600 | 0.513 | 0.651 | 0.770 | 0.492 | 0.733 | 0.525 | 0.561 | 0.427 | 19.3 |
| ground truth instances | 70 | 1.000 | 1.000 | 1.000 | 1.000 | 0.601 | 1.000 | 1.000 | 1.000 | 0.000 | 19.2 |

**Adrenal_gland**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| s > 0.5, components | 134 | 0.628 | 0.438 | 0.598 | 0.738 | 0.390 | 0.028 | 0.021 | 0.454 | 66.890 | 743.3 |
| layer, converged (predicted markers) | 134 | 0.735 | 0.697 | 0.789 | 0.820 | 0.590 | 0.820 | 0.689 | 0.718 | 0.212 | 17.4 |
| layer + fallback markers | 134 | 0.733 | 0.696 | 0.788 | 0.824 | 0.587 | 0.770 | 0.645 | 0.717 | 0.343 | 20.2 |
| layer, ground-truth markers (oracle) | 134 | 0.876 | 0.835 | 0.938 | 0.872 | 0.609 | 0.972 | 0.843 | 0.880 | 0.019 | 16.4 |
| layer, image-gradient costs | 134 | 0.478 | 0.137 | 0.284 | 0.561 | 0.267 | 0.510 | 0.298 | 0.478 | 0.215 | 17.5 |
| marker watershed on the contour map | 134 | 0.661 | 0.484 | 0.654 | 0.732 | 0.438 | 0.795 | 0.601 | 0.637 | 0.215 | 17.5 |
| ground truth instances | 134 | 1.000 | 1.000 | 1.000 | 1.000 | 0.593 | 1.000 | 1.000 | 1.000 | 0.000 | 16.6 |

## Paired per-patch differences (2656 patches; bootstrap 95 % intervals; F1 / PQ / AJI dataset-level, bootstrapped over patches)

| comparison | IoU | BF₂ | edge align. | F1@0.5 | PQ | AJI |
|---|---|---|---|---|---|---|
| layer − this model's own logits | +0.116 [+0.111, +0.122] | +0.183 [+0.178, +0.188] | +0.177 [+0.174, +0.179] | +0.762 [+0.758, +0.767] | +0.619 [+0.614, +0.623] | +0.494 [+0.482, +0.507] |
| layer − marker watershed, same markers | +0.074 [+0.072, +0.076] | +0.124 [+0.122, +0.126] | +0.137 [+0.136, +0.139] | +0.063 [+0.059, +0.067] | +0.124 [+0.121, +0.127] | +0.095 [+0.093, +0.097] |
| layer − layer with image costs | +0.207 [+0.204, +0.210] | +0.384 [+0.379, +0.390] | +0.282 [+0.279, +0.286] | +0.272 [+0.265, +0.279] | +0.328 [+0.323, +0.332] | +0.183 [+0.180, +0.186] |
| layer + fallback − layer | -0.009 [-0.012, -0.005] | -0.007 [-0.011, -0.004] | -0.001 [-0.001, -0.001] | -0.029 [-0.030, -0.027] | -0.024 [-0.025, -0.023] | -0.001 [-0.001, -0.001] |
| layer, ground-truth markers − layer | +0.158 [+0.153, +0.162] | +0.174 [+0.169, +0.178] | +0.019 [+0.017, +0.020] | +0.175 [+0.171, +0.179] | +0.175 [+0.171, +0.178] | +0.207 [+0.202, +0.211] |
| on the 307 limit patches: PW limit (learned) − layer | -0.009 [-0.011, -0.007] | -0.008 [-0.011, -0.005] | +0.002 [+0.000, +0.004] | -0.002 [-0.005, +0.001] | -0.010 [-0.012, -0.006] | -0.013 [-0.016, -0.011] |
| on the 307 limit patches: PW limit (learned) − PW limit (image costs) | +0.209 [+0.200, +0.218] | +0.394 [+0.379, +0.411] | +0.287 [+0.277, +0.298] | +0.282 [+0.262, +0.305] | +0.326 [+0.312, +0.345] | +0.174 [+0.166, +0.184] |

## By crowding (F1@0.5 / PQ / count error)

| patches | n | U-Net (sec. 6) | contour-head U-Net, watershed (b) | layer | layer + fallback | marker watershed, same markers | PW limit (learned, subset) |
|---|---|---|---|---|---|---|---|
| < 10 nuclei | 475 | – | – | 0.717 / 0.576 / 0.49 | 0.645 / 0.517 / 0.87 | 0.673 / 0.477 / 0.52 | 0.768 / 0.608 / 0.39 |
| 10–30 | 1464 | – | – | 0.790 / 0.640 / 0.15 | 0.754 / 0.610 / 0.24 | 0.746 / 0.534 / 0.16 | 0.789 / 0.635 / 0.16 |
| 30–60 | 600 | – | – | 0.797 / 0.643 / 0.10 | 0.775 / 0.624 / 0.12 | 0.730 / 0.514 / 0.10 | 0.800 / 0.641 / 0.08 |
| > 60 | 117 | – | – | 0.769 / 0.621 / 0.17 | 0.760 / 0.611 / 0.13 | 0.651 / 0.450 / 0.16 | 0.684 / 0.537 / 0.20 |

## Marker quality by crowding (nuclei with one / none / several markers; background markers per patch)

| patches | one | none | several | bg markers / patch |
|---|---|---|---|---|
| < 10 nuclei | 83.4 % | 14.0 % | 2.5 % | 1.57 |
| 10–30 | 85.1 % | 12.6 % | 2.3 % | 3.29 |
| 30–60 | 83.2 % | 14.6 % | 2.2 % | 4.41 |
| > 60 | 76.2 % | 22.9 % | 0.9 % | 5.84 |
