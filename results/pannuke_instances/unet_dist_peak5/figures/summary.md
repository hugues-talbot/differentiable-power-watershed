# The fair baseline for the distance-head layer: three-head U-Net + HoVer-Net-style post-processing (fold 1 → fold 2)

Run `results_pannuke_instances/unet_dist_peak5/unet_dist`: 30 epochs, batch 16, binary foreground target (BCE), edge target ×1.0 on the contour head, distance head ×2.0 (MSE, rmax 12); post-processing: markers = h-maxima h 0.3 of the predicted distance map grown to thr 0.5, min area 16 px, marker watershed of the `contour` relief inside s > 0.5, all four chosen by PQ on 300 patches of fold 3.

## Post-processing chosen on fold 3 (300 patches): {'mk_thr': 0.5, 'mk_min_area': 16, 'mk_h': 0.3, 'relief': 'contour'}

| setting | PQ | F1@0.5 | AJI | count err. | n_pred | one | none | several | bg / patch |
|---|---|---|---|---|---|---|---|---|---|
| thr=0.5/min_area=16/h=0.3/contour | 0.632 | 0.768 | 0.680 | 0.196 | 26.0 | 86.9 % | 8.6 % | 4.5 % | 7.20 |
| thr=0.5/min_area=9/h=0.3/contour | 0.632 | 0.769 | 0.681 | 0.206 | 26.4 | 88.4 % | 6.7 % | 4.8 % | 8.94 |
| thr=0.5/min_area=16/h=0.3/both | 0.632 | 0.767 | 0.680 | 0.196 | 26.0 | 86.9 % | 8.6 % | 4.5 % | 7.20 |
| thr=0.5/min_area=16/h=0.3/dist | 0.631 | 0.767 | 0.680 | 0.196 | 26.0 | 86.9 % | 8.6 % | 4.5 % | 7.20 |
| thr=0.5/min_area=9/h=0.3/both | 0.631 | 0.768 | 0.681 | 0.206 | 26.4 | 88.4 % | 6.7 % | 4.8 % | 8.94 |
| thr=0.5/min_area=9/h=0.3/dist | 0.631 | 0.767 | 0.681 | 0.206 | 26.4 | 88.4 % | 6.7 % | 4.8 % | 8.94 |
| thr=0.5/min_area=4/h=0.3/contour | 0.630 | 0.768 | 0.681 | 0.210 | 26.6 | 88.9 % | 6.0 % | 5.1 % | 10.20 |
| thr=0.4/min_area=16/h=0.3/contour | 0.630 | 0.766 | 0.681 | 0.207 | 26.4 | 87.8 % | 7.4 % | 4.8 % | 8.29 |
| thr=0.4/min_area=16/h=0.3/both | 0.630 | 0.765 | 0.681 | 0.207 | 26.4 | 87.8 % | 7.4 % | 4.8 % | 8.29 |
| thr=0.5/min_area=4/h=0.3/both | 0.630 | 0.767 | 0.681 | 0.210 | 26.6 | 88.9 % | 6.0 % | 5.1 % | 10.20 |

(top 10 of 135 settings by PQ)

Best setting per relief, and the layer's own marker setting (thr 0.2 / min area 16 / h 0.2) with each relief:

| setting | PQ | F1@0.5 | AJI | count err. | n_pred |
|---|---|---|---|---|---|
| best contour: thr=0.5/min_area=16/h=0.3/contour | 0.632 | 0.768 | 0.680 | 0.196 | 26.0 |
| best dist: thr=0.5/min_area=16/h=0.3/dist | 0.631 | 0.767 | 0.680 | 0.196 | 26.0 |
| best both: thr=0.5/min_area=16/h=0.3/both | 0.632 | 0.767 | 0.680 | 0.196 | 26.0 |
| thr=0.2/min_area=16/h=0.2/contour | 0.614 | 0.749 | 0.675 | 0.258 | 27.8 |
| thr=0.2/min_area=16/h=0.2/dist | 0.614 | 0.749 | 0.675 | 0.258 | 27.8 |
| thr=0.2/min_area=16/h=0.2/both | 0.615 | 0.750 | 0.675 | 0.258 | 27.8 |

