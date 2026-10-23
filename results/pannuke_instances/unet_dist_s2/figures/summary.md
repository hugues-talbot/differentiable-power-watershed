# The fair baseline for the distance-head layer: three-head U-Net + HoVer-Net-style post-processing (fold 1 → fold 2)

Run `results_pannuke_instances/unet_dist_s2/unet_dist`: 30 epochs, batch 16, binary foreground target (BCE), edge target ×1.0 on the contour head, distance head ×2.0 (MSE, rmax 12); post-processing: markers = h-maxima h 0.2 of the predicted distance map grown to thr 0.4, min area 9 px, marker watershed of the `both` relief inside s > 0.5, all four chosen by PQ on 300 patches of fold 3.

## Post-processing chosen on fold 3 (300 patches): {'mk_thr': 0.4, 'mk_min_area': 9, 'mk_h': 0.2, 'relief': 'both'}

| setting | PQ | F1@0.5 | AJI | count err. | n_pred | one | none | several | bg / patch |
|---|---|---|---|---|---|---|---|---|---|
| thr=0.4/min_area=9/h=0.2/both | 0.665 | 0.803 | 0.682 | 0.150 | 22.6 | 81.2 % | 17.4 % | 1.4 % | 2.34 |
| thr=0.4/min_area=16/h=0.2/both | 0.665 | 0.802 | 0.679 | 0.152 | 22.1 | 79.7 % | 18.9 % | 1.4 % | 2.19 |
| thr=0.4/min_area=9/h=0.2/dist | 0.665 | 0.803 | 0.682 | 0.150 | 22.6 | 81.2 % | 17.4 % | 1.4 % | 2.34 |
| thr=0.4/min_area=9/h=0.2/contour | 0.665 | 0.803 | 0.682 | 0.150 | 22.6 | 81.2 % | 17.4 % | 1.4 % | 2.34 |
| thr=0.4/min_area=4/h=0.2/both | 0.665 | 0.804 | 0.683 | 0.147 | 23.1 | 82.3 % | 16.3 % | 1.4 % | 2.56 |
| thr=0.4/min_area=16/h=0.2/contour | 0.665 | 0.802 | 0.679 | 0.152 | 22.1 | 79.7 % | 18.9 % | 1.4 % | 2.19 |
| thr=0.4/min_area=16/h=0.2/dist | 0.665 | 0.802 | 0.679 | 0.152 | 22.1 | 79.7 % | 18.9 % | 1.4 % | 2.19 |
| thr=0.4/min_area=4/h=0.2/dist | 0.665 | 0.804 | 0.683 | 0.147 | 23.1 | 82.3 % | 16.3 % | 1.4 % | 2.56 |
| thr=0.4/min_area=4/h=0.2/contour | 0.665 | 0.804 | 0.683 | 0.147 | 23.1 | 82.3 % | 16.3 % | 1.4 % | 2.56 |
| thr=0.4/min_area=9/h=0.3/contour | 0.664 | 0.801 | 0.674 | 0.151 | 22.1 | 80.7 % | 18.6 % | 0.7 % | 2.22 |

(top 10 of 135 settings by PQ)

Best setting per relief, and the layer's own marker setting (thr 0.2 / min area 16 / h 0.2) with each relief:

| setting | PQ | F1@0.5 | AJI | count err. | n_pred |
|---|---|---|---|---|---|
| best contour: thr=0.4/min_area=9/h=0.2/contour | 0.665 | 0.803 | 0.682 | 0.150 | 22.6 |
| best dist: thr=0.4/min_area=9/h=0.2/dist | 0.665 | 0.803 | 0.682 | 0.150 | 22.6 |
| best both: thr=0.4/min_area=9/h=0.2/both | 0.665 | 0.803 | 0.682 | 0.150 | 22.6 |
| thr=0.2/min_area=16/h=0.2/contour | 0.650 | 0.787 | 0.686 | 0.156 | 24.6 |
| thr=0.2/min_area=16/h=0.2/dist | 0.650 | 0.786 | 0.686 | 0.156 | 24.6 |
| thr=0.2/min_area=16/h=0.2/both | 0.650 | 0.787 | 0.686 | 0.156 | 24.6 |

