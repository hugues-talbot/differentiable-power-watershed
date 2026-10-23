# Instances as labels: multi-marker layer on PanNuke (fold 1 → fold 2)

Run `results_pannuke_instances/dist_sched10_bg/instances`: p 5.0 → 20.0, erosion [2, 3], edge target ×1.0, seam weight 5.0, 30 epochs, seed 0, training solve tol 0.0001 / maxit 100, training markers predicted from epoch 10 (all from 15; thr 0.2 / min area 16 / h 0.2, unmarked nuclei: bg); marker head `dist` (mse, rmax 12; markers = h-maxima h 0.2 grown to thr 0.2, min area 4 px), chosen by PQ on 300 patches of fold 3; learned edge scale 1.85.

## Marker post-processing chosen on fold 3 (300 patches): {'mk_thr': 0.2, 'mk_min_area': 4, 'mk_h': 0.2}

| setting | PQ | F1@0.5 | AJI | count err. | n_pred | one | none | several | bg / patch |
|---|---|---|---|---|---|---|---|---|---|
| thr=0.2/min_area=4/h=0.2 | 0.655 | 0.797 | 0.671 | 0.161 | 23.2 | 85.7 % | 12.7 % | 1.6 % | 4.47 |
| thr=0.2/min_area=1/h=0.2 | 0.655 | 0.797 | 0.671 | 0.161 | 23.3 | 85.9 % | 12.4 % | 1.6 % | 4.59 |
| thr=0.2/min_area=9/h=0.2 | 0.655 | 0.797 | 0.671 | 0.161 | 23.2 | 85.3 % | 13.1 % | 1.6 % | 4.29 |
| thr=0.2/min_area=16/h=0.2 | 0.654 | 0.796 | 0.671 | 0.161 | 23.1 | 84.6 % | 13.7 % | 1.6 % | 4.04 |
| thr=0.3/min_area=4/h=0.2 | 0.645 | 0.785 | 0.665 | 0.161 | 21.9 | 84.1 % | 14.3 % | 1.7 % | 3.48 |
| thr=0.3/min_area=1/h=0.2 | 0.645 | 0.785 | 0.665 | 0.161 | 21.9 | 84.9 % | 13.5 % | 1.7 % | 3.86 |
| thr=0.3/min_area=9/h=0.2 | 0.644 | 0.785 | 0.665 | 0.161 | 21.8 | 83.2 % | 15.2 % | 1.6 % | 3.31 |
| thr=0.2/min_area=4/h=0.1 | 0.644 | 0.786 | 0.665 | 0.171 | 24.3 | 84.8 % | 10.8 % | 4.4 % | 5.29 |
| thr=0.5/min_area=1/h=0.1 (untuned default) | 0.576 | 0.702 | 0.594 | 0.275 | 17.1 | 76.0 % | 21.2 % | 2.7 % | 2.05 |

(top 8 of 72 settings by PQ)

## All of fold 2

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6, binary target), s > 0.5, components | 2523 | 0.719 | 0.652 | 0.769 | 0.807 | 0.577 | 0.656 | 0.531 | 0.494 | 0.275 | 23.0 |
| U-Net + contour head (sec. 10.1, gap target), logits | 2523 | 0.719 | 0.658 | 0.774 | 0.809 | 0.574 | 0.682 | 0.556 | 0.571 | 0.303 | 25.2 |
| U-Net + contour head, tuned marker watershed (b) | 2523 | 0.718 | 0.658 | 0.774 | 0.809 | 0.568 | 0.715 | 0.583 | 0.657 | 0.344 | 27.2 |
| sec. 11.1 dist run: layer, converged (predicted markers) | 2523 | 0.707 | 0.647 | 0.762 | 0.811 | 0.580 | 0.791 | 0.641 | 0.653 | 0.239 | 24.3 |
| this model: s > 0.5, components | 2523 | 0.616 | 0.448 | 0.604 | 0.717 | 0.401 | 0.141 | 0.098 | 0.236 | 7.489 | 125.5 |
| this model: layer, converged (predicted markers) | 2523 | 0.715 | 0.658 | 0.775 | 0.803 | 0.588 | 0.795 | 0.649 | 0.668 | 0.182 | 22.8 |
| this model: layer + fallback markers | 2523 | 0.715 | 0.658 | 0.775 | 0.803 | 0.588 | 0.793 | 0.648 | 0.668 | 0.184 | 22.9 |
| this model: layer, ground-truth markers (oracle) | 2523 | 0.775 | 0.708 | 0.828 | 0.806 | 0.600 | 0.872 | 0.723 | 0.771 | 0.142 | 20.3 |
| this model: layer, image-gradient costs | 2523 | 0.509 | 0.228 | 0.391 | 0.619 | 0.263 | 0.511 | 0.310 | 0.472 | 0.269 | 25.4 |
| this model: marker watershed on the contour map | 2523 | 0.622 | 0.455 | 0.612 | 0.716 | 0.406 | 0.706 | 0.491 | 0.575 | 0.269 | 25.4 |
| this model: PW limit, learned costs | 307 | 0.625 | 0.579 | 0.691 | 0.733 | 0.622 | 0.700 | 0.564 | 0.554 | 0.285 | 18.4 |
| this model: PW limit, image-gradient costs | 307 | 0.502 | 0.231 | 0.388 | 0.616 | 0.258 | 0.485 | 0.292 | 0.466 | 0.285 | 26.0 |
| this model: ground truth instances | 2523 | 1.000 | 1.000 | 1.000 | 1.000 | 0.559 | 1.000 | 1.000 | 1.000 | 0.000 | 23.7 |

