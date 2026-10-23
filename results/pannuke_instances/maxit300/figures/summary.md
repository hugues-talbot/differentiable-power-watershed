# Instances as labels: multi-marker layer on PanNuke (fold 1 → fold 2)

Run `results_pannuke_instances/maxit300/instances`: p 5.0 → 20.0, erosion [2, 3], edge target ×1.0, seam weight 5.0, 30 epochs, training solve tol 0.0001 / maxit 300; marker head `bce` (thr 0.5, min area 1 px); learned edge scale 2.09.

## All of fold 2

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6, binary target), s > 0.5, components | 2523 | 0.719 | 0.652 | 0.769 | 0.807 | 0.577 | 0.656 | 0.531 | 0.494 | 0.275 | 23.0 |
| U-Net + contour head (sec. 10.1, gap target), logits | 2523 | 0.719 | 0.658 | 0.774 | 0.809 | 0.574 | 0.682 | 0.556 | 0.571 | 0.303 | 25.2 |
| U-Net + contour head, tuned marker watershed (b) | 2523 | 0.718 | 0.658 | 0.774 | 0.809 | 0.568 | 0.715 | 0.583 | 0.657 | 0.344 | 27.2 |
| sec. 11 run: layer, converged (BCE marker head, thr 0.5) | 2523 | 0.706 | 0.643 | 0.759 | 0.795 | 0.585 | 0.681 | 0.554 | 0.652 | 0.460 | 28.6 |
| this model: s > 0.5, components | 2523 | 0.583 | 0.399 | 0.576 | 0.695 | 0.400 | 0.029 | 0.020 | 0.142 | 41.731 | 572.2 |
| this model: layer, converged (predicted markers) | 2523 | 0.704 | 0.642 | 0.757 | 0.794 | 0.581 | 0.658 | 0.536 | 0.652 | 0.542 | 30.2 |
| this model: layer + fallback markers | 2523 | 0.701 | 0.641 | 0.756 | 0.797 | 0.582 | 0.639 | 0.519 | 0.651 | 0.670 | 32.8 |
| this model: layer, ground-truth markers (oracle) | 2523 | 0.859 | 0.798 | 0.922 | 0.859 | 0.590 | 0.960 | 0.806 | 0.858 | 0.020 | 23.3 |
| this model: layer, image-gradient costs | 2523 | 0.492 | 0.206 | 0.355 | 0.595 | 0.249 | 0.352 | 0.218 | 0.475 | 0.661 | 32.4 |
| this model: marker watershed on the contour map | 2523 | 0.618 | 0.442 | 0.624 | 0.688 | 0.426 | 0.568 | 0.396 | 0.536 | 0.707 | 33.0 |
| this model: PW limit, learned costs | 307 | 0.682 | 0.605 | 0.728 | 0.778 | 0.575 | 0.630 | 0.500 | 0.610 | 0.498 | 32.3 |
| this model: PW limit, image-gradient costs | 307 | 0.481 | 0.201 | 0.342 | 0.593 | 0.240 | 0.327 | 0.200 | 0.457 | 0.650 | 34.9 |
| this model: ground truth instances | 2523 | 1.000 | 1.000 | 1.000 | 1.000 | 0.559 | 1.000 | 1.000 | 1.000 | 0.000 | 23.7 |

## Marker quality (predicted markers against the ground-truth nuclei)

- 59872 nuclei in fold 2 (23.7 per patch); predicted markers 33.0 per patch.
- exactly one marker: 72.3 %; none: 17.4 %; several: 10.3 %; markers in background: 7.01 per patch.
- with fallback markers: one 75.9 %, none 13.5 %, several 10.6 %, background 9.42 per patch, 36.5 markers per patch.
- sec. 11 run: one 73.2 %, none 17.4 %, several 9.5 %, background 5.88 per patch, 30.5 markers per patch.

## Inference cost

