**PanNuke fold 1 → fold 2: training losses**

| loss | variant | output | n | IoU | BF₁ | BF₂ | BF₃ | band acc. | soft px | edge align. | F1@0.5 | PQ | count err. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bce | unet | logits | 2523 | 0.719 | 0.652 | 0.769 | 0.825 | 0.807 | 15.4 % | 0.577 | 0.656 | 0.531 | 0.275 |
| bce | rw_learned | logits | 2523 | 0.674 | 0.560 | 0.684 | 0.749 | 0.800 | 17.7 % | 0.481 | 0.083 | 0.067 | 25.352 |
| bce | rw_learned | layer, 20 steps | 2523 | 0.709 | 0.628 | 0.752 | 0.813 | 0.799 | 16.1 % | 0.579 | 0.604 | 0.482 | 0.337 |
| bce | rw_learned | converged | 2523 | 0.710 | 0.630 | 0.751 | 0.812 | 0.805 | 16.2 % | 0.572 | 0.602 | 0.480 | 0.322 |
| bce | rw_learned | PW limit | 307 | 0.661 | 0.591 | 0.711 | 0.768 | 0.771 | 0.0 % | 0.577 | 0.618 | 0.490 | 0.246 |
| boundary | unet | logits | 2523 | 0.718 | 0.669 | 0.787 | 0.841 | 0.819 | 13.2 % | 0.569 | 0.286 | 0.232 | 4.416 |
| boundary | rw_learned | logits | 2523 | 0.696 | 0.633 | 0.753 | 0.810 | 0.818 | 15.3 % | 0.535 | 0.141 | 0.114 | 13.280 |
| boundary | rw_learned | layer, 20 steps | 2523 | 0.714 | 0.656 | 0.778 | 0.835 | 0.816 | 13.2 % | 0.571 | 0.263 | 0.213 | 4.775 |
| boundary | rw_learned | converged | 2523 | 0.715 | 0.657 | 0.778 | 0.834 | 0.819 | 13.2 % | 0.566 | 0.285 | 0.231 | 4.231 |
| boundary | rw_learned | PW limit | 307 | 0.673 | 0.626 | 0.755 | 0.821 | 0.782 | 0.0 % | 0.559 | 0.140 | 0.111 | 8.779 |
| instance | unet | logits | 2523 | 0.719 | 0.651 | 0.769 | 0.827 | 0.807 | 17.0 % | 0.569 | 0.663 | 0.538 | 0.315 |
| instance | rw_learned | logits | 2523 | 0.667 | 0.544 | 0.672 | 0.740 | 0.798 | 21.8 % | 0.475 | 0.075 | 0.059 | 27.989 |
| instance | rw_learned | layer, 20 steps | 2523 | 0.699 | 0.617 | 0.744 | 0.807 | 0.791 | 18.3 % | 0.581 | 0.594 | 0.470 | 0.321 |
| instance | rw_learned | converged | 2523 | 0.701 | 0.619 | 0.742 | 0.804 | 0.799 | 17.8 % | 0.577 | 0.574 | 0.455 | 0.339 |
| instance | rw_learned | PW limit | 307 | 0.592 | 0.539 | 0.659 | 0.715 | 0.729 | 0.0 % | 0.589 | 0.593 | 0.465 | 0.312 |
| – | ground truth | binary mask | 2523 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.0 % | 0.559 | 0.913 | 0.883 | 0.088 |

**Breast**

