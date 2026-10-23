# Instances as labels: multi-marker layer on PanNuke (fold 1 → fold 2)

Run `results_pannuke_instances/dist_s1/instances`: p 5.0 → 20.0, erosion [2, 3], edge target ×1.0, seam weight 5.0, 30 epochs, seed 1, training solve tol 0.0001 / maxit 100; marker head `dist` (mse, rmax 12; markers = h-maxima h 0.2 grown to thr 0.2, min area 16 px), chosen by PQ on 300 patches of fold 3; learned edge scale 2.10.

## Marker post-processing chosen on fold 3 (300 patches): {'mk_thr': 0.2, 'mk_min_area': 16, 'mk_h': 0.2}

| setting | PQ | F1@0.5 | AJI | count err. | n_pred | one | none | several | bg / patch |
|---|---|---|---|---|---|---|---|---|---|
| thr=0.2/min_area=16/h=0.2 | 0.649 | 0.792 | 0.658 | 0.183 | 24.6 | 83.8 % | 14.9 % | 1.3 % | 3.76 |
| thr=0.2/min_area=9/h=0.2 | 0.648 | 0.792 | 0.657 | 0.194 | 25.0 | 84.6 % | 14.2 % | 1.3 % | 4.02 |
| thr=0.2/min_area=4/h=0.2 | 0.646 | 0.790 | 0.657 | 0.212 | 25.3 | 85.0 % | 13.8 % | 1.3 % | 4.22 |
| thr=0.2/min_area=1/h=0.2 | 0.645 | 0.789 | 0.657 | 0.217 | 25.6 | 85.5 % | 13.2 % | 1.3 % | 4.44 |
| thr=0.3/min_area=4/h=0.2 | 0.640 | 0.791 | 0.656 | 0.170 | 24.0 | 83.5 % | 15.2 % | 1.3 % | 3.25 |
| thr=0.3/min_area=9/h=0.2 | 0.640 | 0.790 | 0.655 | 0.168 | 23.6 | 82.4 % | 16.3 % | 1.3 % | 3.06 |
| thr=0.3/min_area=16/h=0.2 | 0.640 | 0.790 | 0.655 | 0.162 | 23.1 | 81.3 % | 17.4 % | 1.2 % | 2.86 |
| thr=0.3/min_area=1/h=0.2 | 0.638 | 0.790 | 0.655 | 0.174 | 24.3 | 84.3 % | 14.4 % | 1.3 % | 3.63 |
| thr=0.5/min_area=1/h=0.1 (untuned default) | 0.570 | 0.723 | 0.607 | 0.176 | 21.6 | 76.3 % | 20.8 % | 3.0 % | 2.14 |

(top 8 of 72 settings by PQ)

## All of fold 2

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6, binary target), s > 0.5, components | 2523 | 0.719 | 0.652 | 0.769 | 0.807 | 0.577 | 0.656 | 0.531 | 0.494 | 0.275 | 23.0 |
| U-Net + contour head (sec. 10.1, gap target), logits | 2523 | 0.719 | 0.658 | 0.774 | 0.809 | 0.574 | 0.682 | 0.556 | 0.571 | 0.303 | 25.2 |
| U-Net + contour head, tuned marker watershed (b) | 2523 | 0.718 | 0.658 | 0.774 | 0.809 | 0.568 | 0.715 | 0.583 | 0.657 | 0.344 | 27.2 |
| sec. 11.1 dist run: layer, converged (predicted markers) | 2523 | 0.707 | 0.647 | 0.762 | 0.811 | 0.580 | 0.791 | 0.641 | 0.653 | 0.239 | 24.3 |
| this model: s > 0.5, components | 2523 | 0.606 | 0.392 | 0.560 | 0.723 | 0.385 | 0.035 | 0.025 | 0.171 | 38.335 | 511.4 |
| this model: layer, converged (predicted markers) | 2523 | 0.708 | 0.650 | 0.764 | 0.811 | 0.580 | 0.790 | 0.642 | 0.653 | 0.244 | 24.2 |
| this model: layer + fallback markers | 2523 | 0.707 | 0.650 | 0.764 | 0.813 | 0.581 | 0.778 | 0.631 | 0.653 | 0.312 | 25.6 |
| this model: layer, ground-truth markers (oracle) | 2523 | 0.859 | 0.799 | 0.923 | 0.859 | 0.589 | 0.959 | 0.806 | 0.859 | 0.022 | 23.3 |
| this model: layer, image-gradient costs | 2523 | 0.560 | 0.278 | 0.464 | 0.654 | 0.311 | 0.637 | 0.410 | 0.529 | 0.246 | 24.2 |
| this model: marker watershed on the contour map | 2523 | 0.639 | 0.432 | 0.608 | 0.720 | 0.414 | 0.727 | 0.523 | 0.573 | 0.246 | 24.2 |
| this model: PW limit, learned costs | 307 | 0.689 | 0.608 | 0.731 | 0.790 | 0.573 | 0.757 | 0.600 | 0.606 | 0.257 | 24.8 |
| this model: PW limit, image-gradient costs | 307 | 0.557 | 0.280 | 0.460 | 0.650 | 0.303 | 0.615 | 0.394 | 0.508 | 0.263 | 24.9 |
| this model: ground truth instances | 2523 | 1.000 | 1.000 | 1.000 | 1.000 | 0.559 | 1.000 | 1.000 | 1.000 | 0.000 | 23.7 |