- U-Net forward: 0.8 ms per image; converged multi-marker solve (tol 1e-05): 176.3 ms per image at K = 33.0 markers per image (85887 systems in 158 batches of 16; 243 PCG iterations per batch).
- exact K-label PW limit (one CPU core): 0.7 s per patch with the learned costs, 0.8 s with image-gradient costs, K = 35.8; 6057 ambiguous plateaus solved over 307 patches.

## Per tissue type

**Breast**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 749 | 0.722 | 0.596 | 0.756 | 0.780 | 0.585 | 0.690 | 0.547 | 0.550 | 0.198 | 21.2 |
| U-Net + contour head, watershed (b) | 749 | 0.722 | 0.601 | 0.761 | 0.782 | 0.576 | 0.757 | 0.605 | 0.671 | 0.242 | 24.5 |
| sec. 11 run: layer | 749 | 0.710 | 0.587 | 0.745 | 0.772 | 0.593 | 0.716 | 0.569 | 0.661 | 0.372 | 26.9 |
| s > 0.5, components | 749 | 0.600 | 0.382 | 0.565 | 0.667 | 0.394 | 0.029 | 0.020 | 0.153 | 35.961 | 541.5 |
| layer, converged (predicted markers) | 749 | 0.708 | 0.584 | 0.743 | 0.770 | 0.589 | 0.697 | 0.553 | 0.663 | 0.427 | 28.1 |
| layer + fallback markers | 749 | 0.706 | 0.584 | 0.742 | 0.771 | 0.590 | 0.678 | 0.538 | 0.662 | 0.527 | 30.0 |
| layer, ground-truth markers (oracle) | 749 | 0.854 | 0.745 | 0.909 | 0.838 | 0.597 | 0.968 | 0.806 | 0.853 | 0.015 | 21.4 |
| layer, image-gradient costs | 749 | 0.521 | 0.218 | 0.370 | 0.592 | 0.236 | 0.427 | 0.268 | 0.505 | 0.554 | 30.2 |
| marker watershed on the contour map | 749 | 0.620 | 0.408 | 0.598 | 0.662 | 0.418 | 0.605 | 0.411 | 0.551 | 0.586 | 30.8 |
| PW limit, learned costs | 89 | 0.707 | 0.559 | 0.723 | 0.756 | 0.582 | 0.679 | 0.526 | 0.637 | 0.450 | 30.1 |
| PW limit, image-gradient costs | 89 | 0.534 | 0.225 | 0.376 | 0.593 | 0.217 | 0.417 | 0.259 | 0.500 | 0.625 | 32.7 |
| ground truth instances | 749 | 1.000 | 1.000 | 1.000 | 1.000 | 0.553 | 1.000 | 1.000 | 1.000 | 0.000 | 21.7 |

