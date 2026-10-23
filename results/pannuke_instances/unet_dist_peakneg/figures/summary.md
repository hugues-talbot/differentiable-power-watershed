# The fair baseline for the distance-head layer: three-head U-Net + HoVer-Net-style post-processing (fold 1 → fold 2)

Run `results_pannuke_instances/unet_dist_peakneg/unet_dist`: 30 epochs, batch 16, binary foreground target (BCE), edge target ×1.0 on the contour head, distance head ×2.0 (MSE, rmax 12); post-processing: markers = h-maxima h 0.3 of the predicted distance map grown to thr 0.5, min area 16 px, marker watershed of the `both` relief inside s > 0.5, all four chosen by PQ on 300 patches of fold 3.

## Post-processing chosen on fold 3 (300 patches): {'mk_thr': 0.5, 'mk_min_area': 16, 'mk_h': 0.3, 'relief': 'both'}

| setting | PQ | F1@0.5 | AJI | count err. | n_pred | one | none | several | bg / patch |
|---|---|---|---|---|---|---|---|---|---|
| thr=0.5/min_area=16/h=0.3/both | 0.620 | 0.754 | 0.638 | 0.170 | 21.2 | 70.3 % | 24.6 % | 5.1 % | 1.68 |
| thr=0.5/min_area=16/h=0.3/contour | 0.618 | 0.752 | 0.632 | 0.170 | 21.2 | 70.3 % | 24.6 % | 5.1 % | 1.68 |
| thr=0.5/min_area=9/h=0.3/both | 0.617 | 0.754 | 0.643 | 0.165 | 22.9 | 72.1 % | 21.1 % | 6.9 % | 2.07 |
| thr=0.5/min_area=9/h=0.3/contour | 0.615 | 0.753 | 0.637 | 0.165 | 22.9 | 72.1 % | 21.1 % | 6.9 % | 2.07 |
| thr=0.4/min_area=16/h=0.3/both | 0.615 | 0.749 | 0.636 | 0.173 | 21.6 | 69.8 % | 24.1 % | 6.1 % | 1.73 |
| thr=0.4/min_area=16/h=0.3/contour | 0.612 | 0.746 | 0.629 | 0.173 | 21.6 | 69.8 % | 24.1 % | 6.1 % | 1.73 |
| thr=0.5/min_area=9/h=0.2/both | 0.611 | 0.745 | 0.630 | 0.173 | 21.8 | 69.1 % | 24.1 % | 6.8 % | 1.65 |
| thr=0.5/min_area=16/h=0.2/both | 0.610 | 0.741 | 0.620 | 0.201 | 19.9 | 66.9 % | 28.1 % | 4.9 % | 1.28 |
| thr=0.4/min_area=9/h=0.3/both | 0.610 | 0.747 | 0.643 | 0.170 | 23.7 | 71.9 % | 20.0 % | 8.0 % | 2.19 |
| thr=0.5/min_area=9/h=0.2/contour | 0.609 | 0.744 | 0.625 | 0.173 | 21.8 | 69.1 % | 24.1 % | 6.8 % | 1.65 |

(top 10 of 135 settings by PQ)

Best setting per relief, and the layer's own marker setting (thr 0.2 / min area 16 / h 0.2) with each relief:

| setting | PQ | F1@0.5 | AJI | count err. | n_pred |
|---|---|---|---|---|---|
| best contour: thr=0.5/min_area=16/h=0.3/contour | 0.618 | 0.752 | 0.632 | 0.170 | 21.2 |
| best dist: thr=0.5/min_area=16/h=0.3/dist | 0.552 | 0.672 | 0.564 | 0.170 | 21.2 |
| best both: thr=0.5/min_area=16/h=0.3/both | 0.620 | 0.754 | 0.638 | 0.170 | 21.2 |
| thr=0.2/min_area=16/h=0.2/contour | 0.527 | 0.654 | 0.585 | 0.212 | 24.3 |
| thr=0.2/min_area=16/h=0.2/dist | 0.495 | 0.613 | 0.556 | 0.212 | 24.3 |
| thr=0.2/min_area=16/h=0.2/both | 0.532 | 0.659 | 0.597 | 0.212 | 24.3 |