## Marker quality (predicted markers against the ground-truth nuclei)

- 59872 nuclei in fold 2 (23.7 per patch); predicted markers 24.2 per patch.
- exactly one marker: 83.5 %; none: 14.8 %; several: 1.7 %; markers in background: 3.56 per patch.
- with fallback markers: one 85.2 %, none 12.8 %, several 2.1 %, background 4.71 per patch, 25.9 markers per patch.
- sec. 11.1 dist run: one 83.9 %, none 14.5 %, several 1.6 %, background 3.58 per patch, 24.3 markers per patch.

## Inference cost

- U-Net forward: 0.9 ms per image; converged multi-marker solve (tol 1e-05): 61.1 ms per image at K = 24.2 markers per image (63567 systems in 158 batches of 16; 179 PCG iterations per batch).
- exact K-label PW limit (one CPU core): 0.8 s per patch with the learned costs, 0.7 s with image-gradient costs, K = 24.9; 6179 ambiguous plateaus solved over 307 patches.

## Per tissue type

**Breast**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 749 | 0.722 | 0.596 | 0.756 | 0.780 | 0.585 | 0.690 | 0.547 | 0.550 | 0.198 | 21.2 |
| U-Net + contour head, watershed (b) | 749 | 0.722 | 0.601 | 0.761 | 0.782 | 0.576 | 0.757 | 0.605 | 0.671 | 0.242 | 24.5 |
| sec. 11.1 dist run: layer | 749 | 0.708 | 0.585 | 0.743 | 0.782 | 0.587 | 0.817 | 0.647 | 0.661 | 0.187 | 22.9 |
| s > 0.5, components | 749 | 0.623 | 0.372 | 0.549 | 0.695 | 0.377 | 0.036 | 0.026 | 0.186 | 31.028 | 468.5 |
| layer, converged (predicted markers) | 749 | 0.712 | 0.592 | 0.749 | 0.784 | 0.589 | 0.817 | 0.650 | 0.664 | 0.185 | 22.8 |
| layer + fallback markers | 749 | 0.712 | 0.593 | 0.749 | 0.784 | 0.590 | 0.807 | 0.641 | 0.664 | 0.244 | 23.7 |
| layer, ground-truth markers (oracle) | 749 | 0.854 | 0.747 | 0.911 | 0.838 | 0.595 | 0.966 | 0.806 | 0.853 | 0.016 | 21.4 |
| layer, image-gradient costs | 749 | 0.573 | 0.265 | 0.437 | 0.636 | 0.287 | 0.663 | 0.430 | 0.548 | 0.186 | 22.8 |
| marker watershed on the contour map | 749 | 0.643 | 0.397 | 0.582 | 0.693 | 0.401 | 0.761 | 0.535 | 0.587 | 0.186 | 22.8 |
| PW limit, learned costs | 89 | 0.706 | 0.551 | 0.712 | 0.761 | 0.579 | 0.799 | 0.617 | 0.636 | 0.138 | 23.3 |
| PW limit, image-gradient costs | 89 | 0.586 | 0.273 | 0.444 | 0.637 | 0.273 | 0.656 | 0.423 | 0.544 | 0.138 | 23.3 |
| ground truth instances | 749 | 1.000 | 1.000 | 1.000 | 1.000 | 0.553 | 1.000 | 1.000 | 1.000 | 0.000 | 21.7 |