## All of fold 2

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6, binary target), s > 0.5, components | 2523 | 0.719 | 0.652 | 0.769 | 0.807 | 0.577 | 0.656 | 0.531 | 0.809 | 0.656 | 0.494 | 0.275 | 23.0 |
| U-Net + contour head (sec. 10.1, gap target), logits | 2523 | 0.719 | 0.658 | 0.774 | 0.809 | 0.574 | 0.682 | 0.556 | 0.814 | 0.682 | 0.571 | 0.303 | 25.2 |
| U-Net + contour head, tuned marker watershed (sec. 10.1 b) | 2523 | 0.718 | 0.658 | 0.774 | 0.809 | 0.568 | 0.715 | 0.583 | 0.816 | 0.715 | 0.657 | 0.344 | 27.2 |
| `bce_tuned` layer (sec. 11.1) | 2523 | 0.708 | 0.646 | 0.761 | 0.801 | 0.587 | 0.769 | 0.630 | 0.819 | 0.769 | 0.645 | 0.208 | 21.7 |
| `dist` layer, converged (sec. 11.1) | 2523 | 0.674 | 0.607 | 0.720 | 0.804 | 0.551 | 0.701 | 0.558 | 0.797 | 0.701 | 0.617 | 0.712 | 33.1 |
| `dist` layer + fallback markers | 2523 | 0.674 | 0.607 | 0.720 | 0.804 | 0.551 | 0.696 | 0.554 | 0.796 | 0.696 | 0.617 | 0.756 | 33.7 |
| `dist` layer, ground-truth markers (oracle) | 2523 | 0.859 | 0.796 | 0.922 | 0.858 | 0.591 | 0.958 | 0.804 | 0.839 | 0.958 | 0.857 | 0.019 | 23.3 |
| `dist` run: marker watershed of its contour map inside its s > 0.5 (sec. 11 `ws` row) | 2523 | 0.615 | 0.429 | 0.607 | 0.703 | 0.419 | 0.616 | 0.431 | 0.700 | 0.616 | 0.558 | 0.817 | 34.1 |
| this model: s > 0.5, components | 2523 | 0.724 | 0.660 | 0.776 | 0.812 | 0.572 | 0.658 | 0.535 | 0.812 | 0.658 | 0.496 | 0.323 | 24.5 |
| this model: tuned post-processing (markers of the distance head, watershed of the chosen relief) | 2523 | 0.725 | 0.660 | 0.776 | 0.811 | 0.575 | 0.766 | 0.626 | 0.816 | 0.766 | 0.675 | 0.233 | 25.6 |
| this model: markers of the distance head, watershed of the contour map | 2523 | 0.725 | 0.660 | 0.776 | 0.811 | 0.575 | 0.766 | 0.626 | 0.816 | 0.766 | 0.675 | 0.233 | 25.6 |
| this model: markers of the distance head, watershed of −distance | 2523 | 0.725 | 0.660 | 0.776 | 0.811 | 0.575 | 0.766 | 0.625 | 0.816 | 0.766 | 0.675 | 0.233 | 25.6 |
| this model: markers of the distance head, watershed of contour − distance | 2523 | 0.725 | 0.660 | 0.776 | 0.811 | 0.575 | 0.766 | 0.626 | 0.816 | 0.766 | 0.675 | 0.233 | 25.6 |
| this model: tuned post-processing + unmarked components kept | 2523 | 0.725 | 0.661 | 0.777 | 0.812 | 0.573 | 0.763 | 0.622 | 0.815 | 0.763 | 0.675 | 0.263 | 26.3 |
| this model: watershed from the ground-truth markers (oracle) | 2523 | 0.773 | 0.703 | 0.826 | 0.812 | 0.586 | 0.870 | 0.709 | 0.816 | 0.870 | 0.765 | 0.067 | 22.2 |
| this model: sec. 11.1 layer, reproduced (its markers, its solve) | 2523 | 0.674 | 0.607 | 0.720 | 0.804 | 0.551 | 0.701 | 0.558 | 0.797 | 0.701 | 0.617 | 0.712 | 33.1 |
| this model: layer's markers, this model's foreground + watershed | 2523 | 0.725 | 0.661 | 0.777 | 0.812 | 0.574 | 0.742 | 0.603 | 0.813 | 0.742 | 0.661 | 0.297 | 27.4 |
| this model: layer's markers, layer's own foreground + watershed of its maps | 2523 | 0.674 | 0.607 | 0.720 | 0.804 | 0.551 | 0.701 | 0.557 | 0.795 | 0.701 | 0.616 | 0.713 | 33.1 |
| this model: this model's markers, layer's solve | 2523 | 0.644 | 0.567 | 0.679 | 0.763 | 0.539 | 0.709 | 0.551 | 0.778 | 0.709 | 0.607 | 0.388 | 28.6 |
| this model: ground truth instances | 2523 | 1.000 | 1.000 | 1.000 | 1.000 | 0.559 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 23.7 |