## All of fold 2

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6, binary target), s > 0.5, components | 2523 | 0.719 | 0.652 | 0.769 | 0.807 | 0.577 | 0.656 | 0.531 | 0.809 | 0.656 | 0.494 | 0.275 | 23.0 |
| U-Net + contour head (sec. 10.1, gap target), logits | 2523 | 0.719 | 0.658 | 0.774 | 0.809 | 0.574 | 0.682 | 0.556 | 0.814 | 0.682 | 0.571 | 0.303 | 25.2 |
| U-Net + contour head, tuned marker watershed (sec. 10.1 b) | 2523 | 0.718 | 0.658 | 0.774 | 0.809 | 0.568 | 0.715 | 0.583 | 0.816 | 0.715 | 0.657 | 0.344 | 27.2 |
| `bce_tuned` layer (sec. 11.1) | 2523 | 0.708 | 0.646 | 0.761 | 0.801 | 0.587 | 0.769 | 0.630 | 0.819 | 0.769 | 0.645 | 0.208 | 21.7 |
| `dist` layer, converged (sec. 11.1) | 2523 | 0.600 | 0.542 | 0.650 | 0.717 | 0.578 | 0.674 | 0.527 | 0.782 | 0.674 | 0.553 | 0.221 | 20.4 |
| `dist` layer + fallback markers | 2523 | 0.599 | 0.546 | 0.656 | 0.725 | 0.572 | 0.644 | 0.502 | 0.780 | 0.644 | 0.556 | 0.277 | 24.5 |
| `dist` layer, ground-truth markers (oracle) | 2523 | 0.855 | 0.792 | 0.918 | 0.856 | 0.591 | 0.956 | 0.800 | 0.837 | 0.956 | 0.854 | 0.020 | 23.3 |
| `dist` run: marker watershed of its contour map inside its s > 0.5 (sec. 11 `ws` row) | 2523 | 0.636 | 0.475 | 0.634 | 0.704 | 0.451 | 0.679 | 0.490 | 0.722 | 0.679 | 0.514 | 0.221 | 20.4 |
| this model: s > 0.5, components | 2523 | 0.720 | 0.649 | 0.767 | 0.808 | 0.566 | 0.604 | 0.489 | 0.810 | 0.604 | 0.481 | 0.488 | 28.2 |
| this model: tuned post-processing (markers of the distance head, watershed of the chosen relief) | 2523 | 0.704 | 0.640 | 0.752 | 0.786 | 0.593 | 0.751 | 0.613 | 0.816 | 0.751 | 0.632 | 0.216 | 20.9 |
| this model: markers of the distance head, watershed of the contour map | 2523 | 0.704 | 0.640 | 0.752 | 0.786 | 0.593 | 0.749 | 0.610 | 0.815 | 0.749 | 0.625 | 0.216 | 20.9 |
| this model: markers of the distance head, watershed of −distance | 2523 | 0.704 | 0.640 | 0.752 | 0.786 | 0.593 | 0.674 | 0.549 | 0.815 | 0.674 | 0.567 | 0.216 | 20.9 |
| this model: markers of the distance head, watershed of contour − distance | 2523 | 0.704 | 0.640 | 0.752 | 0.786 | 0.593 | 0.751 | 0.613 | 0.816 | 0.751 | 0.632 | 0.216 | 20.9 |
| this model: tuned post-processing + unmarked components kept | 2523 | 0.722 | 0.652 | 0.769 | 0.808 | 0.568 | 0.753 | 0.607 | 0.807 | 0.753 | 0.645 | 0.238 | 25.2 |
| this model: watershed from the ground-truth markers (oracle) | 2523 | 0.769 | 0.694 | 0.818 | 0.808 | 0.582 | 0.862 | 0.701 | 0.813 | 0.862 | 0.762 | 0.064 | 22.3 |
| this model: sec. 11.1 layer, reproduced (its markers, its solve) | 2523 | 0.600 | 0.542 | 0.650 | 0.717 | 0.578 | 0.674 | 0.527 | 0.782 | 0.674 | 0.553 | 0.221 | 20.4 |
| this model: layer's markers, this model's foreground + watershed | 2523 | 0.699 | 0.639 | 0.750 | 0.782 | 0.594 | 0.749 | 0.611 | 0.816 | 0.749 | 0.618 | 0.221 | 20.4 |
| this model: layer's markers, layer's own foreground + watershed of its maps | 2523 | 0.600 | 0.542 | 0.650 | 0.717 | 0.578 | 0.678 | 0.529 | 0.781 | 0.678 | 0.559 | 0.221 | 20.4 |
| this model: this model's markers, layer's solve | 2523 | 0.587 | 0.527 | 0.635 | 0.709 | 0.573 | 0.643 | 0.503 | 0.782 | 0.643 | 0.544 | 0.218 | 20.8 |
| this model: ground truth instances | 2523 | 1.000 | 1.000 | 1.000 | 1.000 | 0.559 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 23.7 |

