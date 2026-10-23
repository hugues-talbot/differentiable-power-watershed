# Instances as labels: multi-marker layer on PanNuke (fold 1 → fold 2)

Run `results_pannuke_instances/dist_det/instances`: p 5.0 → 20.0, erosion [2, 3], edge target ×1.0, seam weight 5.0, 30 epochs, seed 0, training solve tol 0.0001 / maxit 100, peak loss ×1.0; marker head `dist` (mse, rmax 12; markers = h-maxima h 0.2 grown to thr 0.2, min area 16 px), chosen by PQ on 300 patches of fold 3; learned edge scale 2.01.

## Marker post-processing chosen on fold 3 (300 patches): {'mk_thr': 0.2, 'mk_min_area': 16, 'mk_h': 0.2}

| setting | PQ | F1@0.5 | AJI | count err. | n_pred | one | none | several | bg / patch |
|---|---|---|---|---|---|---|---|---|---|
| thr=0.2/min_area=16/h=0.2 | 0.517 | 0.665 | 0.580 | 0.273 | 27.8 | 81.1 % | 11.6 % | 7.3 % | 4.58 |
| thr=0.3/min_area=16/h=0.2 | 0.515 | 0.667 | 0.568 | 0.192 | 24.7 | 79.2 % | 15.9 % | 4.9 % | 3.08 |
| thr=0.3/min_area=9/h=0.2 | 0.511 | 0.664 | 0.570 | 0.237 | 26.8 | 81.9 % | 12.0 % | 6.1 % | 4.10 |
| thr=0.4/min_area=16/h=0.2 | 0.510 | 0.664 | 0.559 | 0.181 | 22.7 | 76.9 % | 19.3 % | 3.8 % | 2.25 |
| thr=0.4/min_area=9/h=0.2 | 0.508 | 0.662 | 0.562 | 0.187 | 24.5 | 79.3 % | 15.8 % | 4.9 % | 2.98 |
| thr=0.5/min_area=9/h=0.2 | 0.502 | 0.654 | 0.554 | 0.178 | 22.6 | 76.4 % | 19.7 % | 3.9 % | 2.23 |
| thr=0.4/min_area=4/h=0.2 | 0.501 | 0.654 | 0.563 | 0.241 | 26.9 | 82.1 % | 11.3 % | 6.6 % | 4.48 |
| thr=0.3/min_area=16/h=0.1 | 0.500 | 0.646 | 0.550 | 0.191 | 22.2 | 72.2 % | 22.3 % | 5.5 % | 2.03 |
| thr=0.5/min_area=1/h=0.1 (untuned default) | 0.456 | 0.599 | 0.549 | 0.327 | 29.2 | 73.8 % | 10.4 % | 15.8 % | 6.97 |

(top 8 of 72 settings by PQ)

## All of fold 2

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6, binary target), s > 0.5, components | 2523 | 0.719 | 0.652 | 0.769 | 0.807 | 0.577 | 0.656 | 0.531 | 0.494 | 0.275 | 23.0 |
| U-Net + contour head (sec. 10.1, gap target), logits | 2523 | 0.719 | 0.658 | 0.774 | 0.809 | 0.574 | 0.682 | 0.556 | 0.571 | 0.303 | 25.2 |
| U-Net + contour head, tuned marker watershed (b) | 2523 | 0.718 | 0.658 | 0.774 | 0.809 | 0.568 | 0.715 | 0.583 | 0.657 | 0.344 | 27.2 |
| sec. 11.1 dist run: layer, converged (predicted markers) | 2523 | 0.707 | 0.647 | 0.762 | 0.811 | 0.580 | 0.791 | 0.641 | 0.653 | 0.239 | 24.3 |
| this model: s > 0.5, components | 2523 | 0.582 | 0.399 | 0.568 | 0.701 | 0.387 | 0.026 | 0.018 | 0.159 | 48.269 | 692.5 |
| this model: layer, converged (predicted markers) | 2523 | 0.621 | 0.555 | 0.665 | 0.742 | 0.549 | 0.658 | 0.510 | 0.569 | 0.318 | 27.5 |
| this model: layer + fallback markers | 2523 | 0.618 | 0.554 | 0.664 | 0.745 | 0.545 | 0.644 | 0.498 | 0.569 | 0.440 | 29.6 |
| this model: layer, ground-truth markers (oracle) | 2523 | 0.858 | 0.796 | 0.920 | 0.858 | 0.591 | 0.957 | 0.803 | 0.858 | 0.021 | 23.3 |
| this model: layer, image-gradient costs | 2523 | 0.349 | 0.140 | 0.254 | 0.545 | 0.278 | 0.211 | 0.127 | 0.328 | 0.322 | 27.6 |
| this model: marker watershed on the contour map | 2523 | 0.618 | 0.442 | 0.618 | 0.696 | 0.418 | 0.668 | 0.462 | 0.538 | 0.322 | 27.6 |
| this model: PW limit, learned costs | 307 | 0.648 | 0.583 | 0.701 | 0.761 | 0.564 | 0.681 | 0.527 | 0.571 | 0.307 | 28.7 |
| this model: PW limit, image-gradient costs | 307 | 0.343 | 0.144 | 0.248 | 0.544 | 0.264 | 0.198 | 0.119 | 0.314 | 0.317 | 28.7 |
| this model: ground truth instances | 2523 | 1.000 | 1.000 | 1.000 | 1.000 | 0.559 | 1.000 | 1.000 | 1.000 | 0.000 | 23.7 |

