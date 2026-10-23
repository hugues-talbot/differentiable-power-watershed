# The fair baseline for the distance-head layer: three-head U-Net + HoVer-Net-style post-processing (fold 1 → fold 2)

Run `results_pannuke_instances/unet_dist_grad/unet_dist`: 30 epochs, batch 16, binary foreground target (BCE), edge target ×1.0 on the contour head, distance head ×2.0 (MSE, rmax 12); post-processing: markers = h-maxima h 0.3 of the predicted distance map grown to thr 0.5, min area 4 px, marker watershed of the `dist` relief inside s > 0.5, all four chosen by PQ on 300 patches of fold 3.

## Post-processing chosen on fold 3 (300 patches): {'mk_thr': 0.5, 'mk_min_area': 4, 'mk_h': 0.3, 'relief': 'dist'}

| setting | PQ | F1@0.5 | AJI | count err. | n_pred | one | none | several | bg / patch |
|---|---|---|---|---|---|---|---|---|---|
| thr=0.5/min_area=4/h=0.3/dist | 0.663 | 0.798 | 0.666 | 0.180 | 20.7 | 77.4 % | 21.9 % | 0.8 % | 1.69 |
| thr=0.5/min_area=4/h=0.3/contour | 0.663 | 0.798 | 0.665 | 0.180 | 20.7 | 77.4 % | 21.9 % | 0.8 % | 1.69 |
| thr=0.5/min_area=4/h=0.3/both | 0.663 | 0.798 | 0.665 | 0.180 | 20.7 | 77.4 % | 21.9 % | 0.8 % | 1.69 |
| thr=0.5/min_area=4/h=0.2/dist | 0.662 | 0.798 | 0.667 | 0.176 | 21.1 | 77.2 % | 21.4 % | 1.4 % | 1.75 |
| thr=0.5/min_area=4/h=0.2/contour | 0.662 | 0.798 | 0.667 | 0.176 | 21.1 | 77.2 % | 21.4 % | 1.4 % | 1.75 |
| thr=0.5/min_area=4/h=0.2/both | 0.662 | 0.797 | 0.667 | 0.176 | 21.1 | 77.2 % | 21.4 % | 1.4 % | 1.75 |
| thr=0.4/min_area=9/h=0.3/dist | 0.661 | 0.797 | 0.674 | 0.154 | 22.3 | 80.9 % | 18.2 % | 0.9 % | 2.30 |
| thr=0.4/min_area=16/h=0.3/dist | 0.661 | 0.796 | 0.671 | 0.165 | 21.6 | 79.0 % | 20.1 % | 0.9 % | 2.09 |
| thr=0.4/min_area=9/h=0.3/contour | 0.660 | 0.797 | 0.673 | 0.154 | 22.3 | 80.9 % | 18.2 % | 0.9 % | 2.30 |
| thr=0.4/min_area=9/h=0.3/both | 0.660 | 0.797 | 0.674 | 0.154 | 22.3 | 80.9 % | 18.2 % | 0.9 % | 2.30 |

(top 10 of 135 settings by PQ)

Best setting per relief, and the layer's own marker setting (thr 0.2 / min area 16 / h 0.2) with each relief:

| setting | PQ | F1@0.5 | AJI | count err. | n_pred |
|---|---|---|---|---|---|
| best contour: thr=0.5/min_area=4/h=0.3/contour | 0.663 | 0.798 | 0.665 | 0.180 | 20.7 |
| best dist: thr=0.5/min_area=4/h=0.3/dist | 0.663 | 0.798 | 0.666 | 0.180 | 20.7 |
| best both: thr=0.5/min_area=4/h=0.3/both | 0.663 | 0.798 | 0.665 | 0.180 | 20.7 |
| thr=0.2/min_area=16/h=0.2/contour | 0.643 | 0.780 | 0.681 | 0.156 | 24.6 |
| thr=0.2/min_area=16/h=0.2/dist | 0.644 | 0.780 | 0.681 | 0.156 | 24.6 |
| thr=0.2/min_area=16/h=0.2/both | 0.643 | 0.780 | 0.681 | 0.156 | 24.6 |

