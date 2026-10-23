# Instances as labels: multi-marker layer on PanNuke (fold 1 → fold 2)

Run `results_pannuke_instances/instances`: p 5.0 → 20.0, erosion [2, 3], edge target ×1.0, seam weight 5.0, 30 epochs, seed 0, training solve tol 0.0001 / maxit 100; marker head `bce` (thr 0.5, min area 1 px); learned edge scale 1.99.

## All of fold 2

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6, binary target), s > 0.5, components | 2523 | 0.719 | 0.652 | 0.769 | 0.807 | 0.577 | 0.656 | 0.531 | 0.494 | 0.275 | 23.0 |
| U-Net + contour head (sec. 10.1, gap target), logits | 2523 | 0.719 | 0.658 | 0.774 | 0.809 | 0.574 | 0.682 | 0.556 | 0.571 | 0.303 | 25.2 |
| U-Net + contour head, tuned marker watershed (b) | 2523 | 0.718 | 0.658 | 0.774 | 0.809 | 0.568 | 0.715 | 0.583 | 0.657 | 0.344 | 27.2 |
| this model: s > 0.5, components | 2523 | 0.575 | 0.408 | 0.580 | 0.691 | 0.402 | 0.024 | 0.017 | 0.168 | 52.714 | 723.3 |
| this model: layer, converged (predicted markers) | 2523 | 0.706 | 0.643 | 0.759 | 0.795 | 0.585 | 0.681 | 0.554 | 0.652 | 0.460 | 28.6 |
| this model: layer + fallback markers | 2523 | 0.702 | 0.641 | 0.757 | 0.798 | 0.586 | 0.657 | 0.534 | 0.652 | 0.585 | 31.1 |
| this model: layer, ground-truth markers (oracle) | 2523 | 0.859 | 0.796 | 0.922 | 0.858 | 0.591 | 0.959 | 0.805 | 0.858 | 0.020 | 23.3 |
| this model: layer, image-gradient costs | 2523 | 0.487 | 0.203 | 0.351 | 0.592 | 0.248 | 0.355 | 0.218 | 0.470 | 0.529 | 29.9 |
| this model: marker watershed on the contour map | 2523 | 0.615 | 0.455 | 0.633 | 0.684 | 0.430 | 0.597 | 0.414 | 0.541 | 0.546 | 30.2 |
| this model: PW limit, learned costs | 307 | 0.690 | 0.613 | 0.736 | 0.781 | 0.579 | 0.661 | 0.526 | 0.612 | 0.426 | 29.8 |
| this model: PW limit, image-gradient costs | 307 | 0.479 | 0.202 | 0.341 | 0.589 | 0.241 | 0.335 | 0.204 | 0.451 | 0.507 | 31.5 |
| this model: ground truth instances | 2523 | 1.000 | 1.000 | 1.000 | 1.000 | 0.559 | 1.000 | 1.000 | 1.000 | 0.000 | 23.7 |

## Marker quality (predicted markers against the ground-truth nuclei)

- 59872 nuclei in fold 2 (23.7 per patch); predicted markers 30.5 per patch.
- exactly one marker: 73.2 %; none: 17.4 %; several: 9.5 %; markers in background: 5.88 per patch.
- with fallback markers: one 76.3 %, none 13.8 %, several 9.9 %, background 8.15 per patch, 33.8 markers per patch.

## Inference cost

- U-Net forward: 0.8 ms per image; converged multi-marker solve (tol 1e-05): 224.0 ms per image at K = 30.5 markers per image (79353 systems in 158 batches of 16; 330 PCG iterations per batch).
- exact K-label PW limit (one CPU core): 0.7 s per patch with the learned costs, 0.8 s with image-gradient costs, K = 32.2; 6043 ambiguous plateaus solved over 307 patches.

## Per tissue type