## Marker quality (predicted markers against the ground-truth nuclei)

- 59872 nuclei in fold 2 (23.7 per patch); predicted markers 27.6 per patch.
- exactly one marker: 80.8 %; none: 11.5 %; several: 7.6 %; markers in background: 4.46 per patch.
- with fallback markers: one 82.7 %, none 8.9 %, several 8.4 %, background 6.28 per patch, 30.3 markers per patch.
- sec. 11.1 dist run: one 83.9 %, none 14.5 %, several 1.6 %, background 3.58 per patch, 24.3 markers per patch.

## Inference cost

- U-Net forward: 0.9 ms per image; converged multi-marker solve (tol 1e-05): 74.3 ms per image at K = 27.6 markers per image (72046 systems in 158 batches of 16; 195 PCG iterations per batch).
- exact K-label PW limit (one CPU core): 0.7 s per patch with the learned costs, 0.8 s with image-gradient costs, K = 28.7; 7951 ambiguous plateaus solved over 307 patches.

## Per tissue type

**Breast**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 749 | 0.722 | 0.596 | 0.756 | 0.780 | 0.585 | 0.690 | 0.547 | 0.550 | 0.198 | 21.2 |
| U-Net + contour head, watershed (b) | 749 | 0.722 | 0.601 | 0.761 | 0.782 | 0.576 | 0.757 | 0.605 | 0.671 | 0.242 | 24.5 |
| sec. 11.1 dist run: layer | 749 | 0.708 | 0.585 | 0.743 | 0.782 | 0.587 | 0.817 | 0.647 | 0.661 | 0.187 | 22.9 |
| s > 0.5, components | 749 | 0.597 | 0.376 | 0.554 | 0.675 | 0.377 | 0.025 | 0.017 | 0.186 | 44.411 | 693.4 |
| layer, converged (predicted markers) | 749 | 0.612 | 0.485 | 0.631 | 0.706 | 0.539 | 0.684 | 0.513 | 0.569 | 0.229 | 24.5 |
| layer + fallback markers | 749 | 0.611 | 0.486 | 0.632 | 0.709 | 0.536 | 0.667 | 0.499 | 0.568 | 0.328 | 26.4 |
| layer, ground-truth markers (oracle) | 749 | 0.853 | 0.742 | 0.906 | 0.837 | 0.597 | 0.964 | 0.803 | 0.852 | 0.015 | 21.4 |
| layer, image-gradient costs | 749 | 0.343 | 0.122 | 0.222 | 0.522 | 0.231 | 0.216 | 0.131 | 0.333 | 0.232 | 24.6 |
| marker watershed on the contour map | 749 | 0.620 | 0.405 | 0.589 | 0.670 | 0.405 | 0.716 | 0.483 | 0.547 | 0.232 | 24.6 |
| PW limit, learned costs | 89 | 0.664 | 0.531 | 0.692 | 0.734 | 0.564 | 0.736 | 0.557 | 0.592 | 0.190 | 25.4 |
| PW limit, image-gradient costs | 89 | 0.348 | 0.130 | 0.224 | 0.521 | 0.206 | 0.217 | 0.130 | 0.331 | 0.192 | 25.5 |
| ground truth instances | 749 | 1.000 | 1.000 | 1.000 | 1.000 | 0.553 | 1.000 | 1.000 | 1.000 | 0.000 | 21.7 |