| loss | variant | output | n | IoU | BF₂ | edge align. | F1@0.5 | PQ | count err. |
|---|---|---|---|---|---|---|---|---|---|
| bce | unet | logits | 749 | 0.722 | 0.756 | 0.585 | 0.690 | 0.547 | 0.198 |
| bce | rw_learned | logits | 749 | 0.695 | 0.690 | 0.493 | 0.088 | 0.069 | 21.544 |
| bce | rw_learned | layer, 20 steps | 749 | 0.713 | 0.738 | 0.589 | 0.635 | 0.498 | 0.313 |
| bce | rw_learned | converged | 749 | 0.714 | 0.738 | 0.582 | 0.627 | 0.491 | 0.294 |
| bce | rw_learned | PW limit | 89 | 0.667 | 0.703 | 0.586 | 0.684 | 0.535 | 0.174 |
| boundary | unet | logits | 749 | 0.723 | 0.778 | 0.578 | 0.285 | 0.227 | 4.213 |
| boundary | rw_learned | logits | 749 | 0.706 | 0.749 | 0.548 | 0.145 | 0.115 | 11.874 |
| boundary | rw_learned | layer, 20 steps | 749 | 0.720 | 0.769 | 0.579 | 0.270 | 0.215 | 4.322 |
| boundary | rw_learned | converged | 749 | 0.722 | 0.769 | 0.574 | 0.293 | 0.233 | 3.762 |
| boundary | rw_learned | PW limit | 89 | 0.701 | 0.761 | 0.565 | 0.140 | 0.109 | 7.163 |
| instance | unet | logits | 749 | 0.720 | 0.755 | 0.580 | 0.697 | 0.555 | 0.232 |
| instance | rw_learned | logits | 749 | 0.689 | 0.676 | 0.485 | 0.078 | 0.061 | 22.944 |
| instance | rw_learned | layer, 20 steps | 749 | 0.708 | 0.735 | 0.592 | 0.617 | 0.481 | 0.284 |
| instance | rw_learned | converged | 749 | 0.710 | 0.732 | 0.589 | 0.592 | 0.461 | 0.305 |
| instance | rw_learned | PW limit | 89 | 0.586 | 0.641 | 0.597 | 0.645 | 0.500 | 0.259 |
| – | ground truth | binary mask | 749 | 1.000 | 1.000 | 0.553 | 0.933 | 0.907 | 0.072 |

**Colon**

| loss | variant | output | n | IoU | BF₂ | edge align. | F1@0.5 | PQ | count err. |
|---|---|---|---|---|---|---|---|---|---|
| bce | unet | logits | 468 | 0.698 | 0.738 | 0.558 | 0.547 | 0.431 | 0.274 |
| bce | rw_learned | logits | 468 | 0.633 | 0.637 | 0.461 | 0.060 | 0.046 | 27.984 |
| bce | rw_learned | layer, 20 steps | 468 | 0.681 | 0.711 | 0.565 | 0.495 | 0.384 | 0.319 |
| bce | rw_learned | converged | 468 | 0.685 | 0.711 | 0.560 | 0.483 | 0.375 | 0.316 |
| bce | rw_learned | PW limit | 62 | 0.610 | 0.658 | 0.534 | 0.463 | 0.353 | 0.283 |
| boundary | unet | logits | 468 | 0.692 | 0.752 | 0.557 | 0.219 | 0.173 | 4.378 |
| boundary | rw_learned | logits | 468 | 0.664 | 0.716 | 0.529 | 0.108 | 0.085 | 13.211 |
| boundary | rw_learned | layer, 20 steps | 468 | 0.683 | 0.738 | 0.557 | 0.209 | 0.165 | 4.511 |
| boundary | rw_learned | converged | 468 | 0.687 | 0.740 | 0.553 | 0.230 | 0.182 | 3.661 |
| boundary | rw_learned | PW limit | 62 | 0.618 | 0.717 | 0.503 | 0.089 | 0.068 | 8.000 |
| instance | unet | logits | 468 | 0.698 | 0.736 | 0.544 | 0.548 | 0.431 | 0.289 |
| instance | rw_learned | logits | 468 | 0.632 | 0.631 | 0.455 | 0.050 | 0.039 | 33.207 |
| instance | rw_learned | layer, 20 steps | 468 | 0.667 | 0.700 | 0.566 | 0.482 | 0.371 | 0.300 |
| instance | rw_learned | converged | 468 | 0.674 | 0.696 | 0.563 | 0.441 | 0.341 | 0.351 |
| instance | rw_learned | PW limit | 62 | 0.497 | 0.575 | 0.554 | 0.418 | 0.318 | 0.349 |
| – | ground truth | binary mask | 468 | 1.000 | 1.000 | 0.539 | 0.836 | 0.796 | 0.123 |