## Marker quality (predicted markers against the ground-truth nuclei)

- 59872 nuclei in fold 2 (23.7 per patch); predicted markers 25.4 per patch.
- exactly one marker: 85.5 %; none: 12.7 %; several: 1.8 %; markers in background: 4.27 per patch.
- with fallback markers: one 86.1 %, none 11.9 %, several 2.0 %, background 4.92 per patch, 26.3 markers per patch.
- sec. 11.1 dist run: one 83.9 %, none 14.5 %, several 1.6 %, background 3.58 per patch, 24.3 markers per patch.

## Inference cost

- U-Net forward: 0.9 ms per image; converged multi-marker solve (tol 1e-05): 89.9 ms per image at K = 25.4 markers per image (66650 systems in 158 batches of 16; 254 PCG iterations per batch).
- exact K-label PW limit (one CPU core): 1.0 s per patch with the learned costs, 0.7 s with image-gradient costs, K = 26.0; 11986 ambiguous plateaus solved over 307 patches.

## Per tissue type

**Breast**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 749 | 0.722 | 0.596 | 0.756 | 0.780 | 0.585 | 0.690 | 0.547 | 0.550 | 0.198 | 21.2 |
| U-Net + contour head, watershed (b) | 749 | 0.722 | 0.601 | 0.761 | 0.782 | 0.576 | 0.757 | 0.605 | 0.671 | 0.242 | 24.5 |
| sec. 11.1 dist run: layer | 749 | 0.708 | 0.585 | 0.743 | 0.782 | 0.587 | 0.817 | 0.647 | 0.661 | 0.187 | 22.9 |
| s > 0.5, components | 749 | 0.622 | 0.414 | 0.581 | 0.692 | 0.386 | 0.133 | 0.091 | 0.272 | 7.685 | 128.6 |
| layer, converged (predicted markers) | 749 | 0.715 | 0.598 | 0.757 | 0.777 | 0.597 | 0.822 | 0.657 | 0.677 | 0.141 | 21.5 |
| layer + fallback markers | 749 | 0.715 | 0.598 | 0.757 | 0.777 | 0.598 | 0.821 | 0.656 | 0.677 | 0.142 | 21.6 |
| layer, ground-truth markers (oracle) | 749 | 0.777 | 0.654 | 0.817 | 0.786 | 0.609 | 0.900 | 0.731 | 0.771 | 0.113 | 19.3 |
| layer, image-gradient costs | 749 | 0.523 | 0.218 | 0.369 | 0.604 | 0.235 | 0.554 | 0.340 | 0.507 | 0.200 | 23.8 |
| marker watershed on the contour map | 749 | 0.624 | 0.418 | 0.584 | 0.691 | 0.392 | 0.731 | 0.500 | 0.587 | 0.200 | 23.8 |
| PW limit, learned costs | 89 | 0.629 | 0.514 | 0.663 | 0.705 | 0.630 | 0.753 | 0.591 | 0.585 | 0.260 | 17.2 |
| PW limit, image-gradient costs | 89 | 0.528 | 0.225 | 0.374 | 0.601 | 0.222 | 0.541 | 0.330 | 0.500 | 0.150 | 24.3 |
| ground truth instances | 749 | 1.000 | 1.000 | 1.000 | 1.000 | 0.553 | 1.000 | 1.000 | 1.000 | 0.000 | 21.7 |