## All of fold 2

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6, binary target), s > 0.5, components | 2523 | 0.719 | 0.652 | 0.769 | 0.807 | 0.577 | 0.656 | 0.531 | 0.809 | 0.656 | 0.494 | 0.275 | 23.0 |
| U-Net + contour head (sec. 10.1, gap target), logits | 2523 | 0.719 | 0.658 | 0.774 | 0.809 | 0.574 | 0.682 | 0.556 | 0.814 | 0.682 | 0.571 | 0.303 | 25.2 |
| U-Net + contour head, tuned marker watershed (sec. 10.1 b) | 2523 | 0.718 | 0.658 | 0.774 | 0.809 | 0.568 | 0.715 | 0.583 | 0.816 | 0.715 | 0.657 | 0.344 | 27.2 |
| `bce_tuned` layer (sec. 11.1) | 2523 | 0.708 | 0.646 | 0.761 | 0.801 | 0.587 | 0.769 | 0.630 | 0.819 | 0.769 | 0.645 | 0.208 | 21.7 |
| `dist` layer, converged (sec. 11.1) | 2523 | 0.707 | 0.648 | 0.763 | 0.814 | 0.575 | 0.789 | 0.642 | 0.814 | 0.789 | 0.654 | 0.247 | 24.7 |
| `dist` layer + fallback markers | 2523 | 0.705 | 0.648 | 0.762 | 0.815 | 0.576 | 0.780 | 0.633 | 0.812 | 0.780 | 0.653 | 0.311 | 25.8 |
| `dist` layer, ground-truth markers (oracle) | 2523 | 0.861 | 0.801 | 0.925 | 0.861 | 0.588 | 0.960 | 0.808 | 0.841 | 0.960 | 0.860 | 0.020 | 23.3 |
| `dist` run: marker watershed of its contour map inside its s > 0.5 (sec. 11 `ws` row) | 2523 | 0.629 | 0.432 | 0.606 | 0.711 | 0.411 | 0.717 | 0.507 | 0.707 | 0.717 | 0.566 | 0.248 | 24.7 |
| this model: s > 0.5, components | 2523 | 0.726 | 0.663 | 0.778 | 0.814 | 0.573 | 0.663 | 0.539 | 0.813 | 0.663 | 0.492 | 0.301 | 24.0 |
| this model: tuned post-processing (markers of the distance head, watershed of the chosen relief) | 2523 | 0.727 | 0.667 | 0.780 | 0.808 | 0.580 | 0.799 | 0.656 | 0.822 | 0.799 | 0.673 | 0.174 | 22.2 |
| this model: markers of the distance head, watershed of the contour map | 2523 | 0.727 | 0.667 | 0.780 | 0.808 | 0.580 | 0.799 | 0.656 | 0.822 | 0.799 | 0.672 | 0.174 | 22.2 |
| this model: markers of the distance head, watershed of −distance | 2523 | 0.727 | 0.667 | 0.780 | 0.808 | 0.580 | 0.799 | 0.657 | 0.822 | 0.799 | 0.673 | 0.174 | 22.2 |
| this model: markers of the distance head, watershed of contour − distance | 2523 | 0.727 | 0.667 | 0.780 | 0.808 | 0.580 | 0.799 | 0.656 | 0.822 | 0.799 | 0.673 | 0.174 | 22.2 |
| this model: tuned post-processing + unmarked components kept | 2523 | 0.727 | 0.664 | 0.779 | 0.813 | 0.574 | 0.785 | 0.642 | 0.818 | 0.785 | 0.675 | 0.201 | 24.3 |
| this model: watershed from the ground-truth markers (oracle) | 2523 | 0.776 | 0.707 | 0.828 | 0.814 | 0.587 | 0.871 | 0.711 | 0.817 | 0.871 | 0.767 | 0.068 | 22.2 |
| this model: sec. 11.1 layer, reproduced (its markers, its solve) | 2523 | 0.707 | 0.648 | 0.763 | 0.814 | 0.575 | 0.789 | 0.642 | 0.814 | 0.789 | 0.654 | 0.247 | 24.7 |
| this model: layer's markers, this model's foreground + watershed | 2523 | 0.727 | 0.664 | 0.779 | 0.812 | 0.573 | 0.781 | 0.640 | 0.820 | 0.781 | 0.672 | 0.199 | 23.7 |
| this model: layer's markers, layer's own foreground + watershed of its maps | 2523 | 0.707 | 0.648 | 0.763 | 0.814 | 0.575 | 0.789 | 0.642 | 0.813 | 0.789 | 0.653 | 0.247 | 24.7 |
| this model: this model's markers, layer's solve | 2523 | 0.678 | 0.603 | 0.715 | 0.765 | 0.562 | 0.780 | 0.620 | 0.795 | 0.780 | 0.640 | 0.174 | 22.1 |
| this model: ground truth instances | 2523 | 1.000 | 1.000 | 1.000 | 1.000 | 0.559 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 23.7 |