**Breast**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 749 | 0.722 | 0.596 | 0.756 | 0.780 | 0.585 | 0.690 | 0.547 | 0.550 | 0.198 | 21.2 |
| U-Net + contour head, watershed (b) | 749 | 0.722 | 0.601 | 0.761 | 0.782 | 0.576 | 0.757 | 0.605 | 0.671 | 0.242 | 24.5 |
| s > 0.5, components | 749 | 0.594 | 0.391 | 0.573 | 0.664 | 0.395 | 0.024 | 0.016 | 0.178 | 45.737 | 683.8 |
| layer, converged (predicted markers) | 749 | 0.710 | 0.587 | 0.745 | 0.772 | 0.593 | 0.716 | 0.569 | 0.661 | 0.372 | 26.9 |
| layer + fallback markers | 749 | 0.708 | 0.586 | 0.744 | 0.772 | 0.592 | 0.694 | 0.552 | 0.660 | 0.475 | 28.7 |
| layer, ground-truth markers (oracle) | 749 | 0.854 | 0.744 | 0.908 | 0.838 | 0.596 | 0.967 | 0.806 | 0.853 | 0.015 | 21.4 |
| layer, image-gradient costs | 749 | 0.518 | 0.217 | 0.370 | 0.590 | 0.235 | 0.440 | 0.274 | 0.500 | 0.430 | 28.0 |
| marker watershed on the contour map | 749 | 0.617 | 0.422 | 0.609 | 0.659 | 0.421 | 0.638 | 0.431 | 0.553 | 0.447 | 28.3 |
| PW limit, learned costs | 89 | 0.711 | 0.566 | 0.726 | 0.760 | 0.587 | 0.715 | 0.557 | 0.638 | 0.341 | 27.7 |
| PW limit, image-gradient costs | 89 | 0.529 | 0.225 | 0.375 | 0.591 | 0.219 | 0.442 | 0.272 | 0.494 | 0.425 | 29.1 |
| ground truth instances | 749 | 1.000 | 1.000 | 1.000 | 1.000 | 0.553 | 1.000 | 1.000 | 1.000 | 0.000 | 21.7 |

**Colon**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 468 | 0.698 | 0.617 | 0.738 | 0.788 | 0.558 | 0.547 | 0.431 | 0.349 | 0.274 | 21.1 |
| U-Net + contour head, watershed (b) | 468 | 0.691 | 0.621 | 0.742 | 0.788 | 0.550 | 0.630 | 0.497 | 0.574 | 0.340 | 27.7 |
| s > 0.5, components | 468 | 0.546 | 0.380 | 0.540 | 0.683 | 0.406 | 0.014 | 0.009 | 0.094 | 55.369 | 864.8 |
| layer, converged (predicted markers) | 468 | 0.681 | 0.602 | 0.724 | 0.773 | 0.572 | 0.570 | 0.451 | 0.584 | 0.698 | 32.9 |
| layer + fallback markers | 468 | 0.673 | 0.595 | 0.717 | 0.774 | 0.572 | 0.552 | 0.436 | 0.584 | 0.814 | 35.3 |
| layer, ground-truth markers (oracle) | 468 | 0.850 | 0.773 | 0.906 | 0.851 | 0.569 | 0.939 | 0.770 | 0.842 | 0.025 | 24.8 |
| layer, image-gradient costs | 468 | 0.488 | 0.256 | 0.379 | 0.603 | 0.294 | 0.261 | 0.159 | 0.428 | 0.773 | 34.5 |
| marker watershed on the contour map | 468 | 0.609 | 0.448 | 0.614 | 0.678 | 0.436 | 0.470 | 0.319 | 0.478 | 0.802 | 35.0 |
| PW limit, learned costs | 62 | 0.644 | 0.568 | 0.693 | 0.749 | 0.533 | 0.517 | 0.393 | 0.507 | 0.685 | 41.5 |
| PW limit, image-gradient costs | 62 | 0.441 | 0.239 | 0.353 | 0.590 | 0.266 | 0.214 | 0.129 | 0.375 | 0.733 | 43.6 |
| ground truth instances | 468 | 1.000 | 1.000 | 1.000 | 1.000 | 0.539 | 1.000 | 1.000 | 1.000 | 0.000 | 25.4 |

