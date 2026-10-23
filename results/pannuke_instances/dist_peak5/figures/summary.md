# Instances as labels: multi-marker layer on PanNuke (fold 1 → fold 2)

Run `results_pannuke_instances/dist_peak5/instances`: p 5.0 → 20.0, erosion [2, 3], edge target ×1.0, seam weight 5.0, 30 epochs, seed 0, training solve tol 0.0001 / maxit 100, peak loss ×1.0; marker head `dist` (mse, rmax 12; markers = h-maxima h 0.2 grown to thr 0.3, min area 16 px), chosen by PQ on 300 patches of fold 3; learned edge scale 2.08.

## Marker post-processing chosen on fold 3 (300 patches): {'mk_thr': 0.3, 'mk_min_area': 16, 'mk_h': 0.2}

| setting | PQ | F1@0.5 | AJI | count err. | n_pred | one | none | several | bg / patch |
|---|---|---|---|---|---|---|---|---|---|
| thr=0.3/min_area=16/h=0.2 | 0.560 | 0.698 | 0.621 | 0.589 | 33.8 | 85.9 % | 6.9 % | 7.2 % | 10.42 |
| thr=0.2/min_area=16/h=0.2 | 0.559 | 0.692 | 0.621 | 0.694 | 35.4 | 85.9 % | 6.7 % | 7.3 % | 12.41 |
| thr=0.4/min_area=16/h=0.2 | 0.553 | 0.701 | 0.612 | 0.489 | 32.2 | 85.4 % | 7.6 % | 7.0 % | 8.91 |
| thr=0.2/min_area=9/h=0.2 | 0.553 | 0.685 | 0.620 | 0.738 | 36.2 | 86.2 % | 6.3 % | 7.5 % | 14.10 |
| thr=0.2/min_area=4/h=0.2 | 0.552 | 0.683 | 0.620 | 0.745 | 36.3 | 86.3 % | 6.2 % | 7.6 % | 15.40 |
| thr=0.2/min_area=1/h=0.2 | 0.551 | 0.683 | 0.620 | 0.746 | 36.4 | 86.3 % | 6.1 % | 7.6 % | 16.36 |
| thr=0.3/min_area=9/h=0.2 | 0.551 | 0.688 | 0.619 | 0.666 | 35.0 | 86.4 % | 6.1 % | 7.4 % | 12.20 |
| thr=0.3/min_area=4/h=0.2 | 0.547 | 0.683 | 0.619 | 0.695 | 35.5 | 86.6 % | 5.8 % | 7.5 % | 13.59 |
| thr=0.5/min_area=1/h=0.1 (untuned default) | 0.503 | 0.647 | 0.582 | 0.637 | 35.0 | 84.2 % | 5.3 % | 10.5 % | 12.31 |

(top 8 of 72 settings by PQ)

## All of fold 2

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6, binary target), s > 0.5, components | 2523 | 0.719 | 0.652 | 0.769 | 0.807 | 0.577 | 0.656 | 0.531 | 0.494 | 0.275 | 23.0 |
| U-Net + contour head (sec. 10.1, gap target), logits | 2523 | 0.719 | 0.658 | 0.774 | 0.809 | 0.574 | 0.682 | 0.556 | 0.571 | 0.303 | 25.2 |
| U-Net + contour head, tuned marker watershed (b) | 2523 | 0.718 | 0.658 | 0.774 | 0.809 | 0.568 | 0.715 | 0.583 | 0.657 | 0.344 | 27.2 |
| sec. 11.1 dist run: layer, converged (predicted markers) | 2523 | 0.707 | 0.647 | 0.762 | 0.811 | 0.580 | 0.791 | 0.641 | 0.653 | 0.239 | 24.3 |
| this model: s > 0.5, components | 2523 | 0.591 | 0.398 | 0.571 | 0.704 | 0.391 | 0.030 | 0.021 | 0.169 | 45.725 | 606.4 |
| this model: layer, converged (predicted markers) | 2523 | 0.674 | 0.607 | 0.720 | 0.804 | 0.551 | 0.701 | 0.558 | 0.617 | 0.712 | 33.1 |
| this model: layer + fallback markers | 2523 | 0.674 | 0.607 | 0.720 | 0.804 | 0.551 | 0.696 | 0.554 | 0.617 | 0.756 | 33.7 |
| this model: layer, ground-truth markers (oracle) | 2523 | 0.859 | 0.796 | 0.922 | 0.858 | 0.591 | 0.958 | 0.804 | 0.857 | 0.019 | 23.3 |
| this model: layer, image-gradient costs | 2523 | 0.485 | 0.215 | 0.366 | 0.605 | 0.282 | 0.401 | 0.241 | 0.456 | 0.816 | 34.1 |
| this model: marker watershed on the contour map | 2523 | 0.615 | 0.429 | 0.607 | 0.703 | 0.419 | 0.616 | 0.431 | 0.558 | 0.817 | 34.1 |
| this model: PW limit, learned costs | 307 | 0.658 | 0.588 | 0.708 | 0.795 | 0.549 | 0.683 | 0.534 | 0.574 | 0.695 | 34.4 |
| this model: PW limit, image-gradient costs | 307 | 0.485 | 0.221 | 0.365 | 0.602 | 0.266 | 0.377 | 0.225 | 0.441 | 0.850 | 35.7 |
| this model: ground truth instances | 2523 | 1.000 | 1.000 | 1.000 | 1.000 | 0.559 | 1.000 | 1.000 | 1.000 | 0.000 | 23.7 |