**HeadNeck**

| loss | variant | output | n | IoU | BF₂ | edge align. | F1@0.5 | PQ | count err. |
|---|---|---|---|---|---|---|---|---|---|
| bce | unet | logits | 169 | 0.672 | 0.744 | 0.648 | 0.640 | 0.519 | 0.424 |
| bce | rw_learned | logits | 169 | 0.563 | 0.598 | 0.542 | 0.079 | 0.063 | 26.695 |
| bce | rw_learned | layer, 20 steps | 169 | 0.693 | 0.758 | 0.635 | 0.593 | 0.475 | 0.309 |
| bce | rw_learned | converged | 169 | 0.691 | 0.755 | 0.623 | 0.594 | 0.475 | 0.289 |
| boundary | unet | logits | 169 | 0.672 | 0.760 | 0.641 | 0.261 | 0.215 | 4.777 |
| boundary | rw_learned | logits | 169 | 0.622 | 0.698 | 0.593 | 0.129 | 0.105 | 14.122 |
| boundary | rw_learned | layer, 20 steps | 169 | 0.660 | 0.749 | 0.643 | 0.242 | 0.198 | 5.170 |
| boundary | rw_learned | converged | 169 | 0.660 | 0.747 | 0.639 | 0.260 | 0.213 | 4.803 |
| instance | unet | logits | 169 | 0.678 | 0.750 | 0.632 | 0.648 | 0.525 | 0.459 |
| instance | rw_learned | logits | 169 | 0.543 | 0.573 | 0.537 | 0.066 | 0.053 | 31.707 |
| instance | rw_learned | layer, 20 steps | 169 | 0.665 | 0.733 | 0.640 | 0.584 | 0.463 | 0.328 |
| instance | rw_learned | converged | 169 | 0.665 | 0.733 | 0.627 | 0.568 | 0.448 | 0.332 |
| – | ground truth | binary mask | 169 | 1.000 | 1.000 | 0.629 | 0.927 | 0.897 | 0.061 |

**Paired per-image differences** (mean, 95 % bootstrap interval, fraction of images where the first is better)

