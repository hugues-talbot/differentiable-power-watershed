# Instances as labels: multi-marker layer on PanNuke (fold 1 → fold 2)

Run `results_pannuke_instances/maxit300_tuned/instances`: p 5.0 → 20.0, erosion [2, 3], edge target ×1.0, seam weight 5.0, 30 epochs, training solve tol 0.0001 / maxit 300; marker head `bce` (thr 0.4, min area 16 px), chosen by PQ on 300 patches of fold 3; learned edge scale 2.09.

## Marker post-processing chosen on fold 3 (300 patches): {'mk_thr': 0.4, 'mk_min_area': 16}

| setting | PQ | F1@0.5 | AJI | count err. | n_pred | one | none | several | bg / patch |
|---|---|---|---|---|---|---|---|---|---|
| thr=0.4/min_area=16 | 0.641 | 0.779 | 0.650 | 0.177 | 22.4 | 78.9 % | 20.0 % | 1.1 % | 2.86 |
| thr=0.4/min_area=9 | 0.639 | 0.778 | 0.652 | 0.175 | 23.1 | 80.1 % | 18.5 % | 1.4 % | 3.19 |
| thr=0.5/min_area=16 | 0.638 | 0.776 | 0.658 | 0.187 | 21.5 | 77.1 % | 21.7 % | 1.2 % | 2.31 |
| thr=0.5/min_area=9 | 0.637 | 0.776 | 0.659 | 0.180 | 22.2 | 78.2 % | 20.3 % | 1.5 % | 2.58 |
| thr=0.4/min_area=4 | 0.633 | 0.772 | 0.652 | 0.185 | 24.0 | 80.8 % | 17.1 % | 2.1 % | 3.64 |
| thr=0.5/min_area=4 | 0.631 | 0.770 | 0.659 | 0.189 | 23.1 | 79.0 % | 18.8 % | 2.2 % | 2.94 |
| thr=0.3/min_area=16 | 0.629 | 0.766 | 0.627 | 0.169 | 23.2 | 80.3 % | 18.9 % | 0.8 % | 3.48 |
| thr=0.3/min_area=9 | 0.627 | 0.763 | 0.628 | 0.181 | 24.0 | 81.4 % | 17.6 % | 1.0 % | 3.91 |
| thr=0.5/min_area=1 (untuned default) | 0.541 | 0.661 | 0.658 | 0.585 | 31.3 | 73.7 % | 16.5 % | 9.8 % | 7.71 |

(top 8 of 24 settings by PQ)

## All of fold 2

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6, binary target), s > 0.5, components | 2523 | 0.719 | 0.652 | 0.769 | 0.807 | 0.577 | 0.656 | 0.531 | 0.494 | 0.275 | 23.0 |
| U-Net + contour head (sec. 10.1, gap target), logits | 2523 | 0.719 | 0.658 | 0.774 | 0.809 | 0.574 | 0.682 | 0.556 | 0.571 | 0.303 | 25.2 |
| U-Net + contour head, tuned marker watershed (b) | 2523 | 0.718 | 0.658 | 0.774 | 0.809 | 0.568 | 0.715 | 0.583 | 0.657 | 0.344 | 27.2 |
| sec. 11 run: layer, converged (BCE marker head, thr 0.5) | 2523 | 0.706 | 0.643 | 0.759 | 0.795 | 0.585 | 0.681 | 0.554 | 0.652 | 0.460 | 28.6 |
| this model: s > 0.5, components | 2523 | 0.583 | 0.399 | 0.576 | 0.695 | 0.400 | 0.029 | 0.020 | 0.142 | 41.731 | 572.2 |
| this model: layer, converged (predicted markers) | 2523 | 0.707 | 0.646 | 0.760 | 0.800 | 0.584 | 0.770 | 0.631 | 0.647 | 0.200 | 21.6 |
| this model: layer + fallback markers | 2523 | 0.705 | 0.647 | 0.762 | 0.804 | 0.585 | 0.738 | 0.604 | 0.647 | 0.277 | 24.5 |
| this model: layer, ground-truth markers (oracle) | 2523 | 0.859 | 0.798 | 0.922 | 0.859 | 0.590 | 0.960 | 0.806 | 0.858 | 0.020 | 23.3 |
| this model: layer, image-gradient costs | 2523 | 0.520 | 0.230 | 0.393 | 0.614 | 0.260 | 0.495 | 0.311 | 0.495 | 0.200 | 21.6 |
| this model: marker watershed on the contour map | 2523 | 0.616 | 0.439 | 0.620 | 0.686 | 0.424 | 0.691 | 0.484 | 0.530 | 0.200 | 21.6 |
| this model: PW limit, learned costs | 307 | 0.686 | 0.607 | 0.730 | 0.782 | 0.576 | 0.741 | 0.593 | 0.608 | 0.188 | 22.4 |
| this model: PW limit, image-gradient costs | 307 | 0.510 | 0.224 | 0.380 | 0.612 | 0.252 | 0.470 | 0.293 | 0.477 | 0.191 | 22.4 |
| this model: ground truth instances | 2523 | 1.000 | 1.000 | 1.000 | 1.000 | 0.559 | 1.000 | 1.000 | 1.000 | 0.000 | 23.7 |