## Marker quality (predicted markers against the ground-truth nuclei)

- 59872 nuclei in fold 2 (23.7 per patch); predicted markers 34.1 per patch.
- exactly one marker: 85.7 %; none: 7.0 %; several: 7.4 %; markers in background: 9.97 per patch.
- with fallback markers: one 85.5 %, none 6.7 %, several 7.8 %, background 10.59 per patch, 34.9 markers per patch.
- sec. 11.1 dist run: one 83.9 %, none 14.5 %, several 1.6 %, background 3.58 per patch, 24.3 markers per patch.

## Inference cost

- U-Net forward: 0.8 ms per image; converged multi-marker solve (tol 1e-05): 128.7 ms per image at K = 34.1 markers per image (88573 systems in 158 batches of 16; 171 PCG iterations per batch).
- exact K-label PW limit (one CPU core): 0.7 s per patch with the learned costs, 0.8 s with image-gradient costs, K = 35.7; 8902 ambiguous plateaus solved over 307 patches.

## Per tissue type

**Breast**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 749 | 0.722 | 0.596 | 0.756 | 0.780 | 0.585 | 0.690 | 0.547 | 0.550 | 0.198 | 21.2 |
| U-Net + contour head, watershed (b) | 749 | 0.722 | 0.601 | 0.761 | 0.782 | 0.576 | 0.757 | 0.605 | 0.671 | 0.242 | 24.5 |
| sec. 11.1 dist run: layer | 749 | 0.708 | 0.585 | 0.743 | 0.782 | 0.587 | 0.817 | 0.647 | 0.661 | 0.187 | 22.9 |
| s > 0.5, components | 749 | 0.608 | 0.378 | 0.559 | 0.678 | 0.384 | 0.031 | 0.021 | 0.189 | 37.065 | 560.7 |
| layer, converged (predicted markers) | 749 | 0.681 | 0.554 | 0.708 | 0.770 | 0.559 | 0.738 | 0.575 | 0.627 | 0.512 | 29.0 |
| layer + fallback markers | 749 | 0.681 | 0.554 | 0.708 | 0.770 | 0.559 | 0.732 | 0.571 | 0.627 | 0.543 | 29.5 |
| layer, ground-truth markers (oracle) | 749 | 0.853 | 0.744 | 0.909 | 0.837 | 0.598 | 0.966 | 0.805 | 0.852 | 0.015 | 21.4 |
| layer, image-gradient costs | 749 | 0.506 | 0.211 | 0.353 | 0.588 | 0.254 | 0.460 | 0.279 | 0.476 | 0.583 | 29.9 |
| marker watershed on the contour map | 749 | 0.626 | 0.403 | 0.589 | 0.677 | 0.408 | 0.667 | 0.457 | 0.568 | 0.583 | 29.9 |
| PW limit, learned costs | 89 | 0.673 | 0.538 | 0.697 | 0.761 | 0.557 | 0.738 | 0.566 | 0.605 | 0.391 | 29.9 |
| PW limit, image-gradient costs | 89 | 0.517 | 0.220 | 0.358 | 0.588 | 0.234 | 0.456 | 0.273 | 0.474 | 0.463 | 30.9 |
| ground truth instances | 749 | 1.000 | 1.000 | 1.000 | 1.000 | 0.553 | 1.000 | 1.000 | 1.000 | 0.000 | 21.7 |

