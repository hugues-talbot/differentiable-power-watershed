# Instances as labels: multi-marker layer on PanNuke (fold 1 → fold 2)

Run `results_pannuke_instances/dist_peakgrad/instances`: p 5.0 → 20.0, erosion [2, 3], edge target ×1.0, seam weight 5.0, 30 epochs, seed 0, training solve tol 0.0001 / maxit 100, peak loss ×1.0; marker head `dist` (mse, rmax 12; markers = h-maxima h 0.2 grown to thr 0.3, min area 16 px), chosen by PQ on 300 patches of fold 3; learned edge scale 2.02.

## Marker post-processing chosen on fold 3 (300 patches): {'mk_thr': 0.3, 'mk_min_area': 16, 'mk_h': 0.2}

| setting | PQ | F1@0.5 | AJI | count err. | n_pred | one | none | several | bg / patch |
|---|---|---|---|---|---|---|---|---|---|
| thr=0.3/min_area=16/h=0.2 | 0.578 | 0.719 | 0.629 | 0.543 | 32.6 | 87.2 % | 7.4 % | 5.4 % | 9.68 |
| thr=0.2/min_area=16/h=0.2 | 0.576 | 0.712 | 0.628 | 0.635 | 34.0 | 87.2 % | 7.2 % | 5.6 % | 11.26 |
| thr=0.2/min_area=9/h=0.2 | 0.572 | 0.707 | 0.628 | 0.673 | 34.5 | 87.6 % | 6.8 % | 5.6 % | 12.47 |
| thr=0.3/min_area=9/h=0.2 | 0.571 | 0.711 | 0.628 | 0.602 | 33.5 | 87.6 % | 6.8 % | 5.6 % | 10.99 |
| thr=0.4/min_area=16/h=0.2 | 0.570 | 0.720 | 0.621 | 0.449 | 31.1 | 86.6 % | 8.1 % | 5.3 % | 8.28 |
| thr=0.2/min_area=4/h=0.2 | 0.570 | 0.704 | 0.627 | 0.690 | 34.7 | 87.7 % | 6.7 % | 5.6 % | 13.42 |
| thr=0.2/min_area=1/h=0.2 | 0.570 | 0.704 | 0.627 | 0.690 | 34.7 | 87.7 % | 6.6 % | 5.6 % | 13.98 |
| thr=0.3/min_area=4/h=0.2 | 0.567 | 0.707 | 0.628 | 0.625 | 33.9 | 87.9 % | 6.4 % | 5.6 % | 11.96 |
| thr=0.5/min_area=1/h=0.1 (untuned default) | 0.526 | 0.677 | 0.592 | 0.569 | 33.1 | 85.9 % | 6.0 % | 8.0 % | 10.58 |

(top 8 of 72 settings by PQ)

## All of fold 2

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6, binary target), s > 0.5, components | 2523 | 0.719 | 0.652 | 0.769 | 0.807 | 0.577 | 0.656 | 0.531 | 0.494 | 0.275 | 23.0 |
| U-Net + contour head (sec. 10.1, gap target), logits | 2523 | 0.719 | 0.658 | 0.774 | 0.809 | 0.574 | 0.682 | 0.556 | 0.571 | 0.303 | 25.2 |
| U-Net + contour head, tuned marker watershed (b) | 2523 | 0.718 | 0.658 | 0.774 | 0.809 | 0.568 | 0.715 | 0.583 | 0.657 | 0.344 | 27.2 |
| sec. 11.1 dist run: layer, converged (predicted markers) | 2523 | 0.707 | 0.647 | 0.762 | 0.811 | 0.580 | 0.791 | 0.641 | 0.653 | 0.239 | 24.3 |
| this model: s > 0.5, components | 2523 | 0.591 | 0.397 | 0.566 | 0.710 | 0.386 | 0.029 | 0.020 | 0.170 | 45.471 | 627.9 |
| this model: layer, converged (predicted markers) | 2523 | 0.677 | 0.610 | 0.724 | 0.806 | 0.550 | 0.717 | 0.572 | 0.623 | 0.632 | 32.0 |
| this model: layer + fallback markers | 2523 | 0.677 | 0.610 | 0.724 | 0.806 | 0.550 | 0.711 | 0.567 | 0.623 | 0.672 | 32.6 |
| this model: layer, ground-truth markers (oracle) | 2523 | 0.859 | 0.795 | 0.922 | 0.858 | 0.591 | 0.959 | 0.805 | 0.858 | 0.020 | 23.3 |
| this model: layer, image-gradient costs | 2523 | 0.487 | 0.217 | 0.366 | 0.606 | 0.280 | 0.419 | 0.252 | 0.461 | 0.713 | 32.9 |
| this model: marker watershed on the contour map | 2523 | 0.620 | 0.431 | 0.607 | 0.709 | 0.414 | 0.632 | 0.444 | 0.563 | 0.714 | 32.9 |
| this model: PW limit, learned costs | 307 | 0.653 | 0.581 | 0.701 | 0.794 | 0.548 | 0.690 | 0.540 | 0.577 | 0.665 | 33.4 |
| this model: PW limit, image-gradient costs | 307 | 0.479 | 0.216 | 0.357 | 0.604 | 0.268 | 0.393 | 0.234 | 0.443 | 0.791 | 34.3 |
| this model: ground truth instances | 2523 | 1.000 | 1.000 | 1.000 | 1.000 | 0.559 | 1.000 | 1.000 | 1.000 | 0.000 | 23.7 |