**Colon**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 468 | 0.698 | 0.617 | 0.738 | 0.788 | 0.558 | 0.547 | 0.431 | 0.349 | 0.274 | 21.1 |
| U-Net + contour head, watershed (b) | 468 | 0.691 | 0.621 | 0.742 | 0.788 | 0.550 | 0.630 | 0.497 | 0.574 | 0.340 | 27.7 |
| sec. 11.1 dist run: layer | 468 | 0.683 | 0.605 | 0.726 | 0.791 | 0.569 | 0.709 | 0.558 | 0.579 | 0.238 | 23.8 |
| s > 0.5, components | 468 | 0.598 | 0.438 | 0.582 | 0.711 | 0.406 | 0.094 | 0.064 | 0.134 | 7.673 | 142.3 |
| layer, converged (predicted markers) | 468 | 0.688 | 0.617 | 0.739 | 0.779 | 0.573 | 0.711 | 0.564 | 0.592 | 0.197 | 22.2 |
| layer + fallback markers | 468 | 0.688 | 0.617 | 0.739 | 0.779 | 0.574 | 0.710 | 0.563 | 0.592 | 0.199 | 22.3 |
| layer, ground-truth markers (oracle) | 468 | 0.733 | 0.653 | 0.776 | 0.780 | 0.580 | 0.802 | 0.648 | 0.715 | 0.182 | 20.3 |
| layer, image-gradient costs | 468 | 0.506 | 0.283 | 0.416 | 0.628 | 0.291 | 0.425 | 0.253 | 0.437 | 0.263 | 25.1 |
| marker watershed on the contour map | 468 | 0.605 | 0.446 | 0.589 | 0.709 | 0.409 | 0.600 | 0.407 | 0.506 | 0.265 | 25.1 |
| PW limit, learned costs | 62 | 0.523 | 0.486 | 0.593 | 0.678 | 0.593 | 0.534 | 0.414 | 0.414 | 0.386 | 20.0 |
| PW limit, image-gradient costs | 62 | 0.466 | 0.273 | 0.398 | 0.614 | 0.270 | 0.348 | 0.207 | 0.385 | 0.241 | 30.3 |
| ground truth instances | 468 | 1.000 | 1.000 | 1.000 | 1.000 | 0.539 | 1.000 | 1.000 | 1.000 | 0.000 | 25.4 |

**HeadNeck**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 169 | 0.672 | 0.658 | 0.744 | 0.835 | 0.648 | 0.640 | 0.519 | 0.556 | 0.424 | 20.2 |
| U-Net + contour head, watershed (b) | 169 | 0.682 | 0.675 | 0.756 | 0.839 | 0.638 | 0.688 | 0.565 | 0.660 | 0.474 | 23.6 |
| sec. 11.1 dist run: layer | 169 | 0.701 | 0.711 | 0.782 | 0.846 | 0.631 | 0.784 | 0.647 | 0.651 | 0.203 | 19.8 |
| s > 0.5, components | 169 | 0.600 | 0.499 | 0.628 | 0.769 | 0.487 | 0.149 | 0.104 | 0.304 | 6.149 | 100.4 |
| layer, converged (predicted markers) | 169 | 0.714 | 0.713 | 0.796 | 0.831 | 0.645 | 0.785 | 0.646 | 0.663 | 0.177 | 18.4 |
| layer + fallback markers | 169 | 0.714 | 0.713 | 0.796 | 0.831 | 0.645 | 0.782 | 0.643 | 0.663 | 0.183 | 18.6 |
| layer, ground-truth markers (oracle) | 169 | 0.762 | 0.751 | 0.839 | 0.830 | 0.654 | 0.871 | 0.723 | 0.764 | 0.157 | 15.9 |
| layer, image-gradient costs | 169 | 0.503 | 0.290 | 0.453 | 0.668 | 0.374 | 0.425 | 0.250 | 0.458 | 0.293 | 21.2 |
| marker watershed on the contour map | 169 | 0.622 | 0.523 | 0.651 | 0.767 | 0.488 | 0.706 | 0.497 | 0.574 | 0.293 | 21.2 |
| ground truth instances | 169 | 1.000 | 1.000 | 1.000 | 1.000 | 0.629 | 1.000 | 1.000 | 1.000 | 0.000 | 18.5 |