## Marker quality (predicted markers against the ground-truth nuclei)

- 59872 nuclei in fold 2 (23.7 per patch).
- this model's markers: one 86.3 %, none 8.9 %, several 4.8 %, background 6.82 per patch, 29.7 markers per patch.
- the `dist` layer's markers (recomputed): one 85.7 %, none 7.0 %, several 7.4 %, background 9.97 per patch, 34.1 markers per patch.
- the `dist` layer's markers (sec. 11.1 run): one 85.7 %, none 7.0 %, several 7.4 %, background 9.97 per patch, 34.1 markers per patch.
- the `bce_tuned` layer's markers: one 77.7 %, none 21.1 %, several 1.2 %, background 2.69 per patch, 21.7 markers per patch.

## Inference cost

- U-Net forward: 0.8 ms per image; post-processing (markers + the three watersheds, one CPU core): 16 ms per image; the layer's converged solve: 166 ms per image (GPU).

## Per tissue type

**Breast**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 749 | 0.722 | 0.596 | 0.756 | 0.780 | 0.585 | 0.690 | 0.547 | 0.794 | 0.690 | 0.550 | 0.198 | 21.2 |
| U-Net + contour head, watershed (b) | 749 | 0.722 | 0.601 | 0.761 | 0.782 | 0.576 | 0.757 | 0.605 | 0.799 | 0.757 | 0.671 | 0.242 | 24.5 |
| `bce_tuned` layer | 749 | 0.716 | 0.594 | 0.752 | 0.780 | 0.598 | 0.805 | 0.644 | 0.800 | 0.805 | 0.659 | 0.145 | 21.2 |
| `dist` layer | 749 | 0.681 | 0.554 | 0.708 | 0.770 | 0.559 | 0.738 | 0.575 | 0.779 | 0.738 | 0.627 | 0.512 | 29.0 |
| `dist` layer, GT markers | 749 | 0.853 | 0.744 | 0.909 | 0.837 | 0.598 | 0.966 | 0.805 | 0.833 | 0.966 | 0.852 | 0.015 | 21.4 |
| s > 0.5, components | 749 | 0.725 | 0.599 | 0.760 | 0.783 | 0.581 | 0.692 | 0.551 | 0.796 | 0.692 | 0.576 | 0.252 | 22.5 |
| tuned post-processing (markers of the distance head, watershed of the chosen relief) | 749 | 0.725 | 0.599 | 0.759 | 0.782 | 0.584 | 0.800 | 0.640 | 0.801 | 0.800 | 0.685 | 0.174 | 23.3 |
| markers of the distance head, watershed of the contour map | 749 | 0.725 | 0.599 | 0.759 | 0.782 | 0.584 | 0.800 | 0.640 | 0.801 | 0.800 | 0.685 | 0.174 | 23.3 |
| markers of the distance head, watershed of −distance | 749 | 0.725 | 0.599 | 0.759 | 0.782 | 0.584 | 0.800 | 0.641 | 0.800 | 0.800 | 0.685 | 0.174 | 23.3 |
| markers of the distance head, watershed of contour − distance | 749 | 0.725 | 0.599 | 0.759 | 0.782 | 0.584 | 0.800 | 0.641 | 0.801 | 0.800 | 0.685 | 0.174 | 23.3 |
| tuned post-processing + unmarked components kept | 749 | 0.725 | 0.599 | 0.760 | 0.783 | 0.582 | 0.795 | 0.636 | 0.800 | 0.795 | 0.685 | 0.200 | 23.9 |
| watershed from the ground-truth markers (oracle) | 749 | 0.765 | 0.631 | 0.799 | 0.783 | 0.594 | 0.885 | 0.708 | 0.800 | 0.885 | 0.761 | 0.058 | 20.5 |
| sec. 11.1 layer, reproduced (its markers, its solve) | 749 | 0.681 | 0.554 | 0.708 | 0.770 | 0.559 | 0.738 | 0.575 | 0.779 | 0.738 | 0.627 | 0.512 | 29.0 |
| layer's markers, this model's foreground + watershed | 749 | 0.725 | 0.600 | 0.761 | 0.783 | 0.583 | 0.778 | 0.621 | 0.798 | 0.778 | 0.669 | 0.221 | 24.5 |
| layer's markers, layer's own foreground + watershed of its maps | 749 | 0.681 | 0.554 | 0.708 | 0.770 | 0.559 | 0.738 | 0.574 | 0.778 | 0.738 | 0.626 | 0.512 | 29.0 |
| this model's markers, layer's solve | 749 | 0.635 | 0.497 | 0.645 | 0.724 | 0.533 | 0.732 | 0.551 | 0.753 | 0.732 | 0.609 | 0.288 | 25.7 |
| ground truth instances | 749 | 1.000 | 1.000 | 1.000 | 1.000 | 0.553 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 21.7 |

