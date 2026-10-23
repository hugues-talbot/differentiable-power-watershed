# The fair baseline for the distance-head layer: three-head U-Net + HoVer-Net-style post-processing (fold 1 → fold 2)

Run `results_pannuke_instances/unet_dist_ext/unet_dist`: 30 epochs, batch 16, binary foreground target (BCE), edge target ×1.0 on the contour head, distance head ×2.0 (MSE, rmax 12); post-processing: markers = h-maxima h 0.2 of the predicted distance map grown to thr 0.5, min area 4 px, marker watershed of the `both` relief inside s > 0.5, all four chosen by PQ on 300 patches of fold 3.

## Post-processing chosen on fold 3 (300 patches): {'mk_thr': 0.5, 'mk_min_area': 4, 'mk_h': 0.2, 'relief': 'both'}

| setting | PQ | F1@0.5 | AJI | count err. | n_pred | one | none | several | bg / patch |
|---|---|---|---|---|---|---|---|---|---|
| thr=0.5/min_area=4/h=0.2/both | 0.662 | 0.798 | 0.666 | 0.162 | 21.1 | 77.4 % | 21.3 % | 1.3 % | 1.72 |
| thr=0.5/min_area=4/h=0.3/dist | 0.662 | 0.797 | 0.665 | 0.164 | 20.8 | 77.4 % | 21.8 % | 0.8 % | 1.66 |
| thr=0.5/min_area=4/h=0.3/both | 0.662 | 0.797 | 0.664 | 0.164 | 20.8 | 77.4 % | 21.8 % | 0.8 % | 1.66 |
| thr=0.5/min_area=4/h=0.3/contour | 0.662 | 0.798 | 0.664 | 0.164 | 20.8 | 77.4 % | 21.8 % | 0.8 % | 1.66 |
| thr=0.5/min_area=4/h=0.2/dist | 0.662 | 0.798 | 0.666 | 0.162 | 21.1 | 77.4 % | 21.3 % | 1.3 % | 1.72 |
| thr=0.5/min_area=4/h=0.2/contour | 0.662 | 0.798 | 0.665 | 0.162 | 21.1 | 77.4 % | 21.3 % | 1.3 % | 1.72 |
| thr=0.4/min_area=9/h=0.3/dist | 0.662 | 0.800 | 0.673 | 0.151 | 22.2 | 80.6 % | 18.5 % | 0.9 % | 2.25 |
| thr=0.4/min_area=9/h=0.2/both | 0.662 | 0.800 | 0.676 | 0.148 | 22.7 | 80.9 % | 17.6 % | 1.5 % | 2.36 |
| thr=0.4/min_area=9/h=0.3/both | 0.662 | 0.800 | 0.673 | 0.151 | 22.2 | 80.6 % | 18.5 % | 0.9 % | 2.25 |
| thr=0.4/min_area=16/h=0.2/both | 0.662 | 0.799 | 0.673 | 0.155 | 21.9 | 79.1 % | 19.5 % | 1.4 % | 2.15 |

(top 10 of 72 settings by PQ)

Best setting per relief, and the layer's own marker setting (thr 0.2 / min area 16 / h 0.2) with each relief:

| setting | PQ | F1@0.5 | AJI | count err. | n_pred |
|---|---|---|---|---|---|
| best contour: thr=0.5/min_area=4/h=0.3/contour | 0.662 | 0.798 | 0.664 | 0.164 | 20.8 |
| best dist: thr=0.5/min_area=4/h=0.3/dist | 0.662 | 0.797 | 0.665 | 0.164 | 20.8 |
| best both: thr=0.5/min_area=4/h=0.2/both | 0.662 | 0.798 | 0.666 | 0.162 | 21.1 |