**Adrenal_gland**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 148 | 0.716 | 0.676 | 0.774 | 0.808 | 0.554 | 0.694 | 0.582 | 0.655 | 0.378 | 18.4 |
| U-Net + contour head, watershed (b) | 148 | 0.719 | 0.689 | 0.783 | 0.811 | 0.551 | 0.712 | 0.605 | 0.713 | 0.444 | 20.1 |
| sec. 11.1 dist run: layer | 148 | 0.709 | 0.688 | 0.779 | 0.824 | 0.562 | 0.823 | 0.696 | 0.696 | 0.260 | 17.1 |
| s > 0.5, components | 148 | 0.623 | 0.445 | 0.595 | 0.727 | 0.383 | 0.141 | 0.103 | 0.505 | 9.755 | 128.8 |
| layer, converged (predicted markers) | 148 | 0.713 | 0.693 | 0.788 | 0.809 | 0.567 | 0.822 | 0.697 | 0.705 | 0.203 | 15.7 |
| layer + fallback markers | 148 | 0.713 | 0.693 | 0.788 | 0.809 | 0.567 | 0.820 | 0.695 | 0.705 | 0.201 | 15.8 |
| layer, ground-truth markers (oracle) | 148 | 0.773 | 0.737 | 0.836 | 0.811 | 0.588 | 0.888 | 0.763 | 0.795 | 0.168 | 13.7 |
| layer, image-gradient costs | 148 | 0.484 | 0.152 | 0.312 | 0.587 | 0.244 | 0.528 | 0.319 | 0.488 | 0.299 | 18.1 |
| marker watershed on the contour map | 148 | 0.628 | 0.451 | 0.602 | 0.725 | 0.391 | 0.742 | 0.547 | 0.619 | 0.299 | 18.1 |
| ground truth instances | 148 | 1.000 | 1.000 | 1.000 | 1.000 | 0.557 | 1.000 | 1.000 | 1.000 | 0.000 | 16.0 |

## Paired per-patch differences (2523 patches; bootstrap 95 % intervals; F1 / PQ / AJI dataset-level, bootstrapped over patches)