**Colon**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 468 | 0.698 | 0.617 | 0.738 | 0.788 | 0.558 | 0.547 | 0.431 | 0.787 | 0.547 | 0.349 | 0.274 | 21.1 |
| U-Net + contour head, watershed (b) | 468 | 0.691 | 0.621 | 0.742 | 0.788 | 0.550 | 0.630 | 0.497 | 0.789 | 0.630 | 0.574 | 0.340 | 27.7 |
| `bce_tuned` layer | 468 | 0.685 | 0.606 | 0.728 | 0.781 | 0.573 | 0.693 | 0.551 | 0.796 | 0.693 | 0.576 | 0.216 | 21.7 |
| `dist` layer | 468 | 0.644 | 0.557 | 0.676 | 0.783 | 0.529 | 0.605 | 0.465 | 0.768 | 0.605 | 0.538 | 0.761 | 36.4 |
| `dist` layer, GT markers | 468 | 0.851 | 0.772 | 0.906 | 0.850 | 0.568 | 0.938 | 0.769 | 0.820 | 0.938 | 0.841 | 0.021 | 24.9 |
| s > 0.5, components | 468 | 0.703 | 0.624 | 0.744 | 0.795 | 0.552 | 0.548 | 0.433 | 0.790 | 0.548 | 0.316 | 0.308 | 23.1 |
| tuned post-processing (markers of the distance head, watershed of the chosen relief) | 468 | 0.705 | 0.626 | 0.746 | 0.794 | 0.555 | 0.673 | 0.531 | 0.789 | 0.673 | 0.600 | 0.274 | 27.9 |
| markers of the distance head, watershed of the contour map | 468 | 0.705 | 0.626 | 0.746 | 0.794 | 0.555 | 0.673 | 0.531 | 0.789 | 0.673 | 0.600 | 0.274 | 27.9 |
| markers of the distance head, watershed of −distance | 468 | 0.705 | 0.626 | 0.746 | 0.794 | 0.555 | 0.672 | 0.530 | 0.789 | 0.672 | 0.600 | 0.274 | 27.9 |
| markers of the distance head, watershed of contour − distance | 468 | 0.705 | 0.626 | 0.746 | 0.794 | 0.555 | 0.673 | 0.531 | 0.789 | 0.673 | 0.600 | 0.274 | 27.9 |
| tuned post-processing + unmarked components kept | 468 | 0.705 | 0.626 | 0.746 | 0.794 | 0.554 | 0.669 | 0.528 | 0.789 | 0.669 | 0.600 | 0.300 | 28.5 |
| watershed from the ground-truth markers (oracle) | 468 | 0.745 | 0.661 | 0.786 | 0.795 | 0.562 | 0.820 | 0.647 | 0.790 | 0.820 | 0.717 | 0.075 | 23.5 |
| sec. 11.1 layer, reproduced (its markers, its solve) | 468 | 0.644 | 0.557 | 0.676 | 0.783 | 0.529 | 0.605 | 0.465 | 0.768 | 0.605 | 0.538 | 0.761 | 36.4 |
| layer's markers, this model's foreground + watershed | 468 | 0.705 | 0.627 | 0.747 | 0.794 | 0.555 | 0.643 | 0.504 | 0.784 | 0.643 | 0.583 | 0.352 | 30.1 |
| layer's markers, layer's own foreground + watershed of its maps | 468 | 0.644 | 0.557 | 0.676 | 0.783 | 0.529 | 0.603 | 0.463 | 0.767 | 0.603 | 0.538 | 0.762 | 36.4 |
| this model's markers, layer's solve | 468 | 0.616 | 0.524 | 0.639 | 0.741 | 0.520 | 0.608 | 0.457 | 0.751 | 0.608 | 0.529 | 0.413 | 31.5 |
| ground truth instances | 468 | 1.000 | 1.000 | 1.000 | 1.000 | 0.539 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 25.4 |

