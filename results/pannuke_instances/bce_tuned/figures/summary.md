# Instances as labels: multi-marker layer on PanNuke (fold 1 → fold 2)

Run `results_pannuke_instances/bce_tuned/instances`: p 5.0 → 20.0, erosion [2, 3], edge target ×1.0, seam weight 5.0, 30 epochs, seed 0, training solve tol 0.0001 / maxit 100; marker head `bce` (thr 0.4, min area 16 px), chosen by PQ on 300 patches of fold 3; learned edge scale 1.99.

## Marker post-processing chosen on fold 3 (300 patches): {'mk_thr': 0.4, 'mk_min_area': 16}

| setting | PQ | F1@0.5 | AJI | count err. | n_pred | one | none | several | bg / patch |
|---|---|---|---|---|---|---|---|---|---|
| thr=0.4/min_area=16 | 0.635 | 0.772 | 0.651 | 0.174 | 22.6 | 78.9 % | 20.0 % | 1.1 % | 3.00 |
| thr=0.5/min_area=16 | 0.634 | 0.771 | 0.660 | 0.176 | 21.8 | 77.2 % | 21.2 % | 1.6 % | 2.35 |
| thr=0.4/min_area=9 | 0.633 | 0.771 | 0.651 | 0.182 | 23.4 | 80.1 % | 18.5 % | 1.4 % | 3.34 |
| thr=0.5/min_area=9 | 0.633 | 0.771 | 0.660 | 0.170 | 22.5 | 78.3 % | 19.7 % | 2.0 % | 2.61 |
| thr=0.4/min_area=4 | 0.628 | 0.765 | 0.651 | 0.189 | 24.3 | 80.4 % | 17.3 % | 2.3 % | 3.76 |
| thr=0.5/min_area=4 | 0.627 | 0.765 | 0.661 | 0.181 | 23.5 | 79.0 % | 18.3 % | 2.7 % | 3.07 |
| thr=0.6/min_area=16 | 0.625 | 0.765 | 0.652 | 0.188 | 20.5 | 73.9 % | 24.5 % | 1.6 % | 1.86 |
| thr=0.6/min_area=9 | 0.624 | 0.764 | 0.654 | 0.185 | 21.3 | 75.4 % | 22.6 % | 2.0 % | 2.11 |
| thr=0.5/min_area=1 (untuned default) | 0.557 | 0.680 | 0.659 | 0.434 | 29.8 | 73.9 % | 16.3 % | 9.8 % | 6.33 |

(top 8 of 24 settings by PQ)

## All of fold 2

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6, binary target), s > 0.5, components | 2523 | 0.719 | 0.652 | 0.769 | 0.807 | 0.577 | 0.656 | 0.531 | 0.494 | 0.275 | 23.0 |
| U-Net + contour head (sec. 10.1, gap target), logits | 2523 | 0.719 | 0.658 | 0.774 | 0.809 | 0.574 | 0.682 | 0.556 | 0.571 | 0.303 | 25.2 |
| U-Net + contour head, tuned marker watershed (b) | 2523 | 0.718 | 0.658 | 0.774 | 0.809 | 0.568 | 0.715 | 0.583 | 0.657 | 0.344 | 27.2 |
| sec. 11 run: layer, converged (predicted markers) | 2523 | 0.706 | 0.643 | 0.759 | 0.795 | 0.585 | 0.681 | 0.554 | 0.652 | 0.460 | 28.6 |
| this model: s > 0.5, components | 2523 | 0.575 | 0.408 | 0.580 | 0.691 | 0.402 | 0.024 | 0.017 | 0.168 | 52.714 | 723.3 |
| this model: layer, converged (predicted markers) | 2523 | 0.708 | 0.646 | 0.761 | 0.801 | 0.587 | 0.769 | 0.630 | 0.645 | 0.208 | 21.7 |
| this model: layer + fallback markers | 2523 | 0.705 | 0.645 | 0.761 | 0.803 | 0.588 | 0.734 | 0.600 | 0.645 | 0.284 | 24.6 |
| this model: layer, ground-truth markers (oracle) | 2523 | 0.859 | 0.796 | 0.922 | 0.858 | 0.591 | 0.959 | 0.805 | 0.858 | 0.020 | 23.3 |
| this model: layer, image-gradient costs | 2523 | 0.514 | 0.225 | 0.387 | 0.611 | 0.257 | 0.476 | 0.297 | 0.490 | 0.209 | 21.7 |
| this model: marker watershed on the contour map | 2523 | 0.613 | 0.452 | 0.629 | 0.683 | 0.429 | 0.690 | 0.480 | 0.535 | 0.209 | 21.7 |
| this model: PW limit, learned costs | 307 | 0.692 | 0.613 | 0.736 | 0.784 | 0.578 | 0.742 | 0.594 | 0.608 | 0.197 | 22.4 |
| this model: PW limit, image-gradient costs | 307 | 0.508 | 0.223 | 0.378 | 0.609 | 0.251 | 0.451 | 0.279 | 0.471 | 0.197 | 22.4 |
| this model: ground truth instances | 2523 | 1.000 | 1.000 | 1.000 | 1.000 | 0.559 | 1.000 | 1.000 | 1.000 | 0.000 | 23.7 |