**Colon**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 468 | 0.698 | 0.617 | 0.738 | 0.788 | 0.558 | 0.547 | 0.431 | 0.349 | 0.274 | 21.1 |
| U-Net + contour head, watershed (b) | 468 | 0.691 | 0.621 | 0.742 | 0.788 | 0.550 | 0.630 | 0.497 | 0.574 | 0.340 | 27.7 |
| sec. 11.1 dist run: layer | 468 | 0.683 | 0.605 | 0.726 | 0.791 | 0.569 | 0.709 | 0.558 | 0.579 | 0.238 | 23.8 |
| s > 0.5, components | 468 | 0.569 | 0.377 | 0.536 | 0.695 | 0.392 | 0.017 | 0.012 | 0.091 | 52.594 | 727.8 |
| layer, converged (predicted markers) | 468 | 0.644 | 0.557 | 0.676 | 0.783 | 0.529 | 0.605 | 0.465 | 0.538 | 0.761 | 36.4 |
| layer + fallback markers | 468 | 0.644 | 0.557 | 0.676 | 0.783 | 0.529 | 0.600 | 0.461 | 0.538 | 0.800 | 37.0 |
| layer, ground-truth markers (oracle) | 468 | 0.851 | 0.772 | 0.906 | 0.850 | 0.568 | 0.938 | 0.769 | 0.841 | 0.021 | 24.9 |
| layer, image-gradient costs | 468 | 0.486 | 0.270 | 0.395 | 0.620 | 0.303 | 0.328 | 0.195 | 0.410 | 0.870 | 37.2 |
| marker watershed on the contour map | 468 | 0.596 | 0.410 | 0.575 | 0.694 | 0.420 | 0.503 | 0.344 | 0.488 | 0.870 | 37.2 |
| PW limit, learned costs | 62 | 0.630 | 0.550 | 0.672 | 0.766 | 0.507 | 0.568 | 0.425 | 0.476 | 0.537 | 45.0 |
| PW limit, image-gradient costs | 62 | 0.468 | 0.277 | 0.395 | 0.609 | 0.270 | 0.276 | 0.163 | 0.370 | 0.647 | 46.4 |
| ground truth instances | 468 | 1.000 | 1.000 | 1.000 | 1.000 | 0.539 | 1.000 | 1.000 | 1.000 | 0.000 | 25.4 |

**HeadNeck**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 169 | 0.672 | 0.658 | 0.744 | 0.835 | 0.648 | 0.640 | 0.519 | 0.556 | 0.424 | 20.2 |
| U-Net + contour head, watershed (b) | 169 | 0.682 | 0.675 | 0.756 | 0.839 | 0.638 | 0.688 | 0.565 | 0.660 | 0.474 | 23.6 |
| sec. 11.1 dist run: layer | 169 | 0.701 | 0.711 | 0.782 | 0.846 | 0.631 | 0.784 | 0.647 | 0.651 | 0.203 | 19.8 |
| s > 0.5, components | 169 | 0.491 | 0.367 | 0.510 | 0.758 | 0.468 | 0.027 | 0.019 | 0.215 | 50.006 | 582.6 |
| layer, converged (predicted markers) | 169 | 0.629 | 0.629 | 0.704 | 0.846 | 0.621 | 0.665 | 0.538 | 0.595 | 0.912 | 28.6 |
| layer + fallback markers | 169 | 0.629 | 0.629 | 0.704 | 0.846 | 0.621 | 0.658 | 0.533 | 0.595 | 0.957 | 29.2 |
| layer, ground-truth markers (oracle) | 169 | 0.860 | 0.852 | 0.940 | 0.885 | 0.647 | 0.965 | 0.819 | 0.861 | 0.026 | 18.2 |
| layer, image-gradient costs | 169 | 0.427 | 0.221 | 0.365 | 0.650 | 0.400 | 0.277 | 0.161 | 0.417 | 1.076 | 29.7 |
| marker watershed on the contour map | 169 | 0.566 | 0.444 | 0.592 | 0.755 | 0.492 | 0.586 | 0.416 | 0.547 | 1.076 | 29.7 |
| ground truth instances | 169 | 1.000 | 1.000 | 1.000 | 1.000 | 0.629 | 1.000 | 1.000 | 1.000 | 0.000 | 18.5 |

