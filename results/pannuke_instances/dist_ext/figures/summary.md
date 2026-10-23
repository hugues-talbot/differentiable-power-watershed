# Instances as labels: multi-marker layer on PanNuke (fold 1 → fold 2)

Run `results_pannuke_instances/dist_ext/instances`: p 5.0 → 20.0, erosion [2, 3], edge target ×1.0, seam weight 5.0, 30 epochs, training solve tol 0.0001 / maxit 100; marker head `dist` (mse, rmax 12; markers = h-maxima h 0.3 grown to thr 0.2, min area 9 px), chosen by PQ on 300 patches of fold 3; learned edge scale 2.14.

## Marker post-processing chosen on fold 3 (300 patches): {'mk_thr': 0.2, 'mk_min_area': 9, 'mk_h': 0.3}

| setting | PQ | F1@0.5 | AJI | count err. | n_pred | one | none | several | bg / patch |
|---|---|---|---|---|---|---|---|---|---|
| thr=0.2/min_area=9/h=0.3 | 0.646 | 0.789 | 0.646 | 0.174 | 23.5 | 82.4 % | 17.0 % | 0.6 % | 3.31 |
| thr=0.2/min_area=16/h=0.2 | 0.646 | 0.791 | 0.655 | 0.191 | 24.8 | 84.2 % | 14.5 % | 1.4 % | 3.80 |
| thr=0.2/min_area=16/h=0.3 | 0.645 | 0.788 | 0.646 | 0.172 | 23.3 | 82.0 % | 17.5 % | 0.6 % | 3.26 |
| thr=0.2/min_area=9/h=0.2 | 0.645 | 0.791 | 0.655 | 0.199 | 25.2 | 85.0 % | 13.6 % | 1.4 % | 4.01 |
| thr=0.15/min_area=16/h=0.2 | 0.642 | 0.786 | 0.648 | 0.202 | 25.4 | 84.8 % | 13.8 % | 1.4 % | 4.24 |
| thr=0.15/min_area=16/h=0.3 | 0.641 | 0.782 | 0.636 | 0.175 | 23.5 | 82.0 % | 17.5 % | 0.6 % | 3.44 |
| thr=0.15/min_area=9/h=0.3 | 0.641 | 0.782 | 0.636 | 0.176 | 23.5 | 82.0 % | 17.4 % | 0.6 % | 3.46 |
| thr=0.15/min_area=9/h=0.2 | 0.640 | 0.785 | 0.647 | 0.215 | 25.7 | 85.2 % | 13.5 % | 1.4 % | 4.42 |

(top 8 of 24 settings by PQ)

## All of fold 2

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6, binary target), s > 0.5, components | 2523 | 0.719 | 0.652 | 0.769 | 0.807 | 0.577 | 0.656 | 0.531 | 0.494 | 0.275 | 23.0 |
| U-Net + contour head (sec. 10.1, gap target), logits | 2523 | 0.719 | 0.658 | 0.774 | 0.809 | 0.574 | 0.682 | 0.556 | 0.571 | 0.303 | 25.2 |
| U-Net + contour head, tuned marker watershed (b) | 2523 | 0.718 | 0.658 | 0.774 | 0.809 | 0.568 | 0.715 | 0.583 | 0.657 | 0.344 | 27.2 |
| sec. 11 run: layer, converged (BCE marker head, thr 0.5) | 2523 | 0.706 | 0.643 | 0.759 | 0.795 | 0.585 | 0.681 | 0.554 | 0.652 | 0.460 | 28.6 |
| this model: s > 0.5, components | 2523 | 0.585 | 0.395 | 0.567 | 0.701 | 0.395 | 0.032 | 0.022 | 0.164 | 40.548 | 559.7 |
| this model: layer, converged (predicted markers) | 2523 | 0.705 | 0.646 | 0.761 | 0.809 | 0.584 | 0.788 | 0.641 | 0.642 | 0.222 | 22.9 |
| this model: layer + fallback markers | 2523 | 0.704 | 0.645 | 0.760 | 0.810 | 0.585 | 0.771 | 0.627 | 0.642 | 0.287 | 24.3 |
| this model: layer, ground-truth markers (oracle) | 2523 | 0.859 | 0.796 | 0.922 | 0.858 | 0.591 | 0.959 | 0.805 | 0.857 | 0.020 | 23.3 |
| this model: layer, image-gradient costs | 2523 | 0.545 | 0.265 | 0.445 | 0.642 | 0.301 | 0.618 | 0.390 | 0.512 | 0.223 | 22.9 |
| this model: marker watershed on the contour map | 2523 | 0.619 | 0.435 | 0.614 | 0.698 | 0.423 | 0.704 | 0.493 | 0.539 | 0.223 | 22.9 |
| this model: PW limit, learned costs | 307 | 0.685 | 0.609 | 0.731 | 0.789 | 0.579 | 0.756 | 0.603 | 0.599 | 0.242 | 23.3 |
| this model: PW limit, image-gradient costs | 307 | 0.537 | 0.264 | 0.436 | 0.638 | 0.290 | 0.594 | 0.373 | 0.492 | 0.244 | 23.3 |
| this model: ground truth instances | 2523 | 1.000 | 1.000 | 1.000 | 1.000 | 0.559 | 1.000 | 1.000 | 1.000 | 0.000 | 23.7 |

