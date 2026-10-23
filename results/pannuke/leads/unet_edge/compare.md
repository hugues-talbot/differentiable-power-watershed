**PanNuke fold 1 → fold 2, gap target: the edge-target layer against a U-Net with the same edge supervision and classical post-processing** (2523 patches; PW limit on 307). Watershed marker spacing chosen on fold 3 (300 patches): {'md_ws': 12, 'md_wsc': 25}.

| run | variant | output | IoU | BF₁ | BF₂ | BF₃ | band acc. | soft px | edge align. | F1@0.5 | PQ | count err. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U-Net, gap target (sec. 6.1) | unet | logits | 0.717 | 0.651 | 0.768 | 0.825 | 0.806 | 15.5 % | 0.575 | 0.667 | 0.541 | 0.296 |
| U-Net + contour head, edge target | unet_edge | logits | 0.719 | 0.658 | 0.774 | 0.828 | 0.809 | 15.4 % | 0.574 | 0.682 | 0.556 | 0.303 |
| U-Net + contour head, edge target | unet_edge | logits − contour (c > 0.5) | 0.655 | 0.495 | 0.707 | 0.811 | 0.749 | 0.0 % | 0.512 | 0.665 | 0.492 | 0.415 |
| U-Net + contour head, edge target | unet_edge | watershed, seg markers | 0.718 | 0.658 | 0.774 | 0.829 | 0.809 | 0.0 % | 0.568 | 0.715 | 0.583 | 0.344 |
| U-Net + contour head, edge target | unet_edge | watershed, contour markers | 0.717 | 0.660 | 0.775 | 0.830 | 0.808 | 0.0 % | 0.566 | 0.693 | 0.566 | 0.416 |
| layer, edge target (sec. 10) | rw_learned | layer, 20 steps | 0.713 | 0.649 | 0.766 | 0.822 | 0.799 | 12.5 % | 0.582 | 0.723 | 0.587 | 0.207 |
| layer, edge target (sec. 10) | rw_learned | converged | 0.721 | 0.655 | 0.773 | 0.829 | 0.810 | 13.2 % | 0.569 | 0.724 | 0.588 | 0.214 |
| layer, edge target (sec. 10) | rw_learned | PW limit | 0.637 | 0.612 | 0.718 | 0.763 | 0.746 | 0.0 % | 0.625 | 0.682 | 0.562 | 0.334 |
| ground truth | | gap mask | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.0 % | 0.553 | 0.998 | 0.990 | 0.002 |

**Marker spacing on fold 3** (PQ / F1 / count error / components per patch):

| spacing | pp_ws md=2 | pp_ws md=3 | pp_ws md=4 | pp_ws md=5 | pp_ws md=6 | pp_ws md=8 | pp_ws md=10 | pp_ws md=12 | pp_ws md=15 | pp_ws md=20 | pp_ws md=25 |
| pp_ws | 0.419 / 0.522 / 0.96 / 41.8 | 0.489 / 0.601 / 0.64 / 35.6 | 0.529 / 0.647 / 0.50 / 32.6 | 0.553 / 0.675 / 0.42 / 31.0 | 0.566 / 0.690 / 0.37 / 30.0 | 0.582 / 0.709 / 0.32 / 28.8 | 0.588 / 0.715 / 0.30 / 28.1 | 0.591 / 0.718 / 0.28 / 27.5 | 0.586 / 0.714 / 0.26 / 27.0 | 0.575 / 0.701 / 0.25 / 26.3 | 0.566 / 0.692 / 0.24 / 25.9 |
| pp_wsc | 0.373 / 0.468 / 1.23 / 49.0 | 0.447 / 0.553 / 0.83 / 41.0 | 0.485 / 0.597 / 0.67 / 37.6 | 0.509 / 0.625 / 0.59 / 35.7 | 0.526 / 0.644 / 0.53 / 34.5 | 0.548 / 0.671 / 0.47 / 33.0 | 0.558 / 0.681 / 0.43 / 32.2 | 0.564 / 0.688 / 0.41 / 31.6 | 0.570 / 0.693 / 0.39 / 31.2 | 0.573 / 0.696 / 0.37 / 30.8 | 0.573 / 0.697 / 0.36 / 30.6 |

**Instance metrics after removing components smaller than 8 px, and than 32 px** (IoU against the binary mask)

