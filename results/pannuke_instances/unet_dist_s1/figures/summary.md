# The fair baseline for the distance-head layer: three-head U-Net + HoVer-Net-style post-processing (fold 1 → fold 2)

Run `results_pannuke_instances/unet_dist_s1/unet_dist`: 30 epochs, batch 16, binary foreground target (BCE), edge target ×1.0 on the contour head, distance head ×2.0 (MSE, rmax 12); post-processing: markers = h-maxima h 0.2 of the predicted distance map grown to thr 0.5, min area 4 px, marker watershed of the `both` relief inside s > 0.5, all four chosen by PQ on 300 patches of fold 3.

## Post-processing chosen on fold 3 (300 patches): {'mk_thr': 0.5, 'mk_min_area': 4, 'mk_h': 0.2, 'relief': 'both'}

| setting | PQ | F1@0.5 | AJI | count err. | n_pred | one | none | several | bg / patch |
|---|---|---|---|---|---|---|---|---|---|
| thr=0.5/min_area=4/h=0.2/both | 0.663 | 0.798 | 0.665 | 0.169 | 21.0 | 77.1 % | 21.6 % | 1.3 % | 1.70 |
| thr=0.5/min_area=4/h=0.2/dist | 0.663 | 0.798 | 0.665 | 0.169 | 21.0 | 77.1 % | 21.6 % | 1.3 % | 1.70 |
| thr=0.5/min_area=4/h=0.2/contour | 0.662 | 0.798 | 0.665 | 0.169 | 21.0 | 77.1 % | 21.6 % | 1.3 % | 1.70 |
| thr=0.5/min_area=4/h=0.3/dist | 0.662 | 0.797 | 0.663 | 0.171 | 20.6 | 77.0 % | 22.3 % | 0.7 % | 1.63 |
| thr=0.5/min_area=4/h=0.3/both | 0.662 | 0.796 | 0.663 | 0.171 | 20.6 | 77.0 % | 22.3 % | 0.7 % | 1.63 |
| thr=0.4/min_area=9/h=0.2/both | 0.661 | 0.800 | 0.676 | 0.154 | 22.4 | 80.6 % | 17.9 % | 1.5 % | 2.18 |
| thr=0.5/min_area=4/h=0.3/contour | 0.661 | 0.796 | 0.663 | 0.171 | 20.6 | 77.0 % | 22.3 % | 0.7 % | 1.63 |
| thr=0.4/min_area=9/h=0.2/contour | 0.661 | 0.800 | 0.676 | 0.154 | 22.4 | 80.6 % | 17.9 % | 1.5 % | 2.18 |
| thr=0.4/min_area=9/h=0.2/dist | 0.661 | 0.799 | 0.676 | 0.154 | 22.4 | 80.6 % | 17.9 % | 1.5 % | 2.18 |
| thr=0.4/min_area=9/h=0.3/dist | 0.661 | 0.799 | 0.672 | 0.156 | 21.9 | 80.3 % | 18.9 % | 0.8 % | 2.07 |

(top 10 of 135 settings by PQ)

Best setting per relief, and the layer's own marker setting (thr 0.2 / min area 16 / h 0.2) with each relief:

| setting | PQ | F1@0.5 | AJI | count err. | n_pred |
|---|---|---|---|---|---|
| best contour: thr=0.5/min_area=4/h=0.2/contour | 0.662 | 0.798 | 0.665 | 0.169 | 21.0 |
| best dist: thr=0.5/min_area=4/h=0.2/dist | 0.663 | 0.798 | 0.665 | 0.169 | 21.0 |
| best both: thr=0.5/min_area=4/h=0.2/both | 0.663 | 0.798 | 0.665 | 0.169 | 21.0 |
| thr=0.2/min_area=16/h=0.2/contour | 0.643 | 0.780 | 0.681 | 0.150 | 24.5 |
| thr=0.2/min_area=16/h=0.2/dist | 0.643 | 0.780 | 0.681 | 0.150 | 24.5 |
| thr=0.2/min_area=16/h=0.2/both | 0.643 | 0.780 | 0.681 | 0.150 | 24.5 |

