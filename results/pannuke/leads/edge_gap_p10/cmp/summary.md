**PanNuke, gap target, p 2 → 10, 8·σ edges: training losses**

| loss | variant | output | n | IoU | BF₁ | BF₂ | BF₃ | band acc. | soft px | edge align. | F1@0.5 | PQ | count err. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bce | unet | logits | 2523 | 0.717 | 0.651 | 0.768 | 0.825 | 0.806 | 15.5 % | 0.575 | 0.667 | 0.541 | 0.296 |
| bce | rw_learned | logits | 2523 | 0.658 | 0.563 | 0.674 | 0.728 | 0.820 | 20.6 % | 0.487 | 0.454 | 0.361 | 2.569 |
| bce | rw_learned | layer, 20 steps | 2523 | 0.712 | 0.639 | 0.759 | 0.819 | 0.796 | 14.5 % | 0.585 | 0.678 | 0.548 | 0.225 |
| bce | rw_learned | converged | 2523 | 0.716 | 0.639 | 0.760 | 0.820 | 0.801 | 14.8 % | 0.575 | 0.680 | 0.549 | 0.226 |
| bce | rw_learned | PW limit | 307 | 0.508 | 0.496 | 0.582 | 0.620 | 0.671 | 0.0 % | 0.669 | 0.523 | 0.435 | 0.555 |
| edge_target | rw_learned | logits | 2523 | 0.665 | 0.593 | 0.708 | 0.762 | 0.817 | 22.8 % | 0.503 | 0.586 | 0.466 | 1.365 |
| edge_target | rw_learned | layer, 20 steps | 2523 | 0.713 | 0.649 | 0.766 | 0.822 | 0.799 | 12.5 % | 0.582 | 0.723 | 0.587 | 0.207 |
| edge_target | rw_learned | converged | 2523 | 0.721 | 0.655 | 0.773 | 0.829 | 0.810 | 13.2 % | 0.569 | 0.724 | 0.588 | 0.214 |
| edge_target | rw_learned | PW limit | 307 | 0.637 | 0.612 | 0.718 | 0.763 | 0.746 | 0.0 % | 0.625 | 0.682 | 0.562 | 0.334 |
| – | ground truth | binary mask | 2523 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.0 % | 0.553 | 0.998 | 0.990 | 0.002 |

**Breast**

| loss | variant | output | n | IoU | BF₂ | edge align. | F1@0.5 | PQ | count err. |
|---|---|---|---|---|---|---|---|---|---|
| bce | unet | logits | 749 | 0.720 | 0.755 | 0.582 | 0.704 | 0.560 | 0.211 |
| bce | rw_learned | logits | 749 | 0.676 | 0.677 | 0.496 | 0.523 | 0.408 | 1.726 |
| bce | rw_learned | layer, 20 steps | 749 | 0.713 | 0.742 | 0.594 | 0.706 | 0.560 | 0.168 |
| bce | rw_learned | converged | 749 | 0.718 | 0.744 | 0.583 | 0.708 | 0.561 | 0.175 |
| bce | rw_learned | PW limit | 89 | 0.489 | 0.553 | 0.671 | 0.557 | 0.455 | 0.567 |
| edge_target | rw_learned | logits | 749 | 0.681 | 0.710 | 0.517 | 0.634 | 0.494 | 0.986 |
| edge_target | rw_learned | layer, 20 steps | 749 | 0.713 | 0.747 | 0.588 | 0.749 | 0.596 | 0.163 |
| edge_target | rw_learned | converged | 749 | 0.722 | 0.757 | 0.576 | 0.753 | 0.600 | 0.167 |
| edge_target | rw_learned | PW limit | 89 | 0.664 | 0.726 | 0.629 | 0.729 | 0.589 | 0.290 |
| – | ground truth | binary mask | 749 | 1.000 | 1.000 | 0.547 | 0.999 | 0.994 | 0.001 |

**Colon**

| loss | variant | output | n | IoU | BF₂ | edge align. | F1@0.5 | PQ | count err. |
|---|---|---|---|---|---|---|---|---|---|
| bce | unet | logits | 468 | 0.693 | 0.737 | 0.556 | 0.562 | 0.444 | 0.288 |
| bce | rw_learned | logits | 468 | 0.625 | 0.642 | 0.471 | 0.378 | 0.293 | 2.354 |
| bce | rw_learned | layer, 20 steps | 468 | 0.684 | 0.721 | 0.570 | 0.566 | 0.445 | 0.250 |
| bce | rw_learned | converged | 468 | 0.689 | 0.722 | 0.559 | 0.565 | 0.444 | 0.250 |
| bce | rw_learned | PW limit | 62 | 0.407 | 0.477 | 0.660 | 0.364 | 0.291 | 0.651 |
| edge_target | rw_learned | logits | 468 | 0.635 | 0.675 | 0.481 | 0.499 | 0.385 | 1.287 |
| edge_target | rw_learned | layer, 20 steps | 468 | 0.685 | 0.731 | 0.566 | 0.621 | 0.489 | 0.219 |
| edge_target | rw_learned | converged | 468 | 0.697 | 0.739 | 0.553 | 0.614 | 0.483 | 0.233 |
| edge_target | rw_learned | PW limit | 62 | 0.531 | 0.627 | 0.608 | 0.529 | 0.422 | 0.459 |
| – | ground truth | binary mask | 468 | 1.000 | 1.000 | 0.532 | 0.997 | 0.975 | 0.002 |