| run | output | IoU (8) | F1@0.5 (8) | PQ (8) | count err. (8) | components / patch (raw → 8) | F1@0.5 (32) | PQ (32) | count err. (32) |
|---|---|---|---|---|---|---|---|---|---|
| U-Net, gap target (sec. 6.1) | logits | 0.719 | 0.700 | 0.567 | 0.220 | 24.0 → 21.7 | 0.715 | 0.581 | 0.206 |
| U-Net + contour head, edge target | logits | 0.724 | 0.723 | 0.589 | 0.214 | 25.2 → 22.4 | 0.738 | 0.602 | 0.198 |
| U-Net + contour head, edge target | logits − contour (c > 0.5) | 0.657 | 0.729 | 0.539 | 0.230 | 30.3 → 25.5 | 0.753 | 0.557 | 0.185 |
| U-Net + contour head, edge target | watershed, seg markers | 0.722 | 0.757 | 0.618 | 0.227 | 27.2 → 24.3 | 0.774 | 0.632 | 0.193 |
| U-Net + contour head, edge target | watershed, contour markers | 0.720 | 0.753 | 0.615 | 0.241 | 30.3 → 26.0 | 0.777 | 0.636 | 0.193 |
| layer, edge target (sec. 10) | layer, 20 steps | 0.716 | 0.726 | 0.589 | 0.202 | 22.0 → 21.8 | 0.733 | 0.596 | 0.198 |

Paired bootstrap of the dataset-level F1@0.5 / PQ differences after the 8-px filter (layer = 20 steps):

- layer − gap U-Net: F1 +0.027 [+0.024, +0.029], PQ +0.022 [+0.020, +0.024]
- layer − U-Net + contour head, logits: F1 +0.004 [+0.001, +0.006], PQ +0.001 [-0.001, +0.003]
- layer − U-Net + contour head, watershed, seg markers: F1 -0.031 [-0.034, -0.027], PQ -0.028 [-0.031, -0.025]
- layer − U-Net + contour head, watershed, contour markers: F1 -0.027 [-0.031, -0.022], PQ -0.026 [-0.029, -0.022]
- U-Net + contour head, watershed, seg markers − its logits: F1 +0.034 [+0.031, +0.038], PQ +0.029 [+0.026, +0.031]

**Paired per-patch differences** (2523 patches, 95 % bootstrap intervals; F1 and PQ are dataset-level, bootstrapped over patches). Best post-processed U-Net output by PQ: `pp_ws`.

| comparison | IoU | BF₁ | BF₂ | BF₃ | band acc. | F1@0.5 | PQ | first better on (IoU / BF₂) |
|---|---|---|---|---|---|---|---|---|
| converged layer − gap U-Net (sec. 10) | +0.004 [+0.002, +0.007] | +0.004 [+0.002, +0.007] | +0.005 [+0.003, +0.008] | +0.005 [+0.002, +0.007] | +0.004 [+0.004, +0.005] | +0.057 [+0.054, +0.060] | +0.047 [+0.045, +0.049] | 50 % / 54 % |
| U-Net + contour head, logits − gap U-Net | +0.003 [+0.001, +0.005] | +0.007 [+0.005, +0.009] | +0.005 [+0.003, +0.007] | +0.004 [+0.001, +0.005] | +0.004 [+0.003, +0.004] | +0.015 [+0.012, +0.018] | +0.015 [+0.012, +0.017] | 54 % / 59 % |
| U-Net + contour head, logits − contour (c > 0.5) − its logits | -0.064 [-0.066, -0.063] | -0.163 [-0.167, -0.160] | -0.067 [-0.069, -0.065] | -0.017 [-0.018, -0.016] | -0.060 [-0.062, -0.059] | -0.017 [-0.022, -0.013] | -0.064 [-0.068, -0.061] | 1 % / 4 % |
| U-Net + contour head, watershed, seg markers − its logits | -0.001 [-0.002, -0.001] | +0.001 [+0.000, +0.001] | +0.001 [+0.000, +0.001] | +0.001 [+0.000, +0.001] | -0.001 [-0.001, -0.001] | +0.033 [+0.030, +0.036] | +0.027 [+0.025, +0.030] | 12 % / 37 % |
| U-Net + contour head, watershed, contour markers − its logits | -0.002 [-0.003, -0.002] | +0.002 [+0.002, +0.002] | +0.002 [+0.002, +0.002] | +0.002 [+0.001, +0.002] | -0.001 [-0.001, -0.001] | +0.011 [+0.007, +0.015] | +0.011 [+0.007, +0.014] | 14 % / 47 % |
| converged layer − U-Net + contour head, logits | +0.001 [-0.001, +0.004] | -0.003 [-0.005, -0.000] | -0.000 [-0.003, +0.003] | +0.001 [-0.001, +0.004] | +0.001 [+0.000, +0.001] | +0.042 [+0.039, +0.045] | +0.032 [+0.030, +0.034] | 44 % / 42 % |
| converged layer − U-Net + contour head, logits − contour (c > 0.5) | +0.066 [+0.063, +0.068] | +0.160 [+0.156, +0.164] | +0.067 [+0.064, +0.070] | +0.018 [+0.016, +0.021] | +0.061 [+0.060, +0.062] | +0.059 [+0.054, +0.064] | +0.096 [+0.093, +0.101] | 91 % / 89 % |
| converged layer − U-Net + contour head, watershed, seg markers | +0.003 [+0.000, +0.006] | -0.004 [-0.006, -0.001] | -0.001 [-0.003, +0.002] | +0.000 [-0.002, +0.003] | +0.002 [+0.001, +0.002] | +0.009 [+0.005, +0.013] | +0.005 [+0.002, +0.008] | 47 % / 41 % |
| converged layer − U-Net + contour head, watershed, contour markers | +0.004 [+0.001, +0.006] | -0.005 [-0.007, -0.002] | -0.002 [-0.005, +0.001] | -0.001 [-0.003, +0.002] | +0.002 [+0.001, +0.003] | +0.031 [+0.025, +0.036] | +0.022 [+0.017, +0.026] | 49 % / 39 % |
| layer (20 steps) − U-Net + contour head, watershed, seg markers | -0.005 [-0.007, -0.002] | -0.009 [-0.012, -0.006] | -0.008 [-0.011, -0.005] | -0.007 [-0.010, -0.004] | -0.010 [-0.011, -0.009] | +0.008 [+0.004, +0.012] | +0.004 [+0.001, +0.007] | 36 % / 34 % |