## All of fold 2

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6, binary target), s > 0.5, components | 2523 | 0.719 | 0.652 | 0.769 | 0.807 | 0.577 | 0.656 | 0.531 | 0.809 | 0.656 | 0.494 | 0.275 | 23.0 |
| U-Net + contour head (sec. 10.1, gap target), logits | 2523 | 0.719 | 0.658 | 0.774 | 0.809 | 0.574 | 0.682 | 0.556 | 0.814 | 0.682 | 0.571 | 0.303 | 25.2 |
| U-Net + contour head, tuned marker watershed (sec. 10.1 b) | 2523 | 0.718 | 0.658 | 0.774 | 0.809 | 0.568 | 0.715 | 0.583 | 0.816 | 0.715 | 0.657 | 0.344 | 27.2 |
| `bce_tuned` layer (sec. 11.1) | 2523 | 0.708 | 0.646 | 0.761 | 0.801 | 0.587 | 0.769 | 0.630 | 0.819 | 0.769 | 0.645 | 0.208 | 21.7 |
| `dist` layer, converged (sec. 11.1) | 2523 | 0.707 | 0.647 | 0.762 | 0.811 | 0.580 | 0.791 | 0.641 | 0.811 | 0.791 | 0.653 | 0.239 | 24.3 |
| `dist` layer + fallback markers | 2523 | 0.704 | 0.645 | 0.760 | 0.812 | 0.582 | 0.776 | 0.629 | 0.810 | 0.776 | 0.652 | 0.311 | 25.7 |
| `dist` layer, ground-truth markers (oracle) | 2523 | 0.859 | 0.796 | 0.922 | 0.858 | 0.591 | 0.959 | 0.805 | 0.839 | 0.959 | 0.857 | 0.020 | 23.3 |
| `dist` run: marker watershed of its contour map inside its s > 0.5 (sec. 11 `ws` row) | 2523 | 0.620 | 0.436 | 0.614 | 0.698 | 0.422 | 0.709 | 0.496 | 0.699 | 0.709 | 0.556 | 0.241 | 24.3 |
| this model: s > 0.5, components | 2523 | 0.725 | 0.662 | 0.777 | 0.812 | 0.573 | 0.664 | 0.539 | 0.813 | 0.664 | 0.501 | 0.313 | 24.1 |
| this model: tuned post-processing (markers of the distance head, watershed of the chosen relief) | 2523 | 0.719 | 0.663 | 0.774 | 0.799 | 0.591 | 0.794 | 0.655 | 0.824 | 0.794 | 0.658 | 0.190 | 20.6 |
| this model: markers of the distance head, watershed of the contour map | 2523 | 0.719 | 0.663 | 0.774 | 0.799 | 0.591 | 0.794 | 0.654 | 0.824 | 0.794 | 0.658 | 0.190 | 20.6 |
| this model: markers of the distance head, watershed of −distance | 2523 | 0.719 | 0.663 | 0.774 | 0.799 | 0.591 | 0.794 | 0.655 | 0.825 | 0.794 | 0.658 | 0.190 | 20.6 |
| this model: markers of the distance head, watershed of contour − distance | 2523 | 0.719 | 0.663 | 0.774 | 0.799 | 0.591 | 0.794 | 0.655 | 0.824 | 0.794 | 0.658 | 0.190 | 20.6 |
| this model: tuned post-processing + unmarked components kept | 2523 | 0.725 | 0.662 | 0.777 | 0.812 | 0.574 | 0.780 | 0.637 | 0.817 | 0.780 | 0.666 | 0.202 | 23.9 |
| this model: watershed from the ground-truth markers (oracle) | 2523 | 0.774 | 0.706 | 0.827 | 0.813 | 0.586 | 0.867 | 0.708 | 0.816 | 0.867 | 0.765 | 0.066 | 22.2 |
| this model: ground truth instances | 2523 | 1.000 | 1.000 | 1.000 | 1.000 | 0.559 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 23.7 |

## Marker quality (predicted markers against the ground-truth nuclei)

- 59872 nuclei in fold 2 (23.7 per patch).
- this model's markers: one 76.6 %, none 21.8 %, several 1.6 %, background 1.64 per patch, 20.6 markers per patch.
- the `dist` layer's markers (sec. 11.1 run): one 83.9 %, none 14.5 %, several 1.6 %, background 3.58 per patch, 24.3 markers per patch.
- the `bce_tuned` layer's markers: one 77.7 %, none 21.1 %, several 1.2 %, background 2.69 per patch, 21.7 markers per patch.