## Marker quality (predicted markers against the ground-truth nuclei)

- 59872 nuclei in fold 2 (23.7 per patch).
- this model's markers: one 80.6 %, none 17.7 %, several 1.8 %, background 2.24 per patch, 22.2 markers per patch.
- the `dist` layer's markers (recomputed): one 84.3 %, none 13.9 %, several 1.7 %, background 3.84 per patch, 24.7 markers per patch.
- the `dist` layer's markers (sec. 11.1 run): one 84.3 %, none 13.9 %, several 1.7 %, background 3.84 per patch, 24.7 markers per patch.
- the `bce_tuned` layer's markers: one 77.7 %, none 21.1 %, several 1.2 %, background 2.69 per patch, 21.7 markers per patch.

## Inference cost

- U-Net forward: 2.4 ms per image; post-processing (markers + the three watersheds, one CPU core): 16 ms per image; the layer's converged solve: 103 ms per image (GPU).

## Per tissue type

**Breast**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 749 | 0.722 | 0.596 | 0.756 | 0.780 | 0.585 | 0.690 | 0.547 | 0.794 | 0.690 | 0.550 | 0.198 | 21.2 |
| U-Net + contour head, watershed (b) | 749 | 0.722 | 0.601 | 0.761 | 0.782 | 0.576 | 0.757 | 0.605 | 0.799 | 0.757 | 0.671 | 0.242 | 24.5 |
| `bce_tuned` layer | 749 | 0.716 | 0.594 | 0.752 | 0.780 | 0.598 | 0.805 | 0.644 | 0.800 | 0.805 | 0.659 | 0.145 | 21.2 |
| `dist` layer | 749 | 0.709 | 0.588 | 0.747 | 0.786 | 0.584 | 0.815 | 0.648 | 0.795 | 0.815 | 0.662 | 0.193 | 23.4 |
| `dist` layer, GT markers | 749 | 0.856 | 0.751 | 0.913 | 0.840 | 0.593 | 0.968 | 0.809 | 0.835 | 0.968 | 0.855 | 0.014 | 21.4 |
| s > 0.5, components | 749 | 0.727 | 0.604 | 0.764 | 0.784 | 0.584 | 0.699 | 0.558 | 0.798 | 0.699 | 0.573 | 0.224 | 21.9 |
| tuned post-processing (markers of the distance head, watershed of the chosen relief) | 749 | 0.725 | 0.604 | 0.763 | 0.781 | 0.592 | 0.827 | 0.665 | 0.804 | 0.827 | 0.683 | 0.138 | 20.7 |
| markers of the distance head, watershed of the contour map | 749 | 0.725 | 0.604 | 0.763 | 0.781 | 0.592 | 0.827 | 0.665 | 0.804 | 0.827 | 0.683 | 0.138 | 20.7 |
| markers of the distance head, watershed of −distance | 749 | 0.725 | 0.604 | 0.763 | 0.781 | 0.592 | 0.828 | 0.666 | 0.804 | 0.828 | 0.683 | 0.138 | 20.7 |
| markers of the distance head, watershed of contour − distance | 749 | 0.725 | 0.604 | 0.763 | 0.781 | 0.592 | 0.827 | 0.665 | 0.804 | 0.827 | 0.683 | 0.138 | 20.7 |
| tuned post-processing + unmarked components kept | 749 | 0.727 | 0.604 | 0.763 | 0.784 | 0.585 | 0.811 | 0.650 | 0.802 | 0.811 | 0.685 | 0.149 | 22.4 |
| watershed from the ground-truth markers (oracle) | 749 | 0.767 | 0.635 | 0.801 | 0.784 | 0.597 | 0.883 | 0.708 | 0.802 | 0.883 | 0.762 | 0.059 | 20.5 |
| sec. 11.1 layer, reproduced (its markers, its solve) | 749 | 0.709 | 0.588 | 0.747 | 0.786 | 0.584 | 0.815 | 0.648 | 0.795 | 0.815 | 0.662 | 0.193 | 23.4 |
| layer's markers, this model's foreground + watershed | 749 | 0.727 | 0.603 | 0.762 | 0.784 | 0.584 | 0.804 | 0.645 | 0.802 | 0.804 | 0.681 | 0.154 | 22.3 |
| layer's markers, layer's own foreground + watershed of its maps | 749 | 0.709 | 0.588 | 0.747 | 0.786 | 0.584 | 0.815 | 0.648 | 0.795 | 0.815 | 0.662 | 0.193 | 23.4 |
| this model's markers, layer's solve | 749 | 0.664 | 0.522 | 0.675 | 0.727 | 0.550 | 0.802 | 0.615 | 0.766 | 0.802 | 0.637 | 0.138 | 20.6 |
| ground truth instances | 749 | 1.000 | 1.000 | 1.000 | 1.000 | 0.553 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 21.7 |