## Marker quality (predicted markers against the ground-truth nuclei)

- 59872 nuclei in fold 2 (23.7 per patch).
- this model's markers: one 70.0 %, none 24.6 %, several 5.5 %, background 1.52 per patch, 20.9 markers per patch.
- the `dist` layer's markers (recomputed): one 70.1 %, none 25.4 %, several 4.6 %, background 1.52 per patch, 20.4 markers per patch.
- the `dist` layer's markers (sec. 11.1 run): one 70.1 %, none 25.4 %, several 4.6 %, background 1.52 per patch, 20.4 markers per patch.
- the `bce_tuned` layer's markers: one 77.7 %, none 21.1 %, several 1.2 %, background 2.69 per patch, 21.7 markers per patch.

## Inference cost

- U-Net forward: 2.4 ms per image; post-processing (markers + the three watersheds, one CPU core): 16 ms per image; the layer's converged solve: 121 ms per image (GPU).

## Per tissue type

**Breast**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 749 | 0.722 | 0.596 | 0.756 | 0.780 | 0.585 | 0.690 | 0.547 | 0.794 | 0.690 | 0.550 | 0.198 | 21.2 |
| U-Net + contour head, watershed (b) | 749 | 0.722 | 0.601 | 0.761 | 0.782 | 0.576 | 0.757 | 0.605 | 0.799 | 0.757 | 0.671 | 0.242 | 24.5 |
| `bce_tuned` layer | 749 | 0.716 | 0.594 | 0.752 | 0.780 | 0.598 | 0.805 | 0.644 | 0.800 | 0.805 | 0.659 | 0.145 | 21.2 |
| `dist` layer | 749 | 0.599 | 0.476 | 0.624 | 0.690 | 0.564 | 0.704 | 0.533 | 0.757 | 0.704 | 0.557 | 0.179 | 19.6 |
| `dist` layer, GT markers | 749 | 0.850 | 0.741 | 0.905 | 0.835 | 0.596 | 0.966 | 0.802 | 0.830 | 0.966 | 0.849 | 0.015 | 21.4 |
| s > 0.5, components | 749 | 0.718 | 0.588 | 0.748 | 0.779 | 0.575 | 0.635 | 0.504 | 0.795 | 0.635 | 0.562 | 0.393 | 25.9 |
| tuned post-processing (markers of the distance head, watershed of the chosen relief) | 749 | 0.704 | 0.579 | 0.736 | 0.761 | 0.601 | 0.784 | 0.626 | 0.799 | 0.784 | 0.644 | 0.173 | 19.8 |
| markers of the distance head, watershed of the contour map | 749 | 0.704 | 0.579 | 0.736 | 0.761 | 0.601 | 0.781 | 0.623 | 0.798 | 0.781 | 0.635 | 0.173 | 19.8 |
| markers of the distance head, watershed of −distance | 749 | 0.704 | 0.579 | 0.736 | 0.761 | 0.601 | 0.699 | 0.559 | 0.799 | 0.699 | 0.586 | 0.173 | 19.8 |
| markers of the distance head, watershed of contour − distance | 749 | 0.704 | 0.579 | 0.736 | 0.761 | 0.601 | 0.784 | 0.626 | 0.799 | 0.784 | 0.644 | 0.173 | 19.8 |
| tuned post-processing + unmarked components kept | 749 | 0.720 | 0.591 | 0.751 | 0.779 | 0.578 | 0.780 | 0.617 | 0.792 | 0.780 | 0.656 | 0.192 | 23.4 |
| watershed from the ground-truth markers (oracle) | 749 | 0.760 | 0.623 | 0.790 | 0.779 | 0.591 | 0.877 | 0.700 | 0.797 | 0.877 | 0.758 | 0.056 | 20.6 |
| sec. 11.1 layer, reproduced (its markers, its solve) | 749 | 0.599 | 0.476 | 0.624 | 0.690 | 0.564 | 0.704 | 0.533 | 0.757 | 0.704 | 0.557 | 0.179 | 19.6 |
| layer's markers, this model's foreground + watershed | 749 | 0.704 | 0.582 | 0.738 | 0.760 | 0.601 | 0.782 | 0.625 | 0.799 | 0.782 | 0.633 | 0.178 | 19.6 |
| layer's markers, layer's own foreground + watershed of its maps | 749 | 0.599 | 0.476 | 0.624 | 0.690 | 0.564 | 0.708 | 0.536 | 0.756 | 0.708 | 0.564 | 0.179 | 19.6 |
| this model's markers, layer's solve | 749 | 0.580 | 0.455 | 0.602 | 0.680 | 0.557 | 0.671 | 0.507 | 0.755 | 0.671 | 0.548 | 0.173 | 19.6 |
| ground truth instances | 749 | 1.000 | 1.000 | 1.000 | 1.000 | 0.553 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 21.7 |