## Inference cost

- U-Net forward: 0.8 ms per image; post-processing (markers + the three watersheds, one CPU core): 15 ms per image; the layer's converged solve: 0 ms per image (GPU).

## Per tissue type

**Breast**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 749 | 0.722 | 0.596 | 0.756 | 0.780 | 0.585 | 0.690 | 0.547 | 0.794 | 0.690 | 0.550 | 0.198 | 21.2 |
| U-Net + contour head, watershed (b) | 749 | 0.722 | 0.601 | 0.761 | 0.782 | 0.576 | 0.757 | 0.605 | 0.799 | 0.757 | 0.671 | 0.242 | 24.5 |
| `bce_tuned` layer | 749 | 0.716 | 0.594 | 0.752 | 0.780 | 0.598 | 0.805 | 0.644 | 0.800 | 0.805 | 0.659 | 0.145 | 21.2 |
| `dist` layer | 749 | 0.708 | 0.585 | 0.743 | 0.782 | 0.587 | 0.817 | 0.647 | 0.792 | 0.817 | 0.661 | 0.187 | 22.9 |
| `dist` layer, GT markers | 749 | 0.853 | 0.743 | 0.909 | 0.838 | 0.595 | 0.967 | 0.806 | 0.833 | 0.967 | 0.852 | 0.015 | 21.4 |
| s > 0.5, components | 749 | 0.723 | 0.600 | 0.760 | 0.784 | 0.584 | 0.699 | 0.558 | 0.798 | 0.699 | 0.573 | 0.257 | 22.2 |
| tuned post-processing (markers of the distance head, watershed of the chosen relief) | 749 | 0.717 | 0.601 | 0.758 | 0.774 | 0.600 | 0.825 | 0.665 | 0.806 | 0.825 | 0.673 | 0.155 | 19.6 |
| markers of the distance head, watershed of the contour map | 749 | 0.717 | 0.601 | 0.758 | 0.774 | 0.600 | 0.825 | 0.665 | 0.806 | 0.825 | 0.673 | 0.155 | 19.6 |
| markers of the distance head, watershed of −distance | 749 | 0.717 | 0.601 | 0.758 | 0.774 | 0.600 | 0.824 | 0.665 | 0.806 | 0.824 | 0.673 | 0.155 | 19.6 |
| markers of the distance head, watershed of contour − distance | 749 | 0.717 | 0.601 | 0.758 | 0.774 | 0.600 | 0.825 | 0.665 | 0.806 | 0.825 | 0.673 | 0.155 | 19.6 |
| tuned post-processing + unmarked components kept | 749 | 0.725 | 0.601 | 0.760 | 0.784 | 0.584 | 0.808 | 0.647 | 0.801 | 0.808 | 0.679 | 0.158 | 22.2 |
| watershed from the ground-truth markers (oracle) | 749 | 0.766 | 0.634 | 0.801 | 0.784 | 0.596 | 0.885 | 0.708 | 0.800 | 0.885 | 0.762 | 0.058 | 20.5 |
| ground truth instances | 749 | 1.000 | 1.000 | 1.000 | 1.000 | 0.553 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 21.7 |