## All of fold 2

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6, binary target), s > 0.5, components | 2523 | 0.719 | 0.652 | 0.769 | 0.807 | 0.577 | 0.656 | 0.531 | 0.809 | 0.656 | 0.494 | 0.275 | 23.0 |
| U-Net + contour head (sec. 10.1, gap target), logits | 2523 | 0.719 | 0.658 | 0.774 | 0.809 | 0.574 | 0.682 | 0.556 | 0.814 | 0.682 | 0.571 | 0.303 | 25.2 |
| U-Net + contour head, tuned marker watershed (sec. 10.1 b) | 2523 | 0.718 | 0.658 | 0.774 | 0.809 | 0.568 | 0.715 | 0.583 | 0.816 | 0.715 | 0.657 | 0.344 | 27.2 |
| `bce_tuned` layer (sec. 11.1) | 2523 | 0.708 | 0.646 | 0.761 | 0.801 | 0.587 | 0.769 | 0.630 | 0.819 | 0.769 | 0.645 | 0.208 | 21.7 |
| `dist` layer, converged (sec. 11.1) | 2523 | 0.709 | 0.650 | 0.765 | 0.814 | 0.577 | 0.789 | 0.641 | 0.813 | 0.789 | 0.653 | 0.252 | 24.8 |
| `dist` layer + fallback markers | 2523 | 0.706 | 0.649 | 0.764 | 0.815 | 0.579 | 0.776 | 0.630 | 0.812 | 0.776 | 0.653 | 0.319 | 26.1 |
| `dist` layer, ground-truth markers (oracle) | 2523 | 0.860 | 0.799 | 0.922 | 0.859 | 0.590 | 0.959 | 0.806 | 0.840 | 0.959 | 0.859 | 0.020 | 23.3 |
| `dist` run: marker watershed of its contour map inside its s > 0.5 (sec. 11 `ws` row) | 2523 | 0.635 | 0.442 | 0.621 | 0.711 | 0.430 | 0.720 | 0.512 | 0.712 | 0.720 | 0.572 | 0.254 | 24.8 |
| this model: s > 0.5, components | 2523 | 0.725 | 0.663 | 0.778 | 0.812 | 0.575 | 0.660 | 0.537 | 0.813 | 0.660 | 0.504 | 0.312 | 24.1 |
| this model: tuned post-processing (markers of the distance head, watershed of the chosen relief) | 2523 | 0.720 | 0.664 | 0.775 | 0.800 | 0.592 | 0.796 | 0.657 | 0.826 | 0.796 | 0.658 | 0.189 | 20.4 |
| this model: markers of the distance head, watershed of the contour map | 2523 | 0.720 | 0.664 | 0.775 | 0.800 | 0.592 | 0.795 | 0.656 | 0.825 | 0.795 | 0.657 | 0.189 | 20.4 |
| this model: markers of the distance head, watershed of −distance | 2523 | 0.720 | 0.664 | 0.775 | 0.800 | 0.592 | 0.796 | 0.657 | 0.826 | 0.796 | 0.658 | 0.189 | 20.4 |
| this model: markers of the distance head, watershed of contour − distance | 2523 | 0.720 | 0.664 | 0.775 | 0.800 | 0.592 | 0.796 | 0.657 | 0.826 | 0.796 | 0.658 | 0.189 | 20.4 |
| this model: tuned post-processing + unmarked components kept | 2523 | 0.726 | 0.664 | 0.778 | 0.811 | 0.577 | 0.782 | 0.640 | 0.819 | 0.782 | 0.664 | 0.197 | 23.4 |
| this model: watershed from the ground-truth markers (oracle) | 2523 | 0.773 | 0.706 | 0.826 | 0.812 | 0.588 | 0.865 | 0.707 | 0.816 | 0.865 | 0.765 | 0.068 | 22.2 |
| this model: sec. 11.1 layer, reproduced (its markers, its solve) | 2523 | 0.709 | 0.650 | 0.765 | 0.814 | 0.577 | 0.789 | 0.641 | 0.813 | 0.789 | 0.653 | 0.252 | 24.8 |
| this model: layer's markers, this model's foreground + watershed | 2523 | 0.726 | 0.664 | 0.778 | 0.811 | 0.576 | 0.781 | 0.639 | 0.819 | 0.781 | 0.672 | 0.198 | 23.7 |
| this model: layer's markers, layer's own foreground + watershed of its maps | 2523 | 0.709 | 0.650 | 0.765 | 0.814 | 0.577 | 0.789 | 0.641 | 0.812 | 0.789 | 0.653 | 0.252 | 24.8 |
| this model: this model's markers, layer's solve | 2523 | 0.638 | 0.571 | 0.680 | 0.736 | 0.568 | 0.741 | 0.585 | 0.789 | 0.741 | 0.611 | 0.192 | 20.3 |
| this model: ground truth instances | 2523 | 1.000 | 1.000 | 1.000 | 1.000 | 0.559 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 23.7 |