**Colon**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 468 | 0.698 | 0.617 | 0.738 | 0.788 | 0.558 | 0.547 | 0.431 | 0.349 | 0.274 | 21.1 |
| U-Net + contour head, watershed (b) | 468 | 0.691 | 0.621 | 0.742 | 0.788 | 0.550 | 0.630 | 0.497 | 0.574 | 0.340 | 27.7 |
| sec. 11.1 dist run: layer | 468 | 0.683 | 0.605 | 0.726 | 0.791 | 0.569 | 0.709 | 0.558 | 0.579 | 0.238 | 23.8 |
| s > 0.5, components | 468 | 0.582 | 0.371 | 0.527 | 0.715 | 0.382 | 0.022 | 0.015 | 0.097 | 40.085 | 597.9 |
| layer, converged (predicted markers) | 468 | 0.684 | 0.608 | 0.728 | 0.792 | 0.565 | 0.710 | 0.560 | 0.578 | 0.249 | 23.9 |
| layer + fallback markers | 468 | 0.683 | 0.609 | 0.728 | 0.793 | 0.566 | 0.700 | 0.551 | 0.578 | 0.301 | 25.3 |
| layer, ground-truth markers (oracle) | 468 | 0.850 | 0.775 | 0.906 | 0.851 | 0.565 | 0.941 | 0.772 | 0.842 | 0.025 | 24.8 |
| layer, image-gradient costs | 468 | 0.559 | 0.328 | 0.476 | 0.661 | 0.334 | 0.570 | 0.364 | 0.478 | 0.250 | 23.9 |
| marker watershed on the contour map | 468 | 0.624 | 0.418 | 0.580 | 0.712 | 0.415 | 0.623 | 0.439 | 0.502 | 0.250 | 23.9 |
| PW limit, learned costs | 62 | 0.659 | 0.570 | 0.697 | 0.762 | 0.526 | 0.641 | 0.488 | 0.498 | 0.217 | 28.8 |
| PW limit, image-gradient costs | 62 | 0.535 | 0.331 | 0.473 | 0.650 | 0.306 | 0.509 | 0.324 | 0.427 | 0.218 | 28.8 |
| ground truth instances | 468 | 1.000 | 1.000 | 1.000 | 1.000 | 0.539 | 1.000 | 1.000 | 1.000 | 0.000 | 25.4 |

**HeadNeck**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 169 | 0.672 | 0.658 | 0.744 | 0.835 | 0.648 | 0.640 | 0.519 | 0.556 | 0.424 | 20.2 |
| U-Net + contour head, watershed (b) | 169 | 0.682 | 0.675 | 0.756 | 0.839 | 0.638 | 0.688 | 0.565 | 0.660 | 0.474 | 23.6 |
| sec. 11.1 dist run: layer | 169 | 0.701 | 0.711 | 0.782 | 0.846 | 0.631 | 0.784 | 0.647 | 0.651 | 0.203 | 19.8 |
| s > 0.5, components | 169 | 0.523 | 0.384 | 0.520 | 0.778 | 0.483 | 0.035 | 0.025 | 0.226 | 40.576 | 451.2 |
| layer, converged (predicted markers) | 169 | 0.689 | 0.696 | 0.767 | 0.844 | 0.640 | 0.784 | 0.647 | 0.657 | 0.250 | 19.7 |
| layer + fallback markers | 169 | 0.675 | 0.682 | 0.754 | 0.846 | 0.646 | 0.763 | 0.628 | 0.656 | 0.373 | 21.3 |
| layer, ground-truth markers (oracle) | 169 | 0.859 | 0.852 | 0.937 | 0.886 | 0.646 | 0.964 | 0.819 | 0.861 | 0.033 | 18.1 |
| layer, image-gradient costs | 169 | 0.540 | 0.327 | 0.511 | 0.696 | 0.423 | 0.596 | 0.372 | 0.510 | 0.250 | 19.7 |
| marker watershed on the contour map | 169 | 0.628 | 0.497 | 0.638 | 0.772 | 0.495 | 0.734 | 0.537 | 0.579 | 0.250 | 19.7 |
| ground truth instances | 169 | 1.000 | 1.000 | 1.000 | 1.000 | 0.629 | 1.000 | 1.000 | 1.000 | 0.000 | 18.5 |