**Colon**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 468 | 0.698 | 0.617 | 0.738 | 0.788 | 0.558 | 0.547 | 0.431 | 0.349 | 0.274 | 21.1 |
| U-Net + contour head, watershed (b) | 468 | 0.691 | 0.621 | 0.742 | 0.788 | 0.550 | 0.630 | 0.497 | 0.574 | 0.340 | 27.7 |
| sec. 11.1 dist run: layer | 468 | 0.683 | 0.605 | 0.726 | 0.791 | 0.569 | 0.709 | 0.558 | 0.579 | 0.238 | 23.8 |
| s > 0.5, components | 468 | 0.560 | 0.376 | 0.532 | 0.692 | 0.383 | 0.015 | 0.010 | 0.081 | 50.557 | 823.5 |
| layer, converged (predicted markers) | 468 | 0.580 | 0.509 | 0.620 | 0.715 | 0.527 | 0.535 | 0.402 | 0.483 | 0.380 | 30.4 |
| layer + fallback markers | 468 | 0.577 | 0.507 | 0.618 | 0.717 | 0.526 | 0.524 | 0.394 | 0.482 | 0.473 | 32.3 |
| layer, ground-truth markers (oracle) | 468 | 0.851 | 0.775 | 0.907 | 0.851 | 0.569 | 0.935 | 0.767 | 0.841 | 0.023 | 24.8 |
| layer, image-gradient costs | 468 | 0.349 | 0.203 | 0.293 | 0.560 | 0.299 | 0.159 | 0.094 | 0.281 | 0.386 | 30.5 |
| marker watershed on the contour map | 468 | 0.605 | 0.427 | 0.589 | 0.688 | 0.416 | 0.534 | 0.361 | 0.468 | 0.386 | 30.5 |
| PW limit, learned costs | 62 | 0.593 | 0.531 | 0.651 | 0.725 | 0.519 | 0.532 | 0.394 | 0.464 | 0.322 | 38.0 |
| PW limit, image-gradient costs | 62 | 0.319 | 0.194 | 0.283 | 0.552 | 0.274 | 0.133 | 0.080 | 0.249 | 0.325 | 38.1 |
| ground truth instances | 468 | 1.000 | 1.000 | 1.000 | 1.000 | 0.539 | 1.000 | 1.000 | 1.000 | 0.000 | 25.4 |

**HeadNeck**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 169 | 0.672 | 0.658 | 0.744 | 0.835 | 0.648 | 0.640 | 0.519 | 0.556 | 0.424 | 20.2 |
| U-Net + contour head, watershed (b) | 169 | 0.682 | 0.675 | 0.756 | 0.839 | 0.638 | 0.688 | 0.565 | 0.660 | 0.474 | 23.6 |
| sec. 11.1 dist run: layer | 169 | 0.701 | 0.711 | 0.782 | 0.846 | 0.631 | 0.784 | 0.647 | 0.651 | 0.203 | 19.8 |
| s > 0.5, components | 169 | 0.484 | 0.370 | 0.512 | 0.758 | 0.474 | 0.026 | 0.018 | 0.216 | 46.383 | 604.2 |
| layer, converged (predicted markers) | 169 | 0.614 | 0.614 | 0.687 | 0.792 | 0.632 | 0.624 | 0.489 | 0.553 | 0.362 | 23.2 |
| layer + fallback markers | 169 | 0.601 | 0.602 | 0.675 | 0.795 | 0.635 | 0.609 | 0.477 | 0.552 | 0.520 | 25.1 |
| layer, ground-truth markers (oracle) | 169 | 0.852 | 0.844 | 0.927 | 0.882 | 0.646 | 0.964 | 0.818 | 0.862 | 0.036 | 18.2 |
| layer, image-gradient costs | 169 | 0.352 | 0.195 | 0.302 | 0.603 | 0.407 | 0.142 | 0.084 | 0.296 | 0.366 | 23.3 |
| marker watershed on the contour map | 169 | 0.606 | 0.496 | 0.643 | 0.751 | 0.491 | 0.658 | 0.463 | 0.534 | 0.366 | 23.3 |
| ground truth instances | 169 | 1.000 | 1.000 | 1.000 | 1.000 | 0.629 | 1.000 | 1.000 | 1.000 | 0.000 | 18.5 |