**Colon**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 468 | 0.698 | 0.617 | 0.738 | 0.788 | 0.558 | 0.547 | 0.431 | 0.787 | 0.547 | 0.349 | 0.274 | 21.1 |
| U-Net + contour head, watershed (b) | 468 | 0.691 | 0.621 | 0.742 | 0.788 | 0.550 | 0.630 | 0.497 | 0.789 | 0.630 | 0.574 | 0.340 | 27.7 |
| `bce_tuned` layer | 468 | 0.685 | 0.606 | 0.728 | 0.781 | 0.573 | 0.693 | 0.551 | 0.796 | 0.693 | 0.576 | 0.216 | 21.7 |
| `dist` layer | 468 | 0.685 | 0.608 | 0.728 | 0.795 | 0.561 | 0.711 | 0.559 | 0.787 | 0.711 | 0.579 | 0.248 | 24.8 |
| `dist` layer, GT markers | 468 | 0.853 | 0.776 | 0.910 | 0.853 | 0.565 | 0.942 | 0.774 | 0.821 | 0.942 | 0.844 | 0.024 | 24.9 |
| s > 0.5, components | 468 | 0.708 | 0.630 | 0.751 | 0.796 | 0.553 | 0.555 | 0.439 | 0.790 | 0.555 | 0.310 | 0.296 | 22.6 |
| tuned post-processing (markers of the distance head, watershed of the chosen relief) | 468 | 0.705 | 0.628 | 0.746 | 0.790 | 0.561 | 0.721 | 0.572 | 0.793 | 0.721 | 0.597 | 0.182 | 22.4 |
| markers of the distance head, watershed of the contour map | 468 | 0.705 | 0.628 | 0.746 | 0.790 | 0.561 | 0.720 | 0.571 | 0.793 | 0.720 | 0.596 | 0.182 | 22.4 |
| markers of the distance head, watershed of −distance | 468 | 0.705 | 0.628 | 0.746 | 0.790 | 0.561 | 0.722 | 0.572 | 0.793 | 0.722 | 0.596 | 0.182 | 22.4 |
| markers of the distance head, watershed of contour − distance | 468 | 0.705 | 0.628 | 0.746 | 0.790 | 0.561 | 0.721 | 0.572 | 0.793 | 0.721 | 0.597 | 0.182 | 22.4 |
| tuned post-processing + unmarked components kept | 468 | 0.709 | 0.631 | 0.751 | 0.796 | 0.554 | 0.707 | 0.558 | 0.790 | 0.707 | 0.599 | 0.199 | 24.7 |
| watershed from the ground-truth markers (oracle) | 468 | 0.748 | 0.664 | 0.791 | 0.796 | 0.562 | 0.821 | 0.648 | 0.789 | 0.821 | 0.718 | 0.073 | 23.6 |
| sec. 11.1 layer, reproduced (its markers, its solve) | 468 | 0.685 | 0.608 | 0.728 | 0.795 | 0.561 | 0.711 | 0.559 | 0.787 | 0.711 | 0.579 | 0.248 | 24.8 |
| layer's markers, this model's foreground + watershed | 468 | 0.708 | 0.630 | 0.750 | 0.795 | 0.554 | 0.705 | 0.558 | 0.792 | 0.705 | 0.594 | 0.213 | 23.8 |
| layer's markers, layer's own foreground + watershed of its maps | 468 | 0.685 | 0.608 | 0.728 | 0.795 | 0.561 | 0.711 | 0.559 | 0.787 | 0.711 | 0.579 | 0.248 | 24.8 |
| this model's markers, layer's solve | 468 | 0.644 | 0.552 | 0.668 | 0.738 | 0.547 | 0.694 | 0.533 | 0.768 | 0.694 | 0.564 | 0.181 | 22.3 |
| ground truth instances | 468 | 1.000 | 1.000 | 1.000 | 1.000 | 0.539 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 25.4 |