**Adrenal_gland**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 148 | 0.716 | 0.676 | 0.774 | 0.808 | 0.554 | 0.694 | 0.582 | 0.655 | 0.378 | 18.4 |
| U-Net + contour head, watershed (b) | 148 | 0.719 | 0.689 | 0.783 | 0.811 | 0.551 | 0.712 | 0.605 | 0.713 | 0.444 | 20.1 |
| sec. 11.1 dist run: layer | 148 | 0.709 | 0.688 | 0.779 | 0.824 | 0.562 | 0.823 | 0.696 | 0.696 | 0.260 | 17.1 |
| s > 0.5, components | 148 | 0.604 | 0.410 | 0.574 | 0.716 | 0.358 | 0.029 | 0.021 | 0.462 | 59.662 | 671.7 |
| layer, converged (predicted markers) | 148 | 0.681 | 0.643 | 0.733 | 0.816 | 0.534 | 0.705 | 0.583 | 0.655 | 0.740 | 23.8 |
| layer + fallback markers | 148 | 0.681 | 0.643 | 0.733 | 0.816 | 0.534 | 0.697 | 0.576 | 0.655 | 0.791 | 24.4 |
| layer, ground-truth markers (oracle) | 148 | 0.864 | 0.819 | 0.926 | 0.864 | 0.581 | 0.960 | 0.831 | 0.870 | 0.024 | 15.7 |
| layer, image-gradient costs | 148 | 0.457 | 0.147 | 0.284 | 0.566 | 0.257 | 0.380 | 0.225 | 0.454 | 0.930 | 25.4 |
| marker watershed on the contour map | 148 | 0.628 | 0.446 | 0.617 | 0.713 | 0.397 | 0.626 | 0.467 | 0.606 | 0.930 | 25.4 |
| ground truth instances | 148 | 1.000 | 1.000 | 1.000 | 1.000 | 0.557 | 1.000 | 1.000 | 1.000 | 0.000 | 16.0 |

## Paired per-patch differences (2523 patches; bootstrap 95 % intervals; F1 / PQ / AJI dataset-level, bootstrapped over patches)