**Colon**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 468 | 0.698 | 0.617 | 0.738 | 0.788 | 0.558 | 0.547 | 0.431 | 0.787 | 0.547 | 0.349 | 0.274 | 21.1 |
| U-Net + contour head, watershed (b) | 468 | 0.691 | 0.621 | 0.742 | 0.788 | 0.550 | 0.630 | 0.497 | 0.789 | 0.630 | 0.574 | 0.340 | 27.7 |
| `bce_tuned` layer | 468 | 0.685 | 0.606 | 0.728 | 0.781 | 0.573 | 0.693 | 0.551 | 0.796 | 0.693 | 0.576 | 0.216 | 21.7 |
| `dist` layer | 468 | 0.538 | 0.474 | 0.579 | 0.680 | 0.566 | 0.552 | 0.419 | 0.758 | 0.552 | 0.459 | 0.239 | 20.2 |
| `dist` layer, GT markers | 468 | 0.846 | 0.767 | 0.900 | 0.848 | 0.570 | 0.933 | 0.763 | 0.817 | 0.933 | 0.837 | 0.023 | 24.9 |
| s > 0.5, components | 468 | 0.704 | 0.617 | 0.739 | 0.792 | 0.544 | 0.503 | 0.396 | 0.787 | 0.503 | 0.298 | 0.457 | 27.3 |
| tuned post-processing (markers of the distance head, watershed of the chosen relief) | 468 | 0.682 | 0.599 | 0.715 | 0.769 | 0.572 | 0.659 | 0.518 | 0.786 | 0.659 | 0.554 | 0.233 | 22.2 |
| markers of the distance head, watershed of the contour map | 468 | 0.682 | 0.599 | 0.715 | 0.769 | 0.572 | 0.656 | 0.514 | 0.784 | 0.656 | 0.544 | 0.233 | 22.2 |
| markers of the distance head, watershed of −distance | 468 | 0.682 | 0.599 | 0.715 | 0.769 | 0.572 | 0.562 | 0.441 | 0.786 | 0.562 | 0.467 | 0.233 | 22.2 |
| markers of the distance head, watershed of contour − distance | 468 | 0.682 | 0.599 | 0.715 | 0.769 | 0.572 | 0.659 | 0.518 | 0.786 | 0.659 | 0.554 | 0.233 | 22.2 |
| tuned post-processing + unmarked components kept | 468 | 0.704 | 0.618 | 0.740 | 0.791 | 0.548 | 0.661 | 0.514 | 0.778 | 0.661 | 0.565 | 0.264 | 26.5 |
| watershed from the ground-truth markers (oracle) | 468 | 0.743 | 0.652 | 0.780 | 0.792 | 0.555 | 0.816 | 0.641 | 0.785 | 0.816 | 0.714 | 0.068 | 23.6 |
| sec. 11.1 layer, reproduced (its markers, its solve) | 468 | 0.538 | 0.474 | 0.579 | 0.680 | 0.566 | 0.552 | 0.419 | 0.758 | 0.552 | 0.459 | 0.239 | 20.2 |
| layer's markers, this model's foreground + watershed | 468 | 0.671 | 0.594 | 0.709 | 0.763 | 0.577 | 0.659 | 0.520 | 0.789 | 0.659 | 0.532 | 0.239 | 20.1 |
| layer's markers, layer's own foreground + watershed of its maps | 468 | 0.538 | 0.474 | 0.579 | 0.680 | 0.566 | 0.558 | 0.423 | 0.757 | 0.558 | 0.465 | 0.239 | 20.2 |
| this model's markers, layer's solve | 468 | 0.534 | 0.465 | 0.571 | 0.678 | 0.557 | 0.517 | 0.391 | 0.757 | 0.517 | 0.448 | 0.234 | 22.1 |
| ground truth instances | 468 | 1.000 | 1.000 | 1.000 | 1.000 | 0.539 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 25.4 |