## Marker quality (predicted markers against the ground-truth nuclei)

- 59872 nuclei in fold 2 (23.7 per patch); predicted markers 32.9 per patch.
- exactly one marker: 86.4 %; none: 7.5 %; several: 6.2 %; markers in background: 9.28 per patch.
- with fallback markers: one 86.3 %, none 7.2 %, several 6.6 %, background 9.85 per patch, 33.7 markers per patch.
- sec. 11.1 dist run: one 83.9 %, none 14.5 %, several 1.6 %, background 3.58 per patch, 24.3 markers per patch.

## Inference cost

- U-Net forward: 0.9 ms per image; converged multi-marker solve (tol 1e-05): 74.1 ms per image at K = 32.9 markers per image (85575 systems in 158 batches of 16; 165 PCG iterations per batch).
- exact K-label PW limit (one CPU core): 0.9 s per patch with the learned costs, 0.8 s with image-gradient costs, K = 34.3; 8914 ambiguous plateaus solved over 307 patches.

## Per tissue type

**Breast**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 749 | 0.722 | 0.596 | 0.756 | 0.780 | 0.585 | 0.690 | 0.547 | 0.550 | 0.198 | 21.2 |
| U-Net + contour head, watershed (b) | 749 | 0.722 | 0.601 | 0.761 | 0.782 | 0.576 | 0.757 | 0.605 | 0.671 | 0.242 | 24.5 |
| sec. 11.1 dist run: layer | 749 | 0.708 | 0.585 | 0.743 | 0.782 | 0.587 | 0.817 | 0.647 | 0.661 | 0.187 | 22.9 |
| s > 0.5, components | 749 | 0.609 | 0.377 | 0.555 | 0.683 | 0.381 | 0.029 | 0.020 | 0.176 | 38.752 | 587.1 |
| layer, converged (predicted markers) | 749 | 0.684 | 0.555 | 0.710 | 0.772 | 0.557 | 0.752 | 0.587 | 0.634 | 0.462 | 28.5 |
| layer + fallback markers | 749 | 0.684 | 0.555 | 0.710 | 0.772 | 0.557 | 0.745 | 0.581 | 0.634 | 0.498 | 29.1 |
| layer, ground-truth markers (oracle) | 749 | 0.854 | 0.743 | 0.909 | 0.837 | 0.596 | 0.967 | 0.806 | 0.852 | 0.015 | 21.4 |
| layer, image-gradient costs | 749 | 0.506 | 0.211 | 0.352 | 0.590 | 0.251 | 0.472 | 0.286 | 0.483 | 0.531 | 29.3 |
| marker watershed on the contour map | 749 | 0.628 | 0.401 | 0.584 | 0.682 | 0.405 | 0.677 | 0.465 | 0.574 | 0.531 | 29.3 |
| PW limit, learned costs | 89 | 0.674 | 0.532 | 0.691 | 0.757 | 0.557 | 0.739 | 0.565 | 0.605 | 0.366 | 29.4 |
| PW limit, image-gradient costs | 89 | 0.520 | 0.223 | 0.362 | 0.590 | 0.233 | 0.468 | 0.281 | 0.478 | 0.427 | 30.3 |
| ground truth instances | 749 | 1.000 | 1.000 | 1.000 | 1.000 | 0.553 | 1.000 | 1.000 | 1.000 | 0.000 | 21.7 |