**HeadNeck**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 169 | 0.672 | 0.658 | 0.744 | 0.835 | 0.648 | 0.640 | 0.519 | 0.811 | 0.640 | 0.556 | 0.424 | 20.2 |
| U-Net + contour head, watershed (b) | 169 | 0.682 | 0.675 | 0.756 | 0.839 | 0.638 | 0.688 | 0.565 | 0.821 | 0.688 | 0.660 | 0.474 | 23.6 |
| `bce_tuned` layer | 169 | 0.682 | 0.681 | 0.751 | 0.815 | 0.633 | 0.753 | 0.624 | 0.829 | 0.753 | 0.640 | 0.210 | 16.6 |
| `dist` layer | 169 | 0.688 | 0.696 | 0.768 | 0.848 | 0.625 | 0.780 | 0.645 | 0.826 | 0.780 | 0.648 | 0.257 | 20.4 |
| `dist` layer, GT markers | 169 | 0.859 | 0.853 | 0.937 | 0.886 | 0.643 | 0.968 | 0.822 | 0.849 | 0.968 | 0.863 | 0.031 | 18.2 |
| s > 0.5, components | 169 | 0.688 | 0.682 | 0.760 | 0.845 | 0.634 | 0.645 | 0.529 | 0.821 | 0.645 | 0.555 | 0.426 | 21.0 |
| tuned post-processing (markers of the distance head, watershed of the chosen relief) | 169 | 0.726 | 0.725 | 0.797 | 0.836 | 0.623 | 0.793 | 0.658 | 0.830 | 0.793 | 0.672 | 0.158 | 18.2 |
| markers of the distance head, watershed of the contour map | 169 | 0.726 | 0.725 | 0.797 | 0.836 | 0.623 | 0.792 | 0.658 | 0.830 | 0.792 | 0.672 | 0.158 | 18.2 |
| markers of the distance head, watershed of −distance | 169 | 0.726 | 0.725 | 0.797 | 0.836 | 0.623 | 0.790 | 0.657 | 0.831 | 0.790 | 0.672 | 0.158 | 18.2 |
| markers of the distance head, watershed of contour − distance | 169 | 0.726 | 0.725 | 0.797 | 0.836 | 0.623 | 0.793 | 0.658 | 0.830 | 0.793 | 0.672 | 0.158 | 18.2 |
| tuned post-processing + unmarked components kept | 169 | 0.700 | 0.695 | 0.772 | 0.844 | 0.631 | 0.773 | 0.638 | 0.826 | 0.773 | 0.673 | 0.245 | 20.2 |
| watershed from the ground-truth markers (oracle) | 169 | 0.776 | 0.766 | 0.849 | 0.845 | 0.639 | 0.872 | 0.720 | 0.825 | 0.872 | 0.766 | 0.087 | 17.3 |
| sec. 11.1 layer, reproduced (its markers, its solve) | 169 | 0.688 | 0.696 | 0.768 | 0.848 | 0.625 | 0.780 | 0.645 | 0.826 | 0.780 | 0.648 | 0.257 | 20.4 |
| layer's markers, this model's foreground + watershed | 169 | 0.710 | 0.705 | 0.780 | 0.842 | 0.620 | 0.769 | 0.637 | 0.829 | 0.769 | 0.668 | 0.219 | 19.6 |
| layer's markers, layer's own foreground + watershed of its maps | 169 | 0.688 | 0.696 | 0.768 | 0.848 | 0.625 | 0.782 | 0.645 | 0.825 | 0.782 | 0.648 | 0.257 | 20.4 |
| this model's markers, layer's solve | 169 | 0.694 | 0.685 | 0.759 | 0.806 | 0.629 | 0.771 | 0.621 | 0.805 | 0.771 | 0.639 | 0.158 | 18.1 |
| ground truth instances | 169 | 1.000 | 1.000 | 1.000 | 1.000 | 0.629 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 18.5 |