## Marker quality (predicted markers against the ground-truth nuclei)

- 59872 nuclei in fold 2 (23.7 per patch); predicted markers 21.6 per patch.
- exactly one marker: 77.6 %; none: 21.3 %; several: 1.1 %; markers in background: 2.62 per patch.
- with fallback markers: one 82.1 %, none 16.4 %, several 1.5 %, background 5.15 per patch, 25.4 markers per patch.
- sec. 11 run: one 73.2 %, none 17.4 %, several 9.5 %, background 5.88 per patch, 30.5 markers per patch.

## Inference cost

- U-Net forward: 0.8 ms per image; converged multi-marker solve (tol 1e-05): 113.1 ms per image at K = 21.6 markers per image (56977 systems in 158 batches of 16; 241 PCG iterations per batch).
- exact K-label PW limit (one CPU core): 0.7 s per patch with the learned costs, 0.8 s with image-gradient costs, K = 22.4; 6114 ambiguous plateaus solved over 307 patches.

## Per tissue type

**Breast**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 749 | 0.722 | 0.596 | 0.756 | 0.780 | 0.585 | 0.690 | 0.547 | 0.550 | 0.198 | 21.2 |
| U-Net + contour head, watershed (b) | 749 | 0.722 | 0.601 | 0.761 | 0.782 | 0.576 | 0.757 | 0.605 | 0.671 | 0.242 | 24.5 |
| sec. 11 run: layer | 749 | 0.710 | 0.587 | 0.745 | 0.772 | 0.593 | 0.716 | 0.569 | 0.661 | 0.372 | 26.9 |
| s > 0.5, components | 749 | 0.600 | 0.382 | 0.565 | 0.667 | 0.394 | 0.029 | 0.020 | 0.153 | 35.961 | 541.5 |
| layer, converged (predicted markers) | 749 | 0.714 | 0.593 | 0.751 | 0.778 | 0.595 | 0.808 | 0.646 | 0.661 | 0.144 | 21.0 |
| layer + fallback markers | 749 | 0.712 | 0.593 | 0.751 | 0.780 | 0.597 | 0.780 | 0.623 | 0.661 | 0.204 | 23.0 |
| layer, ground-truth markers (oracle) | 749 | 0.854 | 0.745 | 0.909 | 0.838 | 0.597 | 0.968 | 0.806 | 0.853 | 0.015 | 21.4 |
| layer, image-gradient costs | 749 | 0.548 | 0.240 | 0.404 | 0.612 | 0.250 | 0.575 | 0.367 | 0.525 | 0.144 | 21.0 |
| marker watershed on the contour map | 749 | 0.619 | 0.406 | 0.596 | 0.662 | 0.416 | 0.734 | 0.499 | 0.550 | 0.144 | 21.0 |
| PW limit, learned costs | 89 | 0.710 | 0.558 | 0.722 | 0.758 | 0.586 | 0.795 | 0.620 | 0.630 | 0.126 | 21.4 |
| PW limit, image-gradient costs | 89 | 0.561 | 0.246 | 0.408 | 0.613 | 0.236 | 0.570 | 0.362 | 0.517 | 0.126 | 21.5 |
| ground truth instances | 749 | 1.000 | 1.000 | 1.000 | 1.000 | 0.553 | 1.000 | 1.000 | 1.000 | 0.000 | 21.7 |