**Colon**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 468 | 0.698 | 0.617 | 0.738 | 0.788 | 0.558 | 0.547 | 0.431 | 0.787 | 0.547 | 0.349 | 0.274 | 21.1 |
| U-Net + contour head, watershed (b) | 468 | 0.691 | 0.621 | 0.742 | 0.788 | 0.550 | 0.630 | 0.497 | 0.789 | 0.630 | 0.574 | 0.340 | 27.7 |
| `bce_tuned` layer | 468 | 0.685 | 0.606 | 0.728 | 0.781 | 0.573 | 0.693 | 0.551 | 0.796 | 0.693 | 0.576 | 0.216 | 21.7 |
| `dist` layer | 468 | 0.683 | 0.605 | 0.726 | 0.791 | 0.569 | 0.709 | 0.558 | 0.787 | 0.709 | 0.579 | 0.238 | 23.8 |
| `dist` layer, GT markers | 468 | 0.850 | 0.771 | 0.905 | 0.850 | 0.569 | 0.939 | 0.771 | 0.821 | 0.939 | 0.841 | 0.025 | 24.8 |
| s > 0.5, components | 468 | 0.706 | 0.628 | 0.747 | 0.795 | 0.554 | 0.558 | 0.441 | 0.790 | 0.558 | 0.326 | 0.278 | 22.6 |
| tuned post-processing (markers of the distance head, watershed of the chosen relief) | 468 | 0.696 | 0.620 | 0.736 | 0.780 | 0.572 | 0.708 | 0.564 | 0.796 | 0.708 | 0.571 | 0.207 | 20.4 |
| markers of the distance head, watershed of the contour map | 468 | 0.696 | 0.620 | 0.736 | 0.780 | 0.572 | 0.708 | 0.564 | 0.796 | 0.708 | 0.571 | 0.207 | 20.4 |
| markers of the distance head, watershed of −distance | 468 | 0.696 | 0.620 | 0.736 | 0.780 | 0.572 | 0.709 | 0.564 | 0.796 | 0.709 | 0.571 | 0.207 | 20.4 |
| markers of the distance head, watershed of contour − distance | 468 | 0.696 | 0.620 | 0.736 | 0.780 | 0.572 | 0.708 | 0.564 | 0.796 | 0.708 | 0.571 | 0.207 | 20.4 |
| tuned post-processing + unmarked components kept | 468 | 0.706 | 0.627 | 0.746 | 0.794 | 0.556 | 0.698 | 0.551 | 0.790 | 0.698 | 0.579 | 0.207 | 23.8 |
| watershed from the ground-truth markers (oracle) | 468 | 0.745 | 0.662 | 0.787 | 0.795 | 0.561 | 0.818 | 0.646 | 0.789 | 0.818 | 0.716 | 0.071 | 23.5 |
| ground truth instances | 468 | 1.000 | 1.000 | 1.000 | 1.000 | 0.539 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 25.4 |

**HeadNeck**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 169 | 0.672 | 0.658 | 0.744 | 0.835 | 0.648 | 0.640 | 0.519 | 0.811 | 0.640 | 0.556 | 0.424 | 20.2 |
| U-Net + contour head, watershed (b) | 169 | 0.682 | 0.675 | 0.756 | 0.839 | 0.638 | 0.688 | 0.565 | 0.821 | 0.688 | 0.660 | 0.474 | 23.6 |
| `bce_tuned` layer | 169 | 0.682 | 0.681 | 0.751 | 0.815 | 0.633 | 0.753 | 0.624 | 0.829 | 0.753 | 0.640 | 0.210 | 16.6 |
| `dist` layer | 169 | 0.701 | 0.711 | 0.782 | 0.846 | 0.631 | 0.784 | 0.647 | 0.826 | 0.784 | 0.651 | 0.203 | 19.8 |
| `dist` layer, GT markers | 169 | 0.864 | 0.858 | 0.946 | 0.888 | 0.651 | 0.964 | 0.819 | 0.850 | 0.964 | 0.862 | 0.026 | 18.2 |
| s > 0.5, components | 169 | 0.693 | 0.683 | 0.764 | 0.841 | 0.635 | 0.645 | 0.526 | 0.816 | 0.645 | 0.555 | 0.400 | 20.9 |
| tuned post-processing (markers of the distance head, watershed of the chosen relief) | 169 | 0.710 | 0.711 | 0.784 | 0.825 | 0.641 | 0.788 | 0.655 | 0.831 | 0.788 | 0.658 | 0.179 | 16.6 |
| markers of the distance head, watershed of the contour map | 169 | 0.710 | 0.711 | 0.784 | 0.825 | 0.641 | 0.789 | 0.655 | 0.831 | 0.789 | 0.658 | 0.179 | 16.6 |
| markers of the distance head, watershed of −distance | 169 | 0.710 | 0.711 | 0.784 | 0.825 | 0.641 | 0.787 | 0.654 | 0.831 | 0.787 | 0.658 | 0.179 | 16.6 |
| markers of the distance head, watershed of contour − distance | 169 | 0.710 | 0.711 | 0.784 | 0.825 | 0.641 | 0.788 | 0.655 | 0.831 | 0.788 | 0.658 | 0.179 | 16.6 |
| tuned post-processing + unmarked components kept | 169 | 0.700 | 0.690 | 0.771 | 0.840 | 0.634 | 0.764 | 0.628 | 0.822 | 0.764 | 0.667 | 0.218 | 19.9 |
| watershed from the ground-truth markers (oracle) | 169 | 0.768 | 0.756 | 0.843 | 0.841 | 0.643 | 0.865 | 0.711 | 0.822 | 0.865 | 0.761 | 0.084 | 17.4 |
| ground truth instances | 169 | 1.000 | 1.000 | 1.000 | 1.000 | 0.629 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 18.5 |

