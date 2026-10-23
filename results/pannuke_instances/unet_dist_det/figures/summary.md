# The fair baseline for the distance-head layer: three-head U-Net + HoVer-Net-style post-processing (fold 1 → fold 2)

Run `results_pannuke_instances/unet_dist_det/unet_dist`: 30 epochs, batch 16, binary foreground target (BCE), edge target ×1.0 on the contour head, distance head ×2.0 (MSE, rmax 12); post-processing: markers = h-maxima h 0.3 of the predicted distance map grown to thr 0.5, min area 9 px, marker watershed of the `both` relief inside s > 0.5, all four chosen by PQ on 300 patches of fold 3.

## Post-processing chosen on fold 3 (300 patches): {'mk_thr': 0.5, 'mk_min_area': 9, 'mk_h': 0.3, 'relief': 'both'}

| setting | PQ | F1@0.5 | AJI | count err. | n_pred | one | none | several | bg / patch |
|---|---|---|---|---|---|---|---|---|---|
| thr=0.5/min_area=9/h=0.3/both | 0.637 | 0.776 | 0.654 | 0.163 | 23.1 | 77.5 % | 18.4 % | 4.1 % | 2.40 |
| thr=0.5/min_area=16/h=0.3/both | 0.636 | 0.773 | 0.648 | 0.170 | 21.5 | 74.0 % | 22.4 % | 3.5 % | 1.88 |
| thr=0.5/min_area=9/h=0.3/contour | 0.635 | 0.775 | 0.652 | 0.163 | 23.1 | 77.5 % | 18.4 % | 4.1 % | 2.40 |
| thr=0.5/min_area=9/h=0.2/both | 0.635 | 0.774 | 0.648 | 0.165 | 22.6 | 75.6 % | 20.0 % | 4.4 % | 2.13 |
| thr=0.5/min_area=16/h=0.3/contour | 0.635 | 0.771 | 0.645 | 0.170 | 21.5 | 74.0 % | 22.4 % | 3.5 % | 1.88 |
| thr=0.5/min_area=9/h=0.2/contour | 0.634 | 0.772 | 0.646 | 0.165 | 22.6 | 75.6 % | 20.0 % | 4.4 % | 2.13 |
| thr=0.4/min_area=16/h=0.3/both | 0.633 | 0.772 | 0.654 | 0.167 | 23.3 | 77.2 % | 18.4 % | 4.4 % | 2.48 |
| thr=0.4/min_area=16/h=0.3/contour | 0.632 | 0.770 | 0.651 | 0.167 | 23.3 | 77.2 % | 18.4 % | 4.4 % | 2.48 |
| thr=0.4/min_area=16/h=0.2/both | 0.631 | 0.768 | 0.642 | 0.177 | 21.8 | 73.5 % | 22.2 % | 4.3 % | 1.90 |
| thr=0.5/min_area=16/h=0.2/both | 0.631 | 0.766 | 0.640 | 0.182 | 20.8 | 72.0 % | 24.4 % | 3.5 % | 1.63 |

(top 10 of 135 settings by PQ)

Best setting per relief, and the layer's own marker setting (thr 0.2 / min area 16 / h 0.2) with each relief:

| setting | PQ | F1@0.5 | AJI | count err. | n_pred |
|---|---|---|---|---|---|
| best contour: thr=0.5/min_area=9/h=0.3/contour | 0.635 | 0.775 | 0.652 | 0.163 | 23.1 |
| best dist: thr=0.5/min_area=16/h=0.3/dist | 0.587 | 0.716 | 0.598 | 0.170 | 21.5 |
| best both: thr=0.5/min_area=9/h=0.3/both | 0.637 | 0.776 | 0.654 | 0.163 | 23.1 |
| thr=0.2/min_area=16/h=0.2/contour | 0.608 | 0.744 | 0.639 | 0.191 | 24.6 |
| thr=0.2/min_area=16/h=0.2/dist | 0.566 | 0.696 | 0.604 | 0.191 | 24.6 |
| thr=0.2/min_area=16/h=0.2/both | 0.609 | 0.746 | 0.642 | 0.191 | 24.6 |