**Colon**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 468 | 0.698 | 0.617 | 0.738 | 0.788 | 0.558 | 0.547 | 0.431 | 0.349 | 0.274 | 21.1 |
| U-Net + contour head, watershed (b) | 468 | 0.691 | 0.621 | 0.742 | 0.788 | 0.550 | 0.630 | 0.497 | 0.574 | 0.340 | 27.7 |
| sec. 11.1 dist run: layer | 468 | 0.683 | 0.605 | 0.726 | 0.791 | 0.569 | 0.709 | 0.558 | 0.579 | 0.238 | 23.8 |
| s > 0.5, components | 468 | 0.559 | 0.366 | 0.523 | 0.700 | 0.383 | 0.017 | 0.012 | 0.096 | 45.950 | 731.7 |
| layer, converged (predicted markers) | 468 | 0.651 | 0.566 | 0.685 | 0.785 | 0.534 | 0.628 | 0.484 | 0.547 | 0.609 | 34.2 |
| layer + fallback markers | 468 | 0.650 | 0.566 | 0.684 | 0.785 | 0.535 | 0.623 | 0.480 | 0.547 | 0.646 | 34.8 |
| layer, ground-truth markers (oracle) | 468 | 0.849 | 0.770 | 0.905 | 0.850 | 0.569 | 0.939 | 0.769 | 0.840 | 0.023 | 24.9 |
| layer, image-gradient costs | 468 | 0.491 | 0.272 | 0.396 | 0.622 | 0.300 | 0.356 | 0.212 | 0.417 | 0.684 | 35.1 |
| marker watershed on the contour map | 468 | 0.601 | 0.412 | 0.575 | 0.699 | 0.412 | 0.524 | 0.359 | 0.493 | 0.684 | 35.1 |
| PW limit, learned costs | 62 | 0.636 | 0.551 | 0.673 | 0.767 | 0.512 | 0.576 | 0.432 | 0.480 | 0.480 | 42.7 |
| PW limit, image-gradient costs | 62 | 0.474 | 0.279 | 0.397 | 0.611 | 0.270 | 0.300 | 0.178 | 0.375 | 0.544 | 43.7 |
| ground truth instances | 468 | 1.000 | 1.000 | 1.000 | 1.000 | 0.539 | 1.000 | 1.000 | 1.000 | 0.000 | 25.4 |

**HeadNeck**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 169 | 0.672 | 0.658 | 0.744 | 0.835 | 0.648 | 0.640 | 0.519 | 0.556 | 0.424 | 20.2 |
| U-Net + contour head, watershed (b) | 169 | 0.682 | 0.675 | 0.756 | 0.839 | 0.638 | 0.688 | 0.565 | 0.660 | 0.474 | 23.6 |
| sec. 11.1 dist run: layer | 169 | 0.701 | 0.711 | 0.782 | 0.846 | 0.631 | 0.784 | 0.647 | 0.651 | 0.203 | 19.8 |
| s > 0.5, components | 169 | 0.501 | 0.372 | 0.514 | 0.765 | 0.460 | 0.027 | 0.019 | 0.223 | 50.071 | 585.5 |
| layer, converged (predicted markers) | 169 | 0.624 | 0.624 | 0.699 | 0.847 | 0.618 | 0.687 | 0.555 | 0.605 | 0.860 | 28.0 |
| layer + fallback markers | 169 | 0.623 | 0.623 | 0.698 | 0.847 | 0.618 | 0.680 | 0.550 | 0.604 | 0.908 | 28.6 |
| layer, ground-truth markers (oracle) | 169 | 0.859 | 0.850 | 0.937 | 0.886 | 0.647 | 0.963 | 0.819 | 0.863 | 0.028 | 18.2 |
| layer, image-gradient costs | 169 | 0.438 | 0.232 | 0.376 | 0.655 | 0.404 | 0.315 | 0.183 | 0.428 | 0.955 | 28.9 |
| marker watershed on the contour map | 169 | 0.576 | 0.451 | 0.599 | 0.763 | 0.489 | 0.611 | 0.436 | 0.558 | 0.955 | 28.9 |
| ground truth instances | 169 | 1.000 | 1.000 | 1.000 | 1.000 | 0.629 | 1.000 | 1.000 | 1.000 | 0.000 | 18.5 |