**Colon**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 468 | 0.698 | 0.617 | 0.738 | 0.788 | 0.558 | 0.547 | 0.431 | 0.349 | 0.274 | 21.1 |
| U-Net + contour head, watershed (b) | 468 | 0.691 | 0.621 | 0.742 | 0.788 | 0.550 | 0.630 | 0.497 | 0.574 | 0.340 | 27.7 |
| sec. 11 run: layer | 468 | 0.681 | 0.602 | 0.724 | 0.773 | 0.572 | 0.570 | 0.451 | 0.584 | 0.698 | 32.9 |
| s > 0.5, components | 468 | 0.560 | 0.374 | 0.536 | 0.687 | 0.401 | 0.017 | 0.012 | 0.073 | 41.379 | 646.5 |
| layer, converged (predicted markers) | 468 | 0.688 | 0.610 | 0.730 | 0.781 | 0.571 | 0.693 | 0.551 | 0.576 | 0.205 | 21.9 |
| layer + fallback markers | 468 | 0.682 | 0.607 | 0.727 | 0.784 | 0.573 | 0.669 | 0.532 | 0.576 | 0.276 | 24.5 |
| layer, ground-truth markers (oracle) | 468 | 0.849 | 0.773 | 0.905 | 0.851 | 0.569 | 0.941 | 0.772 | 0.843 | 0.020 | 24.9 |
| layer, image-gradient costs | 468 | 0.525 | 0.287 | 0.423 | 0.627 | 0.305 | 0.424 | 0.262 | 0.452 | 0.205 | 21.9 |
| marker watershed on the contour map | 468 | 0.611 | 0.429 | 0.596 | 0.681 | 0.426 | 0.585 | 0.401 | 0.463 | 0.205 | 21.9 |
| PW limit, learned costs | 62 | 0.651 | 0.569 | 0.694 | 0.754 | 0.529 | 0.624 | 0.478 | 0.510 | 0.200 | 27.3 |
| PW limit, image-gradient costs | 62 | 0.482 | 0.272 | 0.400 | 0.613 | 0.274 | 0.357 | 0.219 | 0.406 | 0.201 | 27.3 |
| ground truth instances | 468 | 1.000 | 1.000 | 1.000 | 1.000 | 0.539 | 1.000 | 1.000 | 1.000 | 0.000 | 25.4 |

**HeadNeck**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 169 | 0.672 | 0.658 | 0.744 | 0.835 | 0.648 | 0.640 | 0.519 | 0.556 | 0.424 | 20.2 |
| U-Net + contour head, watershed (b) | 169 | 0.682 | 0.675 | 0.756 | 0.839 | 0.638 | 0.688 | 0.565 | 0.660 | 0.474 | 23.6 |
| sec. 11 run: layer | 169 | 0.688 | 0.687 | 0.759 | 0.816 | 0.636 | 0.664 | 0.547 | 0.641 | 0.354 | 22.1 |
| s > 0.5, components | 169 | 0.492 | 0.371 | 0.518 | 0.756 | 0.482 | 0.028 | 0.020 | 0.198 | 47.755 | 521.4 |
| layer, converged (predicted markers) | 169 | 0.683 | 0.684 | 0.753 | 0.815 | 0.624 | 0.752 | 0.625 | 0.638 | 0.215 | 16.9 |
| layer + fallback markers | 169 | 0.673 | 0.680 | 0.753 | 0.826 | 0.634 | 0.705 | 0.584 | 0.639 | 0.306 | 20.4 |
| layer, ground-truth markers (oracle) | 169 | 0.860 | 0.854 | 0.937 | 0.887 | 0.645 | 0.965 | 0.819 | 0.862 | 0.028 | 18.2 |
| layer, image-gradient costs | 169 | 0.489 | 0.272 | 0.407 | 0.642 | 0.319 | 0.387 | 0.236 | 0.457 | 0.215 | 16.9 |
| marker watershed on the contour map | 169 | 0.611 | 0.494 | 0.641 | 0.732 | 0.471 | 0.684 | 0.488 | 0.531 | 0.215 | 16.9 |
| ground truth instances | 169 | 1.000 | 1.000 | 1.000 | 1.000 | 0.629 | 1.000 | 1.000 | 1.000 | 0.000 | 18.5 |