| comparison | IoU | BF₂ | edge align. | F1@0.5 | PQ | AJI |
|---|---|---|---|---|---|---|
| layer − U-Net (sec. 6) logits | -0.045 [-0.048, -0.041] | -0.049 [-0.053, -0.045] | -0.028 [-0.029, -0.026] | +0.045 [+0.037, +0.051] | +0.028 [+0.022, +0.033] | +0.123 [+0.106, +0.137] |
| layer − contour-head U-Net, watershed (b) | -0.044 [-0.048, -0.040] | -0.054 [-0.058, -0.050] | -0.019 [-0.020, -0.017] | -0.014 [-0.018, -0.010] | -0.025 [-0.028, -0.021] | -0.040 [-0.044, -0.037] |
| layer − sec. 11.1 dist run layer | -0.033 [-0.036, -0.029] | -0.042 [-0.045, -0.038] | -0.031 [-0.033, -0.030] | -0.090 [-0.095, -0.085] | -0.083 [-0.087, -0.080] | -0.036 [-0.039, -0.033] |
| layer, ground-truth markers − sec. 11.1 dist run layer, ground-truth markers | -0.000 [-0.001, +0.001] | -0.000 [-0.001, +0.000] | -0.000 [-0.001, +0.000] | -0.000 [-0.001, +0.001] | -0.001 [-0.001, +0.000] | +0.000 [-0.000, +0.000] |
| layer − this model's own logits | +0.083 [+0.079, +0.087] | +0.149 [+0.146, +0.154] | +0.163 [+0.161, +0.166] | +0.671 [+0.665, +0.677] | +0.537 [+0.532, +0.543] | +0.448 [+0.434, +0.461] |
| layer − marker watershed, same markers | +0.059 [+0.056, +0.061] | +0.113 [+0.110, +0.115] | +0.132 [+0.130, +0.134] | +0.085 [+0.081, +0.088] | +0.127 [+0.125, +0.130] | +0.059 [+0.058, +0.061] |
| layer − layer with image costs | +0.189 [+0.185, +0.192] | +0.354 [+0.349, +0.359] | +0.269 [+0.265, +0.273] | +0.300 [+0.294, +0.307] | +0.317 [+0.313, +0.322] | +0.160 [+0.158, +0.163] |
| layer + fallback − U-Net (sec. 6) logits | -0.045 [-0.049, -0.041] | -0.049 [-0.053, -0.045] | -0.027 [-0.029, -0.025] | +0.039 [+0.032, +0.046] | +0.023 [+0.017, +0.028] | +0.122 [+0.106, +0.137] |
| layer + fallback − contour-head U-Net, watershed (b) | -0.044 [-0.048, -0.040] | -0.054 [-0.058, -0.050] | -0.019 [-0.020, -0.017] | -0.019 [-0.024, -0.015] | -0.029 [-0.033, -0.026] | -0.041 [-0.045, -0.037] |
| layer + fallback − layer | -0.000 [-0.000, -0.000] | -0.000 [-0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.005 [-0.006, -0.005] | -0.005 [-0.005, -0.004] | -0.000 [-0.000, -0.000] |
| layer, ground-truth markers − layer | +0.185 [+0.179, +0.191] | +0.201 [+0.196, +0.207] | +0.043 [+0.041, +0.045] | +0.257 [+0.251, +0.263] | +0.246 [+0.240, +0.251] | +0.241 [+0.236, +0.245] |
| on the 307 limit patches: PW limit (learned) − layer | -0.018 [-0.025, -0.008] | -0.009 [-0.017, +0.001] | +0.006 [+0.003, +0.009] | +0.005 [+0.001, +0.008] | -0.004 [-0.007, -0.001] | -0.027 [-0.030, -0.024] |
| on the 307 limit patches: PW limit (learned) − PW limit (image costs) | +0.172 [+0.160, +0.186] | +0.343 [+0.325, +0.361] | +0.282 [+0.271, +0.292] | +0.306 [+0.289, +0.325] | +0.309 [+0.295, +0.323] | +0.133 [+0.123, +0.142] |
| on the 307 limit patches: PW limit (learned) − U-Net (sec. 6) logits | -0.056 [-0.066, -0.046] | -0.055 [-0.065, -0.045] | -0.020 [-0.027, -0.013] | +0.050 [+0.033, +0.069] | +0.025 [+0.010, +0.041] | +0.149 [+0.094, +0.195] |

## By crowding (F1@0.5 / PQ / count error)

| patches | n | U-Net (sec. 6) | contour-head U-Net, watershed (b) | layer | layer + fallback | marker watershed, same markers | PW limit (learned, subset) |
|---|---|---|---|---|---|---|---|
| < 10 nuclei | 486 | 0.608 / 0.485 / 0.68 | 0.596 / 0.479 / 0.81 | 0.509 / 0.400 / 1.84 | 0.500 / 0.393 / 1.96 | 0.426 / 0.296 / 2.17 | 0.501 / 0.381 / 1.71 |
| 10–30 | 1383 | 0.691 / 0.563 / 0.18 | 0.719 / 0.591 / 0.27 | 0.686 / 0.548 / 0.50 | 0.680 / 0.543 / 0.53 | 0.614 / 0.434 / 0.57 | 0.693 / 0.547 / 0.51 |
| 30–60 | 525 | 0.650 / 0.524 / 0.15 | 0.733 / 0.596 / 0.15 | 0.725 / 0.577 / 0.33 | 0.720 / 0.573 / 0.35 | 0.643 / 0.448 / 0.36 | 0.701 / 0.548 / 0.35 |
| > 60 | 129 | 0.588 / 0.469 / 0.24 | 0.700 / 0.562 / 0.13 | 0.745 / 0.592 / 0.22 | 0.744 / 0.590 / 0.23 | 0.628 / 0.431 / 0.23 | 0.669 / 0.516 / 0.24 |

## Marker quality by crowding (nuclei with one / none / several markers; background markers per patch)

| patches | one | none | several | bg markers / patch |
|---|---|---|---|---|
| < 10 nuclei | 82.4 % | 6.5 % | 11.1 % | 5.54 |
| 10–30 | 86.1 % | 5.3 % | 8.6 % | 9.45 |
| 30–60 | 85.9 % | 6.9 % | 7.2 % | 12.68 |
| > 60 | 84.7 % | 11.0 % | 4.3 % | 21.14 |