**HeadNeck**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 169 | 0.672 | 0.658 | 0.744 | 0.835 | 0.648 | 0.640 | 0.519 | 0.811 | 0.640 | 0.556 | 0.424 | 20.2 |
| U-Net + contour head, watershed (b) | 169 | 0.682 | 0.675 | 0.756 | 0.839 | 0.638 | 0.688 | 0.565 | 0.821 | 0.688 | 0.660 | 0.474 | 23.6 |
| `bce_tuned` layer | 169 | 0.682 | 0.681 | 0.751 | 0.815 | 0.633 | 0.753 | 0.624 | 0.829 | 0.753 | 0.640 | 0.210 | 16.6 |
| `dist` layer | 169 | 0.629 | 0.629 | 0.704 | 0.846 | 0.621 | 0.665 | 0.538 | 0.809 | 0.665 | 0.595 | 0.912 | 28.6 |
| `dist` layer, GT markers | 169 | 0.860 | 0.852 | 0.940 | 0.885 | 0.647 | 0.965 | 0.819 | 0.848 | 0.965 | 0.861 | 0.026 | 18.2 |
| s > 0.5, components | 169 | 0.693 | 0.682 | 0.765 | 0.841 | 0.634 | 0.641 | 0.524 | 0.817 | 0.641 | 0.556 | 0.461 | 21.2 |
| tuned post-processing (markers of the distance head, watershed of the chosen relief) | 169 | 0.698 | 0.688 | 0.771 | 0.839 | 0.632 | 0.741 | 0.608 | 0.821 | 0.741 | 0.664 | 0.281 | 21.6 |
| markers of the distance head, watershed of the contour map | 169 | 0.698 | 0.688 | 0.771 | 0.839 | 0.632 | 0.741 | 0.608 | 0.821 | 0.741 | 0.664 | 0.281 | 21.6 |
| markers of the distance head, watershed of −distance | 169 | 0.698 | 0.688 | 0.771 | 0.839 | 0.632 | 0.737 | 0.607 | 0.823 | 0.737 | 0.664 | 0.281 | 21.6 |
| markers of the distance head, watershed of contour − distance | 169 | 0.698 | 0.688 | 0.771 | 0.839 | 0.632 | 0.740 | 0.608 | 0.821 | 0.740 | 0.664 | 0.281 | 21.6 |
| tuned post-processing + unmarked components kept | 169 | 0.699 | 0.689 | 0.771 | 0.840 | 0.634 | 0.736 | 0.604 | 0.820 | 0.736 | 0.665 | 0.311 | 22.3 |
| watershed from the ground-truth markers (oracle) | 169 | 0.770 | 0.758 | 0.848 | 0.841 | 0.643 | 0.869 | 0.714 | 0.821 | 0.869 | 0.762 | 0.083 | 17.3 |
| sec. 11.1 layer, reproduced (its markers, its solve) | 169 | 0.629 | 0.629 | 0.704 | 0.846 | 0.621 | 0.665 | 0.538 | 0.809 | 0.665 | 0.595 | 0.912 | 28.6 |
| layer's markers, this model's foreground + watershed | 169 | 0.693 | 0.683 | 0.766 | 0.840 | 0.632 | 0.714 | 0.584 | 0.819 | 0.714 | 0.647 | 0.347 | 23.0 |
| layer's markers, layer's own foreground + watershed of its maps | 169 | 0.629 | 0.629 | 0.704 | 0.846 | 0.621 | 0.664 | 0.537 | 0.808 | 0.664 | 0.595 | 0.913 | 28.6 |
| this model's markers, layer's solve | 169 | 0.620 | 0.609 | 0.686 | 0.813 | 0.620 | 0.680 | 0.535 | 0.787 | 0.680 | 0.587 | 0.518 | 24.6 |
| ground truth instances | 169 | 1.000 | 1.000 | 1.000 | 1.000 | 0.629 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 18.5 |