## All of fold 2

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6, binary target), s > 0.5, components | 2523 | 0.719 | 0.652 | 0.769 | 0.807 | 0.577 | 0.656 | 0.531 | 0.809 | 0.656 | 0.494 | 0.275 | 23.0 |
| U-Net + contour head (sec. 10.1, gap target), logits | 2523 | 0.719 | 0.658 | 0.774 | 0.809 | 0.574 | 0.682 | 0.556 | 0.814 | 0.682 | 0.571 | 0.303 | 25.2 |
| U-Net + contour head, tuned marker watershed (sec. 10.1 b) | 2523 | 0.718 | 0.658 | 0.774 | 0.809 | 0.568 | 0.715 | 0.583 | 0.816 | 0.715 | 0.657 | 0.344 | 27.2 |
| `bce_tuned` layer (sec. 11.1) | 2523 | 0.708 | 0.646 | 0.761 | 0.801 | 0.587 | 0.769 | 0.630 | 0.819 | 0.769 | 0.645 | 0.208 | 21.7 |
| `dist` layer, converged (sec. 11.1) | 2523 | 0.621 | 0.555 | 0.665 | 0.742 | 0.549 | 0.658 | 0.510 | 0.774 | 0.658 | 0.569 | 0.318 | 27.5 |
| `dist` layer + fallback markers | 2523 | 0.618 | 0.554 | 0.664 | 0.745 | 0.545 | 0.644 | 0.498 | 0.773 | 0.644 | 0.569 | 0.440 | 29.6 |
| `dist` layer, ground-truth markers (oracle) | 2523 | 0.858 | 0.796 | 0.920 | 0.858 | 0.591 | 0.957 | 0.803 | 0.839 | 0.957 | 0.858 | 0.021 | 23.3 |
| `dist` run: marker watershed of its contour map inside its s > 0.5 (sec. 11 `ws` row) | 2523 | 0.618 | 0.442 | 0.618 | 0.696 | 0.418 | 0.668 | 0.462 | 0.692 | 0.668 | 0.538 | 0.322 | 27.6 |
| this model: s > 0.5, components | 2523 | 0.720 | 0.650 | 0.768 | 0.808 | 0.567 | 0.623 | 0.505 | 0.810 | 0.623 | 0.495 | 0.421 | 26.8 |
| this model: tuned post-processing (markers of the distance head, watershed of the chosen relief) | 2523 | 0.716 | 0.650 | 0.765 | 0.799 | 0.582 | 0.775 | 0.631 | 0.813 | 0.775 | 0.650 | 0.193 | 22.7 |
| this model: markers of the distance head, watershed of the contour map | 2523 | 0.716 | 0.650 | 0.765 | 0.799 | 0.582 | 0.775 | 0.630 | 0.813 | 0.775 | 0.648 | 0.193 | 22.7 |
| this model: markers of the distance head, watershed of −distance | 2523 | 0.716 | 0.650 | 0.765 | 0.799 | 0.582 | 0.723 | 0.587 | 0.812 | 0.723 | 0.607 | 0.193 | 22.7 |
| this model: markers of the distance head, watershed of contour − distance | 2523 | 0.716 | 0.650 | 0.765 | 0.799 | 0.582 | 0.775 | 0.631 | 0.813 | 0.775 | 0.650 | 0.193 | 22.7 |
| this model: tuned post-processing + unmarked components kept | 2523 | 0.721 | 0.651 | 0.768 | 0.807 | 0.569 | 0.761 | 0.616 | 0.809 | 0.761 | 0.654 | 0.243 | 25.3 |
| this model: watershed from the ground-truth markers (oracle) | 2523 | 0.769 | 0.694 | 0.818 | 0.808 | 0.582 | 0.861 | 0.700 | 0.812 | 0.861 | 0.761 | 0.066 | 22.3 |
| this model: sec. 11.1 layer, reproduced (its markers, its solve) | 2523 | 0.621 | 0.555 | 0.665 | 0.742 | 0.549 | 0.658 | 0.510 | 0.774 | 0.658 | 0.569 | 0.318 | 27.5 |
| this model: layer's markers, this model's foreground + watershed | 2523 | 0.720 | 0.654 | 0.770 | 0.804 | 0.576 | 0.744 | 0.600 | 0.807 | 0.744 | 0.643 | 0.253 | 25.9 |
| this model: layer's markers, layer's own foreground + watershed of its maps | 2523 | 0.621 | 0.555 | 0.665 | 0.742 | 0.549 | 0.659 | 0.510 | 0.773 | 0.659 | 0.571 | 0.318 | 27.5 |
| this model: this model's markers, layer's solve | 2523 | 0.579 | 0.515 | 0.621 | 0.705 | 0.555 | 0.644 | 0.495 | 0.769 | 0.644 | 0.545 | 0.192 | 22.3 |
| this model: ground truth instances | 2523 | 1.000 | 1.000 | 1.000 | 1.000 | 0.559 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 23.7 |