## Marker quality (predicted markers against the ground-truth nuclei)

- 59872 nuclei in fold 2 (23.7 per patch).
- this model's markers: one 77.0 %, none 22.0 %, several 0.9 %, background 1.64 per patch, 20.4 markers per patch.
- the `dist` layer's markers (recomputed): one 84.6 %, none 13.6 %, several 1.8 %, background 3.90 per patch, 24.8 markers per patch.
- the `dist` layer's markers (sec. 11.1 run): one 84.6 %, none 13.6 %, several 1.8 %, background 3.90 per patch, 24.8 markers per patch.
- the `bce_tuned` layer's markers: one 77.7 %, none 21.1 %, several 1.2 %, background 2.69 per patch, 21.7 markers per patch.

## Inference cost

- U-Net forward: 2.4 ms per image; post-processing (markers + the three watersheds, one CPU core): 16 ms per image; the layer's converged solve: 99 ms per image (GPU).

## Per tissue type

**Breast**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 749 | 0.722 | 0.596 | 0.756 | 0.780 | 0.585 | 0.690 | 0.547 | 0.794 | 0.690 | 0.550 | 0.198 | 21.2 |
| U-Net + contour head, watershed (b) | 749 | 0.722 | 0.601 | 0.761 | 0.782 | 0.576 | 0.757 | 0.605 | 0.799 | 0.757 | 0.671 | 0.242 | 24.5 |
| `bce_tuned` layer | 749 | 0.716 | 0.594 | 0.752 | 0.780 | 0.598 | 0.805 | 0.644 | 0.800 | 0.805 | 0.659 | 0.145 | 21.2 |
| `dist` layer | 749 | 0.713 | 0.593 | 0.750 | 0.786 | 0.587 | 0.813 | 0.647 | 0.795 | 0.813 | 0.663 | 0.198 | 23.2 |
| `dist` layer, GT markers | 749 | 0.854 | 0.746 | 0.909 | 0.839 | 0.596 | 0.967 | 0.806 | 0.834 | 0.967 | 0.853 | 0.015 | 21.4 |
| s > 0.5, components | 749 | 0.725 | 0.603 | 0.762 | 0.784 | 0.586 | 0.697 | 0.556 | 0.798 | 0.697 | 0.563 | 0.241 | 22.1 |
| tuned post-processing (markers of the distance head, watershed of the chosen relief) | 749 | 0.720 | 0.602 | 0.760 | 0.776 | 0.601 | 0.827 | 0.667 | 0.807 | 0.827 | 0.674 | 0.148 | 19.5 |
| markers of the distance head, watershed of the contour map | 749 | 0.720 | 0.602 | 0.760 | 0.776 | 0.601 | 0.826 | 0.666 | 0.807 | 0.826 | 0.673 | 0.148 | 19.5 |
| markers of the distance head, watershed of −distance | 749 | 0.720 | 0.602 | 0.760 | 0.776 | 0.601 | 0.827 | 0.667 | 0.807 | 0.827 | 0.674 | 0.148 | 19.5 |
| markers of the distance head, watershed of contour − distance | 749 | 0.720 | 0.602 | 0.760 | 0.776 | 0.601 | 0.827 | 0.667 | 0.807 | 0.827 | 0.674 | 0.148 | 19.5 |
| tuned post-processing + unmarked components kept | 749 | 0.726 | 0.603 | 0.762 | 0.783 | 0.587 | 0.810 | 0.649 | 0.802 | 0.810 | 0.679 | 0.147 | 21.9 |
| watershed from the ground-truth markers (oracle) | 749 | 0.766 | 0.635 | 0.801 | 0.784 | 0.598 | 0.883 | 0.707 | 0.801 | 0.883 | 0.762 | 0.057 | 20.5 |
| sec. 11.1 layer, reproduced (its markers, its solve) | 749 | 0.713 | 0.593 | 0.750 | 0.786 | 0.587 | 0.813 | 0.647 | 0.795 | 0.813 | 0.663 | 0.198 | 23.2 |
| layer's markers, this model's foreground + watershed | 749 | 0.724 | 0.602 | 0.761 | 0.783 | 0.587 | 0.807 | 0.647 | 0.802 | 0.807 | 0.681 | 0.153 | 22.2 |
| layer's markers, layer's own foreground + watershed of its maps | 749 | 0.713 | 0.593 | 0.750 | 0.786 | 0.587 | 0.814 | 0.647 | 0.795 | 0.814 | 0.663 | 0.198 | 23.2 |
| this model's markers, layer's solve | 749 | 0.628 | 0.494 | 0.643 | 0.704 | 0.549 | 0.764 | 0.580 | 0.758 | 0.764 | 0.611 | 0.150 | 19.5 |
| ground truth instances | 749 | 1.000 | 1.000 | 1.000 | 1.000 | 0.553 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 21.7 |

