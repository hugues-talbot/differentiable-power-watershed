**Oxford-IIIT Pet 128 px: training losses**

| loss | variant | output | n | IoU | BF₁ | BF₂ | BF₃ | band acc. | soft px |
|---|---|---|---|---|---|---|---|---|---|
| bce | unet | logits | 3669 | 0.853 | 0.586 | 0.724 | – | 0.778 | 13.4 % |
| bce | rw_learned | logits | 3669 | 0.840 | 0.498 | 0.638 | – | 0.765 | 15.2 % |
| bce | rw_learned | layer, 20 steps | 3669 | 0.852 | 0.584 | 0.722 | – | 0.771 | 14.2 % |
| bce | rw_learned | converged | 3669 | 0.853 | 0.586 | 0.724 | – | 0.775 | 14.9 % |
| bce | rw_learned | PW limit | 300 | 0.822 | 0.561 | 0.695 | – | 0.749 | 0.0 % |
| boundary | unet | logits | 3669 | 0.864 | 0.629 | 0.769 | 0.837 | 0.787 | 7.6 % |
| boundary | rw_learned | logits | 3669 | 0.859 | 0.613 | 0.756 | 0.829 | 0.786 | 11.3 % |
| boundary | rw_learned | layer, 20 steps | 3669 | 0.864 | 0.634 | 0.776 | 0.844 | 0.787 | 9.1 % |
| boundary | rw_learned | converged | 3669 | 0.867 | 0.643 | 0.782 | 0.848 | 0.793 | 9.3 % |
| boundary | rw_learned | PW limit | 300 | 0.851 | 0.634 | 0.776 | 0.843 | 0.778 | 0.0 % |

**Paired per-image differences** (mean, 95 % bootstrap interval, fraction of images where the first is better)

- boundary: rw_learned layer − unet logits: iou: +0.000 [-0.001, +0.002] (better on 51 %) bf2: +0.007 [+0.005, +0.009] (better on 55 %) band_acc: -0.001 [-0.002, +0.000] (better on 49 %)
- boundary: rw_learned layer − its own logits: iou: +0.006 [+0.005, +0.006] (better on 70 %) bf2: +0.020 [+0.019, +0.021] (better on 77 %) band_acc: +0.001 [+0.000, +0.002] (better on 61 %)
- boundary: PW limit − converged on the 300 limit patches: iou: -0.020 [-0.026, -0.013] (better on 24 %) bf2: -0.012 [-0.017, -0.007] (better on 40 %) band_acc: -0.016 [-0.019, -0.012] (better on 21 %)
- boundary: PW limit − unet logits on the 300 limit patches: iou: -0.013 [-0.020, -0.005] (better on 42 %) bf2: +0.008 [-0.000, +0.017] (better on 56 %) band_acc: -0.008 [-0.013, -0.003] (better on 39 %)