**Adrenal_gland**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 148 | 0.716 | 0.676 | 0.774 | 0.808 | 0.554 | 0.694 | 0.582 | 0.655 | 0.378 | 18.4 |
| U-Net + contour head, watershed (b) | 148 | 0.719 | 0.689 | 0.783 | 0.811 | 0.551 | 0.712 | 0.605 | 0.713 | 0.444 | 20.1 |
| sec. 11.1 dist run: layer | 148 | 0.709 | 0.688 | 0.779 | 0.824 | 0.562 | 0.823 | 0.696 | 0.696 | 0.260 | 17.1 |
| s > 0.5, components | 148 | 0.600 | 0.417 | 0.578 | 0.717 | 0.359 | 0.028 | 0.020 | 0.463 | 67.153 | 707.6 |
| layer, converged (predicted markers) | 148 | 0.628 | 0.590 | 0.679 | 0.754 | 0.537 | 0.690 | 0.553 | 0.618 | 0.339 | 18.5 |
| layer + fallback markers | 148 | 0.627 | 0.588 | 0.678 | 0.757 | 0.532 | 0.661 | 0.529 | 0.616 | 0.513 | 20.7 |
| layer, ground-truth markers (oracle) | 148 | 0.864 | 0.827 | 0.929 | 0.865 | 0.582 | 0.958 | 0.831 | 0.871 | 0.024 | 15.7 |
| layer, image-gradient costs | 148 | 0.322 | 0.072 | 0.181 | 0.513 | 0.277 | 0.241 | 0.148 | 0.336 | 0.342 | 18.6 |
| marker watershed on the contour map | 148 | 0.627 | 0.455 | 0.624 | 0.710 | 0.402 | 0.731 | 0.539 | 0.596 | 0.342 | 18.6 |
| ground truth instances | 148 | 1.000 | 1.000 | 1.000 | 1.000 | 0.557 | 1.000 | 1.000 | 1.000 | 0.000 | 16.0 |

## Paired per-patch differences (2523 patches; bootstrap 95 % intervals; F1 / PQ / AJI dataset-level, bootstrapped over patches)

