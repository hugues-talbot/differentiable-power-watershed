# The fair baseline for the distance-head layer: three-head U-Net + HoVer-Net-style post-processing (fold 1 → fold 2)

Run `results_pannuke_instances/unet_dist_peakgrad/unet_dist`: 30 epochs, batch 16, binary foreground target (BCE), edge target ×1.0 on the contour head, distance head ×2.0 (MSE, rmax 12); post-processing: markers = h-maxima h 0.3 of the predicted distance map grown to thr 0.5, min area 16 px, marker watershed of the `both` relief inside s > 0.5, all four chosen by PQ on 300 patches of fold 3.

## Post-processing chosen on fold 3 (300 patches): {'mk_thr': 0.5, 'mk_min_area': 16, 'mk_h': 0.3, 'relief': 'both'}

| setting | PQ | F1@0.5 | AJI | count err. | n_pred | one | none | several | bg / patch |
|---|---|---|---|---|---|---|---|---|---|
| thr=0.5/min_area=16/h=0.3/both | 0.636 | 0.773 | 0.683 | 0.188 | 25.8 | 87.3 % | 8.7 % | 4.0 % | 6.75 |
| thr=0.5/min_area=16/h=0.3/contour | 0.636 | 0.773 | 0.683 | 0.188 | 25.8 | 87.3 % | 8.7 % | 4.0 % | 6.75 |
| thr=0.5/min_area=9/h=0.3/both | 0.636 | 0.773 | 0.683 | 0.199 | 26.2 | 88.6 % | 7.1 % | 4.3 % | 8.19 |
| thr=0.5/min_area=16/h=0.3/dist | 0.636 | 0.772 | 0.683 | 0.188 | 25.8 | 87.3 % | 8.7 % | 4.0 % | 6.75 |
| thr=0.5/min_area=9/h=0.3/contour | 0.635 | 0.773 | 0.683 | 0.199 | 26.2 | 88.6 % | 7.1 % | 4.3 % | 8.19 |
| thr=0.5/min_area=9/h=0.3/dist | 0.635 | 0.772 | 0.683 | 0.199 | 26.2 | 88.6 % | 7.1 % | 4.3 % | 8.19 |
| thr=0.5/min_area=4/h=0.3/both | 0.634 | 0.772 | 0.683 | 0.203 | 26.3 | 89.1 % | 6.4 % | 4.5 % | 9.29 |
| thr=0.5/min_area=4/h=0.3/contour | 0.634 | 0.771 | 0.683 | 0.203 | 26.3 | 89.1 % | 6.4 % | 4.5 % | 9.29 |
| thr=0.5/min_area=4/h=0.3/dist | 0.634 | 0.771 | 0.683 | 0.203 | 26.3 | 89.1 % | 6.4 % | 4.5 % | 9.29 |
| thr=0.4/min_area=16/h=0.3/both | 0.633 | 0.770 | 0.683 | 0.203 | 26.2 | 88.0 % | 7.7 % | 4.3 % | 7.94 |

(top 10 of 135 settings by PQ)

Best setting per relief, and the layer's own marker setting (thr 0.2 / min area 16 / h 0.2) with each relief:

| setting | PQ | F1@0.5 | AJI | count err. | n_pred |
|---|---|---|---|---|---|
| best contour: thr=0.5/min_area=16/h=0.3/contour | 0.636 | 0.773 | 0.683 | 0.188 | 25.8 |
| best dist: thr=0.5/min_area=16/h=0.3/dist | 0.636 | 0.772 | 0.683 | 0.188 | 25.8 |
| best both: thr=0.5/min_area=16/h=0.3/both | 0.636 | 0.773 | 0.683 | 0.188 | 25.8 |
| thr=0.2/min_area=16/h=0.2/contour | 0.617 | 0.752 | 0.677 | 0.253 | 27.5 |
| thr=0.2/min_area=16/h=0.2/dist | 0.617 | 0.752 | 0.677 | 0.253 | 27.5 |
| thr=0.2/min_area=16/h=0.2/both | 0.617 | 0.752 | 0.677 | 0.253 | 27.5 |

