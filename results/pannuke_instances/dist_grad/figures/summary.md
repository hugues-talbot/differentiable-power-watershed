# Instances as labels: multi-marker layer on PanNuke (fold 1 → fold 2)

Run `results_pannuke_instances/dist_grad/instances`: p 5.0 → 20.0, erosion [2, 3], edge target ×1.0, seam weight 5.0, 30 epochs, seed 0, training solve tol 0.0001 / maxit 100; marker head `dist` (mse, rmax 12; markers = h-maxima h 0.2 grown to thr 0.2, min area 16 px), chosen by PQ on 300 patches of fold 3; learned edge scale 2.06.

## Marker post-processing chosen on fold 3 (300 patches): {'mk_thr': 0.2, 'mk_min_area': 16, 'mk_h': 0.2}

| setting | PQ | F1@0.5 | AJI | count err. | n_pred | one | none | several | bg / patch |
|---|---|---|---|---|---|---|---|---|---|
| thr=0.2/min_area=16/h=0.2 | 0.646 | 0.792 | 0.658 | 0.204 | 25.4 | 84.9 % | 13.6 % | 1.5 % | 4.12 |
| thr=0.2/min_area=9/h=0.2 | 0.644 | 0.790 | 0.657 | 0.219 | 25.9 | 85.7 % | 12.8 % | 1.5 % | 4.42 |
| thr=0.2/min_area=4/h=0.2 | 0.643 | 0.790 | 0.657 | 0.228 | 26.1 | 86.1 % | 12.4 % | 1.5 % | 4.64 |
| thr=0.2/min_area=1/h=0.2 | 0.643 | 0.789 | 0.657 | 0.230 | 26.2 | 86.4 % | 12.1 % | 1.5 % | 4.80 |
| thr=0.3/min_area=9/h=0.2 | 0.638 | 0.789 | 0.656 | 0.172 | 24.4 | 83.9 % | 14.6 % | 1.4 % | 3.46 |
| thr=0.3/min_area=16/h=0.2 | 0.638 | 0.788 | 0.656 | 0.165 | 23.8 | 82.5 % | 16.1 % | 1.4 % | 3.16 |
| thr=0.3/min_area=4/h=0.2 | 0.637 | 0.789 | 0.657 | 0.181 | 24.8 | 85.0 % | 13.6 % | 1.5 % | 3.69 |
| thr=0.3/min_area=1/h=0.2 | 0.636 | 0.788 | 0.656 | 0.184 | 24.9 | 85.7 % | 12.8 % | 1.5 % | 4.04 |
| thr=0.5/min_area=1/h=0.1 (untuned default) | 0.577 | 0.729 | 0.610 | 0.174 | 21.5 | 77.1 % | 20.5 % | 2.4 % | 2.07 |

(top 8 of 72 settings by PQ)

## All of fold 2

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6, binary target), s > 0.5, components | 2523 | 0.719 | 0.652 | 0.769 | 0.807 | 0.577 | 0.656 | 0.531 | 0.494 | 0.275 | 23.0 |
| U-Net + contour head (sec. 10.1, gap target), logits | 2523 | 0.719 | 0.658 | 0.774 | 0.809 | 0.574 | 0.682 | 0.556 | 0.571 | 0.303 | 25.2 |
| U-Net + contour head, tuned marker watershed (b) | 2523 | 0.718 | 0.658 | 0.774 | 0.809 | 0.568 | 0.715 | 0.583 | 0.657 | 0.344 | 27.2 |
| sec. 11.1 dist run: layer, converged (predicted markers) | 2523 | 0.707 | 0.647 | 0.762 | 0.811 | 0.580 | 0.791 | 0.641 | 0.653 | 0.239 | 24.3 |
| this model: s > 0.5, components | 2523 | 0.597 | 0.396 | 0.568 | 0.714 | 0.396 | 0.027 | 0.019 | 0.169 | 47.968 | 679.4 |
| this model: layer, converged (predicted markers) | 2523 | 0.709 | 0.650 | 0.765 | 0.814 | 0.577 | 0.789 | 0.641 | 0.653 | 0.252 | 24.8 |
| this model: layer + fallback markers | 2523 | 0.706 | 0.649 | 0.764 | 0.815 | 0.579 | 0.776 | 0.630 | 0.653 | 0.319 | 26.1 |
| this model: layer, ground-truth markers (oracle) | 2523 | 0.860 | 0.799 | 0.922 | 0.859 | 0.590 | 0.959 | 0.806 | 0.859 | 0.020 | 23.3 |
| this model: layer, image-gradient costs | 2523 | 0.561 | 0.280 | 0.466 | 0.653 | 0.312 | 0.633 | 0.406 | 0.530 | 0.254 | 24.8 |
| this model: marker watershed on the contour map | 2523 | 0.635 | 0.442 | 0.621 | 0.711 | 0.430 | 0.720 | 0.512 | 0.572 | 0.254 | 24.8 |
| this model: PW limit, learned costs | 307 | 0.690 | 0.613 | 0.736 | 0.793 | 0.571 | 0.757 | 0.602 | 0.613 | 0.239 | 25.5 |
| this model: PW limit, image-gradient costs | 307 | 0.556 | 0.280 | 0.460 | 0.649 | 0.304 | 0.613 | 0.391 | 0.511 | 0.239 | 25.6 |
| this model: ground truth instances | 2523 | 1.000 | 1.000 | 1.000 | 1.000 | 0.559 | 1.000 | 1.000 | 1.000 | 0.000 | 23.7 |