**Adrenal_gland**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 148 | 0.716 | 0.676 | 0.774 | 0.808 | 0.554 | 0.694 | 0.582 | 0.655 | 0.378 | 18.4 |
| U-Net + contour head, watershed (b) | 148 | 0.719 | 0.689 | 0.783 | 0.811 | 0.551 | 0.712 | 0.605 | 0.713 | 0.444 | 20.1 |
| sec. 11.1 dist run: layer | 148 | 0.709 | 0.688 | 0.779 | 0.824 | 0.562 | 0.823 | 0.696 | 0.696 | 0.260 | 17.1 |
| s > 0.5, components | 148 | 0.608 | 0.413 | 0.573 | 0.723 | 0.355 | 0.028 | 0.021 | 0.466 | 66.158 | 703.5 |
| layer, converged (predicted markers) | 148 | 0.681 | 0.648 | 0.739 | 0.817 | 0.532 | 0.721 | 0.598 | 0.658 | 0.663 | 22.8 |
| layer + fallback markers | 148 | 0.681 | 0.647 | 0.739 | 0.818 | 0.531 | 0.711 | 0.589 | 0.657 | 0.709 | 23.5 |
| layer, ground-truth markers (oracle) | 148 | 0.865 | 0.823 | 0.931 | 0.865 | 0.581 | 0.957 | 0.830 | 0.871 | 0.021 | 15.7 |
| layer, image-gradient costs | 148 | 0.451 | 0.143 | 0.277 | 0.563 | 0.257 | 0.381 | 0.226 | 0.452 | 0.768 | 23.9 |
| marker watershed on the contour map | 148 | 0.632 | 0.450 | 0.617 | 0.720 | 0.393 | 0.647 | 0.486 | 0.614 | 0.768 | 23.9 |
| ground truth instances | 148 | 1.000 | 1.000 | 1.000 | 1.000 | 0.557 | 1.000 | 1.000 | 1.000 | 0.000 | 16.0 |

## Paired per-patch differences (2523 patches; bootstrap 95 % intervals; F1 / PQ / AJI dataset-level, bootstrapped over patches)