## Marker quality (predicted markers against the ground-truth nuclei)

- 59872 nuclei in fold 2 (23.7 per patch); predicted markers 22.9 per patch.
- exactly one marker: 82.1 %; none: 17.3 %; several: 0.7 %; markers in background: 3.06 per patch.
- with fallback markers: one 83.8 %, none 15.2 %, several 1.0 %, background 4.52 per patch, 24.9 markers per patch.
- sec. 11 run: one 73.2 %, none 17.4 %, several 9.5 %, background 5.88 per patch, 30.5 markers per patch.

## Inference cost

- U-Net forward: 2.2 ms per image; converged multi-marker solve (tol 1e-05): 234.4 ms per image at K = 22.9 markers per image (60197 systems in 158 batches of 16; 180 PCG iterations per batch).
- exact K-label PW limit (one CPU core): 0.7 s per patch with the learned costs, 0.8 s with image-gradient costs, K = 23.3; 6732 ambiguous plateaus solved over 307 patches.

## Per tissue type

**Breast**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 749 | 0.722 | 0.596 | 0.756 | 0.780 | 0.585 | 0.690 | 0.547 | 0.550 | 0.198 | 21.2 |
| U-Net + contour head, watershed (b) | 749 | 0.722 | 0.601 | 0.761 | 0.782 | 0.576 | 0.757 | 0.605 | 0.671 | 0.242 | 24.5 |
| sec. 11 run: layer | 749 | 0.710 | 0.587 | 0.745 | 0.772 | 0.593 | 0.716 | 0.569 | 0.661 | 0.372 | 26.9 |
| s > 0.5, components | 749 | 0.601 | 0.375 | 0.555 | 0.673 | 0.387 | 0.031 | 0.021 | 0.171 | 34.803 | 531.2 |
| layer, converged (predicted markers) | 749 | 0.708 | 0.585 | 0.743 | 0.780 | 0.590 | 0.812 | 0.645 | 0.654 | 0.173 | 21.9 |
| layer + fallback markers | 749 | 0.707 | 0.585 | 0.743 | 0.780 | 0.590 | 0.799 | 0.633 | 0.653 | 0.217 | 22.9 |
| layer, ground-truth markers (oracle) | 749 | 0.853 | 0.743 | 0.909 | 0.838 | 0.595 | 0.967 | 0.806 | 0.852 | 0.015 | 21.4 |
| layer, image-gradient costs | 749 | 0.559 | 0.255 | 0.420 | 0.626 | 0.276 | 0.651 | 0.413 | 0.531 | 0.173 | 21.9 |
| marker watershed on the contour map | 749 | 0.621 | 0.399 | 0.585 | 0.671 | 0.410 | 0.735 | 0.500 | 0.555 | 0.173 | 21.9 |
| PW limit, learned costs | 89 | 0.703 | 0.554 | 0.715 | 0.761 | 0.582 | 0.800 | 0.621 | 0.632 | 0.130 | 22.5 |
| PW limit, image-gradient costs | 89 | 0.572 | 0.264 | 0.426 | 0.626 | 0.259 | 0.641 | 0.405 | 0.527 | 0.132 | 22.5 |
| ground truth instances | 749 | 1.000 | 1.000 | 1.000 | 1.000 | 0.553 | 1.000 | 1.000 | 1.000 | 0.000 | 21.7 |