## Marker quality (predicted markers against the ground-truth nuclei)

- 59872 nuclei in fold 2 (23.7 per patch); predicted markers 24.8 per patch.
- exactly one marker: 84.6 %; none: 13.6 %; several: 1.8 %; markers in background: 3.90 per patch.
- with fallback markers: one 85.8 %, none 12.1 %, several 2.2 %, background 5.05 per patch, 26.5 markers per patch.
- sec. 11.1 dist run: one 83.9 %, none 14.5 %, several 1.6 %, background 3.58 per patch, 24.3 markers per patch.

## Inference cost

- U-Net forward: 2.5 ms per image; converged multi-marker solve (tol 1e-05): 102.0 ms per image at K = 24.8 markers per image (65216 systems in 158 batches of 16; 171 PCG iterations per batch).
- exact K-label PW limit (one CPU core): 0.6 s per patch with the learned costs, 0.6 s with image-gradient costs, K = 25.6; 6578 ambiguous plateaus solved over 307 patches.

## Per tissue type

**Breast**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 749 | 0.722 | 0.596 | 0.756 | 0.780 | 0.585 | 0.690 | 0.547 | 0.550 | 0.198 | 21.2 |
| U-Net + contour head, watershed (b) | 749 | 0.722 | 0.601 | 0.761 | 0.782 | 0.576 | 0.757 | 0.605 | 0.671 | 0.242 | 24.5 |
| sec. 11.1 dist run: layer | 749 | 0.708 | 0.585 | 0.743 | 0.782 | 0.587 | 0.817 | 0.647 | 0.661 | 0.187 | 22.9 |
| s > 0.5, components | 749 | 0.618 | 0.376 | 0.557 | 0.687 | 0.389 | 0.027 | 0.019 | 0.178 | 42.249 | 645.7 |
| layer, converged (predicted markers) | 749 | 0.713 | 0.593 | 0.750 | 0.786 | 0.587 | 0.813 | 0.647 | 0.663 | 0.198 | 23.2 |
| layer + fallback markers | 749 | 0.712 | 0.593 | 0.750 | 0.787 | 0.587 | 0.803 | 0.638 | 0.662 | 0.243 | 24.1 |
| layer, ground-truth markers (oracle) | 749 | 0.854 | 0.746 | 0.909 | 0.839 | 0.596 | 0.967 | 0.806 | 0.853 | 0.015 | 21.4 |
| layer, image-gradient costs | 749 | 0.575 | 0.267 | 0.440 | 0.637 | 0.291 | 0.664 | 0.430 | 0.549 | 0.200 | 23.3 |
| marker watershed on the contour map | 749 | 0.638 | 0.403 | 0.591 | 0.685 | 0.419 | 0.755 | 0.525 | 0.583 | 0.200 | 23.3 |
| PW limit, learned costs | 89 | 0.707 | 0.559 | 0.721 | 0.765 | 0.581 | 0.806 | 0.626 | 0.641 | 0.145 | 23.8 |
| PW limit, image-gradient costs | 89 | 0.587 | 0.276 | 0.445 | 0.637 | 0.276 | 0.658 | 0.424 | 0.544 | 0.146 | 23.9 |
| ground truth instances | 749 | 1.000 | 1.000 | 1.000 | 1.000 | 0.553 | 1.000 | 1.000 | 1.000 | 0.000 | 21.7 |