**Colon**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 468 | 0.698 | 0.617 | 0.738 | 0.788 | 0.558 | 0.547 | 0.431 | 0.787 | 0.547 | 0.349 | 0.274 | 21.1 |
| U-Net + contour head, watershed (b) | 468 | 0.691 | 0.621 | 0.742 | 0.788 | 0.550 | 0.630 | 0.497 | 0.789 | 0.630 | 0.574 | 0.340 | 27.7 |
| `bce_tuned` layer | 468 | 0.685 | 0.606 | 0.728 | 0.781 | 0.573 | 0.693 | 0.551 | 0.796 | 0.693 | 0.576 | 0.216 | 21.7 |
| `dist` layer | 468 | 0.684 | 0.608 | 0.728 | 0.794 | 0.562 | 0.709 | 0.558 | 0.788 | 0.709 | 0.579 | 0.253 | 24.5 |
| `dist` layer, GT markers | 468 | 0.851 | 0.777 | 0.908 | 0.852 | 0.569 | 0.939 | 0.771 | 0.821 | 0.939 | 0.842 | 0.022 | 24.8 |
| s > 0.5, components | 468 | 0.706 | 0.626 | 0.747 | 0.794 | 0.553 | 0.552 | 0.436 | 0.790 | 0.552 | 0.348 | 0.286 | 22.9 |
| tuned post-processing (markers of the distance head, watershed of the chosen relief) | 468 | 0.695 | 0.618 | 0.735 | 0.780 | 0.573 | 0.711 | 0.569 | 0.799 | 0.711 | 0.570 | 0.215 | 19.7 |
| markers of the distance head, watershed of the contour map | 468 | 0.695 | 0.618 | 0.735 | 0.780 | 0.573 | 0.711 | 0.568 | 0.799 | 0.711 | 0.569 | 0.215 | 19.7 |
| markers of the distance head, watershed of −distance | 468 | 0.695 | 0.618 | 0.735 | 0.780 | 0.573 | 0.711 | 0.569 | 0.799 | 0.711 | 0.570 | 0.215 | 19.7 |
| markers of the distance head, watershed of contour − distance | 468 | 0.695 | 0.618 | 0.735 | 0.780 | 0.573 | 0.711 | 0.568 | 0.800 | 0.711 | 0.570 | 0.215 | 19.7 |
| tuned post-processing + unmarked components kept | 468 | 0.705 | 0.626 | 0.746 | 0.794 | 0.556 | 0.698 | 0.553 | 0.793 | 0.698 | 0.576 | 0.208 | 23.2 |
| watershed from the ground-truth markers (oracle) | 468 | 0.746 | 0.661 | 0.787 | 0.794 | 0.562 | 0.810 | 0.638 | 0.788 | 0.810 | 0.714 | 0.072 | 23.5 |
| sec. 11.1 layer, reproduced (its markers, its solve) | 468 | 0.684 | 0.608 | 0.728 | 0.794 | 0.562 | 0.709 | 0.558 | 0.788 | 0.709 | 0.579 | 0.253 | 24.5 |
| layer's markers, this model's foreground + watershed | 468 | 0.705 | 0.626 | 0.747 | 0.793 | 0.555 | 0.703 | 0.557 | 0.793 | 0.703 | 0.594 | 0.210 | 23.7 |
| layer's markers, layer's own foreground + watershed of its maps | 468 | 0.684 | 0.608 | 0.728 | 0.794 | 0.562 | 0.709 | 0.559 | 0.787 | 0.709 | 0.579 | 0.253 | 24.5 |
| this model's markers, layer's solve | 468 | 0.588 | 0.512 | 0.620 | 0.704 | 0.558 | 0.643 | 0.491 | 0.764 | 0.643 | 0.525 | 0.217 | 19.6 |
| ground truth instances | 468 | 1.000 | 1.000 | 1.000 | 1.000 | 0.539 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 25.4 |