**HeadNeck**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 169 | 0.672 | 0.658 | 0.744 | 0.835 | 0.648 | 0.640 | 0.519 | 0.811 | 0.640 | 0.556 | 0.424 | 20.2 |
| U-Net + contour head, watershed (b) | 169 | 0.682 | 0.675 | 0.756 | 0.839 | 0.638 | 0.688 | 0.565 | 0.821 | 0.688 | 0.660 | 0.474 | 23.6 |
| `bce_tuned` layer | 169 | 0.682 | 0.681 | 0.751 | 0.815 | 0.633 | 0.753 | 0.624 | 0.829 | 0.753 | 0.640 | 0.210 | 16.6 |
| `dist` layer | 169 | 0.601 | 0.602 | 0.672 | 0.753 | 0.647 | 0.645 | 0.508 | 0.788 | 0.645 | 0.538 | 0.219 | 16.2 |
| `dist` layer, GT markers | 169 | 0.855 | 0.848 | 0.935 | 0.883 | 0.646 | 0.961 | 0.814 | 0.848 | 0.961 | 0.859 | 0.032 | 18.2 |
| s > 0.5, components | 169 | 0.684 | 0.668 | 0.752 | 0.838 | 0.621 | 0.583 | 0.474 | 0.814 | 0.583 | 0.557 | 0.780 | 25.0 |
| tuned post-processing (markers of the distance head, watershed of the chosen relief) | 169 | 0.690 | 0.689 | 0.759 | 0.807 | 0.638 | 0.737 | 0.609 | 0.826 | 0.737 | 0.627 | 0.230 | 16.3 |
| markers of the distance head, watershed of the contour map | 169 | 0.690 | 0.689 | 0.759 | 0.807 | 0.638 | 0.736 | 0.607 | 0.824 | 0.736 | 0.619 | 0.230 | 16.3 |
| markers of the distance head, watershed of −distance | 169 | 0.690 | 0.689 | 0.759 | 0.807 | 0.638 | 0.673 | 0.553 | 0.822 | 0.673 | 0.576 | 0.230 | 16.3 |
| markers of the distance head, watershed of contour − distance | 169 | 0.690 | 0.689 | 0.759 | 0.807 | 0.638 | 0.737 | 0.609 | 0.826 | 0.737 | 0.627 | 0.230 | 16.3 |
| tuned post-processing + unmarked components kept | 169 | 0.696 | 0.684 | 0.767 | 0.837 | 0.621 | 0.739 | 0.602 | 0.815 | 0.739 | 0.642 | 0.257 | 20.6 |
| watershed from the ground-truth markers (oracle) | 169 | 0.766 | 0.750 | 0.842 | 0.838 | 0.636 | 0.860 | 0.704 | 0.819 | 0.860 | 0.761 | 0.085 | 17.4 |
| sec. 11.1 layer, reproduced (its markers, its solve) | 169 | 0.601 | 0.602 | 0.672 | 0.753 | 0.647 | 0.645 | 0.508 | 0.788 | 0.645 | 0.538 | 0.219 | 16.2 |
| layer's markers, this model's foreground + watershed | 169 | 0.684 | 0.684 | 0.755 | 0.804 | 0.642 | 0.742 | 0.610 | 0.822 | 0.742 | 0.617 | 0.214 | 16.2 |
| layer's markers, layer's own foreground + watershed of its maps | 169 | 0.601 | 0.602 | 0.672 | 0.753 | 0.647 | 0.649 | 0.511 | 0.787 | 0.649 | 0.544 | 0.219 | 16.2 |
| this model's markers, layer's solve | 169 | 0.598 | 0.599 | 0.670 | 0.748 | 0.638 | 0.612 | 0.483 | 0.789 | 0.612 | 0.523 | 0.231 | 16.3 |
| ground truth instances | 169 | 1.000 | 1.000 | 1.000 | 1.000 | 0.629 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 18.5 |

**Adrenal_gland**