## Marker quality (predicted markers against the ground-truth nuclei)

- 59872 nuclei in fold 2 (23.7 per patch).
- this model's markers: one 77.3 %, none 18.4 %, several 4.4 %, background 2.21 per patch, 22.7 markers per patch.
- the `dist` layer's markers (recomputed): one 80.8 %, none 11.5 %, several 7.6 %, background 4.46 per patch, 27.6 markers per patch.
- the `dist` layer's markers (sec. 11.1 run): one 80.8 %, none 11.5 %, several 7.6 %, background 4.46 per patch, 27.6 markers per patch.
- the `bce_tuned` layer's markers: one 77.7 %, none 21.1 %, several 1.2 %, background 2.69 per patch, 21.7 markers per patch.

## Inference cost

- U-Net forward: 1.0 ms per image; post-processing (markers + the three watersheds, one CPU core): 18 ms per image; the layer's converged solve: 74 ms per image (GPU).

## Per tissue type

**Breast**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 749 | 0.722 | 0.596 | 0.756 | 0.780 | 0.585 | 0.690 | 0.547 | 0.794 | 0.690 | 0.550 | 0.198 | 21.2 |
| U-Net + contour head, watershed (b) | 749 | 0.722 | 0.601 | 0.761 | 0.782 | 0.576 | 0.757 | 0.605 | 0.799 | 0.757 | 0.671 | 0.242 | 24.5 |
| `bce_tuned` layer | 749 | 0.716 | 0.594 | 0.752 | 0.780 | 0.598 | 0.805 | 0.644 | 0.800 | 0.805 | 0.659 | 0.145 | 21.2 |
| `dist` layer | 749 | 0.612 | 0.485 | 0.631 | 0.706 | 0.539 | 0.684 | 0.513 | 0.749 | 0.684 | 0.569 | 0.229 | 24.5 |
| `dist` layer, GT markers | 749 | 0.853 | 0.742 | 0.906 | 0.837 | 0.597 | 0.964 | 0.803 | 0.833 | 0.964 | 0.852 | 0.015 | 21.4 |
| s > 0.5, components | 749 | 0.721 | 0.592 | 0.752 | 0.780 | 0.576 | 0.655 | 0.521 | 0.795 | 0.655 | 0.568 | 0.340 | 24.6 |
| tuned post-processing (markers of the distance head, watershed of the chosen relief) | 749 | 0.716 | 0.589 | 0.749 | 0.773 | 0.592 | 0.806 | 0.643 | 0.798 | 0.806 | 0.661 | 0.150 | 21.2 |
| markers of the distance head, watershed of the contour map | 749 | 0.716 | 0.589 | 0.749 | 0.773 | 0.592 | 0.805 | 0.642 | 0.798 | 0.805 | 0.658 | 0.150 | 21.2 |
| markers of the distance head, watershed of −distance | 749 | 0.716 | 0.589 | 0.749 | 0.773 | 0.592 | 0.749 | 0.597 | 0.797 | 0.749 | 0.624 | 0.150 | 21.2 |
| markers of the distance head, watershed of contour − distance | 749 | 0.716 | 0.589 | 0.749 | 0.773 | 0.592 | 0.806 | 0.643 | 0.798 | 0.806 | 0.661 | 0.150 | 21.2 |
| tuned post-processing + unmarked components kept | 749 | 0.721 | 0.591 | 0.751 | 0.779 | 0.579 | 0.789 | 0.627 | 0.795 | 0.789 | 0.664 | 0.188 | 23.3 |
| watershed from the ground-truth markers (oracle) | 749 | 0.761 | 0.624 | 0.792 | 0.780 | 0.591 | 0.875 | 0.698 | 0.798 | 0.875 | 0.757 | 0.056 | 20.6 |
| sec. 11.1 layer, reproduced (its markers, its solve) | 749 | 0.612 | 0.485 | 0.631 | 0.706 | 0.539 | 0.684 | 0.513 | 0.749 | 0.684 | 0.569 | 0.229 | 24.5 |
| layer's markers, this model's foreground + watershed | 749 | 0.719 | 0.593 | 0.753 | 0.776 | 0.586 | 0.778 | 0.617 | 0.793 | 0.778 | 0.651 | 0.193 | 23.4 |
| layer's markers, layer's own foreground + watershed of its maps | 749 | 0.612 | 0.485 | 0.631 | 0.706 | 0.539 | 0.685 | 0.513 | 0.749 | 0.685 | 0.570 | 0.229 | 24.5 |
| this model's markers, layer's solve | 749 | 0.572 | 0.445 | 0.587 | 0.675 | 0.536 | 0.670 | 0.497 | 0.743 | 0.670 | 0.549 | 0.152 | 20.9 |
| ground truth instances | 749 | 1.000 | 1.000 | 1.000 | 1.000 | 0.553 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 21.7 |

