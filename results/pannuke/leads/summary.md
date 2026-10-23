**PanNuke fold 1 → fold 2: training losses**

| loss | variant | output | n | IoU | BF₁ | BF₂ | BF₃ | band acc. | soft px | edge align. | F1@0.5 | PQ | count err. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bce | unet | logits | 2523 | 0.719 | 0.652 | 0.769 | 0.825 | 0.807 | 15.4 % | 0.577 | 0.656 | 0.531 | 0.275 |
| bce | rw_learned | logits | 2523 | 0.674 | 0.560 | 0.684 | 0.749 | 0.800 | 17.7 % | 0.481 | 0.083 | 0.067 | 25.352 |
| bce | rw_learned | layer, 20 steps | 2523 | 0.709 | 0.628 | 0.752 | 0.813 | 0.799 | 16.1 % | 0.579 | 0.604 | 0.482 | 0.337 |
| bce | rw_learned | converged | 2523 | 0.710 | 0.630 | 0.751 | 0.812 | 0.805 | 16.2 % | 0.572 | 0.602 | 0.480 | 0.322 |
| bce | rw_learned | PW limit | 307 | 0.661 | 0.591 | 0.711 | 0.768 | 0.771 | 0.0 % | 0.577 | 0.618 | 0.490 | 0.246 |
| dice | unet | logits | 2523 | 0.697 | 0.632 | 0.737 | 0.786 | 0.836 | 14.2 % | 0.555 | 0.612 | 0.498 | 0.876 |
| dice | rw_learned | logits | 2523 | 0.639 | 0.475 | 0.565 | 0.612 | 0.833 | 15.8 % | 0.404 | 0.234 | 0.187 | 9.290 |
| dice | rw_learned | layer, 20 steps | 2523 | 0.693 | 0.621 | 0.728 | 0.778 | 0.831 | 13.6 % | 0.546 | 0.595 | 0.482 | 0.878 |
| dice | rw_learned | converged | 2523 | 0.690 | 0.621 | 0.728 | 0.778 | 0.833 | 14.3 % | 0.544 | 0.601 | 0.486 | 0.818 |
| dice | rw_learned | PW limit | 307 | 0.658 | 0.591 | 0.695 | 0.748 | 0.815 | 0.0 % | 0.518 | 0.633 | 0.502 | 0.487 |
| edge_bce | rw_learned | logits | 2523 | 0.550 | 0.452 | 0.604 | 0.706 | 0.691 | 23.8 % | 0.403 | 0.019 | 0.013 | 72.405 |
| edge_bce | rw_learned | layer, 20 steps | 2523 | 0.703 | 0.630 | 0.752 | 0.813 | 0.792 | 14.1 % | 0.554 | 0.446 | 0.355 | 1.252 |
| edge_bce | rw_learned | converged | 2523 | 0.707 | 0.635 | 0.754 | 0.814 | 0.797 | 14.1 % | 0.558 | 0.435 | 0.347 | 1.111 |
| edge_bce | rw_learned | PW limit | 307 | 0.684 | 0.624 | 0.744 | 0.802 | 0.783 | 0.0 % | 0.569 | 0.501 | 0.395 | 0.489 |
| edge_dice | rw_learned | logits | 2523 | 0.633 | 0.438 | 0.528 | 0.584 | 0.829 | 23.9 % | 0.375 | 0.086 | 0.068 | 30.633 |
| edge_dice | rw_learned | layer, 20 steps | 2523 | 0.690 | 0.608 | 0.715 | 0.767 | 0.830 | 13.9 % | 0.525 | 0.505 | 0.408 | 1.564 |
| edge_dice | rw_learned | converged | 2523 | 0.689 | 0.607 | 0.714 | 0.765 | 0.831 | 14.0 % | 0.526 | 0.498 | 0.402 | 1.504 |
| edge_dice | rw_learned | PW limit | 307 | 0.646 | 0.553 | 0.662 | 0.721 | 0.807 | 0.0 % | 0.495 | 0.428 | 0.339 | 1.404 |
| – | ground truth | binary mask | 2523 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.0 % | 0.559 | 0.913 | 0.883 | 0.088 |