**Per tissue** (converged layer vs `pp_ws`; IoU / BF₂ / F1 / PQ / count err.)

| tissue (n) | converged layer | U-Net + contour head, watershed, seg markers |
|---|---|---|
| Breast (749) | 0.722 / 0.757 / 0.753 / 0.600 / 0.17 | 0.722 / 0.761 / 0.757 / 0.605 / 0.24 |
| Colon (468) | 0.697 / 0.739 / 0.614 / 0.483 / 0.23 | 0.691 / 0.742 / 0.630 / 0.497 / 0.34 |
| HeadNeck (169) | 0.702 / 0.777 / 0.725 / 0.590 / 0.23 | 0.682 / 0.756 / 0.688 / 0.565 / 0.47 |
| Adrenal_gland (148) | 0.724 / 0.785 / 0.778 / 0.654 / 0.22 | 0.719 / 0.783 / 0.712 / 0.605 / 0.44 |

The converged layer has the higher IoU on 9 and the higher F1 on 11 of the 15 tissue types with ≥ 50 patches.

**By crowding** (nuclei per patch; IoU / F1 / PQ / count err.)

| nuclei (n) | gap U-Net | U-Net + contour head, logits | watershed, seg markers | converged layer |
|---|---|---|---|---|
| 0–10 (486) | 0.642 / 0.587 / 0.470 / 0.77 | 0.643 / 0.603 / 0.485 / 0.76 | 0.642 / 0.596 / 0.479 / 0.81 | 0.654 / 0.670 / 0.537 / 0.50 |
| 10–30 (1383) | 0.732 / 0.695 / 0.568 / 0.20 | 0.735 / 0.703 / 0.577 / 0.22 | 0.734 / 0.719 / 0.591 / 0.27 | 0.735 / 0.752 / 0.615 / 0.14 |
| 30–60 (525) | 0.744 / 0.666 / 0.538 / 0.14 | 0.746 / 0.685 / 0.556 / 0.14 | 0.745 / 0.733 / 0.596 / 0.15 | 0.746 / 0.718 / 0.581 / 0.14 |
| 60–∞ (129) | 0.721 / 0.616 / 0.494 / 0.21 | 0.727 / 0.644 / 0.517 / 0.16 | 0.726 / 0.700 / 0.562 / 0.13 | 0.723 / 0.676 / 0.542 / 0.22 |

**Seam statistics** (fraction of the 142211 seam pixels of fold 2 predicted as background / fraction of the 8999 seams entirely background)

| output | seam px bg | seams cut |
|---|---|---|
| gap U-Net, logits | 19 % | 13 % |
| U-Net + contour head, logits | 22 % | 15 % |
| U-Net + contour head, logits − contour (c > 0.5) | 68 % | 55 % |
| U-Net + contour head, watershed, seg markers | 31 % | 17 % |
| U-Net + contour head, watershed, contour markers | 37 % | 17 % |
| layer, edge target (sec. 10), logits | 42 % | 26 % |
| layer, edge target (sec. 10), layer, 20 steps | 29 % | 19 % |
| layer, edge target (sec. 10), converged | 23 % | 15 % |