## All of fold 2

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6, binary target), s > 0.5, components | 2523 | 0.719 | 0.652 | 0.769 | 0.807 | 0.577 | 0.656 | 0.531 | 0.809 | 0.656 | 0.494 | 0.275 | 23.0 |
| U-Net + contour head (sec. 10.1, gap target), logits | 2523 | 0.719 | 0.658 | 0.774 | 0.809 | 0.574 | 0.682 | 0.556 | 0.814 | 0.682 | 0.571 | 0.303 | 25.2 |
| U-Net + contour head, tuned marker watershed (sec. 10.1 b) | 2523 | 0.718 | 0.658 | 0.774 | 0.809 | 0.568 | 0.715 | 0.583 | 0.816 | 0.715 | 0.657 | 0.344 | 27.2 |
| `bce_tuned` layer (sec. 11.1) | 2523 | 0.708 | 0.646 | 0.761 | 0.801 | 0.587 | 0.769 | 0.630 | 0.819 | 0.769 | 0.645 | 0.208 | 21.7 |
| `dist` layer, converged (sec. 11.1) | 2523 | 0.708 | 0.650 | 0.764 | 0.811 | 0.580 | 0.790 | 0.642 | 0.813 | 0.790 | 0.653 | 0.244 | 24.2 |
| `dist` layer + fallback markers | 2523 | 0.707 | 0.650 | 0.764 | 0.813 | 0.581 | 0.778 | 0.631 | 0.811 | 0.778 | 0.653 | 0.312 | 25.6 |
| `dist` layer, ground-truth markers (oracle) | 2523 | 0.859 | 0.799 | 0.923 | 0.859 | 0.589 | 0.959 | 0.806 | 0.840 | 0.959 | 0.859 | 0.022 | 23.3 |
| `dist` run: marker watershed of its contour map inside its s > 0.5 (sec. 11 `ws` row) | 2523 | 0.639 | 0.432 | 0.608 | 0.720 | 0.414 | 0.727 | 0.523 | 0.719 | 0.727 | 0.573 | 0.246 | 24.2 |
| this model: s > 0.5, components | 2523 | 0.723 | 0.659 | 0.774 | 0.810 | 0.573 | 0.654 | 0.531 | 0.812 | 0.654 | 0.494 | 0.307 | 24.2 |
| this model: tuned post-processing (markers of the distance head, watershed of the chosen relief) | 2523 | 0.718 | 0.660 | 0.772 | 0.797 | 0.591 | 0.793 | 0.654 | 0.824 | 0.793 | 0.657 | 0.187 | 20.5 |
| this model: markers of the distance head, watershed of the contour map | 2523 | 0.718 | 0.660 | 0.772 | 0.797 | 0.591 | 0.793 | 0.654 | 0.824 | 0.793 | 0.657 | 0.187 | 20.5 |
| this model: markers of the distance head, watershed of −distance | 2523 | 0.718 | 0.660 | 0.772 | 0.797 | 0.591 | 0.793 | 0.654 | 0.824 | 0.793 | 0.658 | 0.187 | 20.5 |
| this model: markers of the distance head, watershed of contour − distance | 2523 | 0.718 | 0.660 | 0.772 | 0.797 | 0.591 | 0.793 | 0.654 | 0.824 | 0.793 | 0.657 | 0.187 | 20.5 |
| this model: tuned post-processing + unmarked components kept | 2523 | 0.725 | 0.661 | 0.776 | 0.810 | 0.574 | 0.779 | 0.637 | 0.818 | 0.779 | 0.665 | 0.198 | 23.6 |
| this model: watershed from the ground-truth markers (oracle) | 2523 | 0.771 | 0.702 | 0.823 | 0.810 | 0.586 | 0.861 | 0.703 | 0.816 | 0.861 | 0.762 | 0.069 | 22.1 |
| this model: sec. 11.1 layer, reproduced (its markers, its solve) | 2523 | 0.708 | 0.650 | 0.764 | 0.811 | 0.580 | 0.790 | 0.642 | 0.813 | 0.790 | 0.653 | 0.244 | 24.2 |
| this model: layer's markers, this model's foreground + watershed | 2523 | 0.724 | 0.660 | 0.774 | 0.809 | 0.574 | 0.778 | 0.637 | 0.819 | 0.778 | 0.668 | 0.192 | 23.3 |
| this model: layer's markers, layer's own foreground + watershed of its maps | 2523 | 0.708 | 0.650 | 0.764 | 0.811 | 0.580 | 0.790 | 0.642 | 0.813 | 0.790 | 0.653 | 0.244 | 24.2 |
| this model: this model's markers, layer's solve | 2523 | 0.636 | 0.568 | 0.675 | 0.734 | 0.562 | 0.738 | 0.580 | 0.786 | 0.738 | 0.607 | 0.190 | 20.4 |
| this model: ground truth instances | 2523 | 1.000 | 1.000 | 1.000 | 1.000 | 0.559 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 23.7 |