## Marker quality (predicted markers against the ground-truth nuclei)

- 59872 nuclei in fold 2 (23.7 per patch); predicted markers 21.7 per patch.
- exactly one marker: 77.7 %; none: 21.1 %; several: 1.2 %; markers in background: 2.69 per patch.
- with fallback markers: one 81.6 %, none 16.7 %, several 1.7 %, background 5.09 per patch, 25.3 markers per patch.
- sec. 11 run: one 73.2 %, none 17.4 %, several 9.5 %, background 5.88 per patch, 30.5 markers per patch.

## Inference cost

- U-Net forward: 2.1 ms per image; converged multi-marker solve (tol 1e-05): 238.3 ms per image at K = 21.7 markers per image (57260 systems in 158 batches of 16; 195 PCG iterations per batch).
- exact K-label PW limit (one CPU core): 0.7 s per patch with the learned costs, 0.8 s with image-gradient costs, K = 22.4; 6141 ambiguous plateaus solved over 307 patches.

## Per tissue type

**Breast**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 749 | 0.722 | 0.596 | 0.756 | 0.780 | 0.585 | 0.690 | 0.547 | 0.550 | 0.198 | 21.2 |
| U-Net + contour head, watershed (b) | 749 | 0.722 | 0.601 | 0.761 | 0.782 | 0.576 | 0.757 | 0.605 | 0.671 | 0.242 | 24.5 |
| sec. 11 run: layer | 749 | 0.710 | 0.587 | 0.745 | 0.772 | 0.593 | 0.716 | 0.569 | 0.661 | 0.372 | 26.9 |
| s > 0.5, components | 749 | 0.594 | 0.391 | 0.573 | 0.664 | 0.395 | 0.024 | 0.016 | 0.178 | 45.737 | 683.8 |
| layer, converged (predicted markers) | 749 | 0.716 | 0.594 | 0.752 | 0.780 | 0.598 | 0.805 | 0.644 | 0.659 | 0.145 | 21.2 |
| layer + fallback markers | 749 | 0.714 | 0.594 | 0.751 | 0.781 | 0.598 | 0.775 | 0.620 | 0.659 | 0.214 | 23.1 |
| layer, ground-truth markers (oracle) | 749 | 0.854 | 0.744 | 0.908 | 0.838 | 0.596 | 0.967 | 0.806 | 0.853 | 0.015 | 21.4 |
| layer, image-gradient costs | 749 | 0.545 | 0.239 | 0.403 | 0.610 | 0.247 | 0.565 | 0.357 | 0.521 | 0.146 | 21.2 |
| marker watershed on the contour map | 749 | 0.617 | 0.421 | 0.608 | 0.659 | 0.421 | 0.734 | 0.497 | 0.551 | 0.146 | 21.2 |
| PW limit, learned costs | 89 | 0.715 | 0.567 | 0.728 | 0.764 | 0.589 | 0.789 | 0.618 | 0.633 | 0.124 | 21.7 |
| PW limit, image-gradient costs | 89 | 0.558 | 0.247 | 0.408 | 0.611 | 0.235 | 0.555 | 0.349 | 0.512 | 0.124 | 21.7 |
| ground truth instances | 749 | 1.000 | 1.000 | 1.000 | 1.000 | 0.553 | 1.000 | 1.000 | 1.000 | 0.000 | 21.7 |