## All of fold 2

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6, binary target), s > 0.5, components | 2523 | 0.719 | 0.652 | 0.769 | 0.807 | 0.577 | 0.656 | 0.531 | 0.809 | 0.656 | 0.494 | 0.275 | 23.0 |
| U-Net + contour head (sec. 10.1, gap target), logits | 2523 | 0.719 | 0.658 | 0.774 | 0.809 | 0.574 | 0.682 | 0.556 | 0.814 | 0.682 | 0.571 | 0.303 | 25.2 |
| U-Net + contour head, tuned marker watershed (sec. 10.1 b) | 2523 | 0.718 | 0.658 | 0.774 | 0.809 | 0.568 | 0.715 | 0.583 | 0.816 | 0.715 | 0.657 | 0.344 | 27.2 |
| `bce_tuned` layer (sec. 11.1) | 2523 | 0.708 | 0.646 | 0.761 | 0.801 | 0.587 | 0.769 | 0.630 | 0.819 | 0.769 | 0.645 | 0.208 | 21.7 |
| `dist` layer, converged (sec. 11.1) | 2523 | 0.677 | 0.610 | 0.724 | 0.806 | 0.550 | 0.717 | 0.572 | 0.798 | 0.717 | 0.623 | 0.632 | 32.0 |
| `dist` layer + fallback markers | 2523 | 0.677 | 0.610 | 0.724 | 0.806 | 0.550 | 0.711 | 0.567 | 0.798 | 0.711 | 0.623 | 0.672 | 32.6 |
| `dist` layer, ground-truth markers (oracle) | 2523 | 0.859 | 0.795 | 0.922 | 0.858 | 0.591 | 0.959 | 0.805 | 0.839 | 0.959 | 0.858 | 0.020 | 23.3 |
| `dist` run: marker watershed of its contour map inside its s > 0.5 (sec. 11 `ws` row) | 2523 | 0.620 | 0.431 | 0.607 | 0.709 | 0.414 | 0.632 | 0.444 | 0.703 | 0.632 | 0.563 | 0.714 | 32.9 |
| this model: s > 0.5, components | 2523 | 0.724 | 0.659 | 0.776 | 0.812 | 0.572 | 0.654 | 0.531 | 0.812 | 0.654 | 0.493 | 0.333 | 24.8 |
| this model: tuned post-processing (markers of the distance head, watershed of the chosen relief) | 2523 | 0.725 | 0.660 | 0.776 | 0.810 | 0.573 | 0.768 | 0.627 | 0.817 | 0.768 | 0.676 | 0.221 | 25.4 |
| this model: markers of the distance head, watershed of the contour map | 2523 | 0.725 | 0.660 | 0.776 | 0.810 | 0.573 | 0.768 | 0.627 | 0.817 | 0.768 | 0.676 | 0.221 | 25.4 |
| this model: markers of the distance head, watershed of −distance | 2523 | 0.725 | 0.660 | 0.776 | 0.810 | 0.573 | 0.768 | 0.627 | 0.817 | 0.768 | 0.676 | 0.221 | 25.4 |
| this model: markers of the distance head, watershed of contour − distance | 2523 | 0.725 | 0.660 | 0.776 | 0.810 | 0.573 | 0.768 | 0.627 | 0.817 | 0.768 | 0.676 | 0.221 | 25.4 |
| this model: tuned post-processing + unmarked components kept | 2523 | 0.725 | 0.660 | 0.776 | 0.811 | 0.572 | 0.764 | 0.624 | 0.816 | 0.764 | 0.677 | 0.249 | 26.1 |
| this model: watershed from the ground-truth markers (oracle) | 2523 | 0.773 | 0.702 | 0.825 | 0.812 | 0.586 | 0.867 | 0.707 | 0.815 | 0.867 | 0.765 | 0.067 | 22.2 |
| this model: sec. 11.1 layer, reproduced (its markers, its solve) | 2523 | 0.677 | 0.610 | 0.724 | 0.806 | 0.550 | 0.717 | 0.572 | 0.798 | 0.717 | 0.623 | 0.632 | 32.0 |
| this model: layer's markers, this model's foreground + watershed | 2523 | 0.725 | 0.661 | 0.777 | 0.811 | 0.573 | 0.750 | 0.610 | 0.814 | 0.750 | 0.664 | 0.275 | 26.8 |
| this model: layer's markers, layer's own foreground + watershed of its maps | 2523 | 0.677 | 0.610 | 0.724 | 0.806 | 0.550 | 0.717 | 0.572 | 0.798 | 0.717 | 0.623 | 0.632 | 32.0 |
| this model: this model's markers, layer's solve | 2523 | 0.650 | 0.572 | 0.685 | 0.766 | 0.536 | 0.721 | 0.561 | 0.778 | 0.721 | 0.613 | 0.370 | 28.4 |
| this model: ground truth instances | 2523 | 1.000 | 1.000 | 1.000 | 1.000 | 0.559 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 23.7 |