**Adrenal_gland**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 148 | 0.716 | 0.676 | 0.774 | 0.808 | 0.554 | 0.694 | 0.582 | 0.655 | 0.378 | 18.4 |
| U-Net + contour head, watershed (b) | 148 | 0.719 | 0.689 | 0.783 | 0.811 | 0.551 | 0.712 | 0.605 | 0.713 | 0.444 | 20.1 |
| sec. 11.1 dist run: layer | 148 | 0.709 | 0.688 | 0.779 | 0.824 | 0.562 | 0.823 | 0.696 | 0.696 | 0.260 | 17.1 |
| s > 0.5, components | 148 | 0.621 | 0.405 | 0.563 | 0.737 | 0.355 | 0.035 | 0.026 | 0.472 | 51.385 | 559.3 |
| layer, converged (predicted markers) | 148 | 0.711 | 0.686 | 0.781 | 0.821 | 0.558 | 0.815 | 0.690 | 0.694 | 0.256 | 17.1 |
| layer + fallback markers | 148 | 0.710 | 0.685 | 0.779 | 0.822 | 0.558 | 0.790 | 0.667 | 0.693 | 0.332 | 18.5 |
| layer, ground-truth markers (oracle) | 148 | 0.864 | 0.822 | 0.931 | 0.864 | 0.581 | 0.961 | 0.833 | 0.872 | 0.027 | 15.6 |
| layer, image-gradient costs | 148 | 0.535 | 0.202 | 0.398 | 0.623 | 0.281 | 0.649 | 0.418 | 0.535 | 0.260 | 17.1 |
| marker watershed on the contour map | 148 | 0.648 | 0.446 | 0.614 | 0.733 | 0.398 | 0.770 | 0.590 | 0.630 | 0.260 | 17.1 |
| ground truth instances | 148 | 1.000 | 1.000 | 1.000 | 1.000 | 0.557 | 1.000 | 1.000 | 1.000 | 0.000 | 16.0 |

## Paired per-patch differences (2523 patches; bootstrap 95 % intervals; F1 / PQ / AJI dataset-level, bootstrapped over patches)