**Breast**

| loss | variant | output | n | IoU | BF₂ | edge align. | F1@0.5 | PQ | count err. |
|---|---|---|---|---|---|---|---|---|---|
| bce | unet | logits | 749 | 0.722 | 0.756 | 0.585 | 0.690 | 0.547 | 0.198 |
| bce | rw_learned | logits | 749 | 0.695 | 0.690 | 0.493 | 0.088 | 0.069 | 21.544 |
| bce | rw_learned | layer, 20 steps | 749 | 0.713 | 0.738 | 0.589 | 0.635 | 0.498 | 0.313 |
| bce | rw_learned | converged | 749 | 0.714 | 0.738 | 0.582 | 0.627 | 0.491 | 0.294 |
| bce | rw_learned | PW limit | 89 | 0.667 | 0.703 | 0.586 | 0.684 | 0.535 | 0.174 |
| dice | unet | logits | 749 | 0.712 | 0.741 | 0.567 | 0.649 | 0.520 | 0.589 |
| dice | rw_learned | logits | 749 | 0.664 | 0.570 | 0.393 | 0.257 | 0.201 | 6.679 |
| dice | rw_learned | layer, 20 steps | 749 | 0.703 | 0.724 | 0.555 | 0.620 | 0.492 | 0.664 |
| dice | rw_learned | converged | 749 | 0.700 | 0.724 | 0.554 | 0.628 | 0.499 | 0.600 |
| dice | rw_learned | PW limit | 89 | 0.672 | 0.693 | 0.518 | 0.695 | 0.542 | 0.233 |
| edge_bce | rw_learned | logits | 749 | 0.569 | 0.602 | 0.400 | 0.017 | 0.011 | 71.763 |
| edge_bce | rw_learned | layer, 20 steps | 749 | 0.708 | 0.740 | 0.560 | 0.460 | 0.360 | 1.144 |
| edge_bce | rw_learned | converged | 749 | 0.712 | 0.742 | 0.564 | 0.437 | 0.343 | 1.072 |
| edge_bce | rw_learned | PW limit | 89 | 0.715 | 0.752 | 0.578 | 0.529 | 0.415 | 0.422 |
| edge_dice | rw_learned | logits | 749 | 0.658 | 0.531 | 0.358 | 0.091 | 0.070 | 23.510 |
| edge_dice | rw_learned | layer, 20 steps | 749 | 0.703 | 0.716 | 0.536 | 0.535 | 0.424 | 1.178 |
| edge_dice | rw_learned | converged | 749 | 0.703 | 0.714 | 0.537 | 0.521 | 0.413 | 1.131 |
| edge_dice | rw_learned | PW limit | 89 | 0.684 | 0.678 | 0.506 | 0.481 | 0.375 | 0.723 |
| – | ground truth | binary mask | 749 | 1.000 | 1.000 | 0.553 | 0.933 | 0.907 | 0.072 |

**Colon**