**Colon**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 468 | 0.698 | 0.617 | 0.738 | 0.788 | 0.558 | 0.547 | 0.431 | 0.349 | 0.274 | 21.1 |
| U-Net + contour head, watershed (b) | 468 | 0.691 | 0.621 | 0.742 | 0.788 | 0.550 | 0.630 | 0.497 | 0.574 | 0.340 | 27.7 |
| sec. 11.1 dist run: layer | 468 | 0.683 | 0.605 | 0.726 | 0.791 | 0.569 | 0.709 | 0.558 | 0.579 | 0.238 | 23.8 |
| s > 0.5, components | 468 | 0.564 | 0.363 | 0.522 | 0.703 | 0.399 | 0.016 | 0.011 | 0.093 | 51.361 | 812.5 |
| layer, converged (predicted markers) | 468 | 0.684 | 0.608 | 0.728 | 0.794 | 0.562 | 0.709 | 0.558 | 0.579 | 0.253 | 24.5 |
| layer + fallback markers | 468 | 0.681 | 0.606 | 0.726 | 0.795 | 0.564 | 0.698 | 0.549 | 0.579 | 0.312 | 25.8 |
| layer, ground-truth markers (oracle) | 468 | 0.851 | 0.777 | 0.908 | 0.852 | 0.569 | 0.939 | 0.771 | 0.842 | 0.022 | 24.8 |
| layer, image-gradient costs | 468 | 0.563 | 0.331 | 0.481 | 0.663 | 0.339 | 0.570 | 0.361 | 0.482 | 0.254 | 24.6 |
| marker watershed on the contour map | 468 | 0.618 | 0.423 | 0.590 | 0.701 | 0.432 | 0.612 | 0.426 | 0.500 | 0.254 | 24.6 |
| PW limit, learned costs | 62 | 0.658 | 0.576 | 0.700 | 0.767 | 0.523 | 0.635 | 0.488 | 0.508 | 0.211 | 29.9 |
| PW limit, image-gradient costs | 62 | 0.537 | 0.329 | 0.473 | 0.651 | 0.308 | 0.518 | 0.326 | 0.438 | 0.212 | 30.0 |
| ground truth instances | 468 | 1.000 | 1.000 | 1.000 | 1.000 | 0.539 | 1.000 | 1.000 | 1.000 | 0.000 | 25.4 |

**HeadNeck**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 169 | 0.672 | 0.658 | 0.744 | 0.835 | 0.648 | 0.640 | 0.519 | 0.556 | 0.424 | 20.2 |
| U-Net + contour head, watershed (b) | 169 | 0.682 | 0.675 | 0.756 | 0.839 | 0.638 | 0.688 | 0.565 | 0.660 | 0.474 | 23.6 |
| sec. 11.1 dist run: layer | 169 | 0.701 | 0.711 | 0.782 | 0.846 | 0.631 | 0.784 | 0.647 | 0.651 | 0.203 | 19.8 |
| s > 0.5, components | 169 | 0.511 | 0.384 | 0.522 | 0.767 | 0.471 | 0.025 | 0.018 | 0.189 | 50.619 | 632.6 |
| layer, converged (predicted markers) | 169 | 0.696 | 0.703 | 0.777 | 0.848 | 0.625 | 0.783 | 0.644 | 0.650 | 0.246 | 20.8 |
| layer + fallback markers | 169 | 0.670 | 0.678 | 0.752 | 0.850 | 0.636 | 0.764 | 0.628 | 0.648 | 0.352 | 22.1 |
| layer, ground-truth markers (oracle) | 169 | 0.862 | 0.853 | 0.940 | 0.887 | 0.647 | 0.966 | 0.821 | 0.864 | 0.029 | 18.2 |
| layer, image-gradient costs | 169 | 0.549 | 0.334 | 0.519 | 0.696 | 0.411 | 0.580 | 0.362 | 0.511 | 0.247 | 20.8 |
| marker watershed on the contour map | 169 | 0.632 | 0.512 | 0.658 | 0.762 | 0.496 | 0.718 | 0.519 | 0.572 | 0.247 | 20.8 |
| ground truth instances | 169 | 1.000 | 1.000 | 1.000 | 1.000 | 0.629 | 1.000 | 1.000 | 1.000 | 0.000 | 18.5 |