**HeadNeck**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 169 | 0.672 | 0.658 | 0.744 | 0.835 | 0.648 | 0.640 | 0.519 | 0.811 | 0.640 | 0.556 | 0.424 | 20.2 |
| U-Net + contour head, watershed (b) | 169 | 0.682 | 0.675 | 0.756 | 0.839 | 0.638 | 0.688 | 0.565 | 0.821 | 0.688 | 0.660 | 0.474 | 23.6 |
| `bce_tuned` layer | 169 | 0.682 | 0.681 | 0.751 | 0.815 | 0.633 | 0.753 | 0.624 | 0.829 | 0.753 | 0.640 | 0.210 | 16.6 |
| `dist` layer | 169 | 0.696 | 0.703 | 0.777 | 0.848 | 0.625 | 0.783 | 0.644 | 0.823 | 0.783 | 0.650 | 0.246 | 20.8 |
| `dist` layer, GT markers | 169 | 0.862 | 0.853 | 0.940 | 0.887 | 0.647 | 0.966 | 0.821 | 0.850 | 0.966 | 0.864 | 0.029 | 18.2 |
| s > 0.5, components | 169 | 0.686 | 0.679 | 0.759 | 0.840 | 0.645 | 0.636 | 0.521 | 0.818 | 0.636 | 0.545 | 0.531 | 20.9 |
| tuned post-processing (markers of the distance head, watershed of the chosen relief) | 169 | 0.707 | 0.710 | 0.782 | 0.824 | 0.648 | 0.791 | 0.660 | 0.835 | 0.791 | 0.656 | 0.199 | 16.2 |
| markers of the distance head, watershed of the contour map | 169 | 0.707 | 0.710 | 0.782 | 0.824 | 0.648 | 0.791 | 0.660 | 0.835 | 0.791 | 0.656 | 0.199 | 16.2 |
| markers of the distance head, watershed of −distance | 169 | 0.707 | 0.710 | 0.782 | 0.824 | 0.648 | 0.791 | 0.660 | 0.835 | 0.791 | 0.656 | 0.199 | 16.2 |
| markers of the distance head, watershed of contour − distance | 169 | 0.707 | 0.710 | 0.782 | 0.824 | 0.648 | 0.791 | 0.660 | 0.835 | 0.791 | 0.656 | 0.199 | 16.2 |
| tuned post-processing + unmarked components kept | 169 | 0.692 | 0.686 | 0.766 | 0.840 | 0.642 | 0.769 | 0.636 | 0.827 | 0.769 | 0.665 | 0.238 | 19.3 |
| watershed from the ground-truth markers (oracle) | 169 | 0.768 | 0.758 | 0.844 | 0.840 | 0.649 | 0.859 | 0.709 | 0.825 | 0.859 | 0.761 | 0.090 | 17.3 |
| sec. 11.1 layer, reproduced (its markers, its solve) | 169 | 0.696 | 0.703 | 0.777 | 0.848 | 0.625 | 0.783 | 0.644 | 0.823 | 0.783 | 0.650 | 0.246 | 20.8 |
| layer's markers, this model's foreground + watershed | 169 | 0.709 | 0.704 | 0.783 | 0.838 | 0.641 | 0.764 | 0.632 | 0.827 | 0.764 | 0.670 | 0.204 | 19.6 |
| layer's markers, layer's own foreground + watershed of its maps | 169 | 0.696 | 0.703 | 0.777 | 0.848 | 0.625 | 0.783 | 0.645 | 0.824 | 0.783 | 0.650 | 0.246 | 20.8 |
| this model's markers, layer's solve | 169 | 0.642 | 0.642 | 0.715 | 0.776 | 0.649 | 0.721 | 0.576 | 0.799 | 0.721 | 0.599 | 0.201 | 16.2 |
| ground truth instances | 169 | 1.000 | 1.000 | 1.000 | 1.000 | 0.629 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 18.5 |