| comparison | IoU | BF₂ | edge align. | F1@0.5 | PQ | AJI |
|---|---|---|---|---|---|---|
| layer − U-Net (sec. 6) logits | -0.098 [-0.102, -0.094] | -0.104 [-0.108, -0.100] | -0.029 [-0.031, -0.028] | +0.002 [-0.006, +0.009] | -0.021 [-0.027, -0.015] | +0.075 [+0.059, +0.090] |
| layer − contour-head U-Net, watershed (b) | -0.097 [-0.101, -0.094] | -0.109 [-0.113, -0.105] | -0.020 [-0.022, -0.019] | -0.057 [-0.062, -0.051] | -0.074 [-0.078, -0.069] | -0.088 [-0.092, -0.083] |
| layer − sec. 11.1 dist run layer | -0.086 [-0.090, -0.082] | -0.097 [-0.100, -0.093] | -0.033 [-0.035, -0.031] | -0.132 [-0.139, -0.126] | -0.132 [-0.137, -0.126] | -0.083 [-0.087, -0.079] |
| layer, ground-truth markers − sec. 11.1 dist run layer, ground-truth markers | -0.001 [-0.002, +0.000] | -0.002 [-0.004, -0.001] | -0.000 [-0.001, +0.000] | -0.002 [-0.003, -0.001] | -0.002 [-0.003, -0.001] | +0.000 [-0.000, +0.001] |
| layer − this model's own logits | +0.039 [+0.033, +0.045] | +0.097 [+0.091, +0.103] | +0.167 [+0.165, +0.170] | +0.632 [+0.625, +0.639] | +0.491 [+0.485, +0.498] | +0.410 [+0.395, +0.425] |
| layer − marker watershed, same markers | +0.002 [-0.001, +0.005] | +0.047 [+0.045, +0.050] | +0.130 [+0.128, +0.132] | -0.010 [-0.015, -0.004] | +0.047 [+0.043, +0.052] | +0.031 [+0.029, +0.034] |
| layer − layer with image costs | +0.272 [+0.268, +0.275] | +0.411 [+0.405, +0.416] | +0.270 [+0.266, +0.274] | +0.448 [+0.440, +0.455] | +0.382 [+0.377, +0.387] | +0.241 [+0.238, +0.244] |
| layer + fallback − U-Net (sec. 6) logits | -0.101 [-0.104, -0.097] | -0.105 [-0.109, -0.102] | -0.033 [-0.034, -0.031] | -0.013 [-0.020, -0.005] | -0.033 [-0.040, -0.027] | +0.074 [+0.058, +0.089] |
| layer + fallback − contour-head U-Net, watershed (b) | -0.100 [-0.103, -0.097] | -0.110 [-0.114, -0.107] | -0.024 [-0.025, -0.022] | -0.071 [-0.077, -0.066] | -0.086 [-0.090, -0.081] | -0.089 [-0.093, -0.084] |
| layer + fallback − layer | -0.003 [-0.004, -0.001] | -0.002 [-0.004, +0.000] | -0.003 [-0.004, -0.003] | -0.014 [-0.016, -0.013] | -0.012 [-0.013, -0.011] | -0.001 [-0.001, -0.001] |
| layer, ground-truth markers − layer | +0.238 [+0.232, +0.244] | +0.255 [+0.249, +0.261] | +0.045 [+0.042, +0.047] | +0.298 [+0.290, +0.305] | +0.293 [+0.285, +0.300] | +0.288 [+0.283, +0.293] |
| on the 307 limit patches: PW limit (learned) − layer | +0.030 [+0.025, +0.036] | +0.039 [+0.034, +0.046] | +0.018 [+0.014, +0.023] | +0.042 [+0.035, +0.050] | +0.034 [+0.029, +0.041] | +0.014 [+0.011, +0.019] |
| on the 307 limit patches: PW limit (learned) − PW limit (image costs) | +0.304 [+0.291, +0.316] | +0.453 [+0.435, +0.469] | +0.300 [+0.285, +0.314] | +0.484 [+0.461, +0.504] | +0.408 [+0.390, +0.425] | +0.257 [+0.248, +0.267] |
| on the 307 limit patches: PW limit (learned) − U-Net (sec. 6) logits | -0.066 [-0.072, -0.059] | -0.062 [-0.068, -0.056] | -0.006 [-0.011, +0.000] | +0.048 [+0.030, +0.068] | +0.017 [+0.002, +0.033] | +0.146 [+0.091, +0.194] |

## By crowding (F1@0.5 / PQ / count error)

| patches | n | U-Net (sec. 6) | contour-head U-Net, watershed (b) | layer | layer + fallback | marker watershed, same markers | PW limit (learned, subset) |
|---|---|---|---|---|---|---|---|
| < 10 nuclei | 486 | 0.608 / 0.485 / 0.68 | 0.596 / 0.479 / 0.81 | 0.531 / 0.401 / 0.70 | 0.494 / 0.372 / 1.02 | 0.572 / 0.391 / 0.71 | 0.579 / 0.433 / 0.62 |
| 10–30 | 1383 | 0.691 / 0.563 / 0.18 | 0.719 / 0.591 / 0.27 | 0.634 / 0.489 / 0.25 | 0.616 / 0.474 / 0.35 | 0.675 / 0.471 / 0.26 | 0.700 / 0.545 / 0.26 |
| 30–60 | 525 | 0.650 / 0.524 / 0.15 | 0.733 / 0.596 / 0.15 | 0.670 / 0.518 / 0.18 | 0.660 / 0.509 / 0.23 | 0.678 / 0.467 / 0.18 | 0.693 / 0.535 / 0.19 |
| > 60 | 129 | 0.588 / 0.469 / 0.24 | 0.700 / 0.562 / 0.13 | 0.724 / 0.570 / 0.13 | 0.721 / 0.567 / 0.16 | 0.652 / 0.447 / 0.14 | 0.645 / 0.495 / 0.13 |

## Marker quality by crowding (nuclei with one / none / several markers; background markers per patch)

| patches | one | none | several | bg markers / patch |
|---|---|---|---|---|
| < 10 nuclei | 76.2 % | 13.8 % | 10.0 % | 1.82 |
| 10–30 | 80.2 % | 10.4 % | 9.3 % | 3.96 |
| 30–60 | 81.6 % | 11.1 % | 7.3 % | 6.27 |
| > 60 | 81.7 % | 14.5 % | 3.9 % | 12.33 |