## Marker quality (predicted markers against the ground-truth nuclei)

- 59872 nuclei in fold 2 (23.7 per patch).
- this model's markers: one 86.6 %, none 9.1 %, several 4.3 %, background 6.49 per patch, 29.2 markers per patch.
- the `dist` layer's markers (recomputed): one 86.4 %, none 7.5 %, several 6.2 %, background 9.28 per patch, 32.9 markers per patch.
- the `dist` layer's markers (sec. 11.1 run): one 86.4 %, none 7.5 %, several 6.2 %, background 9.28 per patch, 32.9 markers per patch.
- the `bce_tuned` layer's markers: one 77.7 %, none 21.1 %, several 1.2 %, background 2.69 per patch, 21.7 markers per patch.

## Inference cost

- U-Net forward: 0.9 ms per image; post-processing (markers + the three watersheds, one CPU core): 16 ms per image; the layer's converged solve: 98 ms per image (GPU).

## Per tissue type

**Breast**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 749 | 0.722 | 0.596 | 0.756 | 0.780 | 0.585 | 0.690 | 0.547 | 0.794 | 0.690 | 0.550 | 0.198 | 21.2 |
| U-Net + contour head, watershed (b) | 749 | 0.722 | 0.601 | 0.761 | 0.782 | 0.576 | 0.757 | 0.605 | 0.799 | 0.757 | 0.671 | 0.242 | 24.5 |
| `bce_tuned` layer | 749 | 0.716 | 0.594 | 0.752 | 0.780 | 0.598 | 0.805 | 0.644 | 0.800 | 0.805 | 0.659 | 0.145 | 21.2 |
| `dist` layer | 749 | 0.684 | 0.555 | 0.710 | 0.772 | 0.557 | 0.752 | 0.587 | 0.780 | 0.752 | 0.634 | 0.462 | 28.5 |
| `dist` layer, GT markers | 749 | 0.854 | 0.743 | 0.909 | 0.837 | 0.596 | 0.967 | 0.806 | 0.833 | 0.967 | 0.852 | 0.015 | 21.4 |
| s > 0.5, components | 749 | 0.723 | 0.599 | 0.759 | 0.783 | 0.583 | 0.686 | 0.546 | 0.796 | 0.686 | 0.571 | 0.264 | 22.7 |
| tuned post-processing (markers of the distance head, watershed of the chosen relief) | 749 | 0.724 | 0.599 | 0.759 | 0.782 | 0.583 | 0.801 | 0.641 | 0.800 | 0.801 | 0.685 | 0.166 | 23.3 |
| markers of the distance head, watershed of the contour map | 749 | 0.724 | 0.599 | 0.759 | 0.782 | 0.583 | 0.801 | 0.641 | 0.800 | 0.801 | 0.684 | 0.166 | 23.3 |
| markers of the distance head, watershed of −distance | 749 | 0.724 | 0.599 | 0.759 | 0.782 | 0.583 | 0.801 | 0.641 | 0.800 | 0.801 | 0.685 | 0.166 | 23.3 |
| markers of the distance head, watershed of contour − distance | 749 | 0.724 | 0.599 | 0.759 | 0.782 | 0.583 | 0.801 | 0.641 | 0.800 | 0.801 | 0.685 | 0.166 | 23.3 |
| tuned post-processing + unmarked components kept | 749 | 0.724 | 0.599 | 0.759 | 0.783 | 0.582 | 0.796 | 0.637 | 0.800 | 0.796 | 0.685 | 0.187 | 23.8 |
| watershed from the ground-truth markers (oracle) | 749 | 0.765 | 0.631 | 0.799 | 0.783 | 0.595 | 0.885 | 0.707 | 0.799 | 0.885 | 0.761 | 0.056 | 20.6 |
| sec. 11.1 layer, reproduced (its markers, its solve) | 749 | 0.684 | 0.555 | 0.710 | 0.772 | 0.557 | 0.752 | 0.587 | 0.780 | 0.752 | 0.634 | 0.462 | 28.5 |
| layer's markers, this model's foreground + watershed | 749 | 0.724 | 0.600 | 0.760 | 0.783 | 0.583 | 0.784 | 0.626 | 0.798 | 0.784 | 0.673 | 0.209 | 24.3 |
| layer's markers, layer's own foreground + watershed of its maps | 749 | 0.684 | 0.555 | 0.710 | 0.772 | 0.557 | 0.752 | 0.586 | 0.780 | 0.752 | 0.634 | 0.462 | 28.5 |
| this model's markers, layer's solve | 749 | 0.641 | 0.502 | 0.650 | 0.728 | 0.528 | 0.742 | 0.558 | 0.752 | 0.742 | 0.613 | 0.283 | 25.8 |
| ground truth instances | 749 | 1.000 | 1.000 | 1.000 | 1.000 | 0.553 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 21.7 |