**Adrenal_gland**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 148 | 0.716 | 0.676 | 0.774 | 0.808 | 0.554 | 0.694 | 0.582 | 0.840 | 0.694 | 0.655 | 0.378 | 18.4 |
| U-Net + contour head, watershed (b) | 148 | 0.719 | 0.689 | 0.783 | 0.811 | 0.551 | 0.712 | 0.605 | 0.850 | 0.712 | 0.713 | 0.444 | 20.1 |
| `bce_tuned` layer | 148 | 0.716 | 0.693 | 0.785 | 0.816 | 0.571 | 0.808 | 0.688 | 0.852 | 0.808 | 0.694 | 0.246 | 15.7 |
| `dist` layer | 148 | 0.681 | 0.643 | 0.733 | 0.816 | 0.534 | 0.705 | 0.583 | 0.827 | 0.705 | 0.655 | 0.740 | 23.8 |
| `dist` layer, GT markers | 148 | 0.864 | 0.819 | 0.926 | 0.864 | 0.581 | 0.960 | 0.831 | 0.866 | 0.960 | 0.870 | 0.024 | 15.7 |
| s > 0.5, components | 148 | 0.721 | 0.686 | 0.781 | 0.815 | 0.552 | 0.696 | 0.585 | 0.841 | 0.696 | 0.663 | 0.368 | 18.9 |
| tuned post-processing (markers of the distance head, watershed of the chosen relief) | 148 | 0.720 | 0.688 | 0.782 | 0.813 | 0.556 | 0.789 | 0.668 | 0.847 | 0.789 | 0.709 | 0.247 | 17.0 |
| markers of the distance head, watershed of the contour map | 148 | 0.720 | 0.688 | 0.782 | 0.813 | 0.556 | 0.789 | 0.668 | 0.847 | 0.789 | 0.709 | 0.247 | 17.0 |
| markers of the distance head, watershed of −distance | 148 | 0.720 | 0.688 | 0.782 | 0.813 | 0.556 | 0.789 | 0.668 | 0.847 | 0.789 | 0.709 | 0.247 | 17.0 |
| markers of the distance head, watershed of contour − distance | 148 | 0.720 | 0.688 | 0.782 | 0.813 | 0.556 | 0.788 | 0.668 | 0.848 | 0.788 | 0.709 | 0.247 | 17.0 |
| tuned post-processing + unmarked components kept | 148 | 0.721 | 0.687 | 0.782 | 0.814 | 0.554 | 0.781 | 0.661 | 0.846 | 0.781 | 0.709 | 0.266 | 17.6 |
| watershed from the ground-truth markers (oracle) | 148 | 0.772 | 0.733 | 0.834 | 0.815 | 0.571 | 0.864 | 0.733 | 0.849 | 0.864 | 0.785 | 0.087 | 14.7 |
| sec. 11.1 layer, reproduced (its markers, its solve) | 148 | 0.681 | 0.643 | 0.733 | 0.816 | 0.534 | 0.705 | 0.583 | 0.827 | 0.705 | 0.655 | 0.740 | 23.8 |
| layer's markers, this model's foreground + watershed | 148 | 0.721 | 0.688 | 0.783 | 0.814 | 0.555 | 0.767 | 0.648 | 0.845 | 0.767 | 0.703 | 0.283 | 18.0 |
| layer's markers, layer's own foreground + watershed of its maps | 148 | 0.681 | 0.643 | 0.733 | 0.816 | 0.534 | 0.705 | 0.583 | 0.827 | 0.705 | 0.655 | 0.740 | 23.8 |
| this model's markers, layer's solve | 148 | 0.656 | 0.605 | 0.700 | 0.774 | 0.533 | 0.732 | 0.589 | 0.805 | 0.732 | 0.648 | 0.394 | 19.6 |
| ground truth instances | 148 | 1.000 | 1.000 | 1.000 | 1.000 | 0.557 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 16.0 |

## Paired per-patch differences (2523 patches; bootstrap 95 % intervals; F1 / PQ / AJI dataset-level, bootstrapped over patches)