**Adrenal_gland**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 148 | 0.716 | 0.676 | 0.774 | 0.808 | 0.554 | 0.694 | 0.582 | 0.840 | 0.694 | 0.655 | 0.378 | 18.4 |
| U-Net + contour head, watershed (b) | 148 | 0.719 | 0.689 | 0.783 | 0.811 | 0.551 | 0.712 | 0.605 | 0.850 | 0.712 | 0.713 | 0.444 | 20.1 |
| `bce_tuned` layer | 148 | 0.716 | 0.693 | 0.785 | 0.816 | 0.571 | 0.808 | 0.688 | 0.852 | 0.808 | 0.694 | 0.246 | 15.7 |
| `dist` layer | 148 | 0.709 | 0.688 | 0.779 | 0.824 | 0.562 | 0.823 | 0.696 | 0.846 | 0.823 | 0.696 | 0.260 | 17.1 |
| `dist` layer, GT markers | 148 | 0.866 | 0.826 | 0.930 | 0.866 | 0.583 | 0.961 | 0.833 | 0.866 | 0.961 | 0.870 | 0.026 | 15.6 |
| s > 0.5, components | 148 | 0.726 | 0.692 | 0.786 | 0.817 | 0.552 | 0.706 | 0.593 | 0.840 | 0.706 | 0.667 | 0.379 | 18.5 |
| tuned post-processing (markers of the distance head, watershed of the chosen relief) | 148 | 0.711 | 0.690 | 0.779 | 0.797 | 0.579 | 0.824 | 0.706 | 0.857 | 0.824 | 0.705 | 0.221 | 13.9 |
| markers of the distance head, watershed of the contour map | 148 | 0.711 | 0.690 | 0.779 | 0.797 | 0.579 | 0.823 | 0.706 | 0.857 | 0.823 | 0.705 | 0.221 | 13.9 |
| markers of the distance head, watershed of −distance | 148 | 0.711 | 0.690 | 0.779 | 0.797 | 0.579 | 0.824 | 0.706 | 0.857 | 0.824 | 0.705 | 0.221 | 13.9 |
| markers of the distance head, watershed of contour − distance | 148 | 0.711 | 0.690 | 0.779 | 0.797 | 0.579 | 0.824 | 0.706 | 0.857 | 0.824 | 0.705 | 0.221 | 13.9 |
| tuned post-processing + unmarked components kept | 148 | 0.726 | 0.693 | 0.786 | 0.816 | 0.554 | 0.798 | 0.676 | 0.848 | 0.798 | 0.714 | 0.224 | 16.6 |
| watershed from the ground-truth markers (oracle) | 148 | 0.776 | 0.738 | 0.838 | 0.817 | 0.571 | 0.868 | 0.736 | 0.848 | 0.868 | 0.786 | 0.084 | 14.7 |
| ground truth instances | 148 | 1.000 | 1.000 | 1.000 | 1.000 | 0.557 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 16.0 |