**Adrenal_gland**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 148 | 0.716 | 0.676 | 0.774 | 0.808 | 0.554 | 0.694 | 0.582 | 0.840 | 0.694 | 0.655 | 0.378 | 18.4 |
| U-Net + contour head, watershed (b) | 148 | 0.719 | 0.689 | 0.783 | 0.811 | 0.551 | 0.712 | 0.605 | 0.850 | 0.712 | 0.713 | 0.444 | 20.1 |
| `bce_tuned` layer | 148 | 0.716 | 0.693 | 0.785 | 0.816 | 0.571 | 0.808 | 0.688 | 0.852 | 0.808 | 0.694 | 0.246 | 15.7 |
| `dist` layer | 148 | 0.715 | 0.691 | 0.783 | 0.826 | 0.558 | 0.815 | 0.691 | 0.849 | 0.815 | 0.693 | 0.265 | 17.1 |
| `dist` layer, GT markers | 148 | 0.871 | 0.832 | 0.936 | 0.869 | 0.579 | 0.963 | 0.836 | 0.868 | 0.963 | 0.876 | 0.020 | 15.7 |
| s > 0.5, components | 148 | 0.728 | 0.695 | 0.786 | 0.821 | 0.549 | 0.703 | 0.592 | 0.842 | 0.703 | 0.665 | 0.447 | 18.7 |
| tuned post-processing (markers of the distance head, watershed of the chosen relief) | 148 | 0.727 | 0.700 | 0.790 | 0.816 | 0.560 | 0.824 | 0.704 | 0.854 | 0.824 | 0.715 | 0.219 | 15.4 |
| markers of the distance head, watershed of the contour map | 148 | 0.727 | 0.700 | 0.790 | 0.816 | 0.560 | 0.824 | 0.703 | 0.854 | 0.824 | 0.715 | 0.219 | 15.4 |
| markers of the distance head, watershed of −distance | 148 | 0.727 | 0.700 | 0.790 | 0.816 | 0.560 | 0.824 | 0.703 | 0.854 | 0.824 | 0.715 | 0.219 | 15.4 |
| markers of the distance head, watershed of contour − distance | 148 | 0.727 | 0.700 | 0.790 | 0.816 | 0.560 | 0.824 | 0.704 | 0.854 | 0.824 | 0.715 | 0.219 | 15.4 |
| tuned post-processing + unmarked components kept | 148 | 0.729 | 0.696 | 0.788 | 0.820 | 0.552 | 0.799 | 0.680 | 0.850 | 0.799 | 0.716 | 0.256 | 17.0 |
| watershed from the ground-truth markers (oracle) | 148 | 0.782 | 0.744 | 0.843 | 0.821 | 0.571 | 0.874 | 0.743 | 0.851 | 0.874 | 0.790 | 0.091 | 14.7 |
| sec. 11.1 layer, reproduced (its markers, its solve) | 148 | 0.715 | 0.691 | 0.783 | 0.826 | 0.558 | 0.815 | 0.691 | 0.849 | 0.815 | 0.693 | 0.265 | 17.1 |
| layer's markers, this model's foreground + watershed | 148 | 0.730 | 0.699 | 0.790 | 0.819 | 0.556 | 0.801 | 0.683 | 0.853 | 0.801 | 0.714 | 0.216 | 16.2 |
| layer's markers, layer's own foreground + watershed of its maps | 148 | 0.715 | 0.691 | 0.783 | 0.826 | 0.558 | 0.815 | 0.691 | 0.848 | 0.815 | 0.693 | 0.265 | 17.1 |
| this model's markers, layer's solve | 148 | 0.690 | 0.648 | 0.744 | 0.782 | 0.557 | 0.812 | 0.673 | 0.828 | 0.812 | 0.686 | 0.223 | 15.2 |
| ground truth instances | 148 | 1.000 | 1.000 | 1.000 | 1.000 | 0.557 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 16.0 |

## Paired per-patch differences (2523 patches; bootstrap 95 % intervals; F1 / PQ / AJI dataset-level, bootstrapped over patches)