**Colon**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 468 | 0.698 | 0.617 | 0.738 | 0.788 | 0.558 | 0.547 | 0.431 | 0.787 | 0.547 | 0.349 | 0.274 | 21.1 |
| U-Net + contour head, watershed (b) | 468 | 0.691 | 0.621 | 0.742 | 0.788 | 0.550 | 0.630 | 0.497 | 0.789 | 0.630 | 0.574 | 0.340 | 27.7 |
| `bce_tuned` layer | 468 | 0.685 | 0.606 | 0.728 | 0.781 | 0.573 | 0.693 | 0.551 | 0.796 | 0.693 | 0.576 | 0.216 | 21.7 |
| `dist` layer | 468 | 0.651 | 0.566 | 0.685 | 0.785 | 0.534 | 0.628 | 0.484 | 0.771 | 0.628 | 0.547 | 0.609 | 34.2 |
| `dist` layer, GT markers | 468 | 0.849 | 0.770 | 0.905 | 0.850 | 0.569 | 0.939 | 0.769 | 0.819 | 0.939 | 0.840 | 0.023 | 24.9 |
| s > 0.5, components | 468 | 0.706 | 0.625 | 0.747 | 0.794 | 0.553 | 0.547 | 0.433 | 0.791 | 0.547 | 0.314 | 0.312 | 23.4 |
| tuned post-processing (markers of the distance head, watershed of the chosen relief) | 468 | 0.706 | 0.625 | 0.747 | 0.793 | 0.553 | 0.675 | 0.532 | 0.788 | 0.675 | 0.602 | 0.259 | 27.7 |
| markers of the distance head, watershed of the contour map | 468 | 0.706 | 0.625 | 0.747 | 0.793 | 0.553 | 0.675 | 0.532 | 0.788 | 0.675 | 0.602 | 0.259 | 27.7 |
| markers of the distance head, watershed of −distance | 468 | 0.706 | 0.625 | 0.747 | 0.793 | 0.553 | 0.674 | 0.531 | 0.788 | 0.674 | 0.601 | 0.259 | 27.7 |
| markers of the distance head, watershed of contour − distance | 468 | 0.706 | 0.625 | 0.747 | 0.793 | 0.553 | 0.675 | 0.532 | 0.788 | 0.675 | 0.602 | 0.259 | 27.7 |
| tuned post-processing + unmarked components kept | 468 | 0.706 | 0.625 | 0.747 | 0.794 | 0.552 | 0.672 | 0.529 | 0.788 | 0.672 | 0.602 | 0.288 | 28.4 |
| watershed from the ground-truth markers (oracle) | 468 | 0.746 | 0.660 | 0.787 | 0.794 | 0.561 | 0.813 | 0.641 | 0.789 | 0.813 | 0.717 | 0.071 | 23.5 |
| sec. 11.1 layer, reproduced (its markers, its solve) | 468 | 0.651 | 0.566 | 0.685 | 0.785 | 0.534 | 0.628 | 0.484 | 0.771 | 0.628 | 0.547 | 0.609 | 34.2 |
| layer's markers, this model's foreground + watershed | 468 | 0.706 | 0.626 | 0.747 | 0.794 | 0.553 | 0.655 | 0.515 | 0.786 | 0.655 | 0.587 | 0.316 | 28.9 |
| layer's markers, layer's own foreground + watershed of its maps | 468 | 0.651 | 0.566 | 0.685 | 0.785 | 0.534 | 0.628 | 0.484 | 0.770 | 0.628 | 0.548 | 0.610 | 34.3 |
| this model's markers, layer's solve | 468 | 0.624 | 0.531 | 0.648 | 0.744 | 0.517 | 0.625 | 0.469 | 0.751 | 0.625 | 0.538 | 0.386 | 31.0 |
| ground truth instances | 468 | 1.000 | 1.000 | 1.000 | 1.000 | 0.539 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 25.4 |

