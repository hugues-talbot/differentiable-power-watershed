**All of fold 2**

| variant | output | n | IoU | BF₁ | BF₂ | BF₃ | band acc. | soft px | edge align. | F1@0.5 | PQ | AJI | count err. | count bias |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| unet_edge | logits | 2523 | 0.719 | 0.658 | 0.774 | 0.828 | 0.809 | 15.4 % | 0.574 | 0.682 | 0.556 | 0.571 | 0.303 | +1.4 |
| unet_edge | logits − contour | 2523 | 0.655 | 0.495 | 0.707 | 0.811 | 0.749 | 0.0 % | 0.512 | 0.665 | 0.492 | 0.617 | 0.415 | +6.6 |
| unet_edge | watershed (seg markers) | 2523 | 0.718 | 0.658 | 0.774 | 0.829 | 0.809 | 0.0 % | 0.568 | 0.715 | 0.583 | 0.657 | 0.344 | +3.5 |
| unet_edge | watershed (contour markers) | 2523 | 0.717 | 0.660 | 0.775 | 0.830 | 0.808 | 0.0 % | 0.566 | 0.693 | 0.566 | 0.673 | 0.416 | +6.6 |
| ground truth | binary mask | 2523 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.0 % | 0.553 | 0.998 | 0.990 | 0.995 | 0.002 | +0.0 |

**Breast**

| variant | output | n | IoU | BF₁ | BF₂ | edge align. | F1@0.5 | PQ | AJI | count err. |
|---|---|---|---|---|---|---|---|---|---|---|
| unet_edge | logits | 749 | 0.724 | 0.600 | 0.761 | 0.583 | 0.722 | 0.577 | 0.612 | 0.218 |
| unet_edge | logits − contour | 749 | 0.670 | 0.463 | 0.674 | 0.519 | 0.728 | 0.539 | 0.635 | 0.288 |
| unet_edge | watershed (seg markers) | 749 | 0.722 | 0.601 | 0.761 | 0.576 | 0.757 | 0.605 | 0.671 | 0.242 |
| unet_edge | watershed (contour markers) | 749 | 0.722 | 0.603 | 0.763 | 0.574 | 0.748 | 0.599 | 0.681 | 0.285 |
| ground truth | binary mask | 749 | 1.000 | 1.000 | 1.000 | 0.547 | 0.999 | 0.994 | 0.997 | 0.001 |

**Colon**

| variant | output | n | IoU | BF₁ | BF₂ | edge align. | F1@0.5 | PQ | AJI | count err. |
|---|---|---|---|---|---|---|---|---|---|---|
| unet_edge | logits | 468 | 0.694 | 0.620 | 0.741 | 0.556 | 0.582 | 0.460 | 0.435 | 0.287 |
| unet_edge | logits − contour | 468 | 0.631 | 0.486 | 0.670 | 0.498 | 0.532 | 0.378 | 0.540 | 0.447 |
| unet_edge | watershed (seg markers) | 468 | 0.691 | 0.621 | 0.742 | 0.550 | 0.630 | 0.497 | 0.574 | 0.340 |
| unet_edge | watershed (contour markers) | 468 | 0.688 | 0.622 | 0.743 | 0.546 | 0.577 | 0.456 | 0.596 | 0.459 |
| ground truth | binary mask | 468 | 1.000 | 1.000 | 1.000 | 0.532 | 0.997 | 0.975 | 0.989 | 0.002 |

**HeadNeck**

| variant | output | n | IoU | BF₁ | BF₂ | edge align. | F1@0.5 | PQ | AJI | count err. |
|---|---|---|---|---|---|---|---|---|---|---|
| unet_edge | logits | 169 | 0.683 | 0.675 | 0.756 | 0.641 | 0.661 | 0.541 | 0.596 | 0.428 |
| unet_edge | logits − contour | 169 | 0.606 | 0.481 | 0.693 | 0.579 | 0.611 | 0.434 | 0.590 | 0.614 |
| unet_edge | watershed (seg markers) | 169 | 0.682 | 0.675 | 0.756 | 0.638 | 0.688 | 0.565 | 0.660 | 0.474 |
| unet_edge | watershed (contour markers) | 169 | 0.680 | 0.674 | 0.755 | 0.634 | 0.650 | 0.533 | 0.666 | 0.610 |
| ground truth | binary mask | 169 | 1.000 | 1.000 | 1.000 | 0.626 | 1.000 | 0.994 | 0.996 | 0.000 |
