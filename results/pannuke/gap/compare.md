**All of fold 2** (2523 patches).  The first four rows are section 6 (binary target); the rest use the gap target.

| run | output | IoU | BF₁ | BF₂ | BF₃ | band acc. | soft px | edge align. | F1@0.5 | PQ | AJI | count err. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| unet (sec. 6) | sigmoid, thresholded at 0.5 | 0.719 | 0.652 | 0.769 | 0.825 | 0.807 | 15.4 % | 0.577 | 0.656 | 0.531 | 0.494 | 0.275 |
| rw_learned p 5→50 (sec. 6) | layer, 20 steps | 0.709 | 0.628 | 0.752 | 0.813 | 0.799 | 16.1 % | 0.579 | 0.604 | 0.482 | 0.456 | 0.337 |
| rw_learned p 5→50 (sec. 6) | converged | 0.710 | 0.630 | 0.751 | 0.812 | 0.805 | 16.2 % | 0.572 | 0.602 | 0.480 | 0.366 | 0.322 |
| rw_learned p 5→50 (sec. 6) | PW limit (307) | 0.661 | 0.591 | 0.711 | 0.768 | 0.771 | 0.0 % | 0.577 | 0.618 | 0.490 | 0.425 | 0.246 |
| ground truth | binary mask | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0 | 0.559 | 0.913 | 0.883 | 0.701 | 0.088 |
| unet (gap) | sigmoid, thresholded at 0.5 | 0.717 | 0.651 | 0.768 | 0.825 | 0.806 | 15.5 % | 0.575 | 0.667 | 0.541 | 0.531 | 0.296 |
| rw p 5→50 (gap) | layer, 20 steps | 0.705 | 0.624 | 0.747 | 0.809 | 0.797 | 16.4 % | 0.578 | 0.610 | 0.487 | 0.473 | 0.357 |
| rw p 5→50 (gap) | converged | 0.706 | 0.626 | 0.746 | 0.807 | 0.802 | 16.4 % | 0.572 | 0.608 | 0.485 | 0.380 | 0.336 |
| rw p 5→50 (gap) | PW limit (307) | 0.664 | 0.587 | 0.710 | 0.768 | 0.770 | 0.0 % | 0.574 | 0.621 | 0.490 | 0.424 | 0.246 |
| rw p 5→20 (gap) | layer, 20 steps | 0.707 | 0.625 | 0.748 | 0.810 | 0.797 | 15.8 % | 0.573 | 0.635 | 0.508 | 0.495 | 0.313 |
| rw p 5→20 (gap) | converged | 0.709 | 0.629 | 0.750 | 0.813 | 0.801 | 16.0 % | 0.569 | 0.638 | 0.512 | 0.451 | 0.298 |
| rw p 5→20 (gap) | PW limit (307) | 0.476 | 0.482 | 0.562 | 0.597 | 0.669 | 0.0 % | 0.658 | 0.510 | 0.417 | 0.352 | 0.510 |
| rw p 5→20, 8·σ edges (gap) | layer, 20 steps | 0.706 | 0.624 | 0.747 | 0.810 | 0.795 | 16.1 % | 0.577 | 0.625 | 0.499 | 0.481 | 0.295 |
| rw p 5→20, 8·σ edges (gap) | converged | 0.708 | 0.626 | 0.749 | 0.812 | 0.800 | 16.2 % | 0.572 | 0.627 | 0.501 | 0.443 | 0.294 |
| rw p 5→20, 8·σ edges (gap) | PW limit (307) | 0.435 | 0.446 | 0.522 | 0.555 | 0.641 | 0.0 % | 0.684 | 0.474 | 0.390 | 0.356 | 0.567 |
| rw p 2→10, 8·σ edges (gap) | layer, 20 steps | 0.712 | 0.639 | 0.759 | 0.819 | 0.796 | 14.5 % | 0.585 | 0.678 | 0.548 | 0.517 | 0.225 |
| rw p 2→10, 8·σ edges (gap) | converged | 0.716 | 0.639 | 0.760 | 0.820 | 0.801 | 14.8 % | 0.575 | 0.680 | 0.549 | 0.497 | 0.226 |
| rw p 2→10, 8·σ edges (gap) | PW limit (307) | 0.508 | 0.496 | 0.582 | 0.620 | 0.671 | 0 | 0.669 | 0.523 | 0.435 | 0.391 | 0.555 |
| ground truth | gap mask | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0 | 0.553 | 0.998 | 0.990 | 0.995 | 0.002 |

**Paired per-patch differences** (bootstrap 95 % intervals):