**HeadNeck**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 169 | 0.672 | 0.658 | 0.744 | 0.835 | 0.648 | 0.640 | 0.519 | 0.811 | 0.640 | 0.556 | 0.424 | 20.2 |
| U-Net + contour head, watershed (b) | 169 | 0.682 | 0.675 | 0.756 | 0.839 | 0.638 | 0.688 | 0.565 | 0.821 | 0.688 | 0.660 | 0.474 | 23.6 |
| `bce_tuned` layer | 169 | 0.682 | 0.681 | 0.751 | 0.815 | 0.633 | 0.753 | 0.624 | 0.829 | 0.753 | 0.640 | 0.210 | 16.6 |
| `dist` layer | 169 | 0.624 | 0.624 | 0.699 | 0.847 | 0.618 | 0.687 | 0.555 | 0.809 | 0.687 | 0.605 | 0.860 | 28.0 |
| `dist` layer, GT markers | 169 | 0.859 | 0.850 | 0.937 | 0.886 | 0.647 | 0.963 | 0.819 | 0.850 | 0.963 | 0.863 | 0.028 | 18.2 |
| s > 0.5, components | 169 | 0.701 | 0.689 | 0.772 | 0.841 | 0.633 | 0.636 | 0.520 | 0.818 | 0.636 | 0.555 | 0.414 | 21.5 |
| tuned post-processing (markers of the distance head, watershed of the chosen relief) | 169 | 0.700 | 0.690 | 0.772 | 0.840 | 0.633 | 0.750 | 0.619 | 0.825 | 0.750 | 0.671 | 0.266 | 21.2 |
| markers of the distance head, watershed of the contour map | 169 | 0.700 | 0.690 | 0.772 | 0.840 | 0.633 | 0.751 | 0.619 | 0.824 | 0.751 | 0.671 | 0.266 | 21.2 |
| markers of the distance head, watershed of −distance | 169 | 0.700 | 0.690 | 0.772 | 0.840 | 0.633 | 0.751 | 0.619 | 0.825 | 0.751 | 0.671 | 0.266 | 21.2 |
| markers of the distance head, watershed of contour − distance | 169 | 0.700 | 0.690 | 0.772 | 0.840 | 0.633 | 0.750 | 0.619 | 0.825 | 0.750 | 0.671 | 0.266 | 21.2 |
| tuned post-processing + unmarked components kept | 169 | 0.701 | 0.690 | 0.772 | 0.841 | 0.631 | 0.745 | 0.614 | 0.824 | 0.745 | 0.671 | 0.287 | 21.8 |
| watershed from the ground-truth markers (oracle) | 169 | 0.771 | 0.757 | 0.846 | 0.841 | 0.642 | 0.864 | 0.711 | 0.823 | 0.864 | 0.760 | 0.084 | 17.3 |
| sec. 11.1 layer, reproduced (its markers, its solve) | 169 | 0.624 | 0.624 | 0.699 | 0.847 | 0.618 | 0.687 | 0.555 | 0.809 | 0.687 | 0.605 | 0.860 | 28.0 |
| layer's markers, this model's foreground + watershed | 169 | 0.707 | 0.696 | 0.779 | 0.841 | 0.636 | 0.730 | 0.600 | 0.821 | 0.730 | 0.660 | 0.313 | 22.4 |
| layer's markers, layer's own foreground + watershed of its maps | 169 | 0.624 | 0.624 | 0.699 | 0.847 | 0.618 | 0.686 | 0.555 | 0.809 | 0.686 | 0.605 | 0.860 | 28.0 |
| this model's markers, layer's solve | 169 | 0.632 | 0.621 | 0.699 | 0.814 | 0.619 | 0.693 | 0.547 | 0.788 | 0.693 | 0.594 | 0.470 | 24.1 |
| ground truth instances | 169 | 1.000 | 1.000 | 1.000 | 1.000 | 0.629 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 18.5 |