## Marker quality (predicted markers against the ground-truth nuclei)

- 59872 nuclei in fold 2 (23.7 per patch).
- this model's markers: one 76.4 %, none 22.1 %, several 1.5 %, background 1.62 per patch, 20.5 markers per patch.
- the `dist` layer's markers (recomputed): one 83.5 %, none 14.8 %, several 1.7 %, background 3.56 per patch, 24.2 markers per patch.
- the `dist` layer's markers (sec. 11.1 run): one 83.5 %, none 14.8 %, several 1.7 %, background 3.56 per patch, 24.2 markers per patch.
- the `bce_tuned` layer's markers: one 77.7 %, none 21.1 %, several 1.2 %, background 2.69 per patch, 21.7 markers per patch.

## Inference cost

- U-Net forward: 2.4 ms per image; post-processing (markers + the three watersheds, one CPU core): 15 ms per image; the layer's converged solve: 99 ms per image (GPU).

## Per tissue type

**Breast**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 749 | 0.722 | 0.596 | 0.756 | 0.780 | 0.585 | 0.690 | 0.547 | 0.794 | 0.690 | 0.550 | 0.198 | 21.2 |
| U-Net + contour head, watershed (b) | 749 | 0.722 | 0.601 | 0.761 | 0.782 | 0.576 | 0.757 | 0.605 | 0.799 | 0.757 | 0.671 | 0.242 | 24.5 |
| `bce_tuned` layer | 749 | 0.716 | 0.594 | 0.752 | 0.780 | 0.598 | 0.805 | 0.644 | 0.800 | 0.805 | 0.659 | 0.145 | 21.2 |
| `dist` layer | 749 | 0.712 | 0.592 | 0.749 | 0.784 | 0.589 | 0.817 | 0.650 | 0.795 | 0.817 | 0.664 | 0.185 | 22.8 |
| `dist` layer, GT markers | 749 | 0.854 | 0.747 | 0.911 | 0.838 | 0.595 | 0.966 | 0.806 | 0.834 | 0.966 | 0.853 | 0.016 | 21.4 |
| s > 0.5, components | 749 | 0.724 | 0.598 | 0.759 | 0.781 | 0.582 | 0.690 | 0.550 | 0.796 | 0.690 | 0.570 | 0.229 | 22.2 |
| tuned post-processing (markers of the distance head, watershed of the chosen relief) | 749 | 0.717 | 0.597 | 0.756 | 0.771 | 0.599 | 0.822 | 0.662 | 0.806 | 0.822 | 0.671 | 0.156 | 19.5 |
| markers of the distance head, watershed of the contour map | 749 | 0.717 | 0.597 | 0.756 | 0.771 | 0.599 | 0.821 | 0.662 | 0.806 | 0.821 | 0.671 | 0.156 | 19.5 |
| markers of the distance head, watershed of −distance | 749 | 0.717 | 0.597 | 0.756 | 0.771 | 0.599 | 0.822 | 0.663 | 0.806 | 0.822 | 0.671 | 0.156 | 19.5 |
| markers of the distance head, watershed of contour − distance | 749 | 0.717 | 0.597 | 0.756 | 0.771 | 0.599 | 0.822 | 0.662 | 0.806 | 0.822 | 0.671 | 0.156 | 19.5 |
| tuned post-processing + unmarked components kept | 749 | 0.724 | 0.598 | 0.758 | 0.781 | 0.584 | 0.806 | 0.645 | 0.800 | 0.806 | 0.678 | 0.149 | 22.0 |
| watershed from the ground-truth markers (oracle) | 749 | 0.763 | 0.628 | 0.796 | 0.781 | 0.595 | 0.879 | 0.703 | 0.800 | 0.879 | 0.759 | 0.060 | 20.5 |
| sec. 11.1 layer, reproduced (its markers, its solve) | 749 | 0.712 | 0.592 | 0.749 | 0.784 | 0.589 | 0.817 | 0.650 | 0.795 | 0.817 | 0.664 | 0.185 | 22.8 |
| layer's markers, this model's foreground + watershed | 749 | 0.723 | 0.597 | 0.757 | 0.780 | 0.583 | 0.803 | 0.644 | 0.802 | 0.803 | 0.679 | 0.143 | 21.9 |
| layer's markers, layer's own foreground + watershed of its maps | 749 | 0.712 | 0.592 | 0.749 | 0.784 | 0.589 | 0.817 | 0.649 | 0.795 | 0.817 | 0.664 | 0.185 | 22.8 |
| this model's markers, layer's solve | 749 | 0.626 | 0.494 | 0.638 | 0.701 | 0.542 | 0.760 | 0.576 | 0.757 | 0.760 | 0.608 | 0.160 | 19.3 |
| ground truth instances | 749 | 1.000 | 1.000 | 1.000 | 1.000 | 0.553 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 21.7 |