**HeadNeck**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 169 | 0.672 | 0.658 | 0.744 | 0.835 | 0.648 | 0.640 | 0.519 | 0.556 | 0.424 | 20.2 |
| U-Net + contour head, watershed (b) | 169 | 0.682 | 0.675 | 0.756 | 0.839 | 0.638 | 0.688 | 0.565 | 0.660 | 0.474 | 23.6 |
| s > 0.5, components | 169 | 0.481 | 0.376 | 0.518 | 0.751 | 0.489 | 0.025 | 0.017 | 0.218 | 55.611 | 625.7 |
| layer, converged (predicted markers) | 169 | 0.688 | 0.687 | 0.759 | 0.816 | 0.636 | 0.664 | 0.547 | 0.641 | 0.354 | 22.1 |
| layer + fallback markers | 169 | 0.668 | 0.671 | 0.747 | 0.823 | 0.652 | 0.632 | 0.519 | 0.641 | 0.522 | 25.0 |
| layer, ground-truth markers (oracle) | 169 | 0.861 | 0.855 | 0.943 | 0.885 | 0.650 | 0.964 | 0.818 | 0.860 | 0.026 | 18.2 |
| layer, image-gradient costs | 169 | 0.451 | 0.239 | 0.354 | 0.621 | 0.305 | 0.243 | 0.146 | 0.423 | 0.412 | 23.4 |
| marker watershed on the contour map | 169 | 0.615 | 0.515 | 0.659 | 0.734 | 0.487 | 0.597 | 0.422 | 0.539 | 0.420 | 23.4 |
| ground truth instances | 169 | 1.000 | 1.000 | 1.000 | 1.000 | 0.629 | 1.000 | 1.000 | 1.000 | 0.000 | 18.5 |

**Adrenal_gland**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 148 | 0.716 | 0.676 | 0.774 | 0.808 | 0.554 | 0.694 | 0.582 | 0.655 | 0.378 | 18.4 |
| U-Net + contour head, watershed (b) | 148 | 0.719 | 0.689 | 0.783 | 0.811 | 0.551 | 0.712 | 0.605 | 0.713 | 0.444 | 20.1 |
| s > 0.5, components | 148 | 0.589 | 0.420 | 0.587 | 0.699 | 0.369 | 0.024 | 0.017 | 0.455 | 72.936 | 798.9 |
| layer, converged (predicted markers) | 148 | 0.714 | 0.688 | 0.780 | 0.809 | 0.571 | 0.726 | 0.615 | 0.695 | 0.394 | 19.1 |
| layer + fallback markers | 148 | 0.713 | 0.686 | 0.778 | 0.811 | 0.567 | 0.686 | 0.581 | 0.694 | 0.540 | 21.5 |
| layer, ground-truth markers (oracle) | 148 | 0.864 | 0.823 | 0.928 | 0.864 | 0.582 | 0.959 | 0.832 | 0.870 | 0.025 | 15.6 |
| layer, image-gradient costs | 148 | 0.467 | 0.134 | 0.280 | 0.558 | 0.238 | 0.410 | 0.251 | 0.476 | 0.485 | 20.5 |
| marker watershed on the contour map | 148 | 0.620 | 0.465 | 0.640 | 0.691 | 0.418 | 0.660 | 0.486 | 0.597 | 0.492 | 20.6 |
| ground truth instances | 148 | 1.000 | 1.000 | 1.000 | 1.000 | 0.557 | 1.000 | 1.000 | 1.000 | 0.000 | 16.0 |

## Paired per-patch differences (2523 patches; bootstrap 95 % intervals; F1 / PQ / AJI dataset-level, bootstrapped over patches)