**Adrenal_gland**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 148 | 0.716 | 0.676 | 0.774 | 0.808 | 0.554 | 0.694 | 0.582 | 0.840 | 0.694 | 0.655 | 0.378 | 18.4 |
| U-Net + contour head, watershed (b) | 148 | 0.719 | 0.689 | 0.783 | 0.811 | 0.551 | 0.712 | 0.605 | 0.850 | 0.712 | 0.713 | 0.444 | 20.1 |
| `bce_tuned` layer | 148 | 0.716 | 0.693 | 0.785 | 0.816 | 0.571 | 0.808 | 0.688 | 0.852 | 0.808 | 0.694 | 0.246 | 15.7 |
| `dist` layer | 148 | 0.681 | 0.648 | 0.739 | 0.817 | 0.532 | 0.721 | 0.598 | 0.829 | 0.721 | 0.658 | 0.663 | 22.8 |
| `dist` layer, GT markers | 148 | 0.865 | 0.823 | 0.931 | 0.865 | 0.581 | 0.957 | 0.830 | 0.867 | 0.957 | 0.871 | 0.021 | 15.7 |
| s > 0.5, components | 148 | 0.720 | 0.683 | 0.778 | 0.815 | 0.550 | 0.691 | 0.580 | 0.839 | 0.691 | 0.663 | 0.417 | 19.3 |
| tuned post-processing (markers of the distance head, watershed of the chosen relief) | 148 | 0.720 | 0.685 | 0.779 | 0.813 | 0.554 | 0.789 | 0.669 | 0.848 | 0.789 | 0.714 | 0.256 | 16.9 |
| markers of the distance head, watershed of the contour map | 148 | 0.720 | 0.685 | 0.779 | 0.813 | 0.554 | 0.788 | 0.669 | 0.849 | 0.788 | 0.714 | 0.256 | 16.9 |
| markers of the distance head, watershed of −distance | 148 | 0.720 | 0.685 | 0.779 | 0.813 | 0.554 | 0.789 | 0.669 | 0.848 | 0.789 | 0.713 | 0.256 | 16.9 |
| markers of the distance head, watershed of contour − distance | 148 | 0.720 | 0.685 | 0.779 | 0.813 | 0.554 | 0.789 | 0.669 | 0.848 | 0.789 | 0.714 | 0.256 | 16.9 |
| tuned post-processing + unmarked components kept | 148 | 0.719 | 0.684 | 0.778 | 0.814 | 0.551 | 0.779 | 0.659 | 0.846 | 0.779 | 0.713 | 0.292 | 17.7 |
| watershed from the ground-truth markers (oracle) | 148 | 0.773 | 0.732 | 0.834 | 0.815 | 0.570 | 0.867 | 0.735 | 0.848 | 0.867 | 0.787 | 0.087 | 14.7 |
| sec. 11.1 layer, reproduced (its markers, its solve) | 148 | 0.681 | 0.648 | 0.739 | 0.817 | 0.532 | 0.721 | 0.598 | 0.829 | 0.721 | 0.658 | 0.663 | 22.8 |
| layer's markers, this model's foreground + watershed | 148 | 0.720 | 0.686 | 0.780 | 0.814 | 0.553 | 0.771 | 0.651 | 0.845 | 0.771 | 0.706 | 0.295 | 17.9 |
| layer's markers, layer's own foreground + watershed of its maps | 148 | 0.681 | 0.648 | 0.739 | 0.817 | 0.532 | 0.721 | 0.598 | 0.829 | 0.721 | 0.658 | 0.663 | 22.8 |
| this model's markers, layer's solve | 148 | 0.658 | 0.606 | 0.701 | 0.777 | 0.528 | 0.734 | 0.593 | 0.808 | 0.734 | 0.655 | 0.411 | 19.5 |
| ground truth instances | 148 | 1.000 | 1.000 | 1.000 | 1.000 | 0.557 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 16.0 |

## Paired per-patch differences (2523 patches; bootstrap 95 % intervals; F1 / PQ / AJI dataset-level, bootstrapped over patches)