**Colon**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 468 | 0.698 | 0.617 | 0.738 | 0.788 | 0.558 | 0.547 | 0.431 | 0.787 | 0.547 | 0.349 | 0.274 | 21.1 |
| U-Net + contour head, watershed (b) | 468 | 0.691 | 0.621 | 0.742 | 0.788 | 0.550 | 0.630 | 0.497 | 0.789 | 0.630 | 0.574 | 0.340 | 27.7 |
| `bce_tuned` layer | 468 | 0.685 | 0.606 | 0.728 | 0.781 | 0.573 | 0.693 | 0.551 | 0.796 | 0.693 | 0.576 | 0.216 | 21.7 |
| `dist` layer | 468 | 0.684 | 0.608 | 0.728 | 0.792 | 0.565 | 0.710 | 0.560 | 0.789 | 0.710 | 0.578 | 0.249 | 23.9 |
| `dist` layer, GT markers | 468 | 0.850 | 0.775 | 0.906 | 0.851 | 0.565 | 0.941 | 0.772 | 0.821 | 0.941 | 0.842 | 0.025 | 24.8 |
| s > 0.5, components | 468 | 0.698 | 0.620 | 0.739 | 0.790 | 0.556 | 0.541 | 0.428 | 0.790 | 0.541 | 0.320 | 0.293 | 22.7 |
| tuned post-processing (markers of the distance head, watershed of the chosen relief) | 468 | 0.686 | 0.611 | 0.726 | 0.775 | 0.578 | 0.703 | 0.560 | 0.797 | 0.703 | 0.567 | 0.219 | 19.8 |
| markers of the distance head, watershed of the contour map | 468 | 0.686 | 0.611 | 0.726 | 0.775 | 0.578 | 0.703 | 0.560 | 0.797 | 0.703 | 0.567 | 0.219 | 19.8 |
| markers of the distance head, watershed of −distance | 468 | 0.686 | 0.611 | 0.726 | 0.775 | 0.578 | 0.704 | 0.561 | 0.797 | 0.704 | 0.567 | 0.219 | 19.8 |
| markers of the distance head, watershed of contour − distance | 468 | 0.686 | 0.611 | 0.726 | 0.775 | 0.578 | 0.703 | 0.560 | 0.797 | 0.703 | 0.567 | 0.219 | 19.8 |
| tuned post-processing + unmarked components kept | 468 | 0.703 | 0.624 | 0.743 | 0.790 | 0.557 | 0.689 | 0.545 | 0.791 | 0.689 | 0.575 | 0.202 | 23.3 |
| watershed from the ground-truth markers (oracle) | 468 | 0.739 | 0.656 | 0.781 | 0.790 | 0.563 | 0.803 | 0.634 | 0.790 | 0.803 | 0.709 | 0.080 | 23.3 |
| sec. 11.1 layer, reproduced (its markers, its solve) | 468 | 0.684 | 0.608 | 0.728 | 0.792 | 0.565 | 0.710 | 0.560 | 0.789 | 0.710 | 0.578 | 0.249 | 23.9 |
| layer's markers, this model's foreground + watershed | 468 | 0.703 | 0.624 | 0.743 | 0.789 | 0.556 | 0.698 | 0.553 | 0.792 | 0.698 | 0.588 | 0.204 | 23.1 |
| layer's markers, layer's own foreground + watershed of its maps | 468 | 0.684 | 0.608 | 0.728 | 0.792 | 0.565 | 0.710 | 0.559 | 0.788 | 0.710 | 0.578 | 0.249 | 23.9 |
| this model's markers, layer's solve | 468 | 0.583 | 0.502 | 0.609 | 0.700 | 0.552 | 0.631 | 0.480 | 0.760 | 0.631 | 0.518 | 0.221 | 19.7 |
| ground truth instances | 468 | 1.000 | 1.000 | 1.000 | 1.000 | 0.539 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 25.4 |