| loss | variant | output | n | IoU | BF₂ | edge align. | F1@0.5 | PQ | count err. |
|---|---|---|---|---|---|---|---|---|---|
| bce | unet | logits | 468 | 0.698 | 0.738 | 0.558 | 0.547 | 0.431 | 0.274 |
| bce | rw_learned | logits | 468 | 0.633 | 0.637 | 0.461 | 0.060 | 0.046 | 27.984 |
| bce | rw_learned | layer, 20 steps | 468 | 0.681 | 0.711 | 0.565 | 0.495 | 0.384 | 0.319 |
| bce | rw_learned | converged | 468 | 0.685 | 0.711 | 0.560 | 0.483 | 0.375 | 0.316 |
| bce | rw_learned | PW limit | 62 | 0.610 | 0.658 | 0.534 | 0.463 | 0.353 | 0.283 |
| dice | unet | logits | 468 | 0.669 | 0.702 | 0.541 | 0.517 | 0.409 | 0.808 |
| dice | rw_learned | logits | 468 | 0.596 | 0.526 | 0.394 | 0.191 | 0.149 | 9.892 |
| dice | rw_learned | layer, 20 steps | 468 | 0.666 | 0.693 | 0.532 | 0.506 | 0.398 | 0.805 |
| dice | rw_learned | converged | 468 | 0.665 | 0.693 | 0.530 | 0.504 | 0.398 | 0.734 |
| dice | rw_learned | PW limit | 62 | 0.605 | 0.651 | 0.482 | 0.505 | 0.384 | 0.375 |
| edge_bce | rw_learned | logits | 468 | 0.517 | 0.568 | 0.407 | 0.011 | 0.007 | 78.576 |
| edge_bce | rw_learned | layer, 20 steps | 468 | 0.682 | 0.721 | 0.543 | 0.350 | 0.271 | 1.271 |
| edge_bce | rw_learned | converged | 468 | 0.688 | 0.722 | 0.550 | 0.341 | 0.266 | 1.001 |
| edge_bce | rw_learned | PW limit | 62 | 0.638 | 0.700 | 0.529 | 0.381 | 0.288 | 0.360 |
| edge_dice | rw_learned | logits | 468 | 0.589 | 0.497 | 0.371 | 0.067 | 0.051 | 34.379 |
| edge_dice | rw_learned | layer, 20 steps | 468 | 0.663 | 0.683 | 0.511 | 0.418 | 0.329 | 1.411 |
| edge_dice | rw_learned | converged | 468 | 0.665 | 0.681 | 0.512 | 0.406 | 0.320 | 1.338 |
| edge_dice | rw_learned | PW limit | 62 | 0.611 | 0.635 | 0.445 | 0.294 | 0.226 | 1.094 |
| – | ground truth | binary mask | 468 | 1.000 | 1.000 | 0.539 | 0.836 | 0.796 | 0.123 |

**HeadNeck**

| loss | variant | output | n | IoU | BF₂ | edge align. | F1@0.5 | PQ | count err. |
|---|---|---|---|---|---|---|---|---|---|
| bce | unet | logits | 169 | 0.672 | 0.744 | 0.648 | 0.640 | 0.519 | 0.424 |
| bce | rw_learned | logits | 169 | 0.563 | 0.598 | 0.542 | 0.079 | 0.063 | 26.695 |
| bce | rw_learned | layer, 20 steps | 169 | 0.693 | 0.758 | 0.635 | 0.593 | 0.475 | 0.309 |
| bce | rw_learned | converged | 169 | 0.691 | 0.755 | 0.623 | 0.594 | 0.475 | 0.289 |
| dice | unet | logits | 169 | 0.588 | 0.644 | 0.635 | 0.569 | 0.469 | 1.770 |
| dice | rw_learned | logits | 169 | 0.515 | 0.480 | 0.505 | 0.195 | 0.158 | 14.760 |
| dice | rw_learned | layer, 20 steps | 169 | 0.615 | 0.673 | 0.627 | 0.568 | 0.464 | 1.451 |
| dice | rw_learned | converged | 169 | 0.611 | 0.674 | 0.625 | 0.577 | 0.472 | 1.419 |
| edge_bce | rw_learned | logits | 169 | 0.439 | 0.525 | 0.493 | 0.018 | 0.012 | 71.352 |
| edge_bce | rw_learned | layer, 20 steps | 169 | 0.665 | 0.736 | 0.618 | 0.459 | 0.368 | 1.108 |
| edge_bce | rw_learned | converged | 169 | 0.677 | 0.747 | 0.620 | 0.449 | 0.361 | 1.010 |
| edge_dice | rw_learned | logits | 169 | 0.513 | 0.457 | 0.487 | 0.074 | 0.060 | 43.961 |
| edge_dice | rw_learned | layer, 20 steps | 169 | 0.594 | 0.644 | 0.600 | 0.491 | 0.400 | 2.196 |
| edge_dice | rw_learned | converged | 169 | 0.593 | 0.643 | 0.600 | 0.488 | 0.399 | 2.141 |
| – | ground truth | binary mask | 169 | 1.000 | 1.000 | 0.629 | 0.927 | 0.897 | 0.061 |

**Paired per-image differences** (mean, 95 % bootstrap interval, fraction of images where the first is better)