**Adrenal_gland**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 148 | 0.716 | 0.676 | 0.774 | 0.808 | 0.554 | 0.694 | 0.582 | 0.655 | 0.378 | 18.4 |
| U-Net + contour head, watershed (b) | 148 | 0.719 | 0.689 | 0.783 | 0.811 | 0.551 | 0.712 | 0.605 | 0.713 | 0.444 | 20.1 |
| sec. 11 run: layer | 148 | 0.714 | 0.688 | 0.780 | 0.809 | 0.571 | 0.726 | 0.615 | 0.695 | 0.394 | 19.1 |
| s > 0.5, components | 148 | 0.596 | 0.410 | 0.580 | 0.706 | 0.366 | 0.029 | 0.021 | 0.451 | 60.592 | 654.9 |
| layer, converged (predicted markers) | 148 | 0.717 | 0.694 | 0.785 | 0.817 | 0.567 | 0.809 | 0.691 | 0.694 | 0.229 | 15.6 |
| layer + fallback markers | 148 | 0.717 | 0.693 | 0.786 | 0.820 | 0.563 | 0.761 | 0.647 | 0.694 | 0.337 | 18.2 |
| layer, ground-truth markers (oracle) | 148 | 0.868 | 0.829 | 0.933 | 0.867 | 0.579 | 0.961 | 0.833 | 0.872 | 0.025 | 15.6 |
| layer, image-gradient costs | 148 | 0.499 | 0.159 | 0.324 | 0.582 | 0.242 | 0.539 | 0.338 | 0.503 | 0.230 | 15.6 |
| marker watershed on the contour map | 148 | 0.626 | 0.452 | 0.633 | 0.697 | 0.412 | 0.766 | 0.570 | 0.598 | 0.230 | 15.6 |
| ground truth instances | 148 | 1.000 | 1.000 | 1.000 | 1.000 | 0.557 | 1.000 | 1.000 | 1.000 | 0.000 | 16.0 |

## Paired per-patch differences (2523 patches; bootstrap 95 % intervals; F1 / PQ / AJI dataset-level, bootstrapped over patches)