| comparison | IoU | BF₂ | edge align. | F1@0.5 | PQ | AJI |
|---|---|---|---|---|---|---|
| layer − U-Net (sec. 6) logits | -0.013 [-0.016, -0.010] | -0.011 [-0.014, -0.007] | +0.009 [+0.008, +0.010] | +0.024 [+0.019, +0.031] | +0.023 [+0.018, +0.029] | +0.158 [+0.143, +0.172] |
| layer − contour-head U-Net, watershed (b) | -0.012 [-0.015, -0.009] | -0.016 [-0.019, -0.012] | +0.018 [+0.017, +0.020] | -0.034 [-0.039, -0.030] | -0.029 [-0.033, -0.025] | -0.005 [-0.008, -0.003] |
| layer − this model's own logits | +0.131 [+0.125, +0.137] | +0.178 [+0.172, +0.185] | +0.191 [+0.188, +0.193] | +0.657 [+0.650, +0.663] | +0.538 [+0.531, +0.544] | +0.484 [+0.471, +0.496] |
| layer − marker watershed, same markers | +0.091 [+0.089, +0.093] | +0.126 [+0.124, +0.128] | +0.155 [+0.153, +0.157] | +0.084 [+0.081, +0.087] | +0.140 [+0.138, +0.143] | +0.111 [+0.109, +0.113] |
| layer − layer with image costs | +0.218 [+0.215, +0.222] | +0.407 [+0.401, +0.413] | +0.337 [+0.333, +0.341] | +0.325 [+0.317, +0.335] | +0.336 [+0.330, +0.343] | +0.182 [+0.179, +0.185] |
| layer + fallback − U-Net (sec. 6) logits | -0.017 [-0.019, -0.014] | -0.012 [-0.015, -0.009] | +0.009 [+0.007, +0.010] | +0.001 [-0.005, +0.008] | +0.003 [-0.002, +0.009] | +0.157 [+0.142, +0.171] |
| layer + fallback − contour-head U-Net, watershed (b) | -0.016 [-0.018, -0.013] | -0.017 [-0.020, -0.015] | +0.017 [+0.016, +0.019] | -0.058 [-0.062, -0.053] | -0.049 [-0.052, -0.045] | -0.006 [-0.008, -0.003] |
| layer + fallback − layer | -0.004 [-0.007, -0.001] | -0.002 [-0.005, +0.001] | -0.001 [-0.001, -0.000] | -0.024 [-0.025, -0.023] | -0.020 [-0.021, -0.019] | -0.000 [-0.000, -0.000] |
| layer, ground-truth markers − layer | +0.153 [+0.148, +0.158] | +0.163 [+0.158, +0.168] | +0.006 [+0.004, +0.008] | +0.278 [+0.272, +0.285] | +0.251 [+0.245, +0.256] | +0.206 [+0.202, +0.210] |
| on the 307 limit patches: PW limit (learned) − layer | -0.008 [-0.011, -0.005] | -0.013 [-0.016, -0.009] | -0.001 [-0.004, +0.002] | +0.007 [+0.003, +0.010] | -0.003 [-0.006, -0.000] | -0.017 [-0.020, -0.015] |
| on the 307 limit patches: PW limit (learned) − PW limit (image costs) | +0.211 [+0.200, +0.222] | +0.395 [+0.377, +0.413] | +0.338 [+0.324, +0.350] | +0.326 [+0.298, +0.354] | +0.322 [+0.301, +0.344] | +0.161 [+0.152, +0.170] |
| on the 307 limit patches: PW limit (learned) − U-Net (sec. 6) logits | -0.024 [-0.031, -0.016] | -0.027 [-0.036, -0.020] | +0.011 [+0.005, +0.017] | +0.027 [+0.010, +0.043] | +0.017 [+0.003, +0.030] | +0.187 [+0.137, +0.235] |

## By crowding (F1@0.5 / PQ / count error)

| patches | n | U-Net (sec. 6) | contour-head U-Net, watershed (b) | layer | layer + fallback | marker watershed, same markers | PW limit (learned, subset) |
|---|---|---|---|---|---|---|---|
| < 10 nuclei | 486 | 0.608 / 0.485 / 0.68 | 0.596 / 0.479 / 0.81 | 0.559 / 0.449 / 0.94 | 0.509 / 0.408 / 1.31 | 0.484 / 0.334 / 1.11 | 0.533 / 0.407 / 0.80 |
| 10–30 | 1383 | 0.691 / 0.563 / 0.18 | 0.719 / 0.591 / 0.27 | 0.673 / 0.551 / 0.40 | 0.646 / 0.528 / 0.48 | 0.602 / 0.422 / 0.49 | 0.681 / 0.547 / 0.38 |
| 30–60 | 525 | 0.650 / 0.524 / 0.15 | 0.733 / 0.596 / 0.15 | 0.696 / 0.565 / 0.24 | 0.677 / 0.549 / 0.29 | 0.613 / 0.423 / 0.28 | 0.666 / 0.529 / 0.29 |
| > 60 | 129 | 0.588 / 0.469 / 0.24 | 0.700 / 0.562 / 0.13 | 0.703 / 0.569 / 0.16 | 0.688 / 0.556 / 0.13 | 0.582 / 0.394 / 0.17 | 0.632 / 0.497 / 0.16 |

## Marker quality by crowding (nuclei with one / none / several markers; background markers per patch)

| patches | one | none | several | bg markers / patch |
|---|---|---|---|---|
| < 10 nuclei | 69.3 % | 18.6 % | 12.0 % | 2.63 |
| 10–30 | 74.6 % | 14.6 % | 10.9 % | 6.08 |
| 30–60 | 74.4 % | 16.3 % | 9.3 % | 7.85 |
| > 60 | 68.6 % | 25.5 % | 5.9 % | 8.05 |