- bce: rw_learned layer − unet logits: iou: -0.009 [-0.012, -0.007] (better on 25 %) bf2: -0.017 [-0.020, -0.014] (better on 19 %) band_acc: -0.008 [-0.009, -0.008] (better on 19 %)
- bce: rw_learned layer − its own logits: iou: +0.035 [+0.030, +0.041] (better on 81 %) bf2: +0.068 [+0.062, +0.073] (better on 86 %) band_acc: -0.001 [-0.002, -0.001] (better on 42 %)
- bce: PW limit − converged on the 307 limit patches (means): iou: -0.046 bf2: -0.034 band_acc: -0.029
- bce: unet logits by crowding: 0–10 nuclei (n=486): IoU 0.641, count err 0.678; 10–30 nuclei (n=1383): IoU 0.734, count err 0.183; 30–60 nuclei (n=525): IoU 0.748, count err 0.153; 60–∞ nuclei (n=129): IoU 0.728, count err 0.236
- bce: rw_learned layer by crowding: 0–10 nuclei (n=486): IoU 0.637, count err 0.849; 10–30 nuclei (n=1383): IoU 0.724, count err 0.233; 30–60 nuclei (n=525): IoU 0.737, count err 0.156; 60–∞ nuclei (n=129): IoU 0.711, count err 0.252
- boundary: rw_learned layer − unet logits: iou: -0.005 [-0.007, -0.003] (better on 43 %) bf2: -0.009 [-0.011, -0.007] (better on 31 %) band_acc: -0.003 [-0.004, -0.002] (better on 36 %)
- boundary: rw_learned layer − its own logits: iou: +0.017 [+0.014, +0.021] (better on 71 %) bf2: +0.025 [+0.022, +0.029] (better on 78 %) band_acc: -0.002 [-0.003, -0.002] (better on 45 %)
- boundary: PW limit − converged on the 307 limit patches: iou: -0.034 [-0.040, -0.029] (better on 15 %) bf2: -0.013 [-0.016, -0.010] (better on 26 %) band_acc: -0.033 [-0.036, -0.029] (better on 2 %)
- boundary: PW limit − unet logits on the 307 limit patches: iou: -0.038 [-0.047, -0.029] (better on 18 %) bf2: -0.023 [-0.031, -0.016] (better on 18 %) band_acc: -0.032 [-0.036, -0.028] (better on 5 %)
- boundary: unet logits by crowding: 0–10 nuclei (n=486): IoU 0.630, count err 9.336; 10–30 nuclei (n=1383): IoU 0.736, count err 3.780; 30–60 nuclei (n=525): IoU 0.749, count err 2.315; 60–∞ nuclei (n=129): IoU 0.736, count err 1.244
- boundary: rw_learned layer by crowding: 0–10 nuclei (n=486): IoU 0.618, count err 10.470; 10–30 nuclei (n=1383): IoU 0.733, count err 4.017; 30–60 nuclei (n=525): IoU 0.747, count err 2.387; 60–∞ nuclei (n=129): IoU 0.734, count err 1.163
- unet boundary − unet bce: iou: -0.000 [-0.003, +0.002] (better on 48 %) bf2: +0.018 [+0.015, +0.021] (better on 72 %) band_acc: +0.011 [+0.010, +0.012] (better on 75 %)
- rw_learned layer boundary − rw_learned layer bce: iou: +0.004 [+0.001, +0.007] (better on 62 %) bf2: +0.026 [+0.022, +0.029] (better on 81 %) band_acc: +0.017 [+0.016, +0.017] (better on 85 %)
- instance: rw_learned layer − unet logits: iou: -0.019 [-0.022, -0.017] (better on 18 %) bf2: -0.025 [-0.028, -0.023] (better on 16 %) band_acc: -0.015 [-0.016, -0.015] (better on 13 %)
- instance: rw_learned layer − its own logits: iou: +0.032 [+0.027, +0.038] (better on 71 %) bf2: +0.072 [+0.066, +0.077] (better on 86 %) band_acc: -0.007 [-0.007, -0.006] (better on 28 %)
- instance: PW limit − converged on the 307 limit patches: iou: -0.108 [-0.122, -0.095] (better on 7 %) bf2: -0.076 [-0.088, -0.064] (better on 9 %) band_acc: -0.065 [-0.072, -0.059] (better on 3 %)
- instance: PW limit − unet logits on the 307 limit patches: iou: -0.124 [-0.137, -0.111] (better on 4 %) bf2: -0.106 [-0.119, -0.094] (better on 3 %) band_acc: -0.072 [-0.079, -0.066] (better on 4 %)
- instance: unet logits by crowding: 0–10 nuclei (n=486): IoU 0.644, count err 0.863; 10–30 nuclei (n=1383): IoU 0.734, count err 0.199; 30–60 nuclei (n=525): IoU 0.746, count err 0.140; 60–∞ nuclei (n=129): IoU 0.724, count err 0.201
- instance: rw_learned layer by crowding: 0–10 nuclei (n=486): IoU 0.627, count err 0.838; 10–30 nuclei (n=1383): IoU 0.715, count err 0.200; 30–60 nuclei (n=525): IoU 0.726, count err 0.177; 60–∞ nuclei (n=129): IoU 0.693, count err 0.268
- unet instance − unet bce: iou: -0.000 [-0.002, +0.002] (better on 44 %) bf2: +0.000 [-0.001, +0.002] (better on 47 %) band_acc: -0.001 [-0.001, -0.000] (better on 42 %)
- rw_learned layer instance − rw_learned layer bce: iou: -0.010 [-0.012, -0.008] (better on 30 %) bf2: -0.008 [-0.010, -0.006] (better on 36 %) band_acc: -0.007 [-0.008, -0.007] (better on 25 %)