| output | n | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6) | 148 | 0.716 | 0.676 | 0.774 | 0.808 | 0.554 | 0.694 | 0.582 | 0.840 | 0.694 | 0.655 | 0.378 | 18.4 |
| U-Net + contour head, watershed (b) | 148 | 0.719 | 0.689 | 0.783 | 0.811 | 0.551 | 0.712 | 0.605 | 0.850 | 0.712 | 0.713 | 0.444 | 20.1 |
| `bce_tuned` layer | 148 | 0.716 | 0.693 | 0.785 | 0.816 | 0.571 | 0.808 | 0.688 | 0.852 | 0.808 | 0.694 | 0.246 | 15.7 |
| `dist` layer | 148 | 0.620 | 0.591 | 0.681 | 0.733 | 0.578 | 0.728 | 0.595 | 0.817 | 0.728 | 0.613 | 0.265 | 13.8 |
| `dist` layer, GT markers | 148 | 0.860 | 0.817 | 0.926 | 0.861 | 0.582 | 0.955 | 0.825 | 0.863 | 0.955 | 0.867 | 0.023 | 15.7 |
| s > 0.5, components | 148 | 0.717 | 0.675 | 0.773 | 0.809 | 0.546 | 0.636 | 0.533 | 0.838 | 0.636 | 0.660 | 0.636 | 22.0 |
| tuned post-processing (markers of the distance head, watershed of the chosen relief) | 148 | 0.686 | 0.665 | 0.754 | 0.780 | 0.588 | 0.780 | 0.665 | 0.852 | 0.780 | 0.676 | 0.244 | 13.8 |
| markers of the distance head, watershed of the contour map | 148 | 0.686 | 0.665 | 0.754 | 0.780 | 0.588 | 0.779 | 0.663 | 0.851 | 0.779 | 0.670 | 0.244 | 13.8 |
| markers of the distance head, watershed of −distance | 148 | 0.686 | 0.665 | 0.754 | 0.780 | 0.588 | 0.744 | 0.634 | 0.852 | 0.744 | 0.648 | 0.244 | 13.8 |
| markers of the distance head, watershed of contour − distance | 148 | 0.686 | 0.665 | 0.754 | 0.780 | 0.588 | 0.780 | 0.665 | 0.852 | 0.780 | 0.676 | 0.244 | 13.8 |
| tuned post-processing + unmarked components kept | 148 | 0.717 | 0.678 | 0.775 | 0.809 | 0.550 | 0.770 | 0.647 | 0.840 | 0.770 | 0.696 | 0.256 | 17.2 |
| watershed from the ground-truth markers (oracle) | 148 | 0.764 | 0.721 | 0.826 | 0.809 | 0.565 | 0.856 | 0.724 | 0.846 | 0.856 | 0.778 | 0.086 | 14.7 |
| sec. 11.1 layer, reproduced (its markers, its solve) | 148 | 0.620 | 0.591 | 0.681 | 0.733 | 0.578 | 0.728 | 0.595 | 0.817 | 0.728 | 0.613 | 0.265 | 13.8 |
| layer's markers, this model's foreground + watershed | 148 | 0.686 | 0.664 | 0.752 | 0.779 | 0.586 | 0.781 | 0.664 | 0.850 | 0.781 | 0.669 | 0.261 | 13.7 |
| layer's markers, layer's own foreground + watershed of its maps | 148 | 0.620 | 0.591 | 0.681 | 0.733 | 0.578 | 0.731 | 0.597 | 0.816 | 0.731 | 0.616 | 0.265 | 13.8 |
| this model's markers, layer's solve | 148 | 0.606 | 0.578 | 0.667 | 0.723 | 0.580 | 0.700 | 0.570 | 0.814 | 0.700 | 0.601 | 0.249 | 13.7 |
| ground truth instances | 148 | 1.000 | 1.000 | 1.000 | 1.000 | 0.557 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 16.0 |

## Paired per-patch differences (2523 patches; bootstrap 95 % intervals; F1 / PQ / AJI dataset-level, bootstrapped over patches)