**Colon**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 468 | 0.698 | 0.617 | 0.738 | 0.788 | 0.558 | 0.547 | 0.431 | 0.349 | 0.274 | 21.1 |
| U-Net + contour head, watershed (b) | 468 | 0.691 | 0.621 | 0.742 | 0.788 | 0.550 | 0.630 | 0.497 | 0.574 | 0.340 | 27.7 |
| sec. 11 run: layer | 468 | 0.681 | 0.602 | 0.724 | 0.773 | 0.572 | 0.570 | 0.451 | 0.584 | 0.698 | 32.9 |
| s > 0.5, components | 468 | 0.546 | 0.380 | 0.540 | 0.683 | 0.406 | 0.014 | 0.009 | 0.094 | 55.369 | 864.8 |
| layer, converged (predicted markers) | 468 | 0.685 | 0.606 | 0.728 | 0.781 | 0.573 | 0.693 | 0.551 | 0.576 | 0.216 | 21.7 |
| layer + fallback markers | 468 | 0.679 | 0.602 | 0.724 | 0.782 | 0.575 | 0.663 | 0.527 | 0.576 | 0.282 | 24.3 |
| layer, ground-truth markers (oracle) | 468 | 0.850 | 0.773 | 0.906 | 0.851 | 0.569 | 0.939 | 0.770 | 0.842 | 0.025 | 24.8 |
| layer, image-gradient costs | 468 | 0.517 | 0.279 | 0.414 | 0.623 | 0.303 | 0.395 | 0.244 | 0.447 | 0.216 | 21.7 |
| marker watershed on the contour map | 468 | 0.605 | 0.443 | 0.608 | 0.677 | 0.434 | 0.587 | 0.399 | 0.470 | 0.216 | 21.7 |
| PW limit, learned costs | 62 | 0.650 | 0.572 | 0.699 | 0.755 | 0.531 | 0.624 | 0.480 | 0.509 | 0.201 | 26.6 |
| PW limit, image-gradient costs | 62 | 0.479 | 0.264 | 0.392 | 0.610 | 0.275 | 0.329 | 0.201 | 0.402 | 0.201 | 26.6 |
| ground truth instances | 468 | 1.000 | 1.000 | 1.000 | 1.000 | 0.539 | 1.000 | 1.000 | 1.000 | 0.000 | 25.4 |

**HeadNeck**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 169 | 0.672 | 0.658 | 0.744 | 0.835 | 0.648 | 0.640 | 0.519 | 0.556 | 0.424 | 20.2 |
| U-Net + contour head, watershed (b) | 169 | 0.682 | 0.675 | 0.756 | 0.839 | 0.638 | 0.688 | 0.565 | 0.660 | 0.474 | 23.6 |
| sec. 11 run: layer | 169 | 0.688 | 0.687 | 0.759 | 0.816 | 0.636 | 0.664 | 0.547 | 0.641 | 0.354 | 22.1 |
| s > 0.5, components | 169 | 0.481 | 0.376 | 0.518 | 0.751 | 0.489 | 0.025 | 0.017 | 0.218 | 55.611 | 625.7 |
| layer, converged (predicted markers) | 169 | 0.682 | 0.681 | 0.751 | 0.815 | 0.633 | 0.753 | 0.624 | 0.640 | 0.210 | 16.6 |
| layer + fallback markers | 169 | 0.665 | 0.670 | 0.744 | 0.822 | 0.651 | 0.703 | 0.581 | 0.641 | 0.310 | 20.0 |
| layer, ground-truth markers (oracle) | 169 | 0.861 | 0.855 | 0.943 | 0.885 | 0.650 | 0.964 | 0.818 | 0.860 | 0.026 | 18.2 |
| layer, image-gradient costs | 169 | 0.476 | 0.257 | 0.388 | 0.637 | 0.319 | 0.358 | 0.217 | 0.449 | 0.210 | 16.6 |
| marker watershed on the contour map | 169 | 0.607 | 0.505 | 0.647 | 0.729 | 0.484 | 0.688 | 0.488 | 0.538 | 0.210 | 16.6 |
| ground truth instances | 169 | 1.000 | 1.000 | 1.000 | 1.000 | 0.629 | 1.000 | 1.000 | 1.000 | 0.000 | 18.5 |