**Adrenal_gland**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 148 | 0.716 | 0.676 | 0.774 | 0.808 | 0.554 | 0.694 | 0.582 | 0.655 | 0.378 | 18.4 |
| U-Net + contour head, watershed (b) | 148 | 0.719 | 0.689 | 0.783 | 0.811 | 0.551 | 0.712 | 0.605 | 0.713 | 0.444 | 20.1 |
| sec. 11.1 dist run: layer | 148 | 0.709 | 0.688 | 0.779 | 0.824 | 0.562 | 0.823 | 0.696 | 0.696 | 0.260 | 17.1 |
| s > 0.5, components | 148 | 0.615 | 0.414 | 0.577 | 0.728 | 0.363 | 0.028 | 0.021 | 0.462 | 66.583 | 711.6 |
| layer, converged (predicted markers) | 148 | 0.714 | 0.691 | 0.783 | 0.827 | 0.559 | 0.816 | 0.691 | 0.693 | 0.273 | 17.4 |
| layer + fallback markers | 148 | 0.713 | 0.690 | 0.783 | 0.829 | 0.559 | 0.797 | 0.673 | 0.693 | 0.349 | 18.5 |
| layer, ground-truth markers (oracle) | 148 | 0.866 | 0.826 | 0.931 | 0.866 | 0.579 | 0.960 | 0.833 | 0.873 | 0.027 | 15.7 |
| layer, image-gradient costs | 148 | 0.529 | 0.197 | 0.388 | 0.616 | 0.275 | 0.646 | 0.412 | 0.530 | 0.275 | 17.4 |
| marker watershed on the contour map | 148 | 0.642 | 0.456 | 0.628 | 0.723 | 0.409 | 0.770 | 0.584 | 0.624 | 0.275 | 17.4 |
| ground truth instances | 148 | 1.000 | 1.000 | 1.000 | 1.000 | 0.557 | 1.000 | 1.000 | 1.000 | 0.000 | 16.0 |

## Paired per-patch differences (2523 patches; bootstrap 95 % intervals; F1 / PQ / AJI dataset-level, bootstrapped over patches)