**Colon**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 468 | 0.698 | 0.617 | 0.738 | 0.788 | 0.558 | 0.547 | 0.431 | 0.349 | 0.274 | 21.1 |
| U-Net + contour head, watershed (b) | 468 | 0.691 | 0.621 | 0.742 | 0.788 | 0.550 | 0.630 | 0.497 | 0.574 | 0.340 | 27.7 |
| sec. 11 run: layer | 468 | 0.681 | 0.602 | 0.724 | 0.773 | 0.572 | 0.570 | 0.451 | 0.584 | 0.698 | 32.9 |
| s > 0.5, components | 468 | 0.553 | 0.363 | 0.523 | 0.691 | 0.402 | 0.019 | 0.013 | 0.090 | 43.640 | 669.7 |
| layer, converged (predicted markers) | 468 | 0.679 | 0.602 | 0.723 | 0.786 | 0.575 | 0.703 | 0.556 | 0.560 | 0.227 | 21.5 |
| layer + fallback markers | 468 | 0.679 | 0.602 | 0.723 | 0.787 | 0.575 | 0.687 | 0.543 | 0.560 | 0.279 | 23.1 |
| layer, ground-truth markers (oracle) | 468 | 0.850 | 0.771 | 0.905 | 0.850 | 0.569 | 0.939 | 0.771 | 0.841 | 0.025 | 24.8 |
| layer, image-gradient costs | 468 | 0.546 | 0.317 | 0.461 | 0.650 | 0.332 | 0.553 | 0.346 | 0.459 | 0.227 | 21.5 |
| marker watershed on the contour map | 468 | 0.604 | 0.418 | 0.584 | 0.688 | 0.432 | 0.590 | 0.404 | 0.453 | 0.227 | 21.5 |
| PW limit, learned costs | 62 | 0.643 | 0.566 | 0.689 | 0.755 | 0.547 | 0.621 | 0.480 | 0.480 | 0.213 | 25.6 |
| PW limit, image-gradient costs | 62 | 0.512 | 0.309 | 0.445 | 0.635 | 0.301 | 0.488 | 0.303 | 0.408 | 0.213 | 25.6 |
| ground truth instances | 468 | 1.000 | 1.000 | 1.000 | 1.000 | 0.539 | 1.000 | 1.000 | 1.000 | 0.000 | 25.4 |

**HeadNeck**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 169 | 0.672 | 0.658 | 0.744 | 0.835 | 0.648 | 0.640 | 0.519 | 0.556 | 0.424 | 20.2 |
| U-Net + contour head, watershed (b) | 169 | 0.682 | 0.675 | 0.756 | 0.839 | 0.638 | 0.688 | 0.565 | 0.660 | 0.474 | 23.6 |
| sec. 11 run: layer | 169 | 0.688 | 0.687 | 0.759 | 0.816 | 0.636 | 0.664 | 0.547 | 0.641 | 0.354 | 22.1 |
| s > 0.5, components | 169 | 0.495 | 0.376 | 0.515 | 0.762 | 0.472 | 0.032 | 0.023 | 0.238 | 45.463 | 485.3 |
| layer, converged (predicted markers) | 169 | 0.697 | 0.709 | 0.779 | 0.845 | 0.636 | 0.786 | 0.650 | 0.646 | 0.197 | 18.6 |
| layer + fallback markers | 169 | 0.671 | 0.681 | 0.752 | 0.846 | 0.649 | 0.756 | 0.625 | 0.646 | 0.344 | 20.3 |
| layer, ground-truth markers (oracle) | 169 | 0.864 | 0.858 | 0.946 | 0.888 | 0.651 | 0.964 | 0.819 | 0.862 | 0.026 | 18.2 |
| layer, image-gradient costs | 169 | 0.533 | 0.320 | 0.496 | 0.684 | 0.406 | 0.559 | 0.343 | 0.489 | 0.200 | 18.6 |
| marker watershed on the contour map | 169 | 0.622 | 0.507 | 0.653 | 0.756 | 0.490 | 0.709 | 0.508 | 0.548 | 0.200 | 18.6 |
| ground truth instances | 169 | 1.000 | 1.000 | 1.000 | 1.000 | 0.629 | 1.000 | 1.000 | 1.000 | 0.000 | 18.5 |