## Paired per-patch differences (2523 patches; bootstrap 95 % intervals; F1 / PQ / AJI dataset-level, bootstrapped over patches)

| comparison | IoU | BF₂ | edge align. | F1@0.5 | PQ | AJI |
|---|---|---|---|---|---|---|
| this model's post-processing − `dist` layer | +0.012 [+0.008, +0.017] | +0.012 [+0.008, +0.016] | +0.012 [+0.010, +0.013] | +0.003 [+0.001, +0.006] | +0.013 [+0.011, +0.015] | +0.006 [+0.003, +0.009] |
| this model's post-processing − `bce_tuned` layer | +0.011 [+0.008, +0.015] | +0.013 [+0.010, +0.017] | +0.004 [+0.002, +0.005] | +0.025 [+0.022, +0.028] | +0.025 [+0.022, +0.027] | +0.013 [+0.010, +0.016] |
| this model's post-processing − contour-head U-Net, watershed (b) | +0.001 [-0.002, +0.005] | -0.000 [-0.004, +0.004] | +0.024 [+0.023, +0.026] | +0.079 [+0.075, +0.083] | +0.071 [+0.069, +0.074] | +0.001 [-0.001, +0.004] |
| this model's post-processing − U-Net (sec. 6) logits | +0.000 [-0.003, +0.004] | +0.005 [+0.001, +0.009] | +0.015 [+0.013, +0.016] | +0.138 [+0.133, +0.142] | +0.124 [+0.120, +0.128] | +0.164 [+0.150, +0.177] |
| this model's post-processing − this model's logits | -0.006 [-0.009, -0.002] | -0.003 [-0.006, +0.001] | +0.019 [+0.018, +0.021] | +0.130 [+0.125, +0.135] | +0.115 [+0.111, +0.119] | +0.158 [+0.138, +0.179] |
| watershed of −distance − watershed of the contour map (same markers) | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.000 [-0.001, +0.000] | +0.000 [-0.000, +0.001] | +0.000 [-0.000, +0.001] |
| watershed of contour − distance − watershed of the contour map (same markers) | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [-0.000, +0.000] | +0.000 [-0.000, +0.000] | +0.000 [+0.000, +0.000] |
| + unmarked components kept − this model's post-processing | +0.006 [+0.003, +0.009] | +0.002 [-0.001, +0.006] | -0.017 [-0.019, -0.016] | -0.014 [-0.016, -0.012] | -0.017 [-0.019, -0.016] | +0.007 [+0.006, +0.008] |
| ground-truth markers (oracle) − this model's post-processing | +0.055 [+0.052, +0.059] | +0.052 [+0.049, +0.056] | -0.004 [-0.006, -0.002] | +0.073 [+0.070, +0.077] | +0.053 [+0.051, +0.056] | +0.107 [+0.103, +0.111] |
| this model's oracle − `dist` layer's oracle | -0.085 [-0.088, -0.082] | -0.095 [-0.099, -0.092] | -0.004 [-0.006, -0.003] | -0.091 [-0.095, -0.088] | -0.097 [-0.099, -0.094] | -0.092 [-0.095, -0.090] |

## By crowding (F1@0.5 / PQ / count error)

| patches | n | U-Net (sec. 6) | contour-head U-Net, watershed (b) | `dist` layer | this model: post-processing | + unmarked kept | oracle markers |
|---|---|---|---|---|---|---|---|
| < 10 nuclei | 486 | 0.608 / 0.485 / 0.68 | 0.596 / 0.479 / 0.81 | 0.689 / 0.553 / 0.64 | 0.727 / 0.592 / 0.35 | 0.683 / 0.549 / 0.50 | 0.841 / 0.678 / 0.08 |
| 10–30 | 1383 | 0.691 / 0.563 / 0.18 | 0.719 / 0.591 / 0.27 | 0.802 / 0.655 / 0.16 | 0.809 / 0.672 / 0.15 | 0.787 / 0.648 / 0.14 | 0.873 / 0.720 / 0.06 |
| 30–60 | 525 | 0.650 / 0.524 / 0.15 | 0.733 / 0.596 / 0.15 | 0.801 / 0.648 / 0.10 | 0.803 / 0.660 / 0.14 | 0.793 / 0.646 / 0.10 | 0.874 / 0.712 / 0.06 |
| > 60 | 129 | 0.588 / 0.469 / 0.24 | 0.700 / 0.562 / 0.13 | 0.763 / 0.615 / 0.15 | 0.754 / 0.613 / 0.23 | 0.761 / 0.613 / 0.14 | 0.848 / 0.678 / 0.07 |