**HeadNeck**

| loss | variant | output | n | IoU | BF₂ | edge align. | F1@0.5 | PQ | count err. |
|---|---|---|---|---|---|---|---|---|---|
| bce | unet | logits | 169 | 0.670 | 0.741 | 0.646 | 0.649 | 0.528 | 0.576 |
| bce | rw_learned | logits | 169 | 0.533 | 0.568 | 0.587 | 0.384 | 0.307 | 4.700 |
| bce | rw_learned | layer, 20 steps | 169 | 0.697 | 0.765 | 0.646 | 0.671 | 0.547 | 0.264 |
| bce | rw_learned | converged | 169 | 0.697 | 0.764 | 0.636 | 0.676 | 0.550 | 0.263 |
| edge_target | rw_learned | logits | 169 | 0.567 | 0.628 | 0.573 | 0.536 | 0.429 | 2.283 |
| edge_target | rw_learned | layer, 20 steps | 169 | 0.697 | 0.773 | 0.648 | 0.724 | 0.589 | 0.217 |
| edge_target | rw_learned | converged | 169 | 0.702 | 0.777 | 0.633 | 0.725 | 0.590 | 0.229 |
| – | ground truth | binary mask | 169 | 1.000 | 1.000 | 0.626 | 1.000 | 0.994 | 0.000 |

**Paired per-image differences** (mean, 95 % bootstrap interval, fraction of images where the first is better)

- bce: rw_learned layer − unet logits: iou: -0.005 [-0.007, -0.002] (better on 33 %) bf2: -0.009 [-0.012, -0.007] (better on 29 %) band_acc: -0.009 [-0.010, -0.009] (better on 17 %)
- bce: rw_learned layer − its own logits: iou: +0.054 [+0.048, +0.060] (better on 77 %) bf2: +0.085 [+0.079, +0.092] (better on 83 %) band_acc: -0.023 [-0.024, -0.022] (better on 15 %)
- bce: PW limit − converged on the 307 limit patches: iou: -0.200 [-0.220, -0.181] (better on 5 %) bf2: -0.169 [-0.187, -0.150] (better on 5 %) band_acc: -0.124 [-0.131, -0.117] (better on 0 %)
- bce: PW limit − unet logits on the 307 limit patches: iou: -0.203 [-0.222, -0.183] (better on 4 %) bf2: -0.179 [-0.199, -0.160] (better on 4 %) band_acc: -0.129 [-0.136, -0.121] (better on 0 %)
- bce: unet logits by crowding: 0–10 nuclei (n=486): IoU 0.642, count err 0.768; 10–30 nuclei (n=1383): IoU 0.732, count err 0.198; 30–60 nuclei (n=525): IoU 0.744, count err 0.136; 60–∞ nuclei (n=129): IoU 0.721, count err 0.206
- bce: rw_learned layer by crowding: 0–10 nuclei (n=486): IoU 0.648, count err 0.522; 10–30 nuclei (n=1383): IoU 0.726, count err 0.143; 30–60 nuclei (n=525): IoU 0.735, count err 0.158; 60–∞ nuclei (n=129): IoU 0.711, count err 0.255
- edge_target: rw_learned layer − unet logits (bce): iou: -0.003 [-0.006, -0.001] (better on 36 %) bf2: -0.002 [-0.005, +0.000] (better on 42 %) band_acc: -0.007 [-0.008, -0.006] (better on 24 %)
- edge_target: rw_learned layer − its own logits: iou: +0.049 [+0.043, +0.054] (better on 73 %) bf2: +0.058 [+0.052, +0.063] (better on 74 %) band_acc: -0.018 [-0.019, -0.017] (better on 18 %)
- edge_target: PW limit − converged on the 307 limit patches: iou: -0.078 [-0.091, -0.065] (better on 14 %) bf2: -0.047 [-0.058, -0.036] (better on 17 %) band_acc: -0.058 [-0.063, -0.052] (better on 3 %)
- edge_target: PW limit − unet logits (bce) on the 307 limit patches: iou: -0.074 [-0.085, -0.062] (better on 12 %) bf2: -0.044 [-0.055, -0.033] (better on 19 %) band_acc: -0.053 [-0.058, -0.049] (better on 2 %)
- edge_target: unet logits by crowding: 0–10 nuclei (n=486): IoU 0.642, count err 0.768; 10–30 nuclei (n=1383): IoU 0.732, count err 0.198; 30–60 nuclei (n=525): IoU 0.744, count err 0.136; 60–∞ nuclei (n=129): IoU 0.721, count err 0.206
- edge_target: rw_learned layer by crowding: 0–10 nuclei (n=486): IoU 0.650, count err 0.503; 10–30 nuclei (n=1383): IoU 0.727, count err 0.132; 30–60 nuclei (n=525): IoU 0.736, count err 0.130; 60–∞ nuclei (n=129): IoU 0.713, count err 0.215
- unet edge_target − unet bce: iou: +0.000 [+0.000, +0.000] (better on 0 %) bf2: +0.000 [+0.000, +0.000] (better on 0 %) band_acc: +0.000 [+0.000, +0.000] (better on 0 %)
- rw_learned layer edge_target − rw_learned layer bce: iou: +0.001 [-0.001, +0.004] (better on 49 %) bf2: +0.007 [+0.005, +0.009] (better on 58 %) band_acc: +0.002 [+0.001, +0.003] (better on 52 %)