**HeadNeck**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 169 | 0.672 | 0.658 | 0.744 | 0.835 | 0.648 | 0.640 | 0.519 | 0.811 | 0.640 | 0.556 | 0.424 | 20.2 |
| U-Net + contour head, watershed (b) | 169 | 0.682 | 0.675 | 0.756 | 0.839 | 0.638 | 0.688 | 0.565 | 0.821 | 0.688 | 0.660 | 0.474 | 23.6 |
| `bce_tuned` layer | 169 | 0.682 | 0.681 | 0.751 | 0.815 | 0.633 | 0.753 | 0.624 | 0.829 | 0.753 | 0.640 | 0.210 | 16.6 |
| `dist` layer | 169 | 0.689 | 0.696 | 0.767 | 0.844 | 0.640 | 0.784 | 0.647 | 0.825 | 0.784 | 0.657 | 0.250 | 19.7 |
| `dist` layer, GT markers | 169 | 0.859 | 0.852 | 0.937 | 0.886 | 0.646 | 0.964 | 0.819 | 0.850 | 0.964 | 0.861 | 0.033 | 18.1 |
| s > 0.5, components | 169 | 0.701 | 0.691 | 0.772 | 0.838 | 0.639 | 0.638 | 0.522 | 0.818 | 0.638 | 0.554 | 0.344 | 21.0 |
| tuned post-processing (markers of the distance head, watershed of the chosen relief) | 169 | 0.713 | 0.714 | 0.786 | 0.822 | 0.642 | 0.785 | 0.651 | 0.829 | 0.785 | 0.657 | 0.173 | 16.6 |
| markers of the distance head, watershed of the contour map | 169 | 0.713 | 0.714 | 0.786 | 0.822 | 0.642 | 0.784 | 0.651 | 0.829 | 0.784 | 0.656 | 0.173 | 16.6 |
| markers of the distance head, watershed of −distance | 169 | 0.713 | 0.714 | 0.786 | 0.822 | 0.642 | 0.784 | 0.650 | 0.830 | 0.784 | 0.657 | 0.173 | 16.6 |
| markers of the distance head, watershed of contour − distance | 169 | 0.713 | 0.714 | 0.786 | 0.822 | 0.642 | 0.785 | 0.651 | 0.829 | 0.785 | 0.657 | 0.173 | 16.6 |
| tuned post-processing + unmarked components kept | 169 | 0.713 | 0.705 | 0.785 | 0.838 | 0.637 | 0.763 | 0.627 | 0.822 | 0.763 | 0.664 | 0.195 | 19.6 |
| watershed from the ground-truth markers (oracle) | 169 | 0.764 | 0.751 | 0.838 | 0.838 | 0.645 | 0.857 | 0.705 | 0.822 | 0.857 | 0.759 | 0.087 | 17.3 |
| sec. 11.1 layer, reproduced (its markers, its solve) | 169 | 0.689 | 0.696 | 0.767 | 0.844 | 0.640 | 0.784 | 0.647 | 0.825 | 0.784 | 0.657 | 0.250 | 19.7 |
| layer's markers, this model's foreground + watershed | 169 | 0.703 | 0.696 | 0.773 | 0.835 | 0.638 | 0.768 | 0.633 | 0.824 | 0.768 | 0.669 | 0.209 | 19.1 |
| layer's markers, layer's own foreground + watershed of its maps | 169 | 0.689 | 0.696 | 0.767 | 0.844 | 0.640 | 0.784 | 0.647 | 0.824 | 0.784 | 0.657 | 0.250 | 19.7 |
| this model's markers, layer's solve | 169 | 0.650 | 0.649 | 0.720 | 0.776 | 0.639 | 0.717 | 0.571 | 0.797 | 0.717 | 0.594 | 0.177 | 16.4 |
| ground truth instances | 169 | 1.000 | 1.000 | 1.000 | 1.000 | 0.629 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 18.5 |