| comparison | IoU | BF₂ | edge align. | F1@0.5 | PQ | AJI |
|---|---|---|---|---|---|---|
| layer − U-Net (sec. 6) logits | -0.011 [-0.015, -0.008] | -0.009 [-0.013, -0.005] | +0.008 [+0.007, +0.010] | +0.113 [+0.108, +0.118] | +0.100 [+0.096, +0.104] | +0.152 [+0.138, +0.166] |
| layer − contour-head U-Net, watershed (b) | -0.011 [-0.014, -0.007] | -0.014 [-0.017, -0.010] | +0.018 [+0.016, +0.019] | +0.055 [+0.050, +0.059] | +0.048 [+0.045, +0.051] | -0.011 [-0.013, -0.008] |
| layer − sec. 11 layer | +0.001 [-0.001, +0.004] | +0.002 [-0.000, +0.004] | -0.001 [-0.002, -0.000] | +0.089 [+0.083, +0.094] | +0.077 [+0.072, +0.081] | -0.005 [-0.007, -0.003] |
| layer, ground-truth markers − sec. 11 layer, ground-truth markers | -0.000 [-0.001, +0.001] | -0.000 [-0.001, +0.001] | -0.001 [-0.001, -0.000] | +0.001 [-0.000, +0.002] | +0.001 [+0.000, +0.002] | +0.001 [+0.000, +0.001] |
| layer − this model's own logits | +0.125 [+0.119, +0.130] | +0.185 [+0.178, +0.191] | +0.191 [+0.188, +0.193] | +0.740 [+0.733, +0.746] | +0.611 [+0.604, +0.616] | +0.505 [+0.491, +0.517] |
| layer − marker watershed, same markers | +0.091 [+0.089, +0.093] | +0.140 [+0.138, +0.143] | +0.160 [+0.158, +0.161] | +0.079 [+0.075, +0.082] | +0.148 [+0.145, +0.150] | +0.116 [+0.112, +0.123] |
| layer − layer with image costs | +0.188 [+0.184, +0.191] | +0.367 [+0.361, +0.373] | +0.324 [+0.320, +0.327] | +0.274 [+0.267, +0.283] | +0.320 [+0.316, +0.327] | +0.152 [+0.149, +0.155] |
| layer + fallback − U-Net (sec. 6) logits | -0.014 [-0.017, -0.011] | -0.007 [-0.010, -0.004] | +0.009 [+0.007, +0.010] | +0.082 [+0.076, +0.088] | +0.073 [+0.068, +0.078] | +0.153 [+0.138, +0.166] |
| layer + fallback − contour-head U-Net, watershed (b) | -0.013 [-0.016, -0.010] | -0.012 [-0.015, -0.009] | +0.017 [+0.016, +0.019] | +0.023 [+0.020, +0.028] | +0.021 [+0.018, +0.024] | -0.010 [-0.013, -0.008] |
| layer + fallback − layer | -0.002 [-0.005, +0.000] | +0.002 [-0.002, +0.005] | +0.000 [-0.001, +0.001] | -0.031 [-0.033, -0.030] | -0.027 [-0.029, -0.026] | +0.000 [-0.000, +0.000] |
| layer, ground-truth markers − layer | +0.152 [+0.147, +0.157] | +0.161 [+0.156, +0.166] | +0.006 [+0.004, +0.008] | +0.190 [+0.186, +0.196] | +0.175 [+0.171, +0.178] | +0.212 [+0.207, +0.216] |
| on the 307 limit patches: PW limit (learned) − layer | -0.011 [-0.013, -0.009] | -0.018 [-0.020, -0.015] | +0.001 [-0.001, +0.003] | -0.006 [-0.008, -0.003] | -0.016 [-0.018, -0.014] | -0.016 [-0.018, -0.014] |
| on the 307 limit patches: PW limit (learned) − PW limit (image costs) | +0.177 [+0.166, +0.188] | +0.350 [+0.332, +0.367] | +0.324 [+0.312, +0.335] | +0.272 [+0.249, +0.297] | +0.300 [+0.283, +0.320] | +0.131 [+0.122, +0.141] |
| on the 307 limit patches: PW limit (learned) − U-Net (sec. 6) logits | -0.027 [-0.037, -0.018] | -0.034 [-0.044, -0.024] | +0.008 [+0.003, +0.014] | +0.108 [+0.091, +0.122] | +0.084 [+0.071, +0.095] | +0.183 [+0.134, +0.225] |

## By crowding (F1@0.5 / PQ / count error)

| patches | n | U-Net (sec. 6) | contour-head U-Net, watershed (b) | layer | layer + fallback | marker watershed, same markers | PW limit (learned, subset) |
|---|---|---|---|---|---|---|---|
| < 10 nuclei | 486 | 0.608 / 0.485 / 0.68 | 0.596 / 0.479 / 0.81 | 0.706 / 0.573 / 0.43 | 0.618 / 0.500 / 0.78 | 0.656 / 0.457 / 0.43 | 0.673 / 0.526 / 0.36 |
| 10–30 | 1383 | 0.691 / 0.563 / 0.18 | 0.719 / 0.591 / 0.27 | 0.788 / 0.650 / 0.14 | 0.750 / 0.617 / 0.18 | 0.730 / 0.516 / 0.14 | 0.782 / 0.631 / 0.13 |
| 30–60 | 525 | 0.650 / 0.524 / 0.15 | 0.733 / 0.596 / 0.15 | 0.778 / 0.635 / 0.13 | 0.756 / 0.615 / 0.11 | 0.694 / 0.483 / 0.13 | 0.744 / 0.593 / 0.14 |
| > 60 | 129 | 0.588 / 0.469 / 0.24 | 0.700 / 0.562 / 0.13 | 0.719 / 0.586 / 0.26 | 0.703 / 0.572 / 0.16 | 0.592 / 0.406 / 0.26 | 0.668 / 0.528 / 0.27 |

## Marker quality by crowding (nuclei with one / none / several markers; background markers per patch)

| patches | one | none | several | bg markers / patch |
|---|---|---|---|---|
| < 10 nuclei | 76.1 % | 22.2 % | 1.6 % | 1.15 |
| 10–30 | 81.4 % | 17.4 % | 1.2 % | 2.62 |
| 30–60 | 78.7 % | 20.0 % | 1.2 % | 3.57 |
| > 60 | 67.3 % | 32.1 % | 0.6 % | 4.29 |