- bce: rw_learned layer − unet logits: iou: -0.009 [-0.012, -0.007] (better on 25 %) bf2: -0.017 [-0.020, -0.014] (better on 19 %) band_acc: -0.008 [-0.009, -0.008] (better on 19 %)
- bce: rw_learned layer − its own logits: iou: +0.035 [+0.030, +0.041] (better on 81 %) bf2: +0.068 [+0.062, +0.073] (better on 86 %) band_acc: -0.001 [-0.002, -0.001] (better on 42 %)
- bce: PW limit − converged on the 307 limit patches (means): iou: -0.046 bf2: -0.034 band_acc: -0.029
- bce: unet logits by crowding: 0–10 nuclei (n=486): IoU 0.641, count err 0.678; 10–30 nuclei (n=1383): IoU 0.734, count err 0.183; 30–60 nuclei (n=525): IoU 0.748, count err 0.153; 60–∞ nuclei (n=129): IoU 0.728, count err 0.236
- bce: rw_learned layer by crowding: 0–10 nuclei (n=486): IoU 0.637, count err 0.849; 10–30 nuclei (n=1383): IoU 0.724, count err 0.233; 30–60 nuclei (n=525): IoU 0.737, count err 0.156; 60–∞ nuclei (n=129): IoU 0.711, count err 0.252
- dice: rw_learned layer − unet logits: iou: -0.005 [-0.007, -0.002] (better on 28 %) bf2: -0.009 [-0.012, -0.007] (better on 24 %) band_acc: -0.005 [-0.005, -0.004] (better on 22 %)
- dice: rw_learned layer − its own logits: iou: +0.053 [+0.049, +0.058] (better on 95 %) bf2: +0.163 [+0.159, +0.167] (better on 96 %) band_acc: -0.002 [-0.003, -0.002] (better on 38 %)
- dice: PW limit − converged on the 307 limit patches: iou: -0.025 [-0.034, -0.013] (better on 11 %) bf2: -0.021 [-0.030, -0.009] (better on 13 %) band_acc: -0.013 [-0.015, -0.011] (better on 10 %)
- dice: PW limit − unet logits on the 307 limit patches: iou: -0.030 [-0.042, -0.017] (better on 9 %) bf2: -0.027 [-0.039, -0.013] (better on 13 %) band_acc: -0.015 [-0.018, -0.013] (better on 9 %)
- dice: unet logits by crowding: 0–10 nuclei (n=486): IoU 0.550, count err 2.774; 10–30 nuclei (n=1383): IoU 0.726, count err 0.519; 30–60 nuclei (n=525): IoU 0.747, count err 0.227; 60–∞ nuclei (n=129): IoU 0.740, count err 0.203
- dice: rw_learned layer by crowding: 0–10 nuclei (n=486): IoU 0.558, count err 2.593; 10–30 nuclei (n=1383): IoU 0.718, count err 0.578; 30–60 nuclei (n=525): IoU 0.740, count err 0.248; 60–∞ nuclei (n=129): IoU 0.734, count err 0.200
- unet dice − unet bce: iou: -0.021 [-0.026, -0.016] (better on 40 %) bf2: -0.032 [-0.037, -0.026] (better on 35 %) band_acc: +0.028 [+0.027, +0.030] (better on 90 %)
- rw_learned layer dice − rw_learned layer bce: iou: -0.017 [-0.021, -0.012] (better on 43 %) bf2: -0.024 [-0.029, -0.019] (better on 39 %) band_acc: +0.032 [+0.031, +0.033] (better on 92 %)
- edge_bce: rw_learned layer − unet logits (bce): iou: -0.015 [-0.018, -0.013] (better on 19 %) bf2: -0.017 [-0.020, -0.015] (better on 23 %) band_acc: -0.015 [-0.016, -0.015] (better on 10 %)
- edge_bce: rw_learned layer − its own logits: iou: +0.153 [+0.148, +0.158] (better on 96 %) bf2: +0.148 [+0.142, +0.154] (better on 95 %) band_acc: +0.101 [+0.100, +0.103] (better on 94 %)
- edge_bce: PW limit − converged on the 307 limit patches: iou: -0.016 [-0.020, -0.013] (better on 16 %) bf2: +0.002 [-0.002, +0.006] (better on 44 %) band_acc: -0.008 [-0.011, -0.005] (better on 19 %)
- edge_bce: PW limit − unet logits (bce) on the 307 limit patches: iou: -0.030 [-0.039, -0.023] (better on 14 %) bf2: -0.020 [-0.028, -0.012] (better on 27 %) band_acc: -0.019 [-0.022, -0.016] (better on 10 %)
- edge_bce: unet logits by crowding: 0–10 nuclei (n=486): IoU 0.641, count err 0.678; 10–30 nuclei (n=1383): IoU 0.734, count err 0.183; 30–60 nuclei (n=525): IoU 0.748, count err 0.153; 60–∞ nuclei (n=129): IoU 0.728, count err 0.236
- edge_bce: rw_learned layer by crowding: 0–10 nuclei (n=486): IoU 0.627, count err 2.360; 10–30 nuclei (n=1383): IoU 0.719, count err 1.197; 30–60 nuclei (n=525): IoU 0.731, count err 0.625; 60–∞ nuclei (n=129): IoU 0.710, count err 0.218
- unet edge_bce − unet bce: iou: +0.000 [+0.000, +0.000] (better on 0 %) bf2: +0.000 [+0.000, +0.000] (better on 0 %) band_acc: +0.000 [+0.000, +0.000] (better on 0 %)
- rw_learned layer edge_bce − rw_learned layer bce: iou: -0.006 [-0.009, -0.004] (better on 37 %) bf2: -0.000 [-0.003, +0.002] (better on 49 %) band_acc: -0.007 [-0.008, -0.006] (better on 27 %)
- edge_dice: rw_learned layer − unet logits (bce): iou: -0.029 [-0.034, -0.024] (better on 31 %) bf2: -0.054 [-0.059, -0.049] (better on 16 %) band_acc: +0.022 [+0.021, +0.023] (better on 84 %)
- edge_dice: rw_learned layer − its own logits: iou: +0.056 [+0.052, +0.061] (better on 95 %) bf2: +0.187 [+0.183, +0.192] (better on 96 %) band_acc: +0.000 [-0.000, +0.001] (better on 51 %)
- edge_dice: PW limit − converged on the 307 limit patches: iou: -0.031 [-0.034, -0.028] (better on 6 %) bf2: -0.036 [-0.039, -0.033] (better on 5 %) band_acc: -0.019 [-0.021, -0.017] (better on 3 %)
- edge_dice: PW limit − unet logits (bce) on the 307 limit patches: iou: -0.067 [-0.086, -0.051] (better on 12 %) bf2: -0.102 [-0.121, -0.085] (better on 6 %) band_acc: +0.005 [+0.001, +0.009] (better on 46 %)
- edge_dice: unet logits by crowding: 0–10 nuclei (n=486): IoU 0.641, count err 0.678; 10–30 nuclei (n=1383): IoU 0.734, count err 0.183; 30–60 nuclei (n=525): IoU 0.748, count err 0.153; 60–∞ nuclei (n=129): IoU 0.728, count err 0.236
- edge_dice: rw_learned layer by crowding: 0–10 nuclei (n=486): IoU 0.549, count err 4.402; 10–30 nuclei (n=1383): IoU 0.718, count err 1.080; 30–60 nuclei (n=525): IoU 0.737, count err 0.539; 60–∞ nuclei (n=129): IoU 0.725, count err 0.230
- unet edge_dice − unet bce: iou: +0.000 [+0.000, +0.000] (better on 0 %) bf2: +0.000 [+0.000, +0.000] (better on 0 %) band_acc: +0.000 [+0.000, +0.000] (better on 0 %)
- rw_learned layer edge_dice − rw_learned layer bce: iou: -0.020 [-0.025, -0.015] (better on 41 %) bf2: -0.037 [-0.042, -0.032] (better on 31 %) band_acc: +0.031 [+0.030, +0.032] (better on 91 %)