**Colon**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 468 | 0.698 | 0.617 | 0.738 | 0.788 | 0.558 | 0.547 | 0.431 | 0.787 | 0.547 | 0.349 | 0.274 | 21.1 |
| U-Net + contour head, watershed (b) | 468 | 0.691 | 0.621 | 0.742 | 0.788 | 0.550 | 0.630 | 0.497 | 0.789 | 0.630 | 0.574 | 0.340 | 27.7 |
| `bce_tuned` layer | 468 | 0.685 | 0.606 | 0.728 | 0.781 | 0.573 | 0.693 | 0.551 | 0.796 | 0.693 | 0.576 | 0.216 | 21.7 |
| `dist` layer | 468 | 0.580 | 0.509 | 0.620 | 0.715 | 0.527 | 0.535 | 0.402 | 0.751 | 0.535 | 0.483 | 0.380 | 30.4 |
| `dist` layer, GT markers | 468 | 0.851 | 0.775 | 0.907 | 0.851 | 0.569 | 0.935 | 0.767 | 0.820 | 0.935 | 0.841 | 0.023 | 24.8 |
| s > 0.5, components | 468 | 0.703 | 0.616 | 0.738 | 0.792 | 0.545 | 0.522 | 0.412 | 0.788 | 0.522 | 0.325 | 0.390 | 25.7 |
| tuned post-processing (markers of the distance head, watershed of the chosen relief) | 468 | 0.698 | 0.613 | 0.733 | 0.784 | 0.563 | 0.687 | 0.539 | 0.784 | 0.687 | 0.572 | 0.211 | 23.8 |
| markers of the distance head, watershed of the contour map | 468 | 0.698 | 0.613 | 0.733 | 0.784 | 0.563 | 0.685 | 0.537 | 0.784 | 0.685 | 0.567 | 0.211 | 23.8 |
| markers of the distance head, watershed of −distance | 468 | 0.698 | 0.613 | 0.733 | 0.784 | 0.563 | 0.618 | 0.485 | 0.784 | 0.618 | 0.517 | 0.211 | 23.8 |
| markers of the distance head, watershed of contour − distance | 468 | 0.698 | 0.613 | 0.733 | 0.784 | 0.563 | 0.687 | 0.539 | 0.784 | 0.687 | 0.572 | 0.211 | 23.8 |
| tuned post-processing + unmarked components kept | 468 | 0.703 | 0.617 | 0.738 | 0.791 | 0.548 | 0.674 | 0.526 | 0.780 | 0.674 | 0.576 | 0.268 | 26.5 |
| watershed from the ground-truth markers (oracle) | 468 | 0.743 | 0.652 | 0.780 | 0.792 | 0.557 | 0.814 | 0.639 | 0.785 | 0.814 | 0.713 | 0.072 | 23.6 |
| sec. 11.1 layer, reproduced (its markers, its solve) | 468 | 0.580 | 0.509 | 0.620 | 0.715 | 0.527 | 0.535 | 0.402 | 0.751 | 0.535 | 0.483 | 0.380 | 30.4 |
| layer's markers, this model's foreground + watershed | 468 | 0.701 | 0.617 | 0.738 | 0.788 | 0.556 | 0.643 | 0.500 | 0.778 | 0.643 | 0.567 | 0.315 | 28.5 |
| layer's markers, layer's own foreground + watershed of its maps | 468 | 0.580 | 0.509 | 0.620 | 0.715 | 0.527 | 0.535 | 0.401 | 0.750 | 0.535 | 0.484 | 0.380 | 30.4 |
| this model's markers, layer's solve | 468 | 0.526 | 0.457 | 0.561 | 0.674 | 0.544 | 0.519 | 0.386 | 0.744 | 0.519 | 0.450 | 0.214 | 23.3 |
| ground truth instances | 468 | 1.000 | 1.000 | 1.000 | 1.000 | 0.539 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 25.4 |