**Adrenal_gland**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 148 | 0.716 | 0.676 | 0.774 | 0.808 | 0.554 | 0.694 | 0.582 | 0.840 | 0.694 | 0.655 | 0.378 | 18.4 |
| U-Net + contour head, watershed (b) | 148 | 0.719 | 0.689 | 0.783 | 0.811 | 0.551 | 0.712 | 0.605 | 0.850 | 0.712 | 0.713 | 0.444 | 20.1 |
| `bce_tuned` layer | 148 | 0.716 | 0.693 | 0.785 | 0.816 | 0.571 | 0.808 | 0.688 | 0.852 | 0.808 | 0.694 | 0.246 | 15.7 |
| `dist` layer | 148 | 0.714 | 0.691 | 0.783 | 0.827 | 0.559 | 0.816 | 0.691 | 0.847 | 0.816 | 0.693 | 0.273 | 17.4 |
| `dist` layer, GT markers | 148 | 0.866 | 0.826 | 0.931 | 0.866 | 0.579 | 0.960 | 0.833 | 0.868 | 0.960 | 0.873 | 0.027 | 15.7 |
| s > 0.5, components | 148 | 0.724 | 0.696 | 0.788 | 0.816 | 0.557 | 0.705 | 0.593 | 0.841 | 0.705 | 0.663 | 0.394 | 18.6 |
| tuned post-processing (markers of the distance head, watershed of the chosen relief) | 148 | 0.715 | 0.696 | 0.784 | 0.800 | 0.577 | 0.824 | 0.708 | 0.860 | 0.824 | 0.709 | 0.221 | 14.0 |
| markers of the distance head, watershed of the contour map | 148 | 0.715 | 0.696 | 0.784 | 0.800 | 0.577 | 0.824 | 0.708 | 0.860 | 0.824 | 0.709 | 0.221 | 14.0 |
| markers of the distance head, watershed of −distance | 148 | 0.715 | 0.696 | 0.784 | 0.800 | 0.577 | 0.824 | 0.708 | 0.860 | 0.824 | 0.709 | 0.221 | 14.0 |
| markers of the distance head, watershed of contour − distance | 148 | 0.715 | 0.696 | 0.784 | 0.800 | 0.577 | 0.824 | 0.708 | 0.860 | 0.824 | 0.709 | 0.221 | 14.0 |
| tuned post-processing + unmarked components kept | 148 | 0.724 | 0.697 | 0.788 | 0.815 | 0.559 | 0.805 | 0.685 | 0.850 | 0.805 | 0.715 | 0.239 | 16.3 |
| watershed from the ground-truth markers (oracle) | 148 | 0.773 | 0.742 | 0.839 | 0.816 | 0.574 | 0.868 | 0.738 | 0.851 | 0.868 | 0.783 | 0.092 | 14.6 |
| sec. 11.1 layer, reproduced (its markers, its solve) | 148 | 0.714 | 0.691 | 0.783 | 0.827 | 0.559 | 0.816 | 0.691 | 0.847 | 0.816 | 0.693 | 0.273 | 17.4 |
| layer's markers, this model's foreground + watershed | 148 | 0.725 | 0.697 | 0.788 | 0.815 | 0.559 | 0.804 | 0.684 | 0.850 | 0.804 | 0.713 | 0.227 | 16.2 |
| layer's markers, layer's own foreground + watershed of its maps | 148 | 0.714 | 0.691 | 0.783 | 0.827 | 0.559 | 0.816 | 0.691 | 0.847 | 0.816 | 0.694 | 0.273 | 17.4 |
| this model's markers, layer's solve | 148 | 0.651 | 0.613 | 0.702 | 0.747 | 0.562 | 0.777 | 0.640 | 0.824 | 0.777 | 0.662 | 0.225 | 13.9 |
| ground truth instances | 148 | 1.000 | 1.000 | 1.000 | 1.000 | 0.557 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 16.0 |

## Paired per-patch differences (2523 patches; bootstrap 95 % intervals; F1 / PQ / AJI dataset-level, bootstrapped over patches)