| comparison | IoU | BF₂ | edge align. | F1@0.5 | PQ | AJI |
|---|---|---|---|---|---|---|
| this model's post-processing − `dist` layer | +0.051 [+0.047, +0.055] | +0.056 [+0.052, +0.060] | +0.026 [+0.024, +0.028] | +0.065 [+0.061, +0.069] | +0.067 [+0.064, +0.070] | +0.058 [+0.056, +0.061] |
| this model's post-processing − `bce_tuned` layer | +0.017 [+0.015, +0.020] | +0.015 [+0.012, +0.019] | -0.013 [-0.014, -0.011] | -0.003 [-0.007, +0.001] | -0.004 [-0.007, -0.001] | +0.029 [+0.026, +0.033] |
| this model's post-processing − contour-head U-Net, watershed (b) | +0.007 [+0.005, +0.009] | +0.002 [-0.000, +0.004] | +0.007 [+0.005, +0.008] | +0.051 [+0.048, +0.054] | +0.042 [+0.040, +0.045] | +0.018 [+0.015, +0.021] |
| this model's post-processing − U-Net (sec. 6) logits | +0.006 [+0.004, +0.008] | +0.007 [+0.005, +0.009] | -0.002 [-0.004, -0.001] | +0.110 [+0.104, +0.115] | +0.095 [+0.091, +0.099] | +0.181 [+0.165, +0.195] |
| this model's post-processing − this model's logits | +0.001 [-0.001, +0.002] | +0.000 [-0.001, +0.002] | +0.002 [+0.002, +0.003] | +0.108 [+0.103, +0.113] | +0.091 [+0.087, +0.095] | +0.179 [+0.151, +0.212] |
| watershed of −distance − watershed of the contour map (same markers) | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.000 [-0.001, +0.000] | -0.000 [-0.000, +0.000] | +0.000 [-0.000, +0.000] |
| watershed of contour − distance − watershed of the contour map (same markers) | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.000 [-0.000, +0.000] | +0.000 [-0.000, +0.000] | +0.000 [+0.000, +0.000] |
| + unmarked components kept − this model's post-processing | +0.000 [+0.000, +0.001] | +0.000 [-0.000, +0.001] | -0.001 [-0.002, -0.001] | -0.004 [-0.004, -0.003] | -0.004 [-0.004, -0.003] | +0.000 [-0.000, +0.000] |
| ground-truth markers (oracle) − this model's post-processing | +0.049 [+0.044, +0.053] | +0.050 [+0.045, +0.054] | +0.012 [+0.011, +0.014] | +0.103 [+0.100, +0.107] | +0.084 [+0.081, +0.087] | +0.090 [+0.088, +0.093] |
| this model's oracle − `dist` layer's oracle | -0.085 [-0.089, -0.082] | -0.096 [-0.099, -0.093] | -0.004 [-0.006, -0.003] | -0.089 [-0.092, -0.086] | -0.095 [-0.097, -0.092] | -0.092 [-0.095, -0.089] |
| layer reproduced − `dist` layer (sanity) | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| layer's markers, this model's watershed − `dist` layer (same markers: watershed vs solve) | +0.051 [+0.047, +0.055] | +0.057 [+0.053, +0.061] | +0.025 [+0.023, +0.026] | +0.041 [+0.038, +0.045] | +0.045 [+0.042, +0.047] | +0.044 [+0.042, +0.046] |
| layer's markers, layer's own foreground + watershed − `dist` layer (same markers, same foreground) | +0.000 [+0.000, +0.000] | +0.000 [-0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.000 [-0.001, +0.000] | -0.001 [-0.001, -0.001] | -0.000 [-0.001, -0.000] |
| this model's markers, layer's solve − this model's post-processing (same markers: solve vs watershed) | -0.081 [-0.085, -0.077] | -0.098 [-0.101, -0.093] | -0.037 [-0.039, -0.035] | -0.058 [-0.061, -0.054] | -0.074 [-0.077, -0.071] | -0.068 [-0.070, -0.066] |
| this model's markers, layer's solve − `dist` layer (same solve: markers swapped) | -0.030 [-0.033, -0.027] | -0.042 [-0.045, -0.038] | -0.011 [-0.013, -0.009] | +0.008 [+0.005, +0.010] | -0.007 [-0.009, -0.005] | -0.010 [-0.012, -0.008] |
| layer's markers, this model's watershed − this model's post-processing (same watershed: markers swapped) | -0.000 [-0.001, +0.001] | +0.001 [-0.001, +0.002] | -0.001 [-0.001, -0.001] | -0.024 [-0.026, -0.022] | -0.022 [-0.024, -0.021] | -0.014 [-0.016, -0.013] |

## By crowding (F1@0.5 / PQ / count error)

| patches | n | U-Net (sec. 6) | contour-head U-Net, watershed (b) | `dist` layer | this model: post-processing | + unmarked kept | oracle markers | layer's markers, watershed | this model's markers, layer's solve |
|---|---|---|---|---|---|---|---|---|---|
| < 10 nuclei | 486 | 0.608 / 0.485 / 0.68 | 0.596 / 0.479 / 0.81 | 0.509 / 0.400 / 1.84 | 0.667 / 0.536 / 0.54 | 0.650 / 0.523 / 0.62 | 0.837 / 0.676 / 0.09 | 0.628 / 0.503 / 0.64 | 0.562 / 0.428 / 0.97 |
| 10–30 | 1383 | 0.691 / 0.563 / 0.18 | 0.719 / 0.591 / 0.27 | 0.686 / 0.548 / 0.50 | 0.768 / 0.632 / 0.18 | 0.762 / 0.627 / 0.20 | 0.874 / 0.720 / 0.06 | 0.739 / 0.604 / 0.24 | 0.695 / 0.539 / 0.28 |
| 30–60 | 525 | 0.650 / 0.524 / 0.15 | 0.733 / 0.596 / 0.15 | 0.725 / 0.577 / 0.33 | 0.778 / 0.634 / 0.12 | 0.776 / 0.631 / 0.14 | 0.876 / 0.713 / 0.06 | 0.757 / 0.614 / 0.17 | 0.722 / 0.559 / 0.20 |
| > 60 | 129 | 0.588 / 0.469 / 0.24 | 0.700 / 0.562 / 0.13 | 0.745 / 0.592 / 0.22 | 0.760 / 0.612 / 0.12 | 0.764 / 0.614 / 0.12 | 0.853 / 0.683 / 0.07 | 0.750 / 0.602 / 0.13 | 0.751 / 0.593 / 0.15 |

## Marker quality by crowding (nuclei with one / none / several markers; background markers per patch)

| patches | this model: one | none | several | bg / patch | `dist` layer: one | none | several | bg / patch |
|---|---|---|---|---|---|---|---|---|
| < 10 nuclei | 84.1 % | 9.1 % | 6.8 % | 3.29 | 82.4 % | 6.5 % | 11.1 % | 5.54 |
| 10–30 | 87.5 % | 7.3 % | 5.2 % | 6.32 | 86.1 % | 5.3 % | 8.6 % | 9.45 |
| 30–60 | 86.6 % | 8.5 % | 4.9 % | 9.22 | 85.9 % | 6.9 % | 7.2 % | 12.68 |
| > 60 | 83.3 % | 13.5 % | 3.2 % | 15.70 | 84.7 % | 11.0 % | 4.3 % | 21.14 |

## Per tissue (IoU / F1 / PQ): this model's post-processing vs the `dist` layer vs watershed (b)

- Adrenal_gland (148): 0.720 / 0.789 / 0.668 vs 0.681 / 0.705 / 0.583 vs 0.719 / 0.712 / 0.605
- Bile-duct (103): 0.733 / 0.808 / 0.681 vs 0.667 / 0.715 / 0.587 vs 0.729 / 0.757 / 0.640
- Bladder (61): 0.727 / 0.803 / 0.680 vs 0.705 / 0.764 / 0.634 vs 0.723 / 0.732 / 0.618
- Breast (749): 0.725 / 0.800 / 0.640 vs 0.681 / 0.738 / 0.575 vs 0.722 / 0.757 / 0.605
- Cervix (52): 0.781 / 0.805 / 0.667 vs 0.705 / 0.745 / 0.602 vs 0.776 / 0.764 / 0.631
- Colon (468): 0.705 / 0.673 / 0.531 vs 0.644 / 0.605 / 0.465 vs 0.691 / 0.630 / 0.497
- Esophagus (128): 0.741 / 0.763 / 0.633 vs 0.711 / 0.698 / 0.559 vs 0.728 / 0.689 / 0.569
- HeadNeck (169): 0.698 / 0.741 / 0.608 vs 0.629 / 0.665 / 0.538 vs 0.682 / 0.688 / 0.565
- Kidney (56): 0.780 / 0.825 / 0.680 vs 0.691 / 0.789 / 0.640 vs 0.753 / 0.741 / 0.608
- Liver (66): 0.785 / 0.823 / 0.697 vs 0.725 / 0.747 / 0.621 vs 0.780 / 0.768 / 0.649
- Lung (53): 0.686 / 0.735 / 0.586 vs 0.667 / 0.714 / 0.560 vs 0.693 / 0.679 / 0.540
- Pancreatic (89): 0.749 / 0.782 / 0.645 vs 0.699 / 0.704 / 0.568 vs 0.749 / 0.732 / 0.608
- Skin (87): 0.645 / 0.778 / 0.649 vs 0.586 / 0.698 / 0.572 vs 0.640 / 0.722 / 0.601
- Testis (79): 0.772 / 0.806 / 0.682 vs 0.714 / 0.734 / 0.603 vs 0.766 / 0.761 / 0.642
- Thyroid (84): 0.735 / 0.806 / 0.689 vs 0.682 / 0.722 / 0.603 vs 0.729 / 0.759 / 0.646