**HeadNeck**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 169 | 0.672 | 0.658 | 0.744 | 0.835 | 0.648 | 0.640 | 0.519 | 0.811 | 0.640 | 0.556 | 0.424 | 20.2 |
| U-Net + contour head, watershed (b) | 169 | 0.682 | 0.675 | 0.756 | 0.839 | 0.638 | 0.688 | 0.565 | 0.821 | 0.688 | 0.660 | 0.474 | 23.6 |
| `bce_tuned` layer | 169 | 0.682 | 0.681 | 0.751 | 0.815 | 0.633 | 0.753 | 0.624 | 0.829 | 0.753 | 0.640 | 0.210 | 16.6 |
| `dist` layer | 169 | 0.614 | 0.614 | 0.687 | 0.792 | 0.632 | 0.624 | 0.489 | 0.784 | 0.624 | 0.553 | 0.362 | 23.2 |
| `dist` layer, GT markers | 169 | 0.852 | 0.844 | 0.927 | 0.882 | 0.646 | 0.964 | 0.818 | 0.849 | 0.964 | 0.862 | 0.036 | 18.2 |
| s > 0.5, components | 169 | 0.683 | 0.671 | 0.752 | 0.836 | 0.630 | 0.596 | 0.486 | 0.814 | 0.596 | 0.556 | 0.628 | 23.8 |
| tuned post-processing (markers of the distance head, watershed of the chosen relief) | 169 | 0.691 | 0.685 | 0.759 | 0.823 | 0.637 | 0.763 | 0.625 | 0.820 | 0.763 | 0.646 | 0.194 | 18.4 |
| markers of the distance head, watershed of the contour map | 169 | 0.691 | 0.685 | 0.759 | 0.823 | 0.637 | 0.761 | 0.624 | 0.821 | 0.761 | 0.646 | 0.194 | 18.4 |
| markers of the distance head, watershed of −distance | 169 | 0.691 | 0.685 | 0.759 | 0.823 | 0.637 | 0.721 | 0.588 | 0.815 | 0.721 | 0.613 | 0.194 | 18.4 |
| markers of the distance head, watershed of contour − distance | 169 | 0.691 | 0.685 | 0.759 | 0.823 | 0.637 | 0.763 | 0.625 | 0.820 | 0.763 | 0.646 | 0.194 | 18.4 |
| tuned post-processing + unmarked components kept | 169 | 0.689 | 0.678 | 0.757 | 0.835 | 0.629 | 0.741 | 0.604 | 0.816 | 0.741 | 0.651 | 0.294 | 21.1 |
| watershed from the ground-truth markers (oracle) | 169 | 0.760 | 0.746 | 0.833 | 0.836 | 0.637 | 0.853 | 0.699 | 0.819 | 0.853 | 0.758 | 0.091 | 17.3 |
| sec. 11.1 layer, reproduced (its markers, its solve) | 169 | 0.614 | 0.614 | 0.687 | 0.792 | 0.632 | 0.624 | 0.489 | 0.784 | 0.624 | 0.553 | 0.362 | 23.2 |
| layer's markers, this model's foreground + watershed | 169 | 0.694 | 0.685 | 0.763 | 0.832 | 0.635 | 0.725 | 0.589 | 0.812 | 0.725 | 0.637 | 0.262 | 21.4 |
| layer's markers, layer's own foreground + watershed of its maps | 169 | 0.614 | 0.614 | 0.687 | 0.792 | 0.632 | 0.625 | 0.489 | 0.782 | 0.625 | 0.553 | 0.362 | 23.2 |
| this model's markers, layer's solve | 169 | 0.595 | 0.593 | 0.664 | 0.750 | 0.637 | 0.605 | 0.469 | 0.776 | 0.605 | 0.523 | 0.182 | 17.9 |
| ground truth instances | 169 | 1.000 | 1.000 | 1.000 | 1.000 | 0.629 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 18.5 |