**Adrenal_gland**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 148 | 0.716 | 0.676 | 0.774 | 0.808 | 0.554 | 0.694 | 0.582 | 0.655 | 0.378 | 18.4 |
| U-Net + contour head, watershed (b) | 148 | 0.719 | 0.689 | 0.783 | 0.811 | 0.551 | 0.712 | 0.605 | 0.713 | 0.444 | 20.1 |
| sec. 11 run: layer | 148 | 0.714 | 0.688 | 0.780 | 0.809 | 0.571 | 0.726 | 0.615 | 0.695 | 0.394 | 19.1 |
| s > 0.5, components | 148 | 0.604 | 0.413 | 0.576 | 0.715 | 0.362 | 0.032 | 0.024 | 0.458 | 60.639 | 605.9 |
| layer, converged (predicted markers) | 148 | 0.710 | 0.689 | 0.781 | 0.823 | 0.565 | 0.826 | 0.700 | 0.693 | 0.244 | 16.5 |
| layer + fallback markers | 148 | 0.709 | 0.688 | 0.779 | 0.824 | 0.564 | 0.800 | 0.677 | 0.692 | 0.325 | 17.9 |
| layer, ground-truth markers (oracle) | 148 | 0.866 | 0.826 | 0.930 | 0.866 | 0.583 | 0.961 | 0.833 | 0.870 | 0.026 | 15.6 |
| layer, image-gradient costs | 148 | 0.516 | 0.184 | 0.365 | 0.606 | 0.267 | 0.640 | 0.401 | 0.519 | 0.247 | 16.5 |
| marker watershed on the contour map | 148 | 0.628 | 0.447 | 0.617 | 0.711 | 0.403 | 0.769 | 0.573 | 0.608 | 0.247 | 16.5 |
| ground truth instances | 148 | 1.000 | 1.000 | 1.000 | 1.000 | 0.557 | 1.000 | 1.000 | 1.000 | 0.000 | 16.0 |

## Paired per-patch differences (2523 patches; bootstrap 95 % intervals; F1 / PQ / AJI dataset-level, bootstrapped over patches)