| comparison | IoU | BF₂ | edge align. | F1@0.5 | PQ | AJI |
|---|---|---|---|---|---|---|
| this model's post-processing − `dist` layer | +0.020 [+0.017, +0.024] | +0.016 [+0.013, +0.020] | +0.005 [+0.003, +0.006] | +0.010 [+0.007, +0.012] | +0.014 [+0.012, +0.016] | +0.019 [+0.017, +0.021] |
| this model's post-processing − `bce_tuned` layer | +0.020 [+0.017, +0.022] | +0.019 [+0.016, +0.022] | -0.008 [-0.009, -0.006] | +0.030 [+0.027, +0.033] | +0.027 [+0.025, +0.029] | +0.027 [+0.024, +0.030] |
| this model's post-processing − contour-head U-Net, watershed (b) | +0.009 [+0.006, +0.013] | +0.005 [+0.002, +0.009] | +0.013 [+0.011, +0.014] | +0.084 [+0.081, +0.088] | +0.073 [+0.071, +0.076] | +0.015 [+0.013, +0.018] |
| this model's post-processing − U-Net (sec. 6) logits | +0.009 [+0.005, +0.012] | +0.011 [+0.007, +0.014] | +0.003 [+0.002, +0.005] | +0.142 [+0.138, +0.148] | +0.126 [+0.122, +0.130] | +0.178 [+0.163, +0.192] |
| this model's post-processing − this model's logits | +0.001 [-0.001, +0.005] | +0.002 [-0.001, +0.005] | +0.008 [+0.007, +0.009] | +0.136 [+0.131, +0.141] | +0.117 [+0.114, +0.121] | +0.181 [+0.155, +0.214] |
| watershed of −distance − watershed of the contour map (same markers) | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [-0.000, +0.001] | +0.000 [-0.000, +0.001] | +0.000 [+0.000, +0.001] |
| watershed of contour − distance − watershed of the contour map (same markers) | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [-0.000, +0.001] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| + unmarked components kept − this model's post-processing | -0.000 [-0.003, +0.002] | -0.001 [-0.004, +0.002] | -0.006 [-0.007, -0.006] | -0.014 [-0.016, -0.013] | -0.015 [-0.016, -0.014] | +0.002 [+0.002, +0.003] |
| ground-truth markers (oracle) − this model's post-processing | +0.049 [+0.045, +0.053] | +0.049 [+0.045, +0.053] | +0.008 [+0.006, +0.009] | +0.072 [+0.069, +0.075] | +0.055 [+0.052, +0.057] | +0.094 [+0.091, +0.097] |
| this model's oracle − `dist` layer's oracle | -0.085 [-0.087, -0.082] | -0.096 [-0.100, -0.093] | -0.001 [-0.002, +0.000] | -0.089 [-0.092, -0.086] | -0.096 [-0.099, -0.094] | -0.093 [-0.095, -0.090] |
| layer reproduced − `dist` layer (sanity) | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| layer's markers, this model's watershed − `dist` layer (same markers: watershed vs solve) | +0.020 [+0.018, +0.023] | +0.016 [+0.013, +0.018] | -0.002 [-0.003, -0.000] | -0.008 [-0.010, -0.006] | -0.002 [-0.003, -0.000] | +0.019 [+0.017, +0.020] |
| layer's markers, layer's own foreground + watershed − `dist` layer (same markers, same foreground) | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [-0.000, +0.000] | -0.000 [-0.000, -0.000] | -0.000 [-0.000, -0.000] |
| this model's markers, layer's solve − this model's post-processing (same markers: solve vs watershed) | -0.049 [-0.051, -0.047] | -0.064 [-0.067, -0.062] | -0.018 [-0.019, -0.016] | -0.019 [-0.022, -0.017] | -0.037 [-0.039, -0.035] | -0.033 [-0.035, -0.031] |
| this model's markers, layer's solve − `dist` layer (same solve: markers swapped) | -0.029 [-0.032, -0.025] | -0.048 [-0.052, -0.044] | -0.013 [-0.015, -0.011] | -0.010 [-0.013, -0.007] | -0.023 [-0.025, -0.020] | -0.014 [-0.017, -0.011] |
| layer's markers, this model's watershed − this model's post-processing (same watershed: markers swapped) | +0.000 [-0.002, +0.002] | -0.001 [-0.003, +0.001] | -0.006 [-0.007, -0.005] | -0.018 [-0.019, -0.016] | -0.016 [-0.018, -0.015] | -0.001 [-0.002, +0.001] |

## By crowding (F1@0.5 / PQ / count error)