**Adrenal_gland**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 148 | 0.716 | 0.676 | 0.774 | 0.808 | 0.554 | 0.694 | 0.582 | 0.840 | 0.694 | 0.655 | 0.378 | 18.4 |
| U-Net + contour head, watershed (b) | 148 | 0.719 | 0.689 | 0.783 | 0.811 | 0.551 | 0.712 | 0.605 | 0.850 | 0.712 | 0.713 | 0.444 | 20.1 |
| `bce_tuned` layer | 148 | 0.716 | 0.693 | 0.785 | 0.816 | 0.571 | 0.808 | 0.688 | 0.852 | 0.808 | 0.694 | 0.246 | 15.7 |
| `dist` layer | 148 | 0.628 | 0.590 | 0.679 | 0.754 | 0.537 | 0.690 | 0.553 | 0.801 | 0.690 | 0.618 | 0.339 | 18.5 |
| `dist` layer, GT markers | 148 | 0.864 | 0.827 | 0.929 | 0.865 | 0.582 | 0.958 | 0.831 | 0.868 | 0.958 | 0.871 | 0.024 | 15.7 |
| s > 0.5, components | 148 | 0.717 | 0.674 | 0.774 | 0.810 | 0.543 | 0.665 | 0.555 | 0.836 | 0.665 | 0.660 | 0.489 | 20.5 |
| tuned post-processing (markers of the distance head, watershed of the chosen relief) | 148 | 0.708 | 0.672 | 0.767 | 0.797 | 0.567 | 0.804 | 0.680 | 0.846 | 0.804 | 0.696 | 0.220 | 15.2 |
| markers of the distance head, watershed of the contour map | 148 | 0.708 | 0.672 | 0.767 | 0.797 | 0.567 | 0.804 | 0.680 | 0.846 | 0.804 | 0.695 | 0.220 | 15.2 |
| markers of the distance head, watershed of −distance | 148 | 0.708 | 0.672 | 0.767 | 0.797 | 0.567 | 0.776 | 0.654 | 0.843 | 0.776 | 0.673 | 0.220 | 15.2 |
| markers of the distance head, watershed of contour − distance | 148 | 0.708 | 0.672 | 0.767 | 0.797 | 0.567 | 0.804 | 0.680 | 0.846 | 0.804 | 0.696 | 0.220 | 15.2 |
| tuned post-processing + unmarked components kept | 148 | 0.717 | 0.676 | 0.775 | 0.808 | 0.546 | 0.781 | 0.656 | 0.840 | 0.781 | 0.700 | 0.255 | 17.2 |
| watershed from the ground-truth markers (oracle) | 148 | 0.767 | 0.721 | 0.829 | 0.810 | 0.562 | 0.860 | 0.726 | 0.844 | 0.860 | 0.779 | 0.089 | 14.7 |
| sec. 11.1 layer, reproduced (its markers, its solve) | 148 | 0.628 | 0.590 | 0.679 | 0.754 | 0.537 | 0.690 | 0.553 | 0.801 | 0.690 | 0.618 | 0.339 | 18.5 |
| layer's markers, this model's foreground + watershed | 148 | 0.715 | 0.680 | 0.778 | 0.806 | 0.556 | 0.779 | 0.652 | 0.836 | 0.779 | 0.687 | 0.264 | 16.9 |
| layer's markers, layer's own foreground + watershed of its maps | 148 | 0.628 | 0.590 | 0.679 | 0.754 | 0.537 | 0.690 | 0.553 | 0.801 | 0.690 | 0.618 | 0.339 | 18.5 |
| this model's markers, layer's solve | 148 | 0.595 | 0.551 | 0.641 | 0.715 | 0.554 | 0.694 | 0.552 | 0.795 | 0.694 | 0.602 | 0.221 | 14.7 |
| ground truth instances | 148 | 1.000 | 1.000 | 1.000 | 1.000 | 0.557 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 16.0 |

## Paired per-patch differences (2523 patches; bootstrap 95 % intervals; F1 / PQ / AJI dataset-level, bootstrapped over patches)