**Adrenal_gland**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 148 | 0.716 | 0.676 | 0.774 | 0.808 | 0.554 | 0.694 | 0.582 | 0.655 | 0.378 | 18.4 |
| U-Net + contour head, watershed (b) | 148 | 0.719 | 0.689 | 0.783 | 0.811 | 0.551 | 0.712 | 0.605 | 0.713 | 0.444 | 20.1 |
| sec. 11 run: layer | 148 | 0.714 | 0.688 | 0.780 | 0.809 | 0.571 | 0.726 | 0.615 | 0.695 | 0.394 | 19.1 |
| s > 0.5, components | 148 | 0.589 | 0.420 | 0.587 | 0.699 | 0.369 | 0.024 | 0.017 | 0.455 | 72.936 | 798.9 |
| layer, converged (predicted markers) | 148 | 0.716 | 0.693 | 0.785 | 0.816 | 0.571 | 0.808 | 0.688 | 0.694 | 0.246 | 15.7 |
| layer + fallback markers | 148 | 0.716 | 0.692 | 0.784 | 0.818 | 0.568 | 0.758 | 0.644 | 0.694 | 0.333 | 18.1 |
| layer, ground-truth markers (oracle) | 148 | 0.864 | 0.823 | 0.928 | 0.864 | 0.582 | 0.959 | 0.832 | 0.870 | 0.025 | 15.6 |
| layer, image-gradient costs | 148 | 0.492 | 0.156 | 0.320 | 0.578 | 0.240 | 0.521 | 0.325 | 0.497 | 0.249 | 15.7 |
| marker watershed on the contour map | 148 | 0.619 | 0.463 | 0.638 | 0.690 | 0.417 | 0.758 | 0.559 | 0.600 | 0.249 | 15.7 |
| ground truth instances | 148 | 1.000 | 1.000 | 1.000 | 1.000 | 0.557 | 1.000 | 1.000 | 1.000 | 0.000 | 16.0 |

## Paired per-patch differences (2523 patches; bootstrap 95 % intervals; F1 / PQ / AJI dataset-level, bootstrapped over patches)