| comparison | IoU | BF₂ | edge align. | F1@0.5 | PQ | AJI |
|---|---|---|---|---|---|---|
| layer − U-Net (sec. 6) logits | -0.042 [-0.045, -0.038] | -0.045 [-0.049, -0.041] | -0.027 [-0.029, -0.026] | +0.060 [+0.054, +0.067] | +0.041 [+0.036, +0.047] | +0.129 [+0.112, +0.143] |
| layer − contour-head U-Net, watershed (b) | -0.041 [-0.044, -0.037] | -0.050 [-0.053, -0.047] | -0.019 [-0.020, -0.017] | +0.002 [-0.002, +0.006] | -0.011 [-0.014, -0.008] | -0.034 [-0.038, -0.031] |
| layer − sec. 11.1 dist run layer | -0.030 [-0.033, -0.026] | -0.038 [-0.041, -0.034] | -0.031 [-0.033, -0.030] | -0.074 [-0.078, -0.069] | -0.069 [-0.072, -0.066] | -0.030 [-0.033, -0.027] |
| layer, ground-truth markers − sec. 11.1 dist run layer, ground-truth markers | -0.000 [-0.001, +0.000] | -0.000 [-0.002, +0.001] | -0.000 [-0.001, +0.000] | +0.000 [-0.001, +0.001] | +0.000 [-0.001, +0.001] | +0.000 [-0.000, +0.001] |
| layer − this model's own logits | +0.086 [+0.081, +0.090] | +0.158 [+0.154, +0.163] | +0.167 [+0.165, +0.169] | +0.688 [+0.682, +0.693] | +0.552 [+0.546, +0.557] | +0.453 [+0.439, +0.466] |
| layer − marker watershed, same markers | +0.057 [+0.055, +0.060] | +0.117 [+0.115, +0.120] | +0.137 [+0.135, +0.139] | +0.085 [+0.082, +0.088] | +0.128 [+0.126, +0.131] | +0.060 [+0.058, +0.061] |
| layer − layer with image costs | +0.190 [+0.187, +0.194] | +0.358 [+0.352, +0.364] | +0.270 [+0.267, +0.274] | +0.298 [+0.292, +0.305] | +0.321 [+0.316, +0.325] | +0.162 [+0.159, +0.165] |
| layer + fallback − U-Net (sec. 6) logits | -0.042 [-0.045, -0.038] | -0.045 [-0.049, -0.042] | -0.027 [-0.029, -0.026] | +0.055 [+0.048, +0.061] | +0.037 [+0.032, +0.042] | +0.129 [+0.112, +0.143] |
| layer + fallback − contour-head U-Net, watershed (b) | -0.041 [-0.045, -0.038] | -0.050 [-0.054, -0.047] | -0.019 [-0.020, -0.017] | -0.004 [-0.007, -0.000] | -0.016 [-0.019, -0.013] | -0.034 [-0.038, -0.031] |
| layer + fallback − layer | -0.000 [-0.000, -0.000] | -0.000 [-0.000, +0.000] | +0.000 [-0.000, +0.000] | -0.006 [-0.006, -0.005] | -0.005 [-0.005, -0.005] | -0.000 [-0.000, -0.000] |
| layer, ground-truth markers − layer | +0.181 [+0.175, +0.187] | +0.198 [+0.192, +0.203] | +0.043 [+0.041, +0.045] | +0.242 [+0.236, +0.247] | +0.233 [+0.227, +0.237] | +0.235 [+0.230, +0.239] |
| on the 307 limit patches: PW limit (learned) − layer | -0.019 [-0.024, -0.015] | -0.016 [-0.022, -0.010] | +0.006 [+0.003, +0.009] | -0.000 [-0.004, +0.003] | -0.008 [-0.011, -0.006] | -0.025 [-0.028, -0.022] |
| on the 307 limit patches: PW limit (learned) − PW limit (image costs) | +0.174 [+0.163, +0.187] | +0.343 [+0.327, +0.361] | +0.280 [+0.269, +0.291] | +0.298 [+0.281, +0.315] | +0.306 [+0.292, +0.322] | +0.134 [+0.125, +0.142] |
| on the 307 limit patches: PW limit (learned) − U-Net (sec. 6) logits | -0.060 [-0.073, -0.048] | -0.063 [-0.076, -0.050] | -0.021 [-0.028, -0.014] | +0.057 [+0.040, +0.073] | +0.031 [+0.017, +0.043] | +0.152 [+0.094, +0.202] |

## By crowding (F1@0.5 / PQ / count error)

| patches | n | U-Net (sec. 6) | contour-head U-Net, watershed (b) | layer | layer + fallback | marker watershed, same markers | PW limit (learned, subset) |
|---|---|---|---|---|---|---|---|
| < 10 nuclei | 486 | 0.608 / 0.485 / 0.68 | 0.596 / 0.479 / 0.81 | 0.537 / 0.421 / 1.61 | 0.526 / 0.412 / 1.70 | 0.454 / 0.316 / 1.85 | 0.520 / 0.390 / 1.69 |
| 10–30 | 1383 | 0.691 / 0.563 / 0.18 | 0.719 / 0.591 / 0.27 | 0.707 / 0.566 / 0.45 | 0.699 / 0.559 / 0.49 | 0.634 / 0.451 / 0.51 | 0.700 / 0.553 / 0.48 |
| 30–60 | 525 | 0.650 / 0.524 / 0.15 | 0.733 / 0.596 / 0.15 | 0.739 / 0.589 / 0.31 | 0.735 / 0.585 / 0.32 | 0.654 / 0.457 / 0.33 | 0.714 / 0.559 / 0.32 |
| > 60 | 129 | 0.588 / 0.469 / 0.24 | 0.700 / 0.562 / 0.13 | 0.748 / 0.597 / 0.20 | 0.747 / 0.596 / 0.21 | 0.633 / 0.436 / 0.20 | 0.665 / 0.513 / 0.20 |

## Marker quality by crowding (nuclei with one / none / several markers; background markers per patch)

| patches | one | none | several | bg markers / patch |
|---|---|---|---|---|
| < 10 nuclei | 83.3 % | 6.9 % | 9.8 % | 4.84 |
| 10–30 | 87.3 % | 5.7 % | 7.0 % | 8.76 |
| 30–60 | 86.5 % | 7.2 % | 6.3 % | 12.15 |
| > 60 | 84.5 % | 12.1 % | 3.3 % | 19.90 |