| comparison | IoU | BF₂ | edge align. | F1@0.5 | PQ | AJI |
|---|---|---|---|---|---|---|
| layer − U-Net (sec. 6) logits | -0.003 [-0.006, -0.000] | +0.006 [+0.003, +0.009] | +0.011 [+0.009, +0.012] | +0.139 [+0.134, +0.144] | +0.118 [+0.115, +0.123] | +0.173 [+0.158, +0.188] |
| layer − contour-head U-Net, watershed (b) | -0.003 [-0.006, +0.000] | +0.001 [-0.002, +0.004] | +0.020 [+0.018, +0.021] | +0.080 [+0.077, +0.084] | +0.066 [+0.064, +0.069] | +0.010 [+0.008, +0.013] |
| layer − sec. 11.1 dist run layer | +0.009 [+0.005, +0.012] | +0.013 [+0.010, +0.016] | +0.008 [+0.006, +0.009] | +0.005 [+0.002, +0.007] | +0.008 [+0.006, +0.010] | +0.015 [+0.013, +0.017] |
| layer, ground-truth markers − sec. 11.1 dist run layer, ground-truth markers | -0.084 [-0.088, -0.081] | -0.094 [-0.098, -0.090] | +0.010 [+0.008, +0.011] | -0.086 [-0.091, -0.083] | -0.082 [-0.085, -0.079] | -0.087 [-0.089, -0.084] |
| layer − this model's own logits | +0.100 [+0.096, +0.103] | +0.171 [+0.167, +0.175] | +0.188 [+0.186, +0.191] | +0.654 [+0.648, +0.660] | +0.552 [+0.546, +0.557] | +0.431 [+0.413, +0.450] |
| layer − marker watershed, same markers | +0.094 [+0.091, +0.096] | +0.163 [+0.160, +0.167] | +0.183 [+0.180, +0.185] | +0.089 [+0.087, +0.092] | +0.158 [+0.157, +0.160] | +0.093 [+0.091, +0.094] |
| layer − layer with image costs | +0.207 [+0.203, +0.210] | +0.384 [+0.378, +0.390] | +0.326 [+0.322, +0.330] | +0.284 [+0.277, +0.290] | +0.340 [+0.335, +0.344] | +0.196 [+0.180, +0.223] |
| layer + fallback − U-Net (sec. 6) logits | -0.003 [-0.006, -0.000] | +0.006 [+0.003, +0.009] | +0.011 [+0.010, +0.012] | +0.137 [+0.132, +0.142] | +0.117 [+0.113, +0.121] | +0.173 [+0.158, +0.188] |
| layer + fallback − contour-head U-Net, watershed (b) | -0.003 [-0.006, +0.000] | +0.001 [-0.002, +0.004] | +0.020 [+0.019, +0.021] | +0.078 [+0.076, +0.082] | +0.064 [+0.062, +0.067] | +0.010 [+0.008, +0.013] |
| layer + fallback − layer | -0.000 [-0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.002 [-0.002, -0.002] | -0.002 [-0.002, -0.001] | +0.000 [-0.000, +0.000] |
| layer, ground-truth markers − layer | +0.059 [+0.055, +0.064] | +0.053 [+0.049, +0.058] | +0.014 [+0.012, +0.015] | +0.077 [+0.074, +0.080] | +0.074 [+0.071, +0.076] | +0.103 [+0.100, +0.106] |
| on the 307 limit patches: PW limit (learned) − layer | -0.080 [-0.092, -0.065] | -0.072 [-0.084, -0.058] | +0.041 [+0.035, +0.047] | -0.071 [-0.081, -0.060] | -0.062 [-0.069, -0.054] | -0.088 [-0.097, -0.077] |
| on the 307 limit patches: PW limit (learned) − PW limit (image costs) | +0.124 [+0.109, +0.139] | +0.303 [+0.281, +0.324] | +0.367 [+0.353, +0.379] | +0.215 [+0.199, +0.231] | +0.272 [+0.257, +0.286] | +0.088 [+0.076, +0.099] |
| on the 307 limit patches: PW limit (learned) − U-Net (sec. 6) logits | -0.088 [-0.101, -0.073] | -0.072 [-0.085, -0.058] | +0.053 [+0.046, +0.060] | +0.067 [+0.049, +0.083] | +0.055 [+0.040, +0.068] | +0.129 [+0.076, +0.171] |

## By crowding (F1@0.5 / PQ / count error)

| patches | n | U-Net (sec. 6) | contour-head U-Net, watershed (b) | layer | layer + fallback | marker watershed, same markers | PW limit (learned, subset) |
|---|---|---|---|---|---|---|---|
| < 10 nuclei | 486 | 0.608 / 0.485 / 0.68 | 0.596 / 0.479 / 0.81 | 0.716 / 0.576 / 0.42 | 0.713 / 0.574 / 0.43 | 0.590 / 0.407 / 0.71 | 0.605 / 0.475 / 0.42 |
| 10–30 | 1383 | 0.691 / 0.563 / 0.18 | 0.719 / 0.591 / 0.27 | 0.805 / 0.663 / 0.13 | 0.803 / 0.661 / 0.13 | 0.721 / 0.508 / 0.19 | 0.739 / 0.603 / 0.25 |
| 30–60 | 525 | 0.650 / 0.524 / 0.15 | 0.733 / 0.596 / 0.15 | 0.805 / 0.655 / 0.10 | 0.804 / 0.654 / 0.10 | 0.719 / 0.499 / 0.11 | 0.716 / 0.574 / 0.24 |
| > 60 | 129 | 0.588 / 0.469 / 0.24 | 0.700 / 0.562 / 0.13 | 0.769 / 0.619 / 0.16 | 0.767 / 0.617 / 0.15 | 0.669 / 0.453 / 0.13 | 0.622 / 0.492 / 0.34 |

## Marker quality by crowding (nuclei with one / none / several markers; background markers per patch)

| patches | one | none | several | bg markers / patch |
|---|---|---|---|---|
| < 10 nuclei | 84.9 % | 12.6 % | 2.6 % | 2.06 |
| 10–30 | 88.0 % | 10.0 % | 2.1 % | 4.09 |
| 30–60 | 85.7 % | 12.5 % | 1.8 % | 5.68 |
| > 60 | 79.6 % | 19.6 % | 0.8 % | 8.74 |