| comparison | IoU | BF₂ | edge align. | F1@0.5 | PQ | AJI |
|---|---|---|---|---|---|---|
| layer − U-Net (sec. 6) logits | -0.013 [-0.016, -0.010] | -0.008 [-0.011, -0.005] | +0.007 [+0.005, +0.009] | +0.131 [+0.127, +0.136] | +0.110 [+0.106, +0.114] | +0.148 [+0.133, +0.162] |
| layer − contour-head U-Net, watershed (b) | -0.013 [-0.016, -0.009] | -0.013 [-0.016, -0.010] | +0.016 [+0.014, +0.017] | +0.073 [+0.069, +0.076] | +0.058 [+0.055, +0.061] | -0.015 [-0.017, -0.013] |
| layer − sec. 11 layer | -0.000 [-0.004, +0.003] | +0.003 [-0.001, +0.006] | -0.002 [-0.004, -0.001] | +0.107 [+0.102, +0.112] | +0.087 [+0.082, +0.091] | -0.010 [-0.012, -0.007] |
| layer, ground-truth markers − sec. 11 layer, ground-truth markers | -0.000 [-0.001, +0.001] | +0.000 [-0.001, +0.001] | +0.000 [-0.000, +0.001] | -0.000 [-0.002, +0.001] | -0.000 [-0.001, +0.001] | -0.000 [-0.001, +0.000] |
| layer − this model's own logits | +0.121 [+0.116, +0.126] | +0.194 [+0.189, +0.200] | +0.194 [+0.192, +0.197] | +0.756 [+0.750, +0.761] | +0.619 [+0.613, +0.623] | +0.479 [+0.464, +0.492] |
| layer − marker watershed, same markers | +0.086 [+0.084, +0.088] | +0.148 [+0.146, +0.150] | +0.161 [+0.159, +0.163] | +0.084 [+0.081, +0.088] | +0.148 [+0.146, +0.150] | +0.104 [+0.102, +0.106] |
| layer − layer with image costs | +0.160 [+0.157, +0.163] | +0.316 [+0.311, +0.322] | +0.283 [+0.279, +0.287] | +0.170 [+0.164, +0.176] | +0.251 [+0.247, +0.255] | +0.131 [+0.128, +0.134] |
| layer + fallback − U-Net (sec. 6) logits | -0.015 [-0.018, -0.012] | -0.009 [-0.012, -0.007] | +0.007 [+0.005, +0.009] | +0.115 [+0.110, +0.119] | +0.096 [+0.092, +0.100] | +0.148 [+0.133, +0.161] |
| layer + fallback − contour-head U-Net, watershed (b) | -0.015 [-0.017, -0.012] | -0.014 [-0.017, -0.011] | +0.016 [+0.014, +0.017] | +0.056 [+0.053, +0.059] | +0.043 [+0.041, +0.046] | -0.015 [-0.017, -0.013] |
| layer + fallback − layer | -0.002 [-0.004, -0.000] | -0.001 [-0.003, +0.000] | -0.000 [-0.001, +0.000] | -0.017 [-0.018, -0.016] | -0.014 [-0.015, -0.014] | -0.000 [-0.000, +0.000] |
| layer, ground-truth markers − layer | +0.153 [+0.148, +0.159] | +0.161 [+0.155, +0.166] | +0.008 [+0.006, +0.010] | +0.171 [+0.167, +0.175] | +0.164 [+0.161, +0.167] | +0.215 [+0.211, +0.219] |
| on the 307 limit patches: PW limit (learned) − layer | -0.013 [-0.015, -0.011] | -0.019 [-0.022, -0.016] | -0.000 [-0.002, +0.002] | -0.008 [-0.010, -0.005] | -0.016 [-0.018, -0.014] | -0.017 [-0.019, -0.015] |
| on the 307 limit patches: PW limit (learned) − PW limit (image costs) | +0.148 [+0.139, +0.157] | +0.295 [+0.279, +0.311] | +0.289 [+0.278, +0.299] | +0.163 [+0.147, +0.180] | +0.229 [+0.217, +0.244] | +0.108 [+0.100, +0.116] |
| on the 307 limit patches: PW limit (learned) − U-Net (sec. 6) logits | -0.029 [-0.038, -0.019] | -0.033 [-0.042, -0.023] | +0.011 [+0.004, +0.019] | +0.122 [+0.109, +0.137] | +0.094 [+0.082, +0.106] | +0.174 [+0.122, +0.220] |

## By crowding (F1@0.5 / PQ / count error)

| patches | n | U-Net (sec. 6) | contour-head U-Net, watershed (b) | layer | layer + fallback | marker watershed, same markers | PW limit (learned, subset) |
|---|---|---|---|---|---|---|---|
| < 10 nuclei | 486 | 0.608 / 0.485 / 0.68 | 0.596 / 0.479 / 0.81 | 0.697 / 0.560 / 0.60 | 0.649 / 0.520 / 0.86 | 0.631 / 0.438 / 0.61 | 0.645 / 0.498 / 0.67 |
| 10–30 | 1383 | 0.691 / 0.563 / 0.18 | 0.719 / 0.591 / 0.27 | 0.806 / 0.659 / 0.13 | 0.785 / 0.642 / 0.17 | 0.740 / 0.523 / 0.13 | 0.800 / 0.642 / 0.13 |
| 30–60 | 525 | 0.650 / 0.524 / 0.15 | 0.733 / 0.596 / 0.15 | 0.797 / 0.646 / 0.11 | 0.784 / 0.635 / 0.10 | 0.707 / 0.494 / 0.11 | 0.762 / 0.606 / 0.11 |
| > 60 | 129 | 0.588 / 0.469 / 0.24 | 0.700 / 0.562 / 0.13 | 0.745 / 0.602 / 0.20 | 0.739 / 0.596 / 0.17 | 0.620 / 0.426 / 0.20 | 0.680 / 0.538 / 0.26 |

## Marker quality by crowding (nuclei with one / none / several markers; background markers per patch)

| patches | one | none | several | bg markers / patch |
|---|---|---|---|---|
| < 10 nuclei | 83.2 % | 15.3 % | 1.4 % | 1.69 |
| 10–30 | 85.8 % | 13.3 % | 0.9 % | 3.04 |
| 30–60 | 82.0 % | 17.5 % | 0.5 % | 3.91 |
| > 60 | 73.3 % | 26.4 % | 0.3 % | 5.02 |