| comparison | IoU | BF₂ | edge align. | F1@0.5 | PQ | AJI |
|---|---|---|---|---|---|---|
| this model's post-processing − `dist` layer | +0.048 [+0.043, +0.052] | +0.052 [+0.047, +0.056] | +0.024 [+0.022, +0.026] | +0.051 [+0.048, +0.054] | +0.055 [+0.053, +0.058] | +0.053 [+0.051, +0.056] |
| this model's post-processing − `bce_tuned` layer | +0.017 [+0.014, +0.020] | +0.015 [+0.012, +0.019] | -0.014 [-0.016, -0.012] | -0.001 [-0.005, +0.003] | -0.002 [-0.005, +0.001] | +0.031 [+0.028, +0.034] |
| this model's post-processing − contour-head U-Net, watershed (b) | +0.007 [+0.005, +0.009] | +0.002 [-0.001, +0.004] | +0.006 [+0.004, +0.008] | +0.053 [+0.050, +0.057] | +0.044 [+0.042, +0.047] | +0.019 [+0.016, +0.022] |
| this model's post-processing − U-Net (sec. 6) logits | +0.006 [+0.004, +0.008] | +0.007 [+0.004, +0.009] | -0.003 [-0.005, -0.002] | +0.112 [+0.106, +0.117] | +0.097 [+0.092, +0.101] | +0.182 [+0.166, +0.196] |
| this model's post-processing − this model's logits | +0.000 [-0.000, +0.002] | -0.000 [-0.001, +0.001] | +0.002 [+0.001, +0.002] | +0.115 [+0.110, +0.119] | +0.097 [+0.093, +0.100] | +0.183 [+0.157, +0.217] |
| watershed of −distance − watershed of the contour map (same markers) | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.000 [-0.001, +0.000] | -0.000 [-0.001, +0.000] | -0.000 [-0.000, +0.000] |
| watershed of contour − distance − watershed of the contour map (same markers) | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.000 [-0.000, +0.000] | +0.000 [-0.000, +0.000] | +0.000 [-0.000, +0.000] |
| + unmarked components kept − this model's post-processing | -0.000 [-0.001, +0.001] | +0.000 [-0.001, +0.001] | -0.001 [-0.002, -0.001] | -0.004 [-0.005, -0.003] | -0.004 [-0.004, -0.003] | +0.000 [+0.000, +0.000] |
| ground-truth markers (oracle) − this model's post-processing | +0.048 [+0.044, +0.053] | +0.049 [+0.045, +0.053] | +0.013 [+0.011, +0.015] | +0.099 [+0.096, +0.103] | +0.080 [+0.077, +0.083] | +0.089 [+0.086, +0.092] |
| this model's oracle − `dist` layer's oracle | -0.085 [-0.089, -0.082] | -0.097 [-0.100, -0.093] | -0.004 [-0.006, -0.003] | -0.091 [-0.094, -0.088] | -0.098 [-0.100, -0.095] | -0.093 [-0.095, -0.090] |
| layer reproduced − `dist` layer (sanity) | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| layer's markers, this model's watershed − `dist` layer (same markers: watershed vs solve) | +0.048 [+0.044, +0.052] | +0.053 [+0.049, +0.057] | +0.025 [+0.023, +0.026] | +0.033 [+0.030, +0.035] | +0.038 [+0.036, +0.040] | +0.041 [+0.040, +0.043] |
| layer's markers, layer's own foreground + watershed − `dist` layer (same markers, same foreground) | -0.000 [-0.000, +0.000] | -0.000 [-0.000, +0.000] | -0.000 [-0.000, +0.000] | +0.000 [-0.000, +0.001] | -0.000 [-0.000, +0.000] | +0.000 [+0.000, +0.000] |
| this model's markers, layer's solve − this model's post-processing (same markers: solve vs watershed) | -0.074 [-0.078, -0.071] | -0.091 [-0.094, -0.087] | -0.038 [-0.040, -0.035] | -0.047 [-0.051, -0.044] | -0.067 [-0.070, -0.064] | -0.063 [-0.065, -0.061] |
| this model's markers, layer's solve − `dist` layer (same solve: markers swapped) | -0.027 [-0.030, -0.024] | -0.039 [-0.042, -0.036] | -0.014 [-0.015, -0.012] | +0.004 [+0.002, +0.006] | -0.012 [-0.014, -0.010] | -0.010 [-0.012, -0.008] |
| layer's markers, this model's watershed − this model's post-processing (same watershed: markers swapped) | +0.000 [-0.001, +0.002] | +0.001 [+0.000, +0.003] | -0.000 [-0.001, -0.000] | -0.018 [-0.020, -0.017] | -0.017 [-0.019, -0.016] | -0.012 [-0.014, -0.010] |

## By crowding (F1@0.5 / PQ / count error)