**Colon**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 468 | 0.698 | 0.617 | 0.738 | 0.788 | 0.558 | 0.547 | 0.431 | 0.349 | 0.274 | 21.1 |
| U-Net + contour head, watershed (b) | 468 | 0.691 | 0.621 | 0.742 | 0.788 | 0.550 | 0.630 | 0.497 | 0.574 | 0.340 | 27.7 |
| sec. 11 run: layer | 468 | 0.681 | 0.602 | 0.724 | 0.773 | 0.572 | 0.570 | 0.451 | 0.584 | 0.698 | 32.9 |
| s > 0.5, components | 468 | 0.560 | 0.374 | 0.536 | 0.687 | 0.401 | 0.017 | 0.012 | 0.073 | 41.379 | 646.5 |
| layer, converged (predicted markers) | 468 | 0.679 | 0.602 | 0.722 | 0.772 | 0.567 | 0.530 | 0.419 | 0.580 | 0.886 | 37.4 |
| layer + fallback markers | 468 | 0.673 | 0.598 | 0.718 | 0.774 | 0.570 | 0.519 | 0.410 | 0.580 | 1.005 | 39.7 |
| layer, ground-truth markers (oracle) | 468 | 0.849 | 0.773 | 0.905 | 0.851 | 0.569 | 0.941 | 0.772 | 0.843 | 0.020 | 24.9 |
| layer, image-gradient costs | 468 | 0.494 | 0.262 | 0.387 | 0.607 | 0.294 | 0.255 | 0.156 | 0.430 | 1.061 | 40.3 |
| marker watershed on the contour map | 468 | 0.612 | 0.432 | 0.600 | 0.682 | 0.426 | 0.424 | 0.290 | 0.467 | 1.143 | 41.7 |
| PW limit, learned costs | 62 | 0.637 | 0.561 | 0.686 | 0.745 | 0.532 | 0.478 | 0.365 | 0.504 | 0.788 | 47.4 |
| PW limit, image-gradient costs | 62 | 0.445 | 0.245 | 0.360 | 0.593 | 0.268 | 0.213 | 0.129 | 0.380 | 0.891 | 50.5 |
| ground truth instances | 468 | 1.000 | 1.000 | 1.000 | 1.000 | 0.539 | 1.000 | 1.000 | 1.000 | 0.000 | 25.4 |

**HeadNeck**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 169 | 0.672 | 0.658 | 0.744 | 0.835 | 0.648 | 0.640 | 0.519 | 0.556 | 0.424 | 20.2 |
| U-Net + contour head, watershed (b) | 169 | 0.682 | 0.675 | 0.756 | 0.839 | 0.638 | 0.688 | 0.565 | 0.660 | 0.474 | 23.6 |
| sec. 11 run: layer | 169 | 0.688 | 0.687 | 0.759 | 0.816 | 0.636 | 0.664 | 0.547 | 0.641 | 0.354 | 22.1 |
| s > 0.5, components | 169 | 0.492 | 0.371 | 0.518 | 0.756 | 0.482 | 0.028 | 0.020 | 0.198 | 47.755 | 521.4 |
| layer, converged (predicted markers) | 169 | 0.691 | 0.689 | 0.761 | 0.816 | 0.627 | 0.653 | 0.538 | 0.642 | 0.345 | 23.1 |
| layer + fallback markers | 169 | 0.672 | 0.676 | 0.751 | 0.822 | 0.636 | 0.623 | 0.512 | 0.642 | 0.510 | 26.1 |
| layer, ground-truth markers (oracle) | 169 | 0.860 | 0.854 | 0.937 | 0.887 | 0.645 | 0.965 | 0.819 | 0.862 | 0.028 | 18.2 |
| layer, image-gradient costs | 169 | 0.462 | 0.250 | 0.369 | 0.626 | 0.303 | 0.256 | 0.154 | 0.431 | 0.420 | 24.8 |
| marker watershed on the contour map | 169 | 0.620 | 0.504 | 0.653 | 0.738 | 0.474 | 0.578 | 0.411 | 0.533 | 0.426 | 24.9 |
| ground truth instances | 169 | 1.000 | 1.000 | 1.000 | 1.000 | 0.629 | 1.000 | 1.000 | 1.000 | 0.000 | 18.5 |