| comparison | IoU | BF₂ | edge align. | F1@0.5 | PQ | AJI |
|---|---|---|---|---|---|---|
| this model's post-processing − `dist` layer | +0.012 [+0.008, +0.016] | +0.010 [+0.006, +0.014] | +0.015 [+0.014, +0.017] | +0.007 [+0.004, +0.009] | +0.016 [+0.013, +0.018] | +0.005 [+0.002, +0.007] |
| this model's post-processing − `bce_tuned` layer | +0.013 [+0.010, +0.016] | +0.015 [+0.011, +0.018] | +0.005 [+0.003, +0.006] | +0.027 [+0.024, +0.030] | +0.027 [+0.025, +0.029] | +0.012 [+0.010, +0.015] |
| this model's post-processing − contour-head U-Net, watershed (b) | +0.002 [-0.001, +0.006] | +0.001 [-0.003, +0.005] | +0.025 [+0.024, +0.027] | +0.081 [+0.077, +0.084] | +0.074 [+0.071, +0.076] | +0.001 [-0.002, +0.003] |
| this model's post-processing − U-Net (sec. 6) logits | +0.002 [-0.002, +0.006] | +0.006 [+0.002, +0.010] | +0.016 [+0.014, +0.017] | +0.139 [+0.134, +0.144] | +0.126 [+0.122, +0.130] | +0.164 [+0.149, +0.177] |
| this model's post-processing − this model's logits | -0.004 [-0.007, -0.000] | -0.002 [-0.006, +0.001] | +0.018 [+0.016, +0.019] | +0.135 [+0.130, +0.140] | +0.120 [+0.116, +0.124] | +0.154 [+0.137, +0.171] |
| watershed of −distance − watershed of the contour map (same markers) | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.001] | +0.000 [+0.000, +0.001] | +0.001 [+0.000, +0.001] |
| watershed of contour − distance − watershed of the contour map (same markers) | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.001] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.001] |
| + unmarked components kept − this model's post-processing | +0.005 [+0.002, +0.008] | +0.003 [-0.000, +0.006] | -0.016 [-0.017, -0.015] | -0.014 [-0.016, -0.012] | -0.016 [-0.018, -0.015] | +0.006 [+0.005, +0.007] |
| ground-truth markers (oracle) − this model's post-processing | +0.053 [+0.049, +0.057] | +0.051 [+0.047, +0.055] | -0.003 [-0.005, -0.002] | +0.070 [+0.066, +0.073] | +0.050 [+0.047, +0.052] | +0.107 [+0.103, +0.110] |
| this model's oracle − `dist` layer's oracle | -0.086 [-0.090, -0.083] | -0.096 [-0.099, -0.093] | -0.002 [-0.003, -0.000] | -0.094 [-0.097, -0.091] | -0.099 [-0.102, -0.097] | -0.094 [-0.096, -0.091] |
| layer reproduced − `dist` layer (sanity) | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| layer's markers, this model's watershed − `dist` layer (same markers: watershed vs solve) | +0.017 [+0.015, +0.020] | +0.013 [+0.010, +0.015] | -0.001 [-0.002, +0.001] | -0.008 [-0.010, -0.006] | -0.002 [-0.003, -0.000] | +0.019 [+0.018, +0.020] |
| layer's markers, layer's own foreground + watershed − `dist` layer (same markers, same foreground) | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.001] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| this model's markers, layer's solve − this model's post-processing (same markers: solve vs watershed) | -0.083 [-0.085, -0.080] | -0.095 [-0.098, -0.093] | -0.024 [-0.026, -0.022] | -0.054 [-0.058, -0.051] | -0.072 [-0.075, -0.069] | -0.047 [-0.050, -0.044] |
| this model's markers, layer's solve − `dist` layer (same solve: markers swapped) | -0.071 [-0.076, -0.066] | -0.085 [-0.090, -0.080] | -0.008 [-0.011, -0.006] | -0.048 [-0.051, -0.044] | -0.056 [-0.059, -0.053] | -0.043 [-0.046, -0.040] |
| layer's markers, this model's watershed − this model's post-processing (same watershed: markers swapped) | +0.005 [+0.002, +0.008] | +0.003 [-0.001, +0.006] | -0.016 [-0.017, -0.015] | -0.015 [-0.017, -0.013] | -0.017 [-0.019, -0.016] | +0.014 [+0.012, +0.016] |

## By crowding (F1@0.5 / PQ / count error)