**Adrenal_gland**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 148 | 0.716 | 0.676 | 0.774 | 0.808 | 0.554 | 0.694 | 0.582 | 0.840 | 0.694 | 0.655 | 0.378 | 18.4 |
| U-Net + contour head, watershed (b) | 148 | 0.719 | 0.689 | 0.783 | 0.811 | 0.551 | 0.712 | 0.605 | 0.850 | 0.712 | 0.713 | 0.444 | 20.1 |
| `bce_tuned` layer | 148 | 0.716 | 0.693 | 0.785 | 0.816 | 0.571 | 0.808 | 0.688 | 0.852 | 0.808 | 0.694 | 0.246 | 15.7 |
| `dist` layer | 148 | 0.711 | 0.686 | 0.781 | 0.821 | 0.558 | 0.815 | 0.690 | 0.846 | 0.815 | 0.694 | 0.256 | 17.1 |
| `dist` layer, GT markers | 148 | 0.864 | 0.822 | 0.931 | 0.864 | 0.581 | 0.961 | 0.833 | 0.867 | 0.961 | 0.872 | 0.027 | 15.6 |
| s > 0.5, components | 148 | 0.728 | 0.696 | 0.787 | 0.819 | 0.550 | 0.690 | 0.582 | 0.843 | 0.690 | 0.662 | 0.398 | 19.1 |
| tuned post-processing (markers of the distance head, watershed of the chosen relief) | 148 | 0.718 | 0.695 | 0.783 | 0.803 | 0.570 | 0.826 | 0.708 | 0.857 | 0.826 | 0.709 | 0.198 | 14.2 |
| markers of the distance head, watershed of the contour map | 148 | 0.718 | 0.695 | 0.783 | 0.803 | 0.570 | 0.826 | 0.708 | 0.857 | 0.826 | 0.709 | 0.198 | 14.2 |
| markers of the distance head, watershed of −distance | 148 | 0.718 | 0.695 | 0.783 | 0.803 | 0.570 | 0.826 | 0.708 | 0.857 | 0.826 | 0.709 | 0.198 | 14.2 |
| markers of the distance head, watershed of contour − distance | 148 | 0.718 | 0.695 | 0.783 | 0.803 | 0.570 | 0.826 | 0.708 | 0.857 | 0.826 | 0.709 | 0.198 | 14.2 |
| tuned post-processing + unmarked components kept | 148 | 0.728 | 0.697 | 0.788 | 0.818 | 0.553 | 0.800 | 0.681 | 0.851 | 0.800 | 0.714 | 0.228 | 16.5 |
| watershed from the ground-truth markers (oracle) | 148 | 0.781 | 0.745 | 0.843 | 0.819 | 0.571 | 0.864 | 0.736 | 0.852 | 0.864 | 0.787 | 0.083 | 14.7 |
| sec. 11.1 layer, reproduced (its markers, its solve) | 148 | 0.711 | 0.686 | 0.781 | 0.821 | 0.558 | 0.815 | 0.690 | 0.846 | 0.815 | 0.694 | 0.256 | 17.1 |
| layer's markers, this model's foreground + watershed | 148 | 0.729 | 0.697 | 0.788 | 0.817 | 0.554 | 0.798 | 0.680 | 0.852 | 0.798 | 0.714 | 0.213 | 16.2 |
| layer's markers, layer's own foreground + watershed of its maps | 148 | 0.711 | 0.686 | 0.781 | 0.821 | 0.558 | 0.816 | 0.690 | 0.846 | 0.816 | 0.694 | 0.256 | 17.1 |
| this model's markers, layer's solve | 148 | 0.653 | 0.609 | 0.701 | 0.747 | 0.559 | 0.776 | 0.636 | 0.819 | 0.776 | 0.660 | 0.203 | 14.1 |
| ground truth instances | 148 | 1.000 | 1.000 | 1.000 | 1.000 | 0.557 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 16.0 |

## Paired per-patch differences (2523 patches; bootstrap 95 % intervals; F1 / PQ / AJI dataset-level, bootstrapped over patches)