- unet (gap) − unet (sec. 6) (n = 2523): IOU -0.002 [-0.003, -0.000], better on 40 %; BF₂ -0.001 [-0.003, +0.001], better on 44 %
- rw p 5→50 (gap) layer − unet (gap) (n = 2523): IOU -0.012 [-0.015, -0.009], better on 24 %; BF₂ -0.021 [-0.024, -0.019], better on 17 %
- rw p 5→50 (gap) layer − rw_learned layer (sec. 6) (n = 2523): IOU -0.005 [-0.006, -0.003], better on 37 %; BF₂ -0.005 [-0.007, -0.004], better on 38 %
- rw p 5→50 (gap) limit − converged (n = 307): IOU -0.037 [-0.043, -0.031], better on 12 %; BF₂ -0.029 [-0.035, -0.023], better on 19 %
- rw p 5→50 (gap) limit − unet (gap) (n = 307): IOU -0.046 [-0.053, -0.040], better on 10 %; BF₂ -0.052 [-0.059, -0.045], better on 9 %
- rw p 5→20 (gap) layer − unet (gap) (n = 2523): IOU -0.010 [-0.013, -0.008], better on 28 %; BF₂ -0.021 [-0.023, -0.018], better on 18 %
- rw p 5→20 (gap) layer − rw_learned layer (sec. 6) (n = 2523): IOU -0.003 [-0.005, -0.001], better on 43 %; BF₂ -0.005 [-0.007, -0.002], better on 42 %
- rw p 5→20 (gap) limit − converged (n = 307): IOU -0.228 [-0.248, -0.209], better on 4 %; BF₂ -0.180 [-0.198, -0.165], better on 5 %
- rw p 5→20 (gap) limit − unet (gap) (n = 307): IOU -0.234 [-0.254, -0.215], better on 3 %; BF₂ -0.200 [-0.218, -0.184], better on 3 %
- rw p 5→20, 8·σ edges (gap) layer − unet (gap) (n = 2523): IOU -0.011 [-0.014, -0.009], better on 25 %; BF₂ -0.021 [-0.024, -0.018], better on 17 %
- rw p 5→20, 8·σ edges (gap) layer − rw_learned layer (sec. 6) (n = 2523): IOU -0.004 [-0.006, -0.001], better on 39 %; BF₂ -0.005 [-0.007, -0.002], better on 40 %
- rw p 5→20, 8·σ edges (gap) limit − converged (n = 307): IOU -0.270 [-0.291, -0.247], better on 2 %; BF₂ -0.221 [-0.241, -0.199], better on 3 %
- rw p 5→20, 8·σ edges (gap) limit − unet (gap) (n = 307): IOU -0.276 [-0.297, -0.253], better on 2 %; BF₂ -0.240 [-0.261, -0.217], better on 3 %
- rw p 2→10, 8·σ edges (gap) layer − unet (gap) (n = 2523): IOU -0.005 [-0.007, -0.002], better on 33 %; BF₂ -0.009 [-0.012, -0.007], better on 29 %
- rw p 2→10, 8·σ edges (gap) layer − rw_learned layer (sec. 6) (n = 2523): IOU +0.003 [+0.000, +0.005], better on 52 %; BF₂ +0.007 [+0.004, +0.010], better on 59 %
- rw p 2→10, 8·σ edges (gap) limit − converged (n = 307): IOU -0.200 [-0.220, -0.181], better on 5 %; BF₂ -0.169 [-0.187, -0.150], better on 5 %
- rw p 2→10, 8·σ edges (gap) limit − unet (gap) (n = 307): IOU -0.203 [-0.222, -0.183], better on 4 %; BF₂ -0.179 [-0.199, -0.160], better on 4 %

**IoU gap by crowding** (layer − unet (gap), mean paired difference):

| run | < 10 nuclei | 10–50 | > 50 |
|---|---|---|---|
| rw p 5→50 (gap) | -0.011 (n=486) | -0.012 (n=1858) | -0.017 (n=179) |
| rw p 5→20 (gap) | -0.010 (n=486) | -0.010 (n=1858) | -0.016 (n=179) |
| rw p 5→20, 8·σ edges (gap) | -0.007 (n=486) | -0.011 (n=1858) | -0.020 (n=179) |
| rw p 2→10, 8·σ edges (gap) | +0.007 (n=486) | -0.007 (n=1858) | -0.010 (n=179) |

**Breast**