| comparison | IoU | BF₂ | edge align. | F1@0.5 | PQ | AJI |
|---|---|---|---|---|---|---|
| this model's post-processing − `dist` layer | +0.103 [+0.099, +0.107] | +0.102 [+0.098, +0.106] | +0.015 [+0.013, +0.017] | +0.077 [+0.072, +0.082] | +0.086 [+0.082, +0.090] | +0.080 [+0.076, +0.083] |
| this model's post-processing − `bce_tuned` layer | -0.004 [-0.007, -0.000] | -0.009 [-0.012, -0.005] | +0.006 [+0.004, +0.008] | -0.018 [-0.022, -0.015] | -0.017 [-0.020, -0.015] | -0.013 [-0.017, -0.010] |
| this model's post-processing − contour-head U-Net, watershed (b) | -0.014 [-0.018, -0.010] | -0.022 [-0.026, -0.018] | +0.026 [+0.025, +0.028] | +0.036 [+0.032, +0.040] | +0.029 [+0.026, +0.033] | -0.025 [-0.028, -0.022] |
| this model's post-processing − U-Net (sec. 6) logits | -0.015 [-0.019, -0.011] | -0.017 [-0.021, -0.012] | +0.017 [+0.015, +0.019] | +0.094 [+0.089, +0.100] | +0.082 [+0.077, +0.086] | +0.138 [+0.123, +0.152] |
| this model's post-processing − this model's logits | -0.016 [-0.020, -0.012] | -0.015 [-0.019, -0.010] | +0.028 [+0.026, +0.030] | +0.146 [+0.141, +0.152] | +0.123 [+0.118, +0.128] | +0.151 [+0.123, +0.184] |
| watershed of −distance − watershed of the contour map (same markers) | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.075 [-0.079, -0.071] | -0.061 [-0.064, -0.057] | -0.058 [-0.064, -0.052] |
| watershed of contour − distance − watershed of the contour map (same markers) | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.002 [+0.001, +0.003] | +0.002 [+0.002, +0.003] | +0.008 [+0.006, +0.009] |
| + unmarked components kept − this model's post-processing | +0.018 [+0.014, +0.022] | +0.017 [+0.013, +0.021] | -0.025 [-0.026, -0.023] | +0.002 [-0.000, +0.004] | -0.005 [-0.007, -0.003] | +0.013 [+0.012, +0.014] |
| ground-truth markers (oracle) − this model's post-processing | +0.065 [+0.062, +0.069] | +0.066 [+0.062, +0.071] | -0.011 [-0.013, -0.009] | +0.112 [+0.108, +0.116] | +0.088 [+0.085, +0.091] | +0.130 [+0.127, +0.133] |
| this model's oracle − `dist` layer's oracle | -0.086 [-0.089, -0.083] | -0.099 [-0.103, -0.096] | -0.008 [-0.010, -0.007] | -0.093 [-0.097, -0.090] | -0.099 [-0.102, -0.097] | -0.092 [-0.095, -0.090] |
| layer reproduced − `dist` layer (sanity) | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| layer's markers, this model's watershed − `dist` layer (same markers: watershed vs solve) | +0.099 [+0.096, +0.102] | +0.100 [+0.097, +0.103] | +0.017 [+0.015, +0.018] | +0.075 [+0.071, +0.079] | +0.084 [+0.080, +0.088] | +0.066 [+0.062, +0.069] |
| layer's markers, layer's own foreground + watershed − `dist` layer (same markers, same foreground) | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.004 [+0.003, +0.005] | +0.003 [+0.002, +0.003] | +0.006 [+0.005, +0.007] |
| this model's markers, layer's solve − this model's post-processing (same markers: solve vs watershed) | -0.116 [-0.120, -0.113] | -0.117 [-0.120, -0.114] | -0.020 [-0.022, -0.018] | -0.108 [-0.113, -0.103] | -0.110 [-0.114, -0.106] | -0.089 [-0.092, -0.085] |
| this model's markers, layer's solve − `dist` layer (same solve: markers swapped) | -0.013 [-0.016, -0.010] | -0.015 [-0.018, -0.012] | -0.005 [-0.006, -0.004] | -0.031 [-0.034, -0.029] | -0.024 [-0.026, -0.022] | -0.009 [-0.011, -0.007] |
| layer's markers, this model's watershed − this model's post-processing (same watershed: markers swapped) | -0.004 [-0.007, -0.002] | -0.002 [-0.005, +0.001] | +0.002 [+0.001, +0.003] | -0.002 [-0.005, +0.001] | -0.002 [-0.004, +0.000] | -0.014 [-0.017, -0.011] |

## By crowding (F1@0.5 / PQ / count error)