| comparison | IoU | BF₂ | edge align. | F1@0.5 | PQ | AJI |
|---|---|---|---|---|---|---|
| layer − U-Net (sec. 6) logits | -0.011 [-0.014, -0.008] | -0.008 [-0.012, -0.005] | +0.011 [+0.009, +0.012] | +0.112 [+0.107, +0.118] | +0.099 [+0.095, +0.103] | +0.151 [+0.136, +0.165] |
| layer − contour-head U-Net, watershed (b) | -0.010 [-0.014, -0.007] | -0.013 [-0.017, -0.010] | +0.020 [+0.019, +0.022] | +0.054 [+0.050, +0.058] | +0.046 [+0.043, +0.050] | -0.012 [-0.015, -0.009] |
| layer − sec. 11 run layer | +0.002 [+0.000, +0.003] | +0.002 [+0.000, +0.004] | +0.002 [+0.001, +0.003] | +0.088 [+0.082, +0.094] | +0.075 [+0.071, +0.080] | -0.006 [-0.008, -0.005] |
| layer, ground-truth markers − sec. 11 run layer, ground-truth markers | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| layer − this model's own logits | +0.133 [+0.127, +0.138] | +0.180 [+0.174, +0.187] | +0.193 [+0.190, +0.195] | +0.745 [+0.737, +0.750] | +0.613 [+0.606, +0.618] | +0.477 [+0.464, +0.490] |
| layer − marker watershed, same markers | +0.094 [+0.092, +0.096] | +0.132 [+0.130, +0.134] | +0.159 [+0.157, +0.160] | +0.079 [+0.075, +0.082] | +0.150 [+0.148, +0.153] | +0.110 [+0.108, +0.114] |
| layer − layer with image costs | +0.193 [+0.190, +0.197] | +0.374 [+0.368, +0.379] | +0.330 [+0.326, +0.334] | +0.293 [+0.285, +0.302] | +0.333 [+0.328, +0.339] | +0.156 [+0.153, +0.159] |
| layer + fallback − U-Net (sec. 6) logits | -0.014 [-0.017, -0.011] | -0.008 [-0.011, -0.005] | +0.011 [+0.010, +0.013] | +0.077 [+0.071, +0.083] | +0.069 [+0.064, +0.074] | +0.151 [+0.136, +0.165] |
| layer + fallback − contour-head U-Net, watershed (b) | -0.013 [-0.016, -0.011] | -0.013 [-0.016, -0.010] | +0.020 [+0.019, +0.022] | +0.018 [+0.014, +0.023] | +0.017 [+0.013, +0.020] | -0.012 [-0.015, -0.009] |
| layer + fallback − layer | -0.003 [-0.006, -0.000] | +0.000 [-0.003, +0.003] | -0.000 [-0.001, +0.000] | -0.035 [-0.037, -0.034] | -0.030 [-0.031, -0.029] | -0.000 [-0.000, +0.000] |
| layer, ground-truth markers − layer | +0.152 [+0.147, +0.156] | +0.161 [+0.156, +0.166] | +0.004 [+0.002, +0.006] | +0.190 [+0.185, +0.196] | +0.175 [+0.171, +0.179] | +0.212 [+0.208, +0.217] |
| on the 307 limit patches: PW limit (learned) − layer | -0.011 [-0.013, -0.010] | -0.017 [-0.020, -0.015] | -0.001 [-0.003, +0.000] | -0.004 [-0.006, -0.002] | -0.013 [-0.015, -0.011] | -0.015 [-0.017, -0.014] |
| on the 307 limit patches: PW limit (learned) − PW limit (image costs) | +0.184 [+0.174, +0.194] | +0.359 [+0.341, +0.376] | +0.327 [+0.315, +0.339] | +0.290 [+0.266, +0.315] | +0.315 [+0.297, +0.333] | +0.137 [+0.128, +0.147] |
| on the 307 limit patches: PW limit (learned) − U-Net (sec. 6) logits | -0.022 [-0.030, -0.015] | -0.027 [-0.035, -0.019] | +0.010 [+0.004, +0.016] | +0.108 [+0.093, +0.123] | +0.084 [+0.073, +0.097] | +0.183 [+0.133, +0.229] |

## By crowding (F1@0.5 / PQ / count error)

| patches | n | U-Net (sec. 6) | contour-head U-Net, watershed (b) | layer | layer + fallback | marker watershed, same markers | PW limit (learned, subset) |
|---|---|---|---|---|---|---|---|
| < 10 nuclei | 486 | 0.608 / 0.485 / 0.68 | 0.596 / 0.479 / 0.81 | 0.704 / 0.571 / 0.46 | 0.623 / 0.504 / 0.81 | 0.642 / 0.443 / 0.46 | 0.687 / 0.529 / 0.41 |
| 10–30 | 1383 | 0.691 / 0.563 / 0.18 | 0.719 / 0.591 / 0.27 | 0.787 / 0.648 / 0.15 | 0.746 / 0.614 / 0.18 | 0.727 / 0.510 / 0.15 | 0.781 / 0.631 / 0.13 |
| 30–60 | 525 | 0.650 / 0.524 / 0.15 | 0.733 / 0.596 / 0.15 | 0.778 / 0.634 / 0.13 | 0.750 / 0.611 / 0.11 | 0.695 / 0.480 / 0.13 | 0.747 / 0.596 / 0.14 |
| > 60 | 129 | 0.588 / 0.469 / 0.24 | 0.700 / 0.562 / 0.13 | 0.718 / 0.586 / 0.26 | 0.695 / 0.565 / 0.16 | 0.596 / 0.406 / 0.26 | 0.667 / 0.527 / 0.28 |

## Marker quality by crowding (nuclei with one / none / several markers; background markers per patch)

| patches | one | none | several | bg markers / patch |
|---|---|---|---|---|
| < 10 nuclei | 77.0 % | 21.4 % | 1.6 % | 1.23 |
| 10–30 | 81.4 % | 17.3 % | 1.3 % | 2.66 |
| 30–60 | 78.9 % | 19.9 % | 1.2 % | 3.71 |
| > 60 | 67.2 % | 32.2 % | 0.7 % | 4.22 |