**Adrenal_gland**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 148 | 0.716 | 0.676 | 0.774 | 0.808 | 0.554 | 0.694 | 0.582 | 0.655 | 0.378 | 18.4 |
| U-Net + contour head, watershed (b) | 148 | 0.719 | 0.689 | 0.783 | 0.811 | 0.551 | 0.712 | 0.605 | 0.713 | 0.444 | 20.1 |
| sec. 11 run: layer | 148 | 0.714 | 0.688 | 0.780 | 0.809 | 0.571 | 0.726 | 0.615 | 0.695 | 0.394 | 19.1 |
| s > 0.5, components | 148 | 0.596 | 0.410 | 0.580 | 0.706 | 0.366 | 0.029 | 0.021 | 0.451 | 60.592 | 654.9 |
| layer, converged (predicted markers) | 148 | 0.715 | 0.691 | 0.783 | 0.811 | 0.567 | 0.710 | 0.602 | 0.699 | 0.487 | 20.1 |
| layer + fallback markers | 148 | 0.715 | 0.690 | 0.782 | 0.814 | 0.563 | 0.674 | 0.570 | 0.698 | 0.637 | 22.7 |
| layer, ground-truth markers (oracle) | 148 | 0.868 | 0.829 | 0.933 | 0.867 | 0.579 | 0.961 | 0.833 | 0.872 | 0.025 | 15.6 |
| layer, image-gradient costs | 148 | 0.474 | 0.135 | 0.283 | 0.562 | 0.237 | 0.398 | 0.245 | 0.482 | 0.602 | 22.2 |
| marker watershed on the contour map | 148 | 0.627 | 0.456 | 0.637 | 0.698 | 0.414 | 0.644 | 0.477 | 0.597 | 0.612 | 22.3 |
| ground truth instances | 148 | 1.000 | 1.000 | 1.000 | 1.000 | 0.557 | 1.000 | 1.000 | 1.000 | 0.000 | 16.0 |

## Paired per-patch differences (2523 patches; bootstrap 95 % intervals; F1 / PQ / AJI dataset-level, bootstrapped over patches)

| comparison | IoU | BF₂ | edge align. | F1@0.5 | PQ | AJI |
|---|---|---|---|---|---|---|
| layer − U-Net (sec. 6) logits | -0.014 [-0.018, -0.011] | -0.012 [-0.016, -0.008] | +0.006 [+0.004, +0.007] | +0.002 [-0.006, +0.009] | +0.005 [-0.001, +0.011] | +0.157 [+0.143, +0.171] |
| layer − contour-head U-Net, watershed (b) | -0.014 [-0.017, -0.010] | -0.017 [-0.021, -0.013] | +0.015 [+0.013, +0.016] | -0.057 [-0.062, -0.051] | -0.047 [-0.052, -0.043] | -0.006 [-0.008, -0.003] |
| layer − sec. 11 layer | -0.002 [-0.004, +0.001] | -0.002 [-0.004, +0.001] | -0.004 [-0.005, -0.003] | -0.023 [-0.026, -0.019] | -0.018 [-0.021, -0.015] | -0.000 [-0.002, +0.001] |
| layer, ground-truth markers − sec. 11 layer, ground-truth markers | -0.000 [-0.001, +0.001] | -0.000 [-0.001, +0.001] | -0.001 [-0.001, -0.000] | +0.001 [-0.000, +0.002] | +0.001 [+0.000, +0.002] | +0.001 [+0.000, +0.001] |
| layer − this model's own logits | +0.122 [+0.116, +0.127] | +0.181 [+0.175, +0.187] | +0.188 [+0.186, +0.190] | +0.629 [+0.621, +0.637] | +0.515 [+0.508, +0.522] | +0.510 [+0.496, +0.522] |
| layer − marker watershed, same markers | +0.087 [+0.084, +0.089] | +0.133 [+0.131, +0.136] | +0.155 [+0.153, +0.157] | +0.091 [+0.088, +0.094] | +0.140 [+0.137, +0.142] | +0.116 [+0.113, +0.120] |
| layer − layer with image costs | +0.212 [+0.208, +0.216] | +0.402 [+0.396, +0.407] | +0.332 [+0.327, +0.335] | +0.306 [+0.299, +0.315] | +0.318 [+0.312, +0.325] | +0.177 [+0.174, +0.180] |
| layer + fallback − U-Net (sec. 6) logits | -0.018 [-0.021, -0.015] | -0.013 [-0.016, -0.010] | +0.005 [+0.003, +0.007] | -0.018 [-0.026, -0.011] | -0.012 [-0.018, -0.006] | +0.157 [+0.143, +0.171] |
| layer + fallback − contour-head U-Net, watershed (b) | -0.017 [-0.020, -0.015] | -0.018 [-0.021, -0.015] | +0.014 [+0.012, +0.015] | -0.076 [-0.081, -0.070] | -0.064 [-0.068, -0.060] | -0.006 [-0.008, -0.003] |
| layer + fallback − layer | -0.004 [-0.007, -0.001] | -0.001 [-0.004, +0.002] | -0.001 [-0.001, +0.000] | -0.019 [-0.021, -0.018] | -0.017 [-0.018, -0.016] | -0.000 [-0.000, +0.000] |
| layer, ground-truth markers − layer | +0.155 [+0.150, +0.160] | +0.165 [+0.160, +0.170] | +0.009 [+0.007, +0.011] | +0.302 [+0.293, +0.309] | +0.270 [+0.263, +0.276] | +0.207 [+0.202, +0.211] |
| on the 307 limit patches: PW limit (learned) − layer | -0.010 [-0.013, -0.008] | -0.016 [-0.019, -0.013] | +0.002 [-0.000, +0.005] | +0.005 [+0.001, +0.009] | -0.005 [-0.008, -0.003] | -0.019 [-0.022, -0.017] |
| on the 307 limit patches: PW limit (learned) − PW limit (image costs) | +0.201 [+0.191, +0.213] | +0.386 [+0.368, +0.404] | +0.335 [+0.322, +0.347] | +0.303 [+0.278, +0.329] | +0.300 [+0.280, +0.323] | +0.153 [+0.144, +0.164] |
| on the 307 limit patches: PW limit (learned) − U-Net (sec. 6) logits | -0.031 [-0.041, -0.023] | -0.035 [-0.046, -0.026] | +0.007 [+0.002, +0.013] | -0.004 [-0.023, +0.016] | -0.009 [-0.026, +0.007] | +0.185 [+0.132, +0.231] |