| patches | n | U-Net (sec. 6) | contour-head U-Net, watershed (b) | `dist` layer | this model: post-processing | + unmarked kept | oracle markers | layer's markers, watershed | this model's markers, layer's solve |
|---|---|---|---|---|---|---|---|---|---|
| < 10 nuclei | 486 | 0.608 / 0.485 / 0.68 | 0.596 / 0.479 / 0.81 | 0.683 / 0.548 / 0.65 | 0.730 / 0.593 / 0.37 | 0.694 / 0.560 / 0.49 | 0.848 / 0.685 / 0.09 | 0.692 / 0.558 / 0.48 | 0.700 / 0.545 / 0.36 |
| 10–30 | 1383 | 0.691 / 0.563 / 0.18 | 0.719 / 0.591 / 0.27 | 0.798 / 0.654 / 0.17 | 0.809 / 0.670 / 0.13 | 0.790 / 0.652 / 0.15 | 0.877 / 0.723 / 0.06 | 0.788 / 0.651 / 0.14 | 0.785 / 0.622 / 0.13 |
| 30–60 | 525 | 0.650 / 0.524 / 0.15 | 0.733 / 0.596 / 0.15 | 0.802 / 0.650 / 0.10 | 0.810 / 0.663 / 0.11 | 0.797 / 0.651 / 0.10 | 0.874 / 0.713 / 0.06 | 0.793 / 0.648 / 0.09 | 0.787 / 0.624 / 0.11 |
| > 60 | 129 | 0.588 / 0.469 / 0.24 | 0.700 / 0.562 / 0.13 | 0.767 / 0.618 / 0.14 | 0.769 / 0.624 / 0.17 | 0.769 / 0.619 / 0.12 | 0.854 / 0.684 / 0.06 | 0.760 / 0.615 / 0.15 | 0.771 / 0.621 / 0.17 |

## Marker quality by crowding (nuclei with one / none / several markers; background markers per patch)

| patches | this model: one | none | several | bg / patch | `dist` layer: one | none | several | bg / patch |
|---|---|---|---|---|---|---|---|---|
| < 10 nuclei | 78.0 % | 19.5 % | 2.5 % | 0.93 | 82.9 % | 14.1 % | 3.0 % | 1.94 |
| 10–30 | 82.6 % | 15.5 % | 1.9 % | 2.15 | 86.9 % | 11.1 % | 2.0 % | 3.73 |
| 30–60 | 81.3 % | 17.0 % | 1.7 % | 3.06 | 84.8 % | 13.5 % | 1.7 % | 5.14 |
| > 60 | 75.1 % | 23.7 % | 1.3 % | 4.86 | 77.8 % | 21.3 % | 0.9 % | 6.98 |

## Per tissue (IoU / F1 / PQ): this model's post-processing vs the `dist` layer vs watershed (b)

- Adrenal_gland (148): 0.727 / 0.824 / 0.704 vs 0.715 / 0.815 / 0.691 vs 0.719 / 0.712 / 0.605
- Bile-duct (103): 0.733 / 0.844 / 0.716 vs 0.708 / 0.825 / 0.692 vs 0.729 / 0.757 / 0.640
- Bladder (61): 0.715 / 0.828 / 0.707 vs 0.716 / 0.829 / 0.701 vs 0.723 / 0.732 / 0.618
- Breast (749): 0.725 / 0.827 / 0.665 vs 0.709 / 0.815 / 0.648 vs 0.722 / 0.757 / 0.605
- Cervix (52): 0.782 / 0.831 / 0.690 vs 0.748 / 0.828 / 0.685 vs 0.776 / 0.764 / 0.631
- Colon (468): 0.705 / 0.721 / 0.572 vs 0.685 / 0.711 / 0.559 vs 0.691 / 0.630 / 0.497
- Esophagus (128): 0.740 / 0.792 / 0.660 vs 0.736 / 0.797 / 0.657 vs 0.728 / 0.689 / 0.569
- HeadNeck (169): 0.726 / 0.793 / 0.658 vs 0.688 / 0.780 / 0.645 vs 0.682 / 0.688 / 0.565
- Kidney (56): 0.776 / 0.825 / 0.682 vs 0.747 / 0.818 / 0.668 vs 0.753 / 0.741 / 0.608
- Liver (66): 0.772 / 0.836 / 0.715 vs 0.750 / 0.830 / 0.705 vs 0.780 / 0.768 / 0.649
- Lung (53): 0.682 / 0.748 / 0.604 vs 0.692 / 0.761 / 0.609 vs 0.693 / 0.679 / 0.540
- Pancreatic (89): 0.753 / 0.816 / 0.679 vs 0.726 / 0.804 / 0.661 vs 0.749 / 0.732 / 0.608
- Skin (87): 0.658 / 0.810 / 0.681 vs 0.612 / 0.793 / 0.663 vs 0.640 / 0.722 / 0.601
- Testis (79): 0.776 / 0.835 / 0.712 vs 0.752 / 0.826 / 0.692 vs 0.766 / 0.761 / 0.642
- Thyroid (84): 0.744 / 0.832 / 0.711 vs 0.711 / 0.829 / 0.704 vs 0.729 / 0.759 / 0.646