| comparison | IoU | BF₂ | edge align. | F1@0.5 | PQ | AJI |
|---|---|---|---|---|---|---|
| this model's post-processing − `dist` layer | +0.096 [+0.092, +0.100] | +0.099 [+0.095, +0.104] | +0.035 [+0.033, +0.037] | +0.117 [+0.112, +0.123] | +0.121 [+0.117, +0.126] | +0.081 [+0.078, +0.084] |
| this model's post-processing − `bce_tuned` layer | +0.009 [+0.006, +0.012] | +0.004 [+0.001, +0.007] | -0.006 [-0.008, -0.004] | +0.007 [+0.003, +0.010] | +0.001 [-0.002, +0.004] | +0.005 [+0.001, +0.008] |
| this model's post-processing − contour-head U-Net, watershed (b) | -0.002 [-0.004, +0.002] | -0.010 [-0.013, -0.006] | +0.014 [+0.013, +0.016] | +0.060 [+0.057, +0.064] | +0.048 [+0.045, +0.051] | -0.007 [-0.010, -0.004] |
| this model's post-processing − U-Net (sec. 6) logits | -0.002 [-0.005, +0.001] | -0.005 [-0.008, -0.001] | +0.005 [+0.003, +0.007] | +0.119 [+0.114, +0.125] | +0.100 [+0.096, +0.104] | +0.156 [+0.140, +0.170] |
| this model's post-processing − this model's logits | -0.004 [-0.006, -0.001] | -0.003 [-0.006, -0.001] | +0.016 [+0.014, +0.017] | +0.152 [+0.147, +0.157] | +0.126 [+0.122, +0.130] | +0.156 [+0.132, +0.186] |
| watershed of −distance − watershed of the contour map (same markers) | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.052 [-0.056, -0.049] | -0.044 [-0.046, -0.041] | -0.041 [-0.045, -0.037] |
| watershed of contour − distance − watershed of the contour map (same markers) | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.001 [+0.000, +0.001] | +0.001 [+0.000, +0.001] | +0.002 [+0.002, +0.003] |
| + unmarked components kept − this model's post-processing | +0.005 [+0.003, +0.006] | +0.004 [+0.002, +0.006] | -0.013 [-0.014, -0.012] | -0.015 [-0.016, -0.013] | -0.015 [-0.016, -0.014] | +0.004 [+0.003, +0.004] |
| ground-truth markers (oracle) − this model's post-processing | +0.052 [+0.048, +0.056] | +0.054 [+0.050, +0.058] | +0.002 [-0.000, +0.004] | +0.086 [+0.082, +0.090] | +0.069 [+0.066, +0.072] | +0.111 [+0.107, +0.114] |
| this model's oracle − `dist` layer's oracle | -0.089 [-0.092, -0.086] | -0.102 [-0.105, -0.098] | -0.008 [-0.010, -0.006] | -0.095 [-0.098, -0.092] | -0.103 [-0.106, -0.101] | -0.097 [-0.099, -0.094] |
| layer reproduced − `dist` layer (sanity) | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| layer's markers, this model's watershed − `dist` layer (same markers: watershed vs solve) | +0.099 [+0.096, +0.103] | +0.105 [+0.101, +0.109] | +0.029 [+0.027, +0.031] | +0.085 [+0.081, +0.090] | +0.091 [+0.087, +0.094] | +0.074 [+0.071, +0.076] |
| layer's markers, layer's own foreground + watershed − `dist` layer (same markers, same foreground) | -0.000 [-0.000, +0.000] | -0.000 [-0.000, +0.000] | -0.000 [-0.000, +0.000] | +0.001 [-0.000, +0.001] | +0.000 [-0.000, +0.000] | +0.001 [+0.001, +0.001] |
| this model's markers, layer's solve − this model's post-processing (same markers: solve vs watershed) | -0.138 [-0.141, -0.134] | -0.144 [-0.148, -0.140] | -0.027 [-0.030, -0.025] | -0.131 [-0.136, -0.126] | -0.135 [-0.140, -0.131] | -0.105 [-0.108, -0.102] |
| this model's markers, layer's solve − `dist` layer (same solve: markers swapped) | -0.042 [-0.045, -0.038] | -0.045 [-0.048, -0.041] | +0.008 [+0.006, +0.010] | -0.014 [-0.017, -0.011] | -0.014 [-0.016, -0.012] | -0.024 [-0.026, -0.023] |
| layer's markers, this model's watershed − this model's post-processing (same watershed: markers swapped) | +0.004 [+0.001, +0.006] | +0.006 [+0.003, +0.008] | -0.006 [-0.007, -0.005] | -0.032 [-0.034, -0.029] | -0.031 [-0.032, -0.029] | -0.007 [-0.009, -0.005] |

## By crowding (F1@0.5 / PQ / count error)