| patches | n | U-Net (sec. 6) | contour-head U-Net, watershed (b) | `dist` layer | this model: post-processing | + unmarked kept | oracle markers | layer's markers, watershed | this model's markers, layer's solve |
|---|---|---|---|---|---|---|---|---|---|
| < 10 nuclei | 486 | 0.608 / 0.485 / 0.68 | 0.596 / 0.479 / 0.81 | 0.686 / 0.550 / 0.67 | 0.733 / 0.598 / 0.34 | 0.690 / 0.557 / 0.50 | 0.832 / 0.672 / 0.09 | 0.688 / 0.554 / 0.48 | 0.653 / 0.505 / 0.35 |
| 10–30 | 1383 | 0.691 / 0.563 / 0.18 | 0.719 / 0.591 / 0.27 | 0.798 / 0.653 / 0.17 | 0.813 / 0.676 / 0.14 | 0.792 / 0.653 / 0.13 | 0.875 / 0.721 / 0.06 | 0.788 / 0.650 / 0.14 | 0.745 / 0.586 / 0.15 |
| 30–60 | 525 | 0.650 / 0.524 / 0.15 | 0.733 / 0.596 / 0.15 | 0.800 / 0.648 / 0.10 | 0.802 / 0.660 / 0.15 | 0.792 / 0.647 / 0.10 | 0.871 / 0.710 / 0.06 | 0.793 / 0.647 / 0.10 | 0.748 / 0.588 / 0.15 |
| > 60 | 129 | 0.588 / 0.469 / 0.24 | 0.700 / 0.562 / 0.13 | 0.770 / 0.620 / 0.13 | 0.752 / 0.614 / 0.24 | 0.758 / 0.612 / 0.15 | 0.839 / 0.673 / 0.07 | 0.760 / 0.615 / 0.14 | 0.737 / 0.593 / 0.25 |

## Marker quality by crowding (nuclei with one / none / several markers; background markers per patch)

| patches | this model: one | none | several | bg / patch | `dist` layer: one | none | several | bg / patch |
|---|---|---|---|---|---|---|---|---|
| < 10 nuclei | 72.6 % | 26.1 % | 1.2 % | 0.69 | 83.6 % | 13.6 % | 2.8 % | 1.92 |
| 10–30 | 79.7 % | 19.3 % | 1.0 % | 1.58 | 87.0 % | 10.9 % | 2.1 % | 3.77 |
| 30–60 | 77.7 % | 21.4 % | 0.9 % | 2.29 | 84.9 % | 13.3 % | 1.8 % | 5.19 |
| > 60 | 70.6 % | 28.9 % | 0.5 % | 3.24 | 78.7 % | 20.3 % | 0.9 % | 7.49 |

## Per tissue (IoU / F1 / PQ): this model's post-processing vs the `dist` layer vs watershed (b)

- Adrenal_gland (148): 0.715 / 0.824 / 0.708 vs 0.714 / 0.816 / 0.691 vs 0.719 / 0.712 / 0.605
- Bile-duct (103): 0.735 / 0.840 / 0.716 vs 0.716 / 0.823 / 0.686 vs 0.729 / 0.757 / 0.640
- Bladder (61): 0.731 / 0.823 / 0.710 vs 0.718 / 0.830 / 0.698 vs 0.723 / 0.732 / 0.618
- Breast (749): 0.720 / 0.827 / 0.667 vs 0.713 / 0.813 / 0.647 vs 0.722 / 0.757 / 0.605
- Cervix (52): 0.773 / 0.824 / 0.690 vs 0.765 / 0.816 / 0.675 vs 0.776 / 0.764 / 0.631
- Colon (468): 0.695 / 0.711 / 0.569 vs 0.684 / 0.709 / 0.558 vs 0.691 / 0.630 / 0.497
- Esophagus (128): 0.719 / 0.785 / 0.657 vs 0.729 / 0.791 / 0.653 vs 0.728 / 0.689 / 0.569
- HeadNeck (169): 0.707 / 0.791 / 0.660 vs 0.696 / 0.783 / 0.644 vs 0.682 / 0.688 / 0.565
- Kidney (56): 0.774 / 0.820 / 0.680 vs 0.738 / 0.825 / 0.673 vs 0.753 / 0.741 / 0.608
- Liver (66): 0.769 / 0.841 / 0.720 vs 0.751 / 0.839 / 0.710 vs 0.780 / 0.768 / 0.649
- Lung (53): 0.660 / 0.717 / 0.584 vs 0.695 / 0.770 / 0.615 vs 0.693 / 0.679 / 0.540
- Pancreatic (89): 0.752 / 0.822 / 0.686 vs 0.722 / 0.796 / 0.654 vs 0.749 / 0.732 / 0.608
- Skin (87): 0.670 / 0.807 / 0.681 vs 0.620 / 0.795 / 0.662 vs 0.640 / 0.722 / 0.601
- Testis (79): 0.767 / 0.844 / 0.720 vs 0.747 / 0.814 / 0.679 vs 0.766 / 0.761 / 0.642
- Thyroid (84): 0.743 / 0.842 / 0.724 vs 0.710 / 0.823 / 0.699 vs 0.729 / 0.759 / 0.646