| comparison | IoU | BF₂ | edge align. | F1@0.5 | PQ | AJI |
|---|---|---|---|---|---|---|
| layer − U-Net (sec. 6) logits | -0.010 [-0.013, -0.007] | -0.005 [-0.008, -0.002] | +0.003 [+0.002, +0.005] | +0.133 [+0.128, +0.138] | +0.111 [+0.107, +0.115] | +0.159 [+0.143, +0.172] |
| layer − contour-head U-Net, watershed (b) | -0.010 [-0.012, -0.007] | -0.010 [-0.013, -0.007] | +0.012 [+0.011, +0.014] | +0.075 [+0.072, +0.078] | +0.059 [+0.056, +0.061] | -0.004 [-0.007, -0.002] |
| layer − sec. 11.1 dist run layer | +0.002 [-0.001, +0.004] | +0.002 [-0.000, +0.005] | -0.000 [-0.001, +0.001] | -0.001 [-0.003, +0.001] | +0.001 [-0.001, +0.002] | +0.000 [-0.001, +0.002] |
| layer, ground-truth markers − sec. 11.1 dist run layer, ground-truth markers | +0.000 [-0.001, +0.001] | +0.001 [-0.001, +0.002] | -0.002 [-0.002, -0.001] | +0.001 [-0.001, +0.002] | +0.001 [+0.000, +0.002] | +0.001 [+0.001, +0.002] |
| layer − this model's own logits | +0.103 [+0.098, +0.108] | +0.204 [+0.199, +0.209] | +0.200 [+0.198, +0.202] | +0.754 [+0.749, +0.759] | +0.617 [+0.611, +0.621] | +0.482 [+0.468, +0.496] |
| layer − marker watershed, same markers | +0.070 [+0.068, +0.071] | +0.157 [+0.154, +0.159] | +0.166 [+0.164, +0.168] | +0.063 [+0.060, +0.066] | +0.119 [+0.117, +0.121] | +0.079 [+0.078, +0.081] |
| layer − layer with image costs | +0.148 [+0.145, +0.151] | +0.300 [+0.294, +0.305] | +0.269 [+0.266, +0.272] | +0.153 [+0.148, +0.158] | +0.231 [+0.228, +0.235] | +0.123 [+0.121, +0.126] |
| layer + fallback − U-Net (sec. 6) logits | -0.011 [-0.014, -0.008] | -0.005 [-0.008, -0.002] | +0.004 [+0.002, +0.005] | +0.121 [+0.116, +0.127] | +0.100 [+0.096, +0.104] | +0.158 [+0.143, +0.172] |
| layer + fallback − contour-head U-Net, watershed (b) | -0.011 [-0.013, -0.008] | -0.010 [-0.013, -0.008] | +0.013 [+0.011, +0.014] | +0.063 [+0.060, +0.066] | +0.048 [+0.046, +0.051] | -0.005 [-0.007, -0.002] |
| layer + fallback − layer | -0.001 [-0.002, -0.000] | -0.000 [-0.002, +0.001] | +0.000 [-0.000, +0.001] | -0.012 [-0.013, -0.011] | -0.011 [-0.012, -0.010] | -0.000 [-0.000, +0.000] |
| layer, ground-truth markers − layer | +0.151 [+0.146, +0.156] | +0.159 [+0.154, +0.164] | +0.011 [+0.008, +0.013] | +0.169 [+0.166, +0.173] | +0.164 [+0.160, +0.167] | +0.206 [+0.201, +0.210] |
| on the 307 limit patches: PW limit (learned) − layer | -0.017 [-0.020, -0.014] | -0.026 [-0.029, -0.023] | +0.000 [-0.002, +0.002] | -0.010 [-0.013, -0.006] | -0.019 [-0.021, -0.017] | -0.020 [-0.022, -0.017] |
| on the 307 limit patches: PW limit (learned) − PW limit (image costs) | +0.132 [+0.123, +0.142] | +0.271 [+0.256, +0.286] | +0.270 [+0.259, +0.280] | +0.142 [+0.130, +0.154] | +0.206 [+0.193, +0.217] | +0.098 [+0.090, +0.106] |
| on the 307 limit patches: PW limit (learned) − U-Net (sec. 6) logits | -0.025 [-0.033, -0.017] | -0.032 [-0.040, -0.025] | +0.005 [-0.002, +0.012] | +0.124 [+0.109, +0.138] | +0.091 [+0.078, +0.102] | +0.181 [+0.127, +0.231] |

## By crowding (F1@0.5 / PQ / count error)

| patches | n | U-Net (sec. 6) | contour-head U-Net, watershed (b) | layer | layer + fallback | marker watershed, same markers | PW limit (learned, subset) |
|---|---|---|---|---|---|---|---|
| < 10 nuclei | 486 | 0.608 / 0.485 / 0.68 | 0.596 / 0.479 / 0.81 | 0.687 / 0.551 / 0.67 | 0.650 / 0.521 / 0.92 | 0.638 / 0.456 / 0.68 | 0.658 / 0.510 / 0.70 |
| 10–30 | 1383 | 0.691 / 0.563 / 0.18 | 0.719 / 0.591 / 0.27 | 0.800 / 0.655 / 0.16 | 0.784 / 0.641 / 0.19 | 0.750 / 0.546 / 0.16 | 0.789 / 0.630 / 0.16 |
| 30–60 | 525 | 0.650 / 0.524 / 0.15 | 0.733 / 0.596 / 0.15 | 0.801 / 0.649 / 0.10 | 0.793 / 0.641 / 0.11 | 0.734 / 0.525 / 0.10 | 0.772 / 0.609 / 0.11 |
| > 60 | 129 | 0.588 / 0.469 / 0.24 | 0.700 / 0.562 / 0.13 | 0.765 / 0.616 / 0.15 | 0.764 / 0.614 / 0.13 | 0.675 / 0.476 / 0.15 | 0.691 / 0.542 / 0.21 |

## Marker quality by crowding (nuclei with one / none / several markers; background markers per patch)

| patches | one | none | several | bg markers / patch |
|---|---|---|---|---|
| < 10 nuclei | 83.2 % | 14.2 % | 2.6 % | 1.83 |
| 10–30 | 86.1 % | 11.9 % | 2.0 % | 3.43 |
| 30–60 | 83.7 % | 14.5 % | 1.7 % | 4.67 |
| > 60 | 77.0 % | 22.2 % | 0.7 % | 6.92 |