| comparison | IoU | BF₂ | edge align. | F1@0.5 | PQ | AJI |
|---|---|---|---|---|---|---|
| this model's post-processing − `dist` layer | +0.009 [+0.005, +0.014] | +0.008 [+0.004, +0.012] | +0.012 [+0.010, +0.014] | +0.003 [+0.000, +0.006] | +0.012 [+0.009, +0.014] | +0.005 [+0.002, +0.007] |
| this model's post-processing − `bce_tuned` layer | +0.010 [+0.007, +0.014] | +0.011 [+0.008, +0.015] | +0.004 [+0.002, +0.006] | +0.024 [+0.021, +0.027] | +0.024 [+0.022, +0.026] | +0.012 [+0.009, +0.015] |
| this model's post-processing − contour-head U-Net, watershed (b) | -0.000 [-0.004, +0.003] | -0.002 [-0.006, +0.002] | +0.024 [+0.023, +0.026] | +0.078 [+0.074, +0.082] | +0.070 [+0.068, +0.073] | +0.000 [-0.002, +0.003] |
| this model's post-processing − U-Net (sec. 6) logits | -0.001 [-0.005, +0.003] | +0.003 [-0.001, +0.007] | +0.015 [+0.013, +0.016] | +0.137 [+0.132, +0.141] | +0.123 [+0.119, +0.127] | +0.163 [+0.149, +0.176] |
| this model's post-processing − this model's logits | -0.005 [-0.008, -0.001] | -0.002 [-0.006, +0.002] | +0.020 [+0.019, +0.021] | +0.139 [+0.134, +0.143] | +0.122 [+0.118, +0.126] | +0.163 [+0.140, +0.191] |
| watershed of −distance − watershed of the contour map (same markers) | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.001] | +0.000 [+0.000, +0.001] | +0.000 [+0.000, +0.001] |
| watershed of contour − distance − watershed of the contour map (same markers) | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [-0.000, +0.000] | +0.000 [-0.000, +0.000] | +0.000 [-0.000, +0.000] |
| + unmarked components kept − this model's post-processing | +0.007 [+0.004, +0.010] | +0.004 [+0.000, +0.007] | -0.018 [-0.019, -0.016] | -0.014 [-0.016, -0.013] | -0.017 [-0.018, -0.016] | +0.007 [+0.006, +0.008] |
| ground-truth markers (oracle) − this model's post-processing | +0.053 [+0.050, +0.057] | +0.051 [+0.047, +0.055] | -0.004 [-0.006, -0.003] | +0.068 [+0.065, +0.072] | +0.049 [+0.047, +0.052] | +0.105 [+0.101, +0.109] |
| this model's oracle − `dist` layer's oracle | -0.088 [-0.092, -0.085] | -0.100 [-0.103, -0.097] | -0.003 [-0.004, -0.001] | -0.098 [-0.101, -0.094] | -0.103 [-0.105, -0.100] | -0.096 [-0.099, -0.094] |
| layer reproduced − `dist` layer (sanity) | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| layer's markers, this model's watershed − `dist` layer (same markers: watershed vs solve) | +0.016 [+0.013, +0.018] | +0.010 [+0.008, +0.013] | -0.006 [-0.007, -0.004] | -0.012 [-0.014, -0.010] | -0.005 [-0.006, -0.004] | +0.016 [+0.014, +0.017] |
| layer's markers, layer's own foreground + watershed − `dist` layer (same markers, same foreground) | -0.000 [-0.000, +0.000] | -0.000 [-0.000, +0.000] | -0.000 [-0.000, +0.000] | +0.000 [-0.000, +0.000] | -0.000 [-0.000, -0.000] | -0.000 [-0.000, +0.000] |
| this model's markers, layer's solve − this model's post-processing (same markers: solve vs watershed) | -0.082 [-0.084, -0.079] | -0.097 [-0.100, -0.095] | -0.028 [-0.030, -0.026] | -0.055 [-0.058, -0.052] | -0.074 [-0.077, -0.070] | -0.051 [-0.054, -0.048] |
| this model's markers, layer's solve − `dist` layer (same solve: markers swapped) | -0.072 [-0.077, -0.067] | -0.090 [-0.095, -0.084] | -0.016 [-0.019, -0.014] | -0.052 [-0.056, -0.048] | -0.062 [-0.065, -0.059] | -0.046 [-0.049, -0.043] |
| layer's markers, this model's watershed − this model's post-processing (same watershed: markers swapped) | +0.006 [+0.003, +0.009] | +0.002 [-0.001, +0.006] | -0.018 [-0.019, -0.016] | -0.015 [-0.017, -0.013] | -0.017 [-0.018, -0.015] | +0.011 [+0.009, +0.013] |

## By crowding (F1@0.5 / PQ / count error)