| patches | n | U-Net (sec. 6) | contour-head U-Net, watershed (b) | `dist` layer | this model: post-processing | + unmarked kept | oracle markers | layer's markers, watershed | this model's markers, layer's solve |
|---|---|---|---|---|---|---|---|---|---|
| < 10 nuclei | 486 | 0.608 / 0.485 / 0.68 | 0.596 / 0.479 / 0.81 | 0.568 / 0.437 / 0.41 | 0.671 / 0.543 / 0.41 | 0.654 / 0.519 / 0.54 | 0.821 / 0.658 / 0.09 | 0.667 / 0.538 / 0.40 | 0.540 / 0.413 / 0.41 |
| 10–30 | 1383 | 0.691 / 0.563 / 0.18 | 0.719 / 0.591 / 0.27 | 0.661 / 0.514 / 0.18 | 0.759 / 0.624 / 0.17 | 0.752 / 0.611 / 0.19 | 0.868 / 0.712 / 0.06 | 0.756 / 0.621 / 0.18 | 0.628 / 0.489 / 0.17 |
| 30–60 | 525 | 0.650 / 0.524 / 0.15 | 0.733 / 0.596 / 0.15 | 0.686 / 0.535 / 0.16 | 0.760 / 0.617 / 0.15 | 0.764 / 0.615 / 0.12 | 0.868 / 0.705 / 0.05 | 0.760 / 0.618 / 0.16 | 0.651 / 0.507 / 0.15 |
| > 60 | 129 | 0.588 / 0.469 / 0.24 | 0.700 / 0.562 / 0.13 | 0.705 / 0.564 / 0.26 | 0.728 / 0.589 / 0.23 | 0.752 / 0.602 / 0.12 | 0.846 / 0.675 / 0.06 | 0.725 / 0.586 / 0.26 | 0.684 / 0.546 / 0.24 |

## Marker quality by crowding (nuclei with one / none / several markers; background markers per patch)

| patches | this model: one | none | several | bg / patch | `dist` layer: one | none | several | bg / patch |
|---|---|---|---|---|---|---|---|---|
| < 10 nuclei | 62.0 % | 31.9 % | 6.1 % | 0.58 | 62.9 % | 31.4 % | 5.7 % | 0.63 |
| 10–30 | 70.5 % | 22.9 % | 6.6 % | 1.44 | 70.7 % | 23.4 % | 5.9 % | 1.45 |
| 30–60 | 71.3 % | 23.1 % | 5.6 % | 2.17 | 71.5 % | 24.1 % | 4.4 % | 2.18 |
| > 60 | 67.8 % | 29.7 % | 2.5 % | 3.34 | 67.4 % | 31.0 % | 1.6 % | 2.98 |

## Per tissue (IoU / F1 / PQ): this model's post-processing vs the `dist` layer vs watershed (b)

- Adrenal_gland (148): 0.686 / 0.780 / 0.665 vs 0.620 / 0.728 / 0.595 vs 0.719 / 0.712 / 0.605
- Bile-duct (103): 0.721 / 0.794 / 0.670 vs 0.632 / 0.719 / 0.578 vs 0.729 / 0.757 / 0.640
- Bladder (61): 0.697 / 0.783 / 0.667 vs 0.655 / 0.728 / 0.592 vs 0.723 / 0.732 / 0.618
- Breast (749): 0.704 / 0.784 / 0.626 vs 0.599 / 0.704 / 0.533 vs 0.722 / 0.757 / 0.605
- Cervix (52): 0.762 / 0.771 / 0.637 vs 0.679 / 0.709 / 0.554 vs 0.776 / 0.764 / 0.631
- Colon (468): 0.682 / 0.659 / 0.518 vs 0.538 / 0.552 / 0.419 vs 0.691 / 0.630 / 0.497
- Esophagus (128): 0.701 / 0.739 / 0.608 vs 0.574 / 0.647 / 0.501 vs 0.728 / 0.689 / 0.569
- HeadNeck (169): 0.690 / 0.737 / 0.609 vs 0.601 / 0.645 / 0.508 vs 0.682 / 0.688 / 0.565
- Kidney (56): 0.766 / 0.808 / 0.668 vs 0.712 / 0.801 / 0.647 vs 0.753 / 0.741 / 0.608
- Liver (66): 0.745 / 0.804 / 0.684 vs 0.663 / 0.739 / 0.609 vs 0.780 / 0.768 / 0.649
- Lung (53): 0.631 / 0.655 / 0.531 vs 0.557 / 0.628 / 0.492 vs 0.693 / 0.679 / 0.540
- Pancreatic (89): 0.741 / 0.774 / 0.643 vs 0.619 / 0.671 / 0.527 vs 0.749 / 0.732 / 0.608
- Skin (87): 0.644 / 0.781 / 0.652 vs 0.563 / 0.708 / 0.576 vs 0.640 / 0.722 / 0.601
- Testis (79): 0.756 / 0.797 / 0.672 vs 0.655 / 0.722 / 0.584 vs 0.766 / 0.761 / 0.642
- Thyroid (84): 0.729 / 0.806 / 0.685 vs 0.655 / 0.750 / 0.617 vs 0.729 / 0.759 / 0.646