| patches | n | U-Net (sec. 6) | contour-head U-Net, watershed (b) | `dist` layer | this model: post-processing | + unmarked kept | oracle markers | layer's markers, watershed | this model's markers, layer's solve |
|---|---|---|---|---|---|---|---|---|---|
| < 10 nuclei | 486 | 0.608 / 0.485 / 0.68 | 0.596 / 0.479 / 0.81 | 0.537 / 0.421 / 1.61 | 0.668 / 0.536 / 0.51 | 0.656 / 0.526 / 0.58 | 0.832 / 0.671 / 0.09 | 0.636 / 0.508 / 0.61 | 0.580 / 0.440 / 0.90 |
| 10–30 | 1383 | 0.691 / 0.563 / 0.18 | 0.719 / 0.591 / 0.27 | 0.707 / 0.566 / 0.45 | 0.772 / 0.636 / 0.17 | 0.765 / 0.630 / 0.19 | 0.875 / 0.720 / 0.06 | 0.748 / 0.614 / 0.22 | 0.710 / 0.550 / 0.27 |
| 30–60 | 525 | 0.650 / 0.524 / 0.15 | 0.733 / 0.596 / 0.15 | 0.739 / 0.589 / 0.31 | 0.779 / 0.635 / 0.12 | 0.776 / 0.632 / 0.13 | 0.874 / 0.711 / 0.06 | 0.765 / 0.620 / 0.15 | 0.733 / 0.569 / 0.19 |
| > 60 | 129 | 0.588 / 0.469 / 0.24 | 0.700 / 0.562 / 0.13 | 0.748 / 0.597 / 0.20 | 0.760 / 0.612 / 0.12 | 0.763 / 0.613 / 0.11 | 0.846 / 0.677 / 0.07 | 0.752 / 0.605 / 0.12 | 0.757 / 0.599 / 0.14 |

## Marker quality by crowding (nuclei with one / none / several markers; background markers per patch)

| patches | this model: one | none | several | bg / patch | `dist` layer: one | none | several | bg / patch |
|---|---|---|---|---|---|---|---|---|
| < 10 nuclei | 84.7 % | 9.1 % | 6.2 % | 3.08 | 83.3 % | 6.9 % | 9.8 % | 4.84 |
| 10–30 | 87.9 % | 7.5 % | 4.5 % | 6.02 | 87.3 % | 5.7 % | 7.0 % | 8.76 |
| 30–60 | 86.7 % | 8.6 % | 4.6 % | 8.76 | 86.5 % | 7.2 % | 6.3 % | 12.15 |
| > 60 | 83.5 % | 13.6 % | 2.9 % | 15.15 | 84.5 % | 12.1 % | 3.3 % | 19.90 |

## Per tissue (IoU / F1 / PQ): this model's post-processing vs the `dist` layer vs watershed (b)

- Adrenal_gland (148): 0.720 / 0.789 / 0.669 vs 0.681 / 0.721 / 0.598 vs 0.719 / 0.712 / 0.605
- Bile-duct (103): 0.733 / 0.816 / 0.687 vs 0.678 / 0.733 / 0.603 vs 0.729 / 0.757 / 0.640
- Bladder (61): 0.728 / 0.815 / 0.691 vs 0.704 / 0.777 / 0.645 vs 0.723 / 0.732 / 0.618
- Breast (749): 0.724 / 0.801 / 0.641 vs 0.684 / 0.752 / 0.587 vs 0.722 / 0.757 / 0.605
- Cervix (52): 0.778 / 0.801 / 0.665 vs 0.706 / 0.740 / 0.599 vs 0.776 / 0.764 / 0.631
- Colon (468): 0.706 / 0.675 / 0.532 vs 0.651 / 0.628 / 0.484 vs 0.691 / 0.630 / 0.497
- Esophagus (128): 0.733 / 0.768 / 0.638 vs 0.713 / 0.719 / 0.576 vs 0.728 / 0.689 / 0.569
- HeadNeck (169): 0.700 / 0.750 / 0.619 vs 0.624 / 0.687 / 0.555 vs 0.682 / 0.688 / 0.565
- Kidney (56): 0.762 / 0.828 / 0.682 vs 0.691 / 0.803 / 0.653 vs 0.753 / 0.741 / 0.608
- Liver (66): 0.779 / 0.819 / 0.693 vs 0.726 / 0.760 / 0.632 vs 0.780 / 0.768 / 0.649
- Lung (53): 0.689 / 0.736 / 0.587 vs 0.668 / 0.720 / 0.566 vs 0.693 / 0.679 / 0.540
- Pancreatic (89): 0.755 / 0.783 / 0.647 vs 0.700 / 0.712 / 0.577 vs 0.749 / 0.732 / 0.608
- Skin (87): 0.661 / 0.777 / 0.648 vs 0.591 / 0.714 / 0.588 vs 0.640 / 0.722 / 0.601
- Testis (79): 0.774 / 0.813 / 0.691 vs 0.727 / 0.747 / 0.615 vs 0.766 / 0.761 / 0.642
- Thyroid (84): 0.733 / 0.803 / 0.686 vs 0.683 / 0.729 / 0.612 vs 0.729 / 0.759 / 0.646