| run | output | IoU | BF₂ | F1@0.5 | PQ | count err. |
|---|---|---|---|---|---|---|
| unet (sec. 6) | sigmoid, thresholded at 0.5 | 0.722 | 0.756 | 0.690 | 0.547 | 0.198 |
| rw_learned p 5→50 (sec. 6) | layer, 20 steps | 0.713 | 0.738 | 0.635 | 0.498 | 0.313 |
| rw_learned p 5→50 (sec. 6) | PW limit (89) | 0.667 | 0.703 | 0.684 | 0.535 | 0.174 |
| unet (gap) | sigmoid, thresholded at 0.5 | 0.720 | 0.755 | 0.704 | 0.560 | 0.211 |
| rw p 5→50 (gap) | layer, 20 steps | 0.710 | 0.734 | 0.639 | 0.501 | 0.317 |
| rw p 5→50 (gap) | PW limit (89) | 0.679 | 0.703 | 0.681 | 0.531 | 0.164 |
| rw p 5→20 (gap) | layer, 20 steps | 0.711 | 0.734 | 0.665 | 0.522 | 0.275 |
| rw p 5→20 (gap) | PW limit (89) | 0.399 | 0.485 | 0.517 | 0.420 | 0.604 |
| rw p 5→20, 8·σ edges (gap) | layer, 20 steps | 0.712 | 0.736 | 0.654 | 0.513 | 0.247 |
| rw p 5→20, 8·σ edges (gap) | PW limit (89) | 0.385 | 0.465 | 0.495 | 0.403 | 0.628 |
| rw p 2→10, 8·σ edges (gap) | layer, 20 steps | 0.713 | 0.742 | 0.706 | 0.560 | 0.168 |
| rw p 2→10, 8·σ edges (gap) | PW limit (89) | 0.489 | 0.553 | 0.557 | 0.455 | 0.567 |
| ground truth | gap mask | 1.000 | 1.000 | 0.999 | 0.994 | 0.001 |

**Colon**

| run | output | IoU | BF₂ | F1@0.5 | PQ | count err. |
|---|---|---|---|---|---|---|
| unet (sec. 6) | sigmoid, thresholded at 0.5 | 0.698 | 0.738 | 0.547 | 0.431 | 0.274 |
| rw_learned p 5→50 (sec. 6) | layer, 20 steps | 0.681 | 0.711 | 0.495 | 0.384 | 0.319 |
| rw_learned p 5→50 (sec. 6) | PW limit (62) | 0.610 | 0.658 | 0.463 | 0.353 | 0.283 |
| unet (gap) | sigmoid, thresholded at 0.5 | 0.693 | 0.737 | 0.562 | 0.444 | 0.288 |
| rw p 5→50 (gap) | layer, 20 steps | 0.674 | 0.704 | 0.500 | 0.388 | 0.336 |
| rw p 5→50 (gap) | PW limit (62) | 0.600 | 0.650 | 0.466 | 0.352 | 0.274 |
| rw p 5→20 (gap) | layer, 20 steps | 0.679 | 0.711 | 0.531 | 0.413 | 0.302 |
| rw p 5→20 (gap) | PW limit (62) | 0.402 | 0.489 | 0.352 | 0.276 | 0.578 |
| rw p 5→20, 8·σ edges (gap) | layer, 20 steps | 0.678 | 0.708 | 0.515 | 0.399 | 0.283 |
| rw p 5→20, 8·σ edges (gap) | PW limit (62) | 0.371 | 0.459 | 0.334 | 0.265 | 0.623 |
| rw p 2→10, 8·σ edges (gap) | layer, 20 steps | 0.684 | 0.721 | 0.566 | 0.445 | 0.250 |
| rw p 2→10, 8·σ edges (gap) | PW limit (62) | 0.407 | 0.477 | 0.364 | 0.291 | 0.651 |
| ground truth | gap mask | 1.000 | 1.000 | 0.997 | 0.975 | 0.002 |

**HeadNeck**

| run | output | IoU | BF₂ | F1@0.5 | PQ | count err. |
|---|---|---|---|---|---|---|
| unet (sec. 6) | sigmoid, thresholded at 0.5 | 0.672 | 0.744 | 0.640 | 0.519 | 0.424 |
| rw_learned p 5→50 (sec. 6) | layer, 20 steps | 0.693 | 0.758 | 0.593 | 0.475 | 0.309 |
| unet (gap) | sigmoid, thresholded at 0.5 | 0.670 | 0.741 | 0.649 | 0.528 | 0.576 |
| rw p 5→50 (gap) | layer, 20 steps | 0.681 | 0.748 | 0.597 | 0.479 | 0.353 |
| rw p 5→20 (gap) | layer, 20 steps | 0.674 | 0.736 | 0.622 | 0.499 | 0.313 |
| rw p 5→20, 8·σ edges (gap) | layer, 20 steps | 0.674 | 0.734 | 0.604 | 0.483 | 0.337 |
| rw p 2→10, 8·σ edges (gap) | layer, 20 steps | 0.697 | 0.765 | 0.671 | 0.547 | 0.264 |
| ground truth | gap mask | 1.000 | 1.000 | 1.000 | 0.994 | 0.000 |

Learned edge-cost scales: rw p 5→20, 8·σ edges (gap): 3.42, rw p 2→10, 8·σ edges (gap): 4.09