## Marker quality by crowding (nuclei with one / none / several markers; background markers per patch)

| patches | this model: one | none | several | bg / patch | `dist` layer: one | none | several | bg / patch |
|---|---|---|---|---|---|---|---|---|
| < 10 nuclei | 72.1 % | 25.7 % | 2.2 % | 0.67 | 83.3 % | 14.3 % | 2.3 % | 1.81 |
| 10–30 | 79.0 % | 19.2 % | 1.7 % | 1.58 | 86.7 % | 11.4 % | 1.9 % | 3.48 |
| 30–60 | 77.4 % | 21.0 % | 1.5 % | 2.31 | 84.1 % | 14.3 % | 1.6 % | 4.73 |
| > 60 | 70.4 % | 28.5 % | 1.1 % | 3.24 | 77.1 % | 22.2 % | 0.7 % | 6.62 |

## Per tissue (IoU / F1 / PQ): this model's post-processing vs the `dist` layer vs watershed (b)

- Adrenal_gland (148): 0.711 / 0.824 / 0.706 vs 0.709 / 0.823 / 0.696 vs 0.719 / 0.712 / 0.605
- Bile-duct (103): 0.732 / 0.844 / 0.719 vs 0.717 / 0.824 / 0.690 vs 0.729 / 0.757 / 0.640
- Bladder (61): 0.729 / 0.831 / 0.714 vs 0.712 / 0.827 / 0.697 vs 0.723 / 0.732 / 0.618
- Breast (749): 0.717 / 0.825 / 0.665 vs 0.708 / 0.817 / 0.647 vs 0.722 / 0.757 / 0.605
- Cervix (52): 0.776 / 0.824 / 0.688 vs 0.730 / 0.826 / 0.681 vs 0.776 / 0.764 / 0.631
- Colon (468): 0.696 / 0.708 / 0.564 vs 0.683 / 0.709 / 0.558 vs 0.691 / 0.630 / 0.497
- Esophagus (128): 0.725 / 0.790 / 0.662 vs 0.734 / 0.798 / 0.655 vs 0.728 / 0.689 / 0.569
- HeadNeck (169): 0.710 / 0.788 / 0.655 vs 0.701 / 0.784 / 0.647 vs 0.682 / 0.688 / 0.565
- Kidney (56): 0.774 / 0.833 / 0.690 vs 0.742 / 0.816 / 0.665 vs 0.753 / 0.741 / 0.608
- Liver (66): 0.761 / 0.835 / 0.718 vs 0.750 / 0.835 / 0.706 vs 0.780 / 0.768 / 0.649
- Lung (53): 0.657 / 0.713 / 0.580 vs 0.690 / 0.764 / 0.612 vs 0.693 / 0.679 / 0.540
- Pancreatic (89): 0.747 / 0.814 / 0.680 vs 0.724 / 0.802 / 0.657 vs 0.749 / 0.732 / 0.608
- Skin (87): 0.656 / 0.803 / 0.678 vs 0.617 / 0.791 / 0.660 vs 0.640 / 0.722 / 0.601
- Testis (79): 0.770 / 0.845 / 0.721 vs 0.747 / 0.821 / 0.684 vs 0.766 / 0.761 / 0.642
- Thyroid (84): 0.744 / 0.838 / 0.720 vs 0.712 / 0.830 / 0.702 vs 0.729 / 0.759 / 0.646