| patches | n | U-Net (sec. 6) | contour-head U-Net, watershed (b) | `dist` layer | this model: post-processing | + unmarked kept | oracle markers | layer's markers, watershed | this model's markers, layer's solve |
|---|---|---|---|---|---|---|---|---|---|
| < 10 nuclei | 486 | 0.608 / 0.485 / 0.68 | 0.596 / 0.479 / 0.81 | 0.687 / 0.551 / 0.67 | 0.730 / 0.595 / 0.33 | 0.687 / 0.554 / 0.49 | 0.829 / 0.669 / 0.09 | 0.688 / 0.555 / 0.46 | 0.646 / 0.499 / 0.33 |
| 10–30 | 1383 | 0.691 / 0.563 / 0.18 | 0.719 / 0.591 / 0.27 | 0.800 / 0.655 / 0.16 | 0.809 / 0.672 / 0.15 | 0.786 / 0.648 / 0.14 | 0.869 / 0.717 / 0.06 | 0.785 / 0.648 / 0.14 | 0.742 / 0.580 / 0.15 |
| 30–60 | 525 | 0.650 / 0.524 / 0.15 | 0.733 / 0.596 / 0.15 | 0.801 / 0.649 / 0.10 | 0.800 / 0.657 / 0.15 | 0.791 / 0.644 / 0.10 | 0.866 / 0.706 / 0.06 | 0.790 / 0.645 / 0.10 | 0.741 / 0.582 / 0.15 |
| > 60 | 129 | 0.588 / 0.469 / 0.24 | 0.700 / 0.562 / 0.13 | 0.765 / 0.616 / 0.15 | 0.753 / 0.614 / 0.23 | 0.756 / 0.610 / 0.14 | 0.841 / 0.674 / 0.07 | 0.756 / 0.612 / 0.16 | 0.738 / 0.593 / 0.24 |

## Marker quality by crowding (nuclei with one / none / several markers; background markers per patch)

| patches | this model: one | none | several | bg / patch | `dist` layer: one | none | several | bg / patch |
|---|---|---|---|---|---|---|---|---|
| < 10 nuclei | 72.5 % | 25.7 % | 1.8 % | 0.69 | 83.2 % | 14.2 % | 2.6 % | 1.83 |
| 10–30 | 78.6 % | 19.8 % | 1.7 % | 1.55 | 86.1 % | 11.9 % | 2.0 % | 3.43 |
| 30–60 | 77.0 % | 21.5 % | 1.6 % | 2.28 | 83.7 % | 14.5 % | 1.7 % | 4.67 |
| > 60 | 70.9 % | 28.1 % | 1.0 % | 3.25 | 77.0 % | 22.2 % | 0.7 % | 6.92 |

## Per tissue (IoU / F1 / PQ): this model's post-processing vs the `dist` layer vs watershed (b)

- Adrenal_gland (148): 0.718 / 0.826 / 0.708 vs 0.711 / 0.815 / 0.690 vs 0.719 / 0.712 / 0.605
- Bile-duct (103): 0.734 / 0.840 / 0.715 vs 0.721 / 0.829 / 0.693 vs 0.729 / 0.757 / 0.640
- Bladder (61): 0.725 / 0.818 / 0.700 vs 0.715 / 0.828 / 0.701 vs 0.723 / 0.732 / 0.618
- Breast (749): 0.717 / 0.822 / 0.662 vs 0.712 / 0.817 / 0.650 vs 0.722 / 0.757 / 0.605
- Cervix (52): 0.778 / 0.828 / 0.690 vs 0.759 / 0.824 / 0.681 vs 0.776 / 0.764 / 0.631
- Colon (468): 0.686 / 0.703 / 0.560 vs 0.684 / 0.710 / 0.560 vs 0.691 / 0.630 / 0.497
- Esophagus (128): 0.716 / 0.785 / 0.659 vs 0.735 / 0.795 / 0.654 vs 0.728 / 0.689 / 0.569
- HeadNeck (169): 0.713 / 0.785 / 0.651 vs 0.689 / 0.784 / 0.647 vs 0.682 / 0.688 / 0.565
- Kidney (56): 0.776 / 0.830 / 0.689 vs 0.748 / 0.824 / 0.672 vs 0.753 / 0.741 / 0.608
- Liver (66): 0.770 / 0.842 / 0.723 vs 0.752 / 0.834 / 0.704 vs 0.780 / 0.768 / 0.649
- Lung (53): 0.664 / 0.733 / 0.596 vs 0.686 / 0.759 / 0.608 vs 0.693 / 0.679 / 0.540
- Pancreatic (89): 0.745 / 0.822 / 0.686 vs 0.722 / 0.798 / 0.656 vs 0.749 / 0.732 / 0.608
- Skin (87): 0.663 / 0.808 / 0.681 vs 0.617 / 0.787 / 0.655 vs 0.640 / 0.722 / 0.601
- Testis (79): 0.766 / 0.840 / 0.716 vs 0.749 / 0.828 / 0.691 vs 0.766 / 0.761 / 0.642
- Thyroid (84): 0.751 / 0.834 / 0.714 vs 0.710 / 0.820 / 0.696 vs 0.729 / 0.759 / 0.646