## By crowding (F1@0.5 / PQ / count error)

| patches | n | U-Net (sec. 6) | contour-head U-Net, watershed (b) | layer | layer + fallback | marker watershed, same markers | PW limit (learned, subset) |
|---|---|---|---|---|---|---|---|
| < 10 nuclei | 486 | 0.608 / 0.485 / 0.68 | 0.596 / 0.479 / 0.81 | 0.530 / 0.426 / 1.02 | 0.484 / 0.388 / 1.39 | 0.447 / 0.310 / 1.33 | 0.526 / 0.406 / 0.67 |
| 10–30 | 1383 | 0.691 / 0.563 / 0.18 | 0.719 / 0.591 / 0.27 | 0.644 / 0.527 / 0.50 | 0.621 / 0.508 / 0.59 | 0.562 / 0.397 / 0.67 | 0.641 / 0.514 / 0.52 |
| 30–60 | 525 | 0.650 / 0.524 / 0.15 | 0.733 / 0.596 / 0.15 | 0.680 / 0.552 / 0.29 | 0.666 / 0.539 / 0.33 | 0.592 / 0.411 / 0.35 | 0.637 / 0.504 / 0.38 |
| > 60 | 129 | 0.588 / 0.469 / 0.24 | 0.700 / 0.562 / 0.13 | 0.688 / 0.557 / 0.20 | 0.677 / 0.548 / 0.16 | 0.567 / 0.387 / 0.20 | 0.610 / 0.480 / 0.20 |

## Marker quality by crowding (nuclei with one / none / several markers; background markers per patch)

| patches | one | none | several | bg markers / patch |
|---|---|---|---|---|
| < 10 nuclei | 66.0 % | 19.1 % | 14.9 % | 3.12 |
| 10–30 | 73.4 % | 14.5 % | 12.1 % | 7.56 |
| 30–60 | 73.7 % | 16.2 % | 10.1 % | 8.74 |
| > 60 | 68.2 % | 25.9 % | 5.9 % | 8.83 |