| patches | n | U-Net (sec. 6) | contour-head U-Net, watershed (b) | `dist` layer | this model: post-processing | + unmarked kept | oracle markers | layer's markers, watershed | this model's markers, layer's solve |
|---|---|---|---|---|---|---|---|---|---|
| < 10 nuclei | 486 | 0.608 / 0.485 / 0.68 | 0.596 / 0.479 / 0.81 | 0.531 / 0.401 / 0.70 | 0.683 / 0.548 / 0.41 | 0.643 / 0.511 / 0.58 | 0.818 / 0.657 / 0.09 | 0.641 / 0.509 / 0.54 | 0.530 / 0.397 / 0.40 |
| 10–30 | 1383 | 0.691 / 0.563 / 0.18 | 0.719 / 0.591 / 0.27 | 0.634 / 0.489 / 0.25 | 0.780 / 0.639 / 0.15 | 0.759 / 0.619 / 0.19 | 0.866 / 0.711 / 0.06 | 0.739 / 0.600 / 0.21 | 0.626 / 0.478 / 0.15 |
| 30–60 | 525 | 0.650 / 0.524 / 0.15 | 0.733 / 0.596 / 0.15 | 0.670 / 0.518 / 0.18 | 0.785 / 0.636 / 0.12 | 0.774 / 0.625 / 0.12 | 0.866 / 0.703 / 0.06 | 0.755 / 0.608 / 0.14 | 0.651 / 0.498 / 0.12 |
| > 60 | 129 | 0.588 / 0.469 / 0.24 | 0.700 / 0.562 / 0.13 | 0.724 / 0.570 / 0.13 | 0.765 / 0.616 / 0.16 | 0.767 / 0.613 / 0.11 | 0.850 / 0.677 / 0.06 | 0.756 / 0.605 / 0.12 | 0.701 / 0.552 / 0.16 |

## Marker quality by crowding (nuclei with one / none / several markers; background markers per patch)

| patches | this model: one | none | several | bg / patch | `dist` layer: one | none | several | bg / patch |
|---|---|---|---|---|---|---|---|---|
| < 10 nuclei | 69.8 % | 23.9 % | 6.3 % | 0.87 | 76.2 % | 13.8 % | 10.0 % | 1.82 |
| 10–30 | 78.2 % | 16.6 % | 5.1 % | 2.04 | 80.2 % | 10.4 % | 9.3 % | 3.96 |
| 30–60 | 78.1 % | 17.6 % | 4.3 % | 3.22 | 81.6 % | 11.1 % | 7.3 % | 6.27 |
| > 60 | 74.9 % | 22.7 % | 2.4 % | 4.91 | 81.7 % | 14.5 % | 3.9 % | 12.33 |

## Per tissue (IoU / F1 / PQ): this model's post-processing vs the `dist` layer vs watershed (b)

- Adrenal_gland (148): 0.708 / 0.804 / 0.680 vs 0.628 / 0.690 / 0.553 vs 0.719 / 0.712 / 0.605
- Bile-duct (103): 0.726 / 0.811 / 0.682 vs 0.640 / 0.707 / 0.564 vs 0.729 / 0.757 / 0.640
- Bladder (61): 0.722 / 0.816 / 0.692 vs 0.662 / 0.728 / 0.587 vs 0.723 / 0.732 / 0.618
- Breast (749): 0.716 / 0.806 / 0.643 vs 0.612 / 0.684 / 0.513 vs 0.722 / 0.757 / 0.605
- Cervix (52): 0.770 / 0.805 / 0.662 vs 0.707 / 0.700 / 0.545 vs 0.776 / 0.764 / 0.631
- Colon (468): 0.698 / 0.687 / 0.539 vs 0.580 / 0.535 / 0.402 vs 0.691 / 0.630 / 0.497
- Esophagus (128): 0.720 / 0.769 / 0.634 vs 0.618 / 0.624 / 0.481 vs 0.728 / 0.689 / 0.569
- HeadNeck (169): 0.691 / 0.763 / 0.625 vs 0.614 / 0.624 / 0.489 vs 0.682 / 0.688 / 0.565
- Kidney (56): 0.772 / 0.836 / 0.686 vs 0.709 / 0.794 / 0.638 vs 0.753 / 0.741 / 0.608
- Liver (66): 0.764 / 0.819 / 0.694 vs 0.689 / 0.741 / 0.601 vs 0.780 / 0.768 / 0.649
- Lung (53): 0.673 / 0.725 / 0.582 vs 0.612 / 0.698 / 0.536 vs 0.693 / 0.679 / 0.540
- Pancreatic (89): 0.746 / 0.791 / 0.652 vs 0.647 / 0.663 / 0.516 vs 0.749 / 0.732 / 0.608
- Skin (87): 0.644 / 0.791 / 0.657 vs 0.554 / 0.694 / 0.558 vs 0.640 / 0.722 / 0.601
- Testis (79): 0.763 / 0.816 / 0.686 vs 0.664 / 0.699 / 0.560 vs 0.766 / 0.761 / 0.642
- Thyroid (84): 0.739 / 0.817 / 0.692 vs 0.663 / 0.726 / 0.594 vs 0.729 / 0.759 / 0.646