| comparison | IoU | BF₂ | edge align. | F1@0.5 | PQ | AJI |
|---|---|---|---|---|---|---|
| layer − U-Net (sec. 6) logits | -0.010 [-0.013, -0.007] | -0.004 [-0.007, -0.001] | +0.000 [-0.001, +0.002] | +0.133 [+0.127, +0.137] | +0.110 [+0.106, +0.114] | +0.159 [+0.144, +0.173] |
| layer − contour-head U-Net, watershed (b) | -0.009 [-0.012, -0.006] | -0.009 [-0.012, -0.006] | +0.009 [+0.008, +0.011] | +0.074 [+0.071, +0.077] | +0.058 [+0.055, +0.060] | -0.004 [-0.006, -0.001] |
| layer − sec. 11.1 dist run layer | +0.002 [+0.000, +0.004] | +0.003 [+0.001, +0.006] | -0.003 [-0.004, -0.002] | -0.002 [-0.004, +0.001] | -0.000 [-0.002, +0.001] | +0.001 [-0.001, +0.002] |
| layer, ground-truth markers − sec. 11.1 dist run layer, ground-truth markers | +0.001 [+0.000, +0.002] | +0.000 [-0.001, +0.001] | -0.001 [-0.002, -0.001] | +0.001 [-0.000, +0.002] | +0.001 [+0.000, +0.002] | +0.001 [+0.001, +0.002] |
| layer − this model's own logits | +0.111 [+0.106, +0.117] | +0.197 [+0.192, +0.203] | +0.187 [+0.184, +0.189] | +0.762 [+0.757, +0.766] | +0.622 [+0.617, +0.626] | +0.485 [+0.470, +0.499] |
| layer − marker watershed, same markers | +0.074 [+0.072, +0.075] | +0.144 [+0.142, +0.146] | +0.147 [+0.146, +0.149] | +0.069 [+0.066, +0.073] | +0.129 [+0.126, +0.131] | +0.082 [+0.080, +0.083] |
| layer − layer with image costs | +0.148 [+0.145, +0.150] | +0.299 [+0.294, +0.304] | +0.265 [+0.262, +0.269] | +0.156 [+0.151, +0.162] | +0.235 [+0.231, +0.239] | +0.123 [+0.121, +0.126] |
| layer + fallback − U-Net (sec. 6) logits | -0.012 [-0.016, -0.009] | -0.006 [-0.009, -0.002] | +0.001 [-0.001, +0.002] | +0.120 [+0.114, +0.125] | +0.099 [+0.095, +0.103] | +0.159 [+0.143, +0.172] |
| layer + fallback − contour-head U-Net, watershed (b) | -0.012 [-0.015, -0.009] | -0.011 [-0.013, -0.008] | +0.010 [+0.008, +0.011] | +0.061 [+0.058, +0.064] | +0.047 [+0.044, +0.049] | -0.004 [-0.007, -0.002] |
| layer + fallback − layer | -0.002 [-0.005, -0.001] | -0.002 [-0.004, +0.000] | +0.000 [+0.000, +0.001] | -0.013 [-0.013, -0.012] | -0.011 [-0.012, -0.010] | -0.001 [-0.001, -0.000] |
| layer, ground-truth markers − layer | +0.151 [+0.146, +0.156] | +0.157 [+0.152, +0.163] | +0.014 [+0.012, +0.016] | +0.170 [+0.167, +0.174] | +0.165 [+0.161, +0.168] | +0.205 [+0.201, +0.209] |
| on the 307 limit patches: PW limit (learned) − layer | -0.015 [-0.017, -0.013] | -0.021 [-0.024, -0.018] | +0.000 [-0.002, +0.002] | -0.007 [-0.010, -0.003] | -0.017 [-0.019, -0.014] | -0.018 [-0.020, -0.017] |
| on the 307 limit patches: PW limit (learned) − PW limit (image costs) | +0.133 [+0.125, +0.141] | +0.276 [+0.259, +0.292] | +0.267 [+0.258, +0.277] | +0.145 [+0.130, +0.159] | +0.212 [+0.199, +0.225] | +0.101 [+0.094, +0.109] |
| on the 307 limit patches: PW limit (learned) − U-Net (sec. 6) logits | -0.024 [-0.031, -0.017] | -0.028 [-0.034, -0.021] | +0.003 [-0.003, +0.009] | +0.124 [+0.109, +0.139] | +0.093 [+0.082, +0.106] | +0.188 [+0.138, +0.233] |

## By crowding (F1@0.5 / PQ / count error)

| patches | n | U-Net (sec. 6) | contour-head U-Net, watershed (b) | layer | layer + fallback | marker watershed, same markers | PW limit (learned, subset) |
|---|---|---|---|---|---|---|---|
| < 10 nuclei | 486 | 0.608 / 0.485 / 0.68 | 0.596 / 0.479 / 0.81 | 0.686 / 0.550 / 0.67 | 0.652 / 0.522 / 0.89 | 0.625 / 0.443 / 0.68 | 0.647 / 0.497 / 0.58 |
| 10–30 | 1383 | 0.691 / 0.563 / 0.18 | 0.719 / 0.591 / 0.27 | 0.798 / 0.653 / 0.17 | 0.782 / 0.639 / 0.21 | 0.743 / 0.536 / 0.17 | 0.786 / 0.630 / 0.17 |
| 30–60 | 525 | 0.650 / 0.524 / 0.15 | 0.733 / 0.596 / 0.15 | 0.800 / 0.648 / 0.10 | 0.790 / 0.639 / 0.12 | 0.730 / 0.517 / 0.10 | 0.778 / 0.617 / 0.10 |
| > 60 | 129 | 0.588 / 0.469 / 0.24 | 0.700 / 0.562 / 0.13 | 0.770 / 0.620 / 0.13 | 0.765 / 0.615 / 0.12 | 0.661 / 0.460 / 0.13 | 0.689 / 0.543 / 0.19 |

## Marker quality by crowding (nuclei with one / none / several markers; background markers per patch)

| patches | one | none | several | bg markers / patch |
|---|---|---|---|---|
| < 10 nuclei | 83.6 % | 13.6 % | 2.8 % | 1.92 |
| 10–30 | 87.0 % | 10.9 % | 2.1 % | 3.77 |
| 30–60 | 84.9 % | 13.3 % | 1.8 % | 5.19 |
| > 60 | 78.7 % | 20.3 % | 0.9 % | 7.49 |
