# The Random Walker / Power Watershed as a finishing layer: first experiments

Hugues Talbot with Claude, 16–17 October 2026. Companion to `pw_unrolling_note.tex`
and the conversation export. Code in `experiments/`, raw results and figures in
`results/`. Everything ran on jacobian (RTX 6000 Ada) except the plotting.

## 0. Setting

Prior-augmented Random Walker (Grady 2005) with every term raised to the inverse
temperature p:

    E(x) = Σ_e w_e (x_u − x_v)² + Σ_i a1_i (x_i − 1)² + Σ_i a0_i x_i²,
    w_e = exp(−p c_e),   a1_i = exp(−p c1_i),   a0_i = exp(−p c0_i),

costs c ≥ 0. The solution of (L(w) + diag(a0 + a1)) x = a1 is the probability that a
random 2-forest at inverse temperature p connects pixel i to the foreground label
(probabilistic watershed reading). Its p → ∞ limit is the Power Watershed on the
grid augmented with two virtual label nodes, i.e. a watershed cut flooded from the
confident pixels, computable exactly in quasi-linear time (`pw_limit_numpy`).

In the finishing-layer use, c1 = −α log s and c0 = −α log(1 − s) with s the
network's soft foreground probability, and c_e either the image gradient or a
learned edge-cost head. α is Grady's γ: it sets how strongly the unaries compete
with the edges.

Three experiments:

1. **Conditioning study** (`pw_conditioning.py`): hard-seeded RW on 512² images,
   what p costs to solve, how far x^p is from the limit, how the gradient collapses.
2. **Tunable softmax, no training** (`exp_softmax_synthetic.py`): simulated soft
   U-Net outputs through the layer, aligned and misaligned image edges.
3. **U-Net + layer, trained end to end** (`exp_unet_pets.py`): Oxford-IIIT Pet.

## 1. Conditioning study (hard seeds, 512²)

Cases: synthetic shapes with noise σ ∈ {0.05, 0.1}, 8-bit, costs c_e = ((I_u − I_v)/255)²;
seeds = ground truth eroded by r = 5 px (refinement regime) or r = 30 px, or a few
scribbles (global regime); the `camera` image with Otsu labels eroded likewise.
Reference x^p by a diagonally scaled sparse LU in float64 (flagged unreliable when
its residual exceeds 1e-8, which happens for the noisy cases beyond p ≈ 500); limit
x^∞ by the exact MSF + plateau algorithm on the integer costs.
Figures: `results/conditioning/figures512/*.png`, table `summary.md`.

**Where the limit is reached, and what it costs** (refinement regime, r = 5):

| case | p | κ(L_U) | CG fp32 iters to 1e-3 | labels ≠ x^∞ | edges carrying 90 % of the gradient |
|---|---|---|---|---|---|
| clean, σ = 0.05 | 10 | 1.8e2 | 39 | 0.7 % | 14 276 |
| | 100 | 4.7e2 | 53 | 0 | 5 945 |
| | 200 | 5.7e3 | 63 | 0 | 844 |
| | 1000 | 2.3e17 | 173 | 0 | 7 |
| noisy, σ = 0.1 | 10 | 2.0e2 | 42 | 3.1 % | 14 645 |
| | 100 | 1.5e10 | 89 | 2.2 % | 8 351 |
| | 500 | 1.0e48 | 240 | 1.2 % | 681 |
| camera | 10 | 5.5e2 | 62 | 9.8 % | 23 602 |
| | 100 | 1.7e7 | 104 | 5.5 % | 13 044 |
| | 500 | 4.1e33 | 154 | 4.1 % | 5 503 |

- On the clean image the labels of the limit are reached at p ≈ 100 while κ is still
  a few hundred and CG to a loose tolerance needs about 50 iterations: a comfortable
  training window. The gradient support has already shrunk by half there and is
  gone by p ≈ 500 (the zero-temperature collapse of the note).
- On noisy or natural images x^p approaches the limit only slowly (a few per cent
  of the free pixels still differ at p = 500) while κ explodes far beyond anything
  CG can resolve; the float64 LU itself fails beyond p ≈ 500–1000. The central
  tension of the note is real there: the last few per cent of agreement with the
  limit are not reachable by a finite-p solve. They have to come from deploying the
  combinatorial limit (section 3 measures what that costs).
- The CG iteration count to a loose tolerance grows much more slowly than √κ
  because the ill-conditioning sits in near-isolated pixels that barely affect the
  residual; Jacobi preconditioning helps by one to two orders of magnitude in κ.
- Natural images are the hard case. On `astronaut` (Otsu labels eroded by 5 px) x^p
  still disagrees with the limit on 15 % of the free pixels at p = 10, 11 % at p = 100
  and 6 % at p = 500, where the float64 reference already fails; the textures give
  κ ≈ 5e9 at p = 100. The PW limit of a raw-gradient graph on a photograph is simply
  far from any finite-p solution, which is the same message as the Pets results
  below: on photographs the edge costs have to be learned.
- **Resolution does not change the cost in the refinement regime.** At 1024² with the
  same 5-px erosion, CG needs 39 / 44 / 54 iterations to 1e-3 at p = 10 / 100 / 200,
  against 39 / 53 / 63 at 512²: the work is set by the width of the band, not by the
  image. In the global regime (r = 30) it grows with the image (160–205 at 1024²
  against 245–260 at 512² for a band that is relatively narrower). Truncation at
  1024², clean, p = 100: 20 CG steps disagree with the converged solve on 0.01 % of
  the labels, 50 Jacobi steps on 0.8 %. Figures: `results/conditioning/figures1024/`.

**Truncation** (label disagreement with the converged x^p after K steps):

| case, p = 100 | CG K=10 | CG K=20 | CG K=50 | Jacobi K=10 | Jacobi K=50 | Jacobi K=200 |
|---|---|---|---|---|---|---|
| clean, r = 5 | 1.2 % | 0.04 % | 0 | 24 % | 1.3 % | 0.01 % |
| noisy, r = 5 | 18 % | 2.9 % | 0.5 % | 25 % | 13 % | 0.6 % |
| camera, r = 5 | 20 % | 11 % | 3 % | 52 % | 18 % | 7 % |
| clean, r = 30 | 25 % | 23 % | 16 % | 26 % | 25 % | 23 % |

- In the refinement regime (band of 10 px) 20 unrolled CG steps suffice on clean
  images, plain Jacobi needs ten times more. In the global regime (r = 30, scribbles)
  no truncation works: the note's "match the application to the method's weakness"
  is confirmed quantitatively.

**Cost transform** (`figures_transforms/`, four 512² cases, squared cost vs |ΔI| vs
dense rank of the distinct values; all three share the same limit). The transform
only moves the p scale. Measured at equal agreement with the limit, it does not buy a
cheaper solve: on the clean refinement case the squared cost reaches the limit's
labels at p = 100 for 53 CG iterations, |ΔI| at p = 50 for 115, the rank at p = 50
for 259. On the natural image the rank and |ΔI| get closer to the limit than the
squared cost ever does (1–2 % of the free pixels at p = 100–200 against 4 % at
p = 500) for about twice the iterations, but with the float64 reference already
failing there. What the transforms do change is where the gradient dies: with the
rank, 90 % of the gradient mass sits on 20 edges by p = 50, at the very p where the
limit is first reached, while with the squared cost 6 000 edges still carry it at the
corresponding point. So for annealing, the squared cost, which spends the dynamic
range on the strong edges, is the better path: the limit is reached while the
gradient is still alive. The rank normalisation keeps its other role, fixing the
output distribution of a learned cost head so that p means the same thing on every
image.

## 2. The layer as a tunable softmax (no training, 256²)

Simulated U-Net output: ground truth elastically displaced by up to 3 px, blurred
(σ = 4 px), soft logits with smooth noise; four scenes × noise σ ∈ {0.05, 0.1} ×
{image edge on the true boundary, image edge shifted by 4 px}. Edge costs from the
image, unaries α(−log s, −log(1 − s)), α ∈ {0.03, 0.1, 0.3, 1}. Converged solves
(implicit layer) for p ∈ [1, 500], the exact limit, and truncated layers.
Figures: `results/softmax/figures/`.

| noise | image edge | α | soft prediction BF₂ | best p | BF₂ at best p | soft pixels at best p | limit BF₂ | limit IoU |
|---|---|---|---|---|---|---|---|---|
| 0.05 | aligned | 0.1 | 0.958 | 200 | **1.000** | 0.3 % | **1.000** | 1.000 |
| 0.05 | aligned | 1 | 0.958 | 50 | 0.954 | 21 % | 0.000 | 0.08 |
| 0.1 | aligned | 0.1 | 0.958 | 200 | 0.968 | 2.4 % | 0.870 | 0.966 |
| 0.05 | shifted 4 px | 0.1 | 0.963 | 1 | 0.959 | 100 % | 0.002 | 0.865 |
| 0.1 | shifted 4 px | 0.03 | 0.955 | 2 | 0.955 | 100 % | 0.688 | 0.920 |

(BF₂ = boundary F-score at 2 px tolerance, computed against the ground truth.)

- **Crisper and more correct.** With α ≤ 0.1 and the image edge where the true
  boundary is, the layer turns a 0.96 boundary score into 1.00 at p = 200 and in the
  limit, with the thin protrusion that the soft prediction rounds off fully
  recovered (`examples.png`), and the output goes from mostly soft to binary.
  This is the "better, tunable softmax": p is the temperature, and sharpening is
  spatially coupled through the edges rather than per pixel.
- **The unary scale is a real hyperparameter.** With α = 1 the unaries of confident
  pixels compete with the noise edges, nothing attaches to a label before the whole
  image has merged, and both large p and the limit collapse to one label. In the
  trained setting the network sets this scale itself through the logit magnitude.
- **The failure mode is as predicted.** When the true boundary is 4 px away from the
  image edge, p ≤ 10 is harmless but larger p snaps the boundary to the wrong edge
  and the limit is poor (BF₂ 0.002 at α = 0.1). The layer is only as good as its
  edge costs, which argues for learning them.
- **Truncation** (`truncation.png`, clean, aligned, α = 0.1): 10 unrolled PCG steps at
  p = 50 agree with the converged solve on 99.9 % of the labels and reach the full
  boundary score; Jacobi needs about 50 steps for the same.

## 3. U-Net with the layer as its last layer, trained end to end (Oxford-IIIT Pet)

Binary pet / background from the trimap (border band counted as pet), 128², small
U-Net (32-64-128-256), Adam, 30 epochs, batch 16, horizontal flips. Variants:

- `unet`: BCE on the logits.
- `rw_img`: logits → unary costs; edge costs = squared colour differences; the layer
  = 20 unrolled Jacobi-PCG steps in float32, p annealed geometrically from 5 to 50;
  BCE on the layer output plus 0.5 BCE on the logits.
- `rw_learned`: as `rw_img`, but the edge costs come from a second head of the same
  U-Net (sigmoid, averaged onto the edges).

Test split (3669 images): IoU, boundary F-scores at 1 and 2 px, accuracy within 3 px of
the true boundary, fraction of pixels in (0.1, 0.9). Every "thresholded at 0.5" row is the
practitioner's pipeline, the network's sigmoid output cut at 0.5 (and, where instance
metrics appear, its connected components); it is the baseline every layer row is to be
read against. Section 9 adds the tuned-threshold version of it. For the RW variants the output is
evaluated as trained (20 steps), converged at p = 50, and as the exact PW limit on
300 images (deployment at p = ∞).

| variant | output | IoU | BF₁ | BF₂ | band acc. | soft pixels |
|---|---|---|---|---|---|---|
| unet | sigmoid, thresholded at 0.5 | 0.853 | 0.586 | 0.724 | 0.778 | 13.4 % |
| rw_img | sigmoid, thresholded at 0.5 | 0.838 | 0.500 | 0.633 | 0.768 | 12.6 % |
| rw_img | layer, 20 steps | 0.840 | 0.508 | 0.681 | 0.742 | 18.0 % |
| rw_img | converged | 0.842 | 0.508 | 0.681 | 0.749 | 18.9 % |
| rw_img | PW limit (300) | 0.405 | 0.134 | 0.260 | 0.510 | 0.2 % |
| rw_learned | sigmoid, thresholded at 0.5 | 0.840 | 0.498 | 0.638 | 0.765 | 15.2 % |
| rw_learned | layer, 20 steps | 0.852 | 0.584 | 0.722 | 0.771 | 14.2 % |
| rw_learned | converged | 0.853 | 0.586 | 0.724 | 0.775 | 14.9 % |
| rw_learned | PW limit (300) | 0.822 | 0.561 | 0.695 | 0.749 | 0 |

Figures: `results/pets/figures/` (training curves, example panels with the learned
edge costs).

- **Honest outcome at 128²: no gain over the plain U-Net.** The learned-cost variant
  matches the U-Net on every metric (0.853 vs 0.853 IoU, 0.724 vs 0.724 BF₂); the
  image-gradient variant is worse, and its limit is useless (0.41 IoU): raw colour
  edges on photographs are not where pet boundaries are. The U-Net trained with BCE
  for 30 epochs is already nearly binary (13 % soft pixels), so there was little
  softness to remove at this resolution.
- **What the layer does do.** Inside the trained model the layer adds about 0.085 BF₂
  over its own logits (0.638 → 0.722): the network learned to leave the boundary
  decision to the layer and the learned cost head is a clean contour detector
  (`examples_rw_learned.png`). The 20-step layer is within 0.002 of the converged
  solve, so K = 20 is enough here.
- **Deployment at p = ∞ works, with a price.** The exact combinatorial PW on the
  learned costs, which nothing was ever trained with directly, loses 0.03 IoU and
  0.03 BF₂ against the converged finite-p solve, and is perfectly binary. That is
  the train-at-finite-p / deploy-at-the-limit scheme of the note, demonstrated.
- **The 256² repeat says the same.** Same recipe at 256 px (`results/pets256/`):

  | variant | output | IoU | BF₁ | BF₂ | band acc. | soft pixels |
  |---|---|---|---|---|---|---|
  | unet | sigmoid, thresholded at 0.5 | 0.842 | 0.364 | 0.503 | 0.685 | 18.7 % |
  | rw_learned | sigmoid, thresholded at 0.5 | 0.817 | 0.211 | 0.310 | 0.670 | 22.2 % |
  | rw_learned | layer, 20 steps | 0.844 | 0.359 | 0.498 | 0.678 | 17.8 % |
  | rw_learned | converged | 0.845 | 0.369 | 0.506 | 0.688 | 19.5 % |
  | rw_learned | PW limit (200) | 0.795 | 0.296 | 0.412 | 0.637 | 0 |

  Parity with the plain U-Net on every metric, a 0.19 BF₂ gain of the layer over its
  own logits, and a 0.05 IoU price for the exact limit. Higher resolution did not
  open a gap; the boundary scores of both methods simply drop because the 1–2 px
  tolerance is now tighter relative to the trimap's own boundary band.

## 4. Status

All runs complete (17 October 2026). Sections 6, 6.1, 7 and 10 (PanNuke; losses;
edge target on the cost head) were added by side sessions, 8 and 9 by the main one.

## 5. What this says about the plan

1. The one-parameter family works as advertised: p is a usable temperature, the
   layer is a spatially coupled softmax, and its limit is deployable without
   retraining. On synthetic data with the right edges the boundary gain is dramatic.
2. The gain on real data depends entirely on the edge costs. Image gradients are not
   enough on photographs or on H&E; a learned head is, but on Pets (128² and 256²)
   it only matches a plain U-Net, and on PanNuke nuclei it sits 0.01 IoU below one
   (section 6). The claim "crisper than a U-Net" did not survive contact with real
   data under a plain BCE loss: a U-Net trained for 30 epochs is already nearly
   binary, and the layer's boundary gain over its own logits (+0.1 to +0.2 BF₂) is
   exactly what the U-Net learns to do on its own when it has to. Where the layer
   does something a per-pixel output cannot is the limit: the exact Power Watershed
   on the learned costs gives the best object-count error on touching nuclei, at a
   price of 0.05 IoU. Boundary-sensitive losses, or instance-level training signals,
   are the natural next step (tried in section 7: a boundary loss narrows the PanNuke
   gap without closing it and opens a small one in the layer's favour on Pets; an
   instance-seam loss does not help).
3. Train at finite p with implicit or unrolled gradients (20 CG steps suffice in
   the refinement regime), keep p ≤ 100–200 where the gradient still has support,
   and deploy with the combinatorial limit when a binary, quasi-linear output is
   wanted. Beyond p ≈ 200 on real images neither the solve nor the gradient is
   usable, so the last few per cent towards the limit are not something to train
   through.

## 6. U-Net with the layer as its last layer on real nuclei (PanNuke)

Added 17 October 2026 (side session). Code: `experiments/convert_pannuke.py`,
`experiments/exp_unet_seg.py` (dataset-agnostic version of `exp_unet_pets.py`, reusing
its model and loss), `experiments/seg_metrics.py`, `experiments/plot_pannuke.py`.
Raw results, per-image metrics and figures: `results/pannuke/`.

**Data.** PanNuke (Gamper et al. 2019/2020), 256² H&E patches at 40×, 19 tissue types,
semi-automatic instance labels. Train on fold 1 (2656 patches), test on all of fold 2
(2523 patches; Breast 749, Colon 468, HeadNeck 169, Adrenal 148, ...). Binary target =
union of the five nucleus channels (17 % of the pixels; 23.7 nuclei per patch on
average; 0.09 % of the pixels sit on an interface between two touching nuclei).
Native 256 px, flips and 90° rotations, otherwise the Pets recipe: small U-Net
(32-64-128-256), Adam 1e-3 with cosine decay, 30 epochs, batch 16, p annealed 5 → 50,
K = 20 unrolled Jacobi-PCG steps, BCE on the layer output + 0.5 BCE on the logits.
Training takes 11 s per epoch; evaluating fold 2 takes a few minutes, dominated by the
CPU-side metrics.

**Metrics.** Pixel level as before (IoU, boundary F at 1, 2 and 3 px, accuracy in a
3-px band around the true boundary, fraction of pixels in (0.1, 0.9)). Instance level,
on the 4-connected components of the thresholded output (4-adjacency is the graph the
layer works on) against the instance masks: object-count error |n_pred − n_gt| / n_gt,
F1 of the matches at IoU ≥ 0.5, panoptic quality PQ and AJI, all aggregated over the
whole test set. Because the target is a binary mask, touching nuclei merge for every
method; the row "ground truth / binary mask" (components of the true binary mask
against the instances) is the ceiling any binary method can reach on these metrics.
Label-free edge alignment: fraction of predicted boundary pixels within 1 px of a strong
image edge (top 10 % of the colour-gradient magnitude after a σ = 1 px Gaussian). The
same score for the ground-truth boundary calibrates it. The exact PW limit (p = ∞) is
computed on 307 patches: 300 evenly spaced through fold 2 plus the 8 patches with the
most touching-nuclei pixels, which also serve as the example panels.

**A note on the limit's cost.** With float32 costs quantised to 2⁻²⁰, a 256² patch has
about 200 000 plateaus of which 40 000 have 2–7 tied edges; the general plateau path
of `power_watershed` (sparse graph + connected components per plateau) made the exact
limit cost 50–60 s per patch. A pure-Python route for plateaus of ≤ 64 edges, with the
same semantics (checked bit-identical), brings it to 2 s per patch.

**Results on all of fold 2** (2523 patches; the PW limit on 307). Instance metrics on
4-connected components of the thresholded output; "count err." = mean |n_pred − n_gt| / n_gt.

| variant | output | IoU | BF₁ | BF₂ | BF₃ | band acc. | soft px | edge align. | F1@0.5 | PQ | AJI | count err. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| unet | sigmoid, thresholded at 0.5 | **0.719** | **0.652** | **0.769** | **0.825** | **0.807** | 15.4 % | 0.577 | **0.656** | **0.531** | **0.494** | 0.275 |
| rw_img | sigmoid, thresholded at 0.5 | 0.669 | 0.547 | 0.672 | 0.737 | 0.806 | 13.2 % | 0.481 | 0.303 | 0.240 | 0.529 | 5.01 |
| rw_img | layer, 20 steps | 0.683 | 0.571 | 0.714 | 0.794 | 0.775 | 19.9 % | 0.559 | 0.516 | 0.400 | 0.396 | 0.513 |
| rw_img | converged | 0.686 | 0.570 | 0.713 | 0.794 | 0.779 | 20.3 % | 0.548 | 0.531 | 0.411 | 0.336 | 0.441 |
| rw_img | PW limit (307) | 0.181 | 0.217 | 0.254 | 0.273 | 0.540 | 0 | 0.796 | 0.194 | 0.150 | 0.109 | 0.675 |
| rw_learned | sigmoid, thresholded at 0.5 | 0.674 | 0.560 | 0.684 | 0.749 | 0.800 | 17.7 % | 0.481 | 0.083 | 0.067 | 0.533 | 25.4 |
| rw_learned | layer, 20 steps | 0.709 | 0.628 | 0.752 | 0.813 | 0.799 | 16.1 % | 0.579 | 0.604 | 0.482 | 0.456 | 0.337 |
| rw_learned | converged | 0.710 | 0.630 | 0.751 | 0.812 | 0.805 | 16.2 % | 0.572 | 0.602 | 0.480 | 0.366 | 0.322 |
| rw_learned | PW limit (307) | 0.661 | 0.591 | 0.711 | 0.768 | 0.771 | 0 | 0.577 | 0.618 | 0.490 | 0.425 | **0.246** |
| ground truth | binary mask | 1 | 1 | 1 | 1 | 1 | 0 | 0.559 | 0.913 | 0.883 | 0.701 | 0.088 |

(The AJI of the raw logits is inflated by their hundreds of tiny components, which
AJI only counts in the denominator by area; F1, PQ and the count error are the
honest instance numbers.)

**Per tissue type** (the three most common in fold 2; `figures/summary.md` has the
full tables, `rw_learned.json` all 15 types with ≥ 50 patches):

| tissue (n) | variant / output | IoU | BF₂ | edge align. | F1@0.5 | PQ | count err. |
|---|---|---|---|---|---|---|---|
| Breast (749) | unet / logits | 0.722 | 0.756 | 0.585 | 0.690 | 0.547 | 0.198 |
| | rw_learned / layer | 0.713 | 0.738 | 0.589 | 0.635 | 0.498 | 0.313 |
| | rw_learned / PW limit (89) | 0.667 | 0.703 | 0.586 | 0.684 | 0.535 | 0.174 |
| | ground truth / binary | 1 | 1 | 0.553 | 0.933 | 0.907 | 0.072 |
| Colon (468) | unet / logits | 0.698 | 0.738 | 0.558 | 0.547 | 0.431 | 0.274 |
| | rw_learned / layer | 0.681 | 0.711 | 0.565 | 0.495 | 0.384 | 0.319 |
| | rw_learned / PW limit (62) | 0.610 | 0.658 | 0.534 | 0.463 | 0.353 | 0.283 |
| | ground truth / binary | 1 | 1 | 0.539 | 0.836 | 0.796 | 0.123 |
| HeadNeck (169) | unet / logits | 0.672 | 0.744 | 0.648 | 0.640 | 0.519 | 0.424 |
| | rw_learned / layer | **0.693** | **0.758** | 0.635 | 0.593 | 0.475 | 0.309 |
| | ground truth / binary | 1 | 1 | 0.629 | 0.927 | 0.897 | 0.061 |

Paired per-patch differences (2523 patches, bootstrap 95 % intervals), `rw_learned`
layer minus `unet`: IoU −0.009 [−0.012, −0.007], BF₂ −0.017 [−0.020, −0.014], band
accuracy −0.008; the layer is better than the U-Net on 25 % of the patches. The gap
grows with crowding: −0.004 IoU on patches with fewer than 10 nuclei, −0.016 on patches
with more than 50. Within the trained `rw_learned` model, layer minus its own logits:
+0.035 IoU, +0.068 BF₂, better on 81 % / 86 % of the patches. Limit minus converged on
the same 307 patches: −0.046 IoU [−0.066, −0.027], −0.034 BF₂.

Figures: `results/pannuke/figures/training.png`, `examples_<variant>.png` (full
patches) and `examples_<variant>_crop.png` (64-px crops around the densest cluster of
touching nuclei), for the 8 fold-2 patches with the most touching-nuclei pixels; all
eight are Colon, where crowding is worst.

- **Honest outcome: on real nuclei the layer does not help, and costs a little.** The
  learned-cost variant is 0.01 IoU and 0.017 BF₂ below the plain U-Net, consistently
  across tolerances (1, 2, 3 px), tissues (HeadNeck is the one exception, +0.02 IoU
  and +0.014 BF₂ on 169 patches), and at the instance level (F1 0.60 vs 0.66, PQ 0.48 vs
  0.53). The difference is small but not noise. The image-gradient variant is clearly
  worse, as on Pets.
- **Why: the layer is a smoother here, and nuclei are small.** With p ≤ 50 the layer
  diffuses the unaries across every edge whose cost is not large, so the output is
  softer than the U-Net's (16 % soft pixels against 15 %, and visibly blurrier blobs
  in `examples_rw_learned_crop.png`), and it bridges the 1–2 px gaps between touching
  nuclei that the U-Net's logits keep. On Pets the object was 100 px across and this
  cost nothing; on nuclei about 25 px across it costs the boundary metrics directly and the
  instance count indirectly (the IoU gap grows with the number of nuclei per patch).
  The learned edge head is nevertheless a clean contour detector that does respond
  to the interfaces between touching nuclei (last column of the crop panels), but
  its contours are 2–3 px wide and the costs along them are not large enough at
  p = 50 to stop the diffusion. Lower p than Pets was never tried, nor a sharper
  cost parametrisation (e.g. the costs through an exponential rather than a sigmoid).
- **The division of labour is extreme.** As on Pets, the network leaves the decision
  to the layer: its own logits are a checkerboard of speckle (348 components per
  patch against 24 true nuclei, F1 0.08) that the layer cleans up into 23.8
  components with F1 0.60. The layer adds 0.035 IoU and 0.068 BF₂ over its own
  logits, but the two-stage system does not beat the one-stage one.
- **Deployment at p = ∞ costs 0.05 IoU at the pixel level but is the best instance
  segmenter of the RW outputs.** The exact PW limit on the learned costs loses
  0.046 IoU and 0.034 BF₂ against the converged finite-p solve, and the panels show
  why: in crowded regions it floods whole clusters into one component. Yet on the
  same 307 patches its instance metrics are better than the layer's (F1 0.618 vs
  0.581, PQ 0.49 vs 0.46, count error 0.25 vs 0.34), because it is binary and
  removes the faint spurious blobs that survive thresholding the soft output; on
  Breast it even reaches the U-Net's PQ (0.535 vs 0.547) with a lower count error.
  The train-at-finite-p / deploy-at-the-limit scheme therefore works on real data
  in the sense that the limit is usable (unlike with image-gradient costs, 0.18
  IoU), but it is not free.
- **The label-noise caveat, measured.** The ground-truth boundaries lie within 1 px of
  a strong colour edge only 55.9 % of the time; every method's output does so at
  least as often (U-Net 57.7 %, layer 57.9 %, limit 57.7 %). Either the labels are
  indeed a pixel or two off the visible edge, or nucleus boundaries on H&E are
  often not strong colour edges at all (cytoplasm and nucleus of similar hue). In
  both cases boundary F-scores at 1 px against these labels cannot separate a
  method that follows the image from one that follows the label noise, which is
  part of the reason the BF₁ gap (−0.023) is larger than the BF₃ gap (−0.012). The
  `rw_img` limit shows the other side: it follows image edges 80 % of the time and
  is useless. A dataset with pixel-accurate manual boundaries (CoNSeP, MoNuSeg) is
  needed for the pixel-level boundary claim; the instance metrics above do not
  depend on the exact boundary and already tell the same story.
- **What the layer would need to help here.** Edge costs that are sharp and large
  where nuclei touch (a cost head trained with an explicit boundary target, or
  costs from the instance interfaces that the data provide), a target that leaves
  the interface pixels as background so that separating nuclei is rewarded, and a
  lower p, or a p-dependent cost scale, so that the layer stops being a smoother
  before it is a cutter. Section 6.1 tries the target, the lower p and the sharper
  parametrisation.

### 6.1 Letting the layer cut: gap target, lower p, sharper edge costs

Added 17 October 2026 (side session). Code: `--gap`, `--edge-param`, `--edge-cmax`,
`--edge-learn-scale`, `--tag` in `experiments/exp_unet_seg.py` (class `SegmenterX`),
`experiments/run_gap.sh`, `experiments/compare_gap.py` (table, paired statistics),
`experiments/seam_stats.py` (does the output cut the seams?), `plot_pannuke.py --runs`.
Raw results, per-image metrics and figures: `results/pannuke/gap/` (`compare.md`,
`seam_stats.json`, `figures/`).

**What was changed.** Three of the four things section 6 asked for, together. (i) *Gap
target*: the binary mask with the 2-px seam between touching nuclei set to background,
for training, validation and test, for every variant, so that separating nuclei is
rewarded instead of punished (the seam is 0.09 % of the pixels, so pixel metrics against
the gap mask and against the binary mask are comparable; the U-Net of section 6 scores
0.717 against the gap mask instead of 0.719). The instance metrics are unchanged, and
the "ground truth" ceiling row becomes the gap mask itself, F1 0.998. (ii) *Lower p*:
5 → 20 and 2 → 10 instead of 5 → 50, so that the unaries s^p stay soft and anchor the
solution while a contour can still be a hard cut. (iii) *Sharper edge costs*: 8·σ(h)
instead of σ(h), with the scale 8 learnable (initialised at the unary clamp c_max = 8), so
that the cost head can make a contour as expensive as a confident unary. Everything else
is section 6's recipe (fold 1 → fold 2, 30 epochs, K = 20, BCE + 0.5 aux BCE). Five
runs: the U-Net under the gap target, and the learned-cost layer under the gap target at
5 → 50, at 5 → 20, at 5 → 20 with sharp edges and at 2 → 10 with sharp edges.

**Results on all of fold 2** (2523 patches; the PW limit on the same 307 patches as
section 6). The first rows are section 6's runs. Instance metrics on the raw 4-connected
components of the thresholded output.

| target | run | output | IoU | BF₁ | BF₂ | BF₃ | band acc. | soft px | F1@0.5 | PQ | count err. |
|---|---|---|---|---|---|---|---|---|---|---|---|
| binary | unet (sec. 6) | sigmoid, thresholded at 0.5 | **0.719** | **0.652** | **0.769** | **0.825** | **0.807** | 15.4 % | 0.656 | 0.531 | 0.275 |
| binary | rw_learned, p 5 → 50 (sec. 6) | layer, 20 steps | 0.709 | 0.628 | 0.752 | 0.813 | 0.799 | 16.1 % | 0.604 | 0.482 | 0.337 |
| binary | rw_learned, p 5 → 50 (sec. 6) | PW limit (307) | 0.661 | 0.591 | 0.711 | 0.768 | 0.771 | 0 | 0.618 | 0.490 | 0.246 |
| gap | unet | sigmoid, thresholded at 0.5 | 0.717 | 0.651 | 0.768 | 0.825 | 0.806 | 15.5 % | 0.667 | 0.541 | 0.296 |
| gap | rw_learned, p 5 → 50 | layer, 20 steps | 0.705 | 0.624 | 0.747 | 0.809 | 0.797 | 16.4 % | 0.610 | 0.487 | 0.357 |
| gap | rw_learned, p 5 → 50 | PW limit (307) | 0.664 | 0.587 | 0.710 | 0.768 | 0.770 | 0 | 0.621 | 0.490 | 0.246 |
| gap | rw_learned, p 5 → 20 | layer, 20 steps | 0.707 | 0.625 | 0.748 | 0.810 | 0.797 | 15.8 % | 0.635 | 0.508 | 0.313 |
| gap | rw_learned, p 5 → 20 | PW limit (307) | 0.476 | 0.482 | 0.562 | 0.597 | 0.669 | 0 | 0.510 | 0.417 | 0.510 |
| gap | rw_learned, p 5 → 20, 8·σ edges | layer, 20 steps | 0.706 | 0.624 | 0.747 | 0.810 | 0.795 | 16.1 % | 0.625 | 0.499 | 0.295 |
| gap | rw_learned, p 5 → 20, 8·σ edges | PW limit (307) | 0.435 | 0.446 | 0.522 | 0.555 | 0.641 | 0 | 0.474 | 0.390 | 0.567 |
| gap | rw_learned, p 2 → 10, 8·σ edges | layer, 20 steps | 0.712 | 0.639 | 0.759 | 0.819 | 0.796 | 14.5 % | **0.678** | **0.548** | **0.225** |
| gap | rw_learned, p 2 → 10, 8·σ edges | converged | 0.716 | 0.639 | 0.760 | 0.820 | 0.801 | 14.8 % | **0.680** | **0.549** | 0.226 |
| gap | rw_learned, p 2 → 10, 8·σ edges | PW limit (307) | 0.508 | 0.496 | 0.582 | 0.620 | 0.671 | 0 | 0.523 | 0.435 | 0.555 |
| gap | ground truth | gap mask | 1 | 1 | 1 | 1 | 1 | 0 | 0.998 | 0.990 | 0.002 |

Paired per-patch differences (2523 patches, bootstrap 95 % intervals), layer minus the
U-Net trained on the same gap target: p 5 → 50: IoU −0.012 [−0.015, −0.009], BF₂ −0.021;
p 5 → 20: −0.010, −0.021; p 5 → 20 sharp: −0.011, −0.021; **p 2 → 10 sharp: IoU −0.005
[−0.007, −0.002], BF₂ −0.009 [−0.012, −0.007]**, better than the U-Net on 33 % of the
patches, and +0.007 IoU on the 486 patches with fewer than 10 nuclei (−0.010 on the 179
with more than 50). On HeadNeck (169 patches) the p 2 → 10 layer is above the U-Net on
every metric (IoU 0.697 vs 0.670, BF₂ 0.765 vs 0.741, F1 0.671 vs 0.649, PQ 0.547 vs 0.528).
Limit minus converged on the 307 patches: −0.037 IoU at p = 50, −0.23 at p = 20, −0.20 at
p = 10. The learnable edge scale went *down*, from 8 to 3.4 (p 5 → 20) and 4.1 (p 2 → 10),
within the first six epochs and stayed there (`figures/training.png`; the dotted p axis
there shows the 5 → 50 schedule only).

**Does anything cut the seams?** `seam_stats.json`: fraction of the 142 211 seam pixels
of fold 2 predicted as background, and fraction of the 8999 seams (components of the
touch mask) entirely background. U-Net, binary target: 15.1 % / 10.6 %; U-Net, gap target:
19.1 % / 13.0 %. Layer, gap target: 16.8 % / 11.9 % at p = 50, 18.5 % at p = 20, 19.9 % /
13.6 % at p = 10 with sharp edges. In every run the layer output cuts *fewer* seam pixels
than its own logits do (25–31 % for the logits), and the converged solve fewer still
(11–18 %); at best the layer matches the U-Net. The crops (`figures/examples_rw_p10_sharp_crop.png`,
`examples_unet_gap_crop.png`) show the same thing: at p 2 → 10 the network's own logits
are now a recognisable nucleus detector with dark seams (54 components per patch instead
of 340 at p = 50), the layer blurs those seams half shut, and the exact limit floods whole
crops into one component or none.

- **Honest outcome: the three changes together close half of the pixel-level gap and
  make the layer the best raw instance segmenter, but the layer still does not cut, and it
  still does not beat the U-Net.** The gap target on its own changes little (U-Net: F1
  0.656 → 0.667, seam pixels cut 15 → 19 %; the layer at p 5 → 50 is slightly *worse* than
  under the binary target, −0.005 IoU paired). Lower p at the old parametrisation changes
  nothing at the pixel level. Only the lowest schedule with the sharp parametrisation
  moves: −0.005 IoU and −0.009 BF₂ instead of −0.012 and −0.021, and instance F1 0.678,
  PQ 0.548, count error 0.225 against the gap-target U-Net's 0.667 / 0.541 / 0.296 at the
  same threshold and without any post-processing (section 7's min-area-filtered,
  boundary-trained U-Net, F1 0.714, remains better). But the seam statistics say the gain
  is not the mechanism we wanted: the layer cuts no more seam pixels than the U-Net and a
  third fewer than its own logits, the network *lowered* the edge-cost scale it was
  given rather than raising it, and the inner logits at p = 10 are far closer to a plain
  U-Net's output than at p = 50. At p ≈ 10 the unaries s^p are strong enough to anchor
  every moderately confident pixel, so the layer degenerates toward a mild, edge-aware
  smoothing of a U-Net that now does most of the work itself, and the result is a system
  that behaves like the U-Net plus a small denoiser: fewer spurious components (hence the
  instance numbers), slightly blurrier boundaries (hence BF₁–BF₃ still below).
- **The limit is lost at low p.** Costs learned at p = 10 or 20 mean nothing at p = ∞:
  the exact PW on them scores 0.44–0.51 IoU and about 10 components per patch, because
  the network relied on unaries whose p-th power no longer saturates and on contours with
  holes that a maximum-spanning-forest path walks through. The train-at-finite-p /
  deploy-at-the-limit scheme of section 6 (−0.04 IoU at p = 50) and the finite-p gains
  above therefore pull in opposite directions on this data; one cannot have both with
  a single schedule. What is left untried, and would be needed before concluding that a
  cut-capable last layer cannot help on nuclei: supervising the cost head directly with
  the seam mask (an edge target rather than hoping the segmentation loss finds it), a
  loss that pays for the separation of instances rather than for pixels near seams, and
  a dataset with pixel-accurate boundaries where a 1-px seam is a real image feature.

## 7. Does a boundary- or instance-level loss open a gap? (PanNuke, Pets)

Added 17 October 2026 (side session). Code: `--loss {bce,boundary,instance}` in
`experiments/exp_unet_seg.py`, `experiments/run_losses.sh`,
`experiments/compare_losses.py` (tables, paired statistics, `losses.png`). Raw results,
per-image metrics and figures: `results/pannuke_losses/{boundary,instance}/` and
`results/pets_losses/boundary/`.

**Hypothesis.** Sections 3 and 6 trained everything with a per-pixel BCE, and under
that loss the plain U-Net learned to sharpen its own output as well as the layer does.
A loss that pays for boundary placement or for separating neighbouring objects should
favour a model with an explicit spatial prior, if the layer is to be worth anything.
Both losses are applied to the final output of *both* variants (for `rw_learned` the
same loss on the layer output, plus 0.5 times the same loss on the logits, as the aux
BCE before), so the comparison stays fair; everything else is the recipe of section 6
(fold 1 → fold 2, 30 epochs, p annealed 5 → 50, K = 20).

- **Boundary loss.** Per-pixel BCE with the pixels within 3 px of the true boundary
  weighted ×5 (band = max-pool minus min-pool of the target with a 7×7 window), plus a
  differentiable boundary-F surrogate at a 2-px tolerance (Bokhovkin & Burnaev 2019:
  soft boundaries as the inner morphological gradient x − minpool₃(x), precision and
  recall through max-pooled tolerance regions, loss = 1 − 2PR/(P+R)), weight 1.
- **Instance loss (PanNuke only).** The 2-px seam between touching nuclei (pixels with
  a 4-neighbour in a different instance, 0.09 % of the pixels) is set to *background*
  in the target, and the seam plus a 1-px flank is weighted ×21 in the BCE. This is the
  "target that leaves the interface pixels as background" of section 6: separating
  touching nuclei is now rewarded, where the binary union target punished it. Test
  metrics are still computed against the original binary mask and the instance masks.

**Results on all of fold 2** (2523 patches; the PW limit on the same 307 patches as
section 6). The `bce` rows are section 6's runs. Instance metrics on the raw
4-connected components, as before; see the next table for what they become after a
minimum-area filter.

| loss | variant | output | IoU | BF₁ | BF₂ | BF₃ | band acc. | soft px | edge align. | F1@0.5 | PQ | count err. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bce | unet | sigmoid, thresholded at 0.5 | 0.719 | 0.652 | 0.769 | 0.825 | 0.807 | 15.4 % | 0.577 | 0.656 | 0.531 | 0.275 |
| bce | rw_learned | layer, 20 steps | 0.709 | 0.628 | 0.752 | 0.813 | 0.799 | 16.1 % | 0.579 | 0.604 | 0.482 | 0.337 |
| bce | rw_learned | converged | 0.710 | 0.630 | 0.751 | 0.812 | 0.805 | 16.2 % | 0.572 | 0.602 | 0.480 | 0.322 |
| bce | rw_learned | PW limit (307) | 0.661 | 0.591 | 0.711 | 0.768 | 0.771 | 0 | 0.577 | 0.618 | 0.490 | 0.246 |
| boundary | unet | sigmoid, thresholded at 0.5 | **0.718** | **0.669** | **0.787** | **0.841** | **0.819** | 13.2 % | 0.569 | 0.286 | 0.232 | 4.42 |
| boundary | rw_learned | layer, 20 steps | 0.714 | 0.656 | 0.778 | 0.835 | 0.816 | 13.2 % | 0.571 | 0.263 | 0.213 | 4.78 |
| boundary | rw_learned | converged | 0.715 | 0.657 | 0.778 | 0.834 | 0.819 | 13.2 % | 0.566 | 0.285 | 0.231 | 4.23 |
| boundary | rw_learned | PW limit (307) | 0.673 | 0.626 | 0.755 | 0.821 | 0.782 | 0 | 0.559 | 0.140 | 0.111 | 8.78 |
| instance | unet | sigmoid, thresholded at 0.5 | **0.719** | 0.651 | 0.769 | 0.827 | 0.807 | 17.0 % | 0.569 | **0.663** | **0.538** | 0.315 |
| instance | rw_learned | layer, 20 steps | 0.699 | 0.617 | 0.744 | 0.807 | 0.791 | 18.3 % | 0.581 | 0.594 | 0.470 | 0.321 |
| instance | rw_learned | converged | 0.701 | 0.619 | 0.742 | 0.804 | 0.799 | 17.8 % | 0.577 | 0.574 | 0.455 | 0.339 |
| instance | rw_learned | PW limit (307) | 0.592 | 0.539 | 0.659 | 0.715 | 0.729 | 0 | 0.589 | 0.593 | 0.465 | 0.312 |
| ground truth | binary mask | | 1 | 1 | 1 | 1 | 1 | 0 | 0.559 | 0.913 | 0.883 | 0.088 |

The raw logits of the `rw_learned` models are in `results/pannuke_losses/summary.md`;
as in section 6 they are speckle that the layer cleans up (215–387 components per patch).

**Instance metrics after removing components smaller than 8 px**
(`experiments/inst_minarea.py`, `results/pannuke_losses/minarea.json`; 8 px is 1.5 % of
the mean nucleus area, the filter is the same for every row; the raw rows above are
min-area 1):

| loss | variant | output | IoU | F1@0.5 | PQ | count err. | components / patch (raw → filtered) |
|---|---|---|---|---|---|---|---|
| bce | unet | sigmoid, thresholded at 0.5 | 0.720 | 0.683 | 0.552 | 0.224 | 23.0 → 21.2 |
| bce | rw_learned | layer | 0.711 | 0.633 | 0.505 | 0.268 | 23.8 → 21.6 |
| bce | rw_learned | PW limit (307) | 0.661 | 0.618 | 0.490 | 0.246 | 20.8 → 20.8 |
| boundary | unet | sigmoid, thresholded at 0.5 | 0.725 | **0.714** | **0.582** | 0.236 | 90.8 → 22.1 |
| boundary | rw_learned | layer | 0.722 | 0.682 | 0.553 | 0.252 | 93.5 → 21.5 |
| boundary | rw_learned | PW limit (307) | 0.684 | 0.598 | 0.475 | 0.275 | 160.7 → 18.5 |
| instance | unet | sigmoid, thresholded at 0.5 | 0.719 | 0.696 | 0.565 | 0.226 | 24.1 → 21.8 |
| instance | rw_learned | layer | 0.701 | 0.617 | 0.488 | 0.278 | 22.4 → 20.6 |
| instance | rw_learned | PW limit (307) | 0.592 | 0.593 | 0.465 | 0.312 | 19.8 → 19.8 |

**Paired per-patch differences** (2523 patches, bootstrap 95 % intervals;
`results/pannuke_losses/summary.md` has the full list):

| comparison | loss | IoU | BF₂ | band acc. | layer better on |
|---|---|---|---|---|---|
| rw_learned layer − unet | bce | −0.009 [−0.012, −0.007] | −0.017 [−0.020, −0.014] | −0.008 | 25 % / 19 % |
| rw_learned layer − unet | boundary | −0.005 [−0.007, −0.003] | −0.009 [−0.011, −0.007] | −0.003 | 43 % / 31 % |
| rw_learned layer − unet | instance | −0.019 [−0.022, −0.017] | −0.025 [−0.028, −0.023] | −0.015 | 18 % / 16 % |
| unet, loss − bce | boundary | −0.000 [−0.003, +0.002] | +0.018 [+0.015, +0.021] | +0.011 | |
| unet, loss − bce | instance | −0.000 [−0.002, +0.002] | +0.000 [−0.001, +0.002] | −0.001 | |
| rw_learned layer, loss − bce | boundary | +0.004 [+0.001, +0.007] | +0.026 [+0.022, +0.029] | +0.017 | |
| rw_learned layer, loss − bce | instance | −0.010 [−0.012, −0.008] | −0.008 [−0.010, −0.006] | −0.007 | |
| PW limit − converged (307) | boundary | −0.034 [−0.040, −0.029] | −0.013 [−0.016, −0.010] | −0.033 | |
| PW limit − converged (307) | instance | −0.108 [−0.122, −0.095] | −0.076 [−0.088, −0.064] | −0.065 | |

**Oxford-IIIT Pet, 128 px, boundary loss** (3669 test images; limit on 300; the `bce`
rows are section 3's runs, which did not compute BF₃):

| loss | variant | output | IoU | BF₁ | BF₂ | BF₃ | band acc. | soft px |
|---|---|---|---|---|---|---|---|---|
| bce | unet | sigmoid, thresholded at 0.5 | 0.853 | 0.586 | 0.724 | – | 0.778 | 13.4 % |
| bce | rw_learned | layer, 20 steps | 0.852 | 0.584 | 0.722 | – | 0.771 | 14.2 % |
| bce | rw_learned | converged | 0.853 | 0.586 | 0.724 | – | 0.775 | 14.9 % |
| bce | rw_learned | PW limit (300) | 0.822 | 0.561 | 0.695 | – | 0.749 | 0 |
| boundary | unet | sigmoid, thresholded at 0.5 | 0.864 | 0.629 | 0.769 | 0.837 | 0.787 | 7.6 % |
| boundary | rw_learned | sigmoid, thresholded at 0.5 | 0.859 | 0.613 | 0.756 | 0.829 | 0.786 | 11.3 % |
| boundary | rw_learned | layer, 20 steps | 0.864 | 0.634 | 0.776 | 0.844 | 0.787 | 9.1 % |
| boundary | rw_learned | converged | **0.867** | **0.643** | **0.782** | **0.848** | **0.793** | 9.3 % |
| boundary | rw_learned | PW limit (300) | 0.851 | 0.634 | 0.776 | 0.843 | 0.778 | 0 |

Paired, rw_learned layer − unet under the boundary loss: IoU +0.000 [−0.001, +0.002],
BF₂ +0.007 [+0.005, +0.009] (layer better on 55 % of the images); PW limit − unet on the
300 limit images: IoU −0.013 [−0.020, −0.005], BF₂ +0.008 [−0.000, +0.017].

Figures: `results/pannuke_losses/losses.png` (the first table as a dot chart),
`results/pets_losses/losses.png`, and per loss the training curves and the example
panels of section 6 (`results/pannuke_losses/<loss>/figures/`).

- **Honest outcome: neither loss opened a gap in the layer's favour on PanNuke.** The
  boundary loss narrowed it, from −0.009 to −0.005 IoU and from −0.017 to −0.009 BF₂
  (both intervals still exclude zero; the layer wins on 43 % of the patches instead
  of 25 %), because it helped the layer model more than the U-Net (+0.026 vs +0.018
  BF₂, +0.017 vs +0.011 band accuracy). The instance loss widened it to −0.019 IoU.
  The U-Net stays the better nucleus segmenter under all three losses, on every
  tolerance and on the instance metrics, raw or filtered.
- **The boundary loss does what it should, for both models.** +0.018 BF₂ and +0.011
  band accuracy for the U-Net at unchanged IoU, +0.026 / +0.017 for the layer; the
  outputs are sharper (13 % soft pixels against 15–16 %). Its one pathology is worth
  recording: the soft boundary-F surrogate, which measures boundaries by a 1-px
  morphological gradient inside pooled tolerance regions, is satisfied as cheaply
  by a dotted line as by a solid one, and both models learned to sprinkle isolated
  pixels along the outer side of every contour (`boundary/figures/examples_unet_crop.png`).
  The raw instance numbers therefore collapse (91 components per patch, F1 0.29), but
  the dots are 1–4 px and a minimum-area filter of 8 px removes them, after which the
  boundary-trained U-Net is the best instance segmenter of the whole study (F1 0.714,
  PQ 0.582 against 0.683 / 0.552 for the BCE U-Net with the same filter). The same
  filter is applied to every row of the second table, so the ranking it gives is fair:
  boundary loss > instance loss > BCE for the U-Net, and the layer 0.03–0.08 F1 below
  the U-Net under each. The filter also corrects one reading of section 6: with it,
  the BCE layer (F1 0.633) is above its own exact limit (0.618), so the limit's raw
  instance advantage there was partly that it carries no faint blobs to begin with;
  its count error (0.246 vs 0.268) remains the best of the RW outputs under BCE.
- **The instance loss did not teach either model to separate nuclei.** The seam is
  0.09 % of the pixels; even at ×21 it is 2 % of the loss, and the U-Net's output is
  indistinguishable from its BCE output at the pixel level (paired differences within
  ±0.002), with a marginal instance gain (F1 0.663 vs 0.656 raw, 0.696 vs 0.683
  filtered) and more spurious small components (count error 0.315 vs 0.275 raw). For the
  layer the effect was negative on everything: 0.01 IoU below its BCE self, 18 % soft
  pixels, and the learned edge head stopped being a contour detector: under this loss
  its costs are diffuse blobs inside the nuclei rather than lines along their
  boundaries (last column of `instance/figures/examples_rw_learned_crop.png`), so
  the exact limit floods whole clusters (0.59 IoU, −0.108 against the converged solve).
  Asking the layer to put a 2-px background seam between two touching nuclei at
  p ≤ 50 is asking a diffusion to produce a line; the cost head would need a cost of
  order cmax across the seam and nothing elsewhere, and the gradient through 20 PCG
  steps did not find that solution. A seam loss on the cost head directly (an edge
  target), rather than on the layer output, is the obvious next thing to try, and was
  not tried here.
- **Where the limit stands.** Under the boundary loss the exact PW limit improves on
  its BCE self (0.673 vs 0.661 IoU, 0.755 vs 0.711 BF₂) and its price against the
  converged solve drops from 0.046 to 0.034 IoU and from 0.034 to 0.013 BF₂, i.e. the
  sharper the trained solution, the less the limit loses. Its raw instance numbers
  are the speckle problem again (161 components per patch); filtered, they are no
  better than under BCE (F1 0.598 vs 0.618, count error 0.275 vs 0.246), so the
  boundary loss improved the limit's pixels but not its objects.
- **Pets is the one place a gap opened, and it is small.** With the boundary loss both
  models gain 0.011–0.012 IoU and 0.045–0.054 BF₂ over BCE, and the converged layer is now above
  the U-Net on every metric (0.867 vs 0.864 IoU, 0.782 vs 0.769 BF₂, 0.643 vs 0.629
  BF₁); the paired BF₂ advantage of the 20-step layer, +0.007, is significant but
  tiny, and the exact limit now matches the U-Net's boundary scores (0.776 vs 0.769
  BF₂) at a 0.013 IoU cost, down from 0.03 under BCE. On large objects a loss that
  pays for boundary placement does let a spatial prior earn its keep; on 25-px nuclei
  it does not, which is consistent with section 6's diagnosis (the layer is a smoother
  at p ≤ 50) and leaves the p / cost-scale question open.

## 8. Fixed-point reweighting instead of exponentiation

Added 17 October 2026 after Hugues' suggestion: rather than raising the weights to a
growing p, keep a benign base p₀ and iterate, multiplying each weight by a factor of
the current solution until the pair (weights, solution) stops changing. This is the
half-quadratic / majorize–minimize reweighting of the ℓ0 project applied inside the
layer. Implementation: `RWLayer(mode="reweighted")` in `experiments/pw_layer.py`;
base weights exp(−p₀ c), then `outer` = 5 steps of

    w_e ← w_e⁰ · ρ(x_u − x_v),   a1_i ← a1_i⁰ · ρ(x_i − 1),   a0_i ← a0_i⁰ · ρ(x_i),

ρ(d) = ε²/(ε² + d²) (Cauchy, the smoothed-ℓ0 weight) or 1/(1 + |d|/ε) (smoothed ℓ1).
The unaries are reweighted too: they are the edges to the two label nodes of the
augmented graph, and without this the output stays as soft as the unaries. Inner
solves are implicit, autograd runs through the outer loop (checked against finite
differences). Comparison on the synthetic scenes of section 2 (256², three scenes per
case, α = 0.1), `experiments/exp_reweighted_synthetic.py`, results and figures in
`results/reweighted/`. Besides the quality metrics we record the inner PCG iterations
(to 1e-9) of the last solve and of all solves, the smallest weight, and two gradient
supports: that of the loss to the ground truth (which shrinks trivially as the loss is
minimised) and that of a fixed random linear functional of the output, the number of
edges through which the output can be influenced at all.

| scene | method | BF₂ | soft px | PCG iters last / cum. | w_min | sensitivity support (edges) |
|---|---|---|---|---|---|---|
| clean, aligned | soft prediction | 0.956 | 22 % | | | |
| | annealed p = 100 | 0.977 | 0.9 % | 128 | 6e-13 | 6 855 |
| | annealed p = 200 | **1.000** | 0.3 % | 211 | 5e-25 | 4 007 |
| | annealed p = 500 | **1.000** | 0.0 % | 484 | 4e-61 | 1 164 |
| | reweighted Cauchy ε = 0.1, p₀ = 50 | 0.980 | 0.1 % | 99 / 575 | 6e-9 | 1 428 |
| | reweighted Cauchy ε = 0.1, p₀ = 100 | **1.000** | 0.0 % | 153 / 892 | 6e-15 | 1 304 |
| noisy, aligned | soft prediction | 0.967 | 22 % | | | |
| | annealed p = 100 | 0.966 | 3.0 % | 127 | 3e-24 | 5 495 |
| | annealed p = 200 | 0.970 | 2.2 % | 408 | 1e-47 | 3 948 |
| | annealed p = 500 | 0.967 | 1.5 % | 5000 (not converged) | 1e-117 | 917 |
| | reweighted Cauchy ε = 0.1, p₀ = 50 | 0.971 | 0.1 % | 102 / 597 | 2e-14 | 111 |
| | reweighted Cauchy ε = 0.1, p₀ = 100 | **0.976** | 0.2 % | 181 / 1087 | 4e-26 | 71 |
| clean, edge shifted 4 px | soft prediction | 0.960 | 22 % | | | |
| | annealed p = 100 / 500 | 0.733 / 0.005 | | | | |
| | reweighted Cauchy ε = 0.1, p₀ = 10 / 50 / 100 | 0.870 / 0.451 / 0.062 | | | | |

- **The reweighting sharpens, cheaply and without the dynamic range.** Five Cauchy
  steps make the output binary (0.0–0.2 % soft pixels) from any base, with the weights
  never below 1e-14 at p₀ = 50 where annealing needs 1e-47 and beyond. On the noisy
  scene this is the win Hugues anticipated: the reweighted layer reaches the best
  quality the annealed family ever gets (0.971–0.976 against 0.970) with a last solve
  of 100–180 PCG iterations, where the annealed solve at p = 500 does not converge in
  5000. The smoothed-ℓ1 weight is too weak to sharpen within five steps; the Cauchy
  weight is the right one, as in the ℓ0 project.
- **It does not move the boundary; the base weights do.** From p₀ = 10 the fixed
  point sharpens the soft prediction in place (boundary score equal to the soft
  prediction's on the clean scene, 0.96). The cut lands on the image edge only when
  the base edge contrast is strong enough, p₀ ≈ 50–100, which is where plain
  annealing already places it. So the reweighting is a complement to annealing, not a
  replacement: anneal to a moderate p₀ where the solve is still cheap and the boundary
  is right, then reweight to binary instead of pushing p further. Counting all solves
  it costs 3–4 times one annealed solve, each of them well conditioned.
- **The fixed point is rigid.** At the fixed point the losing unary of every pixel is
  down-weighted by ε², so each pixel is locked to its label and the output's
  sensitivity to the edge costs collapses onto 70–140 edges on the noisy scene, against
  4 000 for the annealed solution of the same quality; on the clean scene the two are
  comparable (1 300 vs 1 200–4 000). This is the self-reinforcing nature of the
  scheme, the same thing that makes it sharp, and it is the price of losing the
  temperature: for training, the gradient should be taken after one or two
  reweighting steps or with a larger ε, i.e. at finite temperature again, with the
  fully converged fixed point used only at deployment. Note that the ground-truth loss
  gradient is not the right measure here: it shrinks whenever the output is right.
- **Same failure mode, gentler.** With the image edge off the true boundary, the fixed
  point from p₀ = 10 degrades gracefully (0.87–0.89 against 0.96) because it sharpens
  the soft prediction rather than snapping to an edge; from p₀ ≥ 50 it snaps like
  annealing does. The limit object also changes: the fixed point is a local minimiser
  of a nonconvex piecewise-constant energy, not the unique Power Watershed, and it has
  no quasi-linear combinatorial evaluation; deployment is a few linear solves.

## 9. PanNuke: the reweighted layer, and the thresholded U-Net done properly

Added 17 October 2026. Two additions to the PanNuke comparison of sections 6 and 7.

**The practitioner's baseline with a tuned threshold.** Every "thresholded at 0.5" row
above is what most practitioners deploy. The stronger form of the same baseline sweeps
the threshold (`experiments/threshold_sweep.py`, all of fold 2, results in
`results/pannuke/threshold_sweep_*.json`):

| plain U-Net (BCE), threshold | IoU | BF₁ | BF₂ | band acc. | instance F1 | PQ |
|---|---|---|---|---|---|---|
| 0.3 | 0.711 | 0.633 | 0.753 | 0.815 | 0.601 | 0.483 |
| 0.4 | 0.722 | 0.654 | 0.770 | 0.816 | 0.635 | 0.513 |
| 0.5 | 0.719 | 0.652 | 0.769 | 0.807 | 0.656 | 0.531 |
| 0.6 | 0.702 | 0.626 | 0.753 | 0.788 | 0.662 | 0.541 |
| 0.7 | 0.666 | 0.569 | 0.712 | 0.755 | 0.648 | 0.525 |

Tuning the cut is worth 0.003 IoU at most; the 0.5 baseline is already the best case
of that pipeline, and the same holds for the boundary-loss U-Net (best IoU at 0.5, best
BF₂ at 0.6) and for the unrolled layer's own output (best at 0.4, +0.002). The sweep
also shows, in passing, what the layer does for the learned-cost model: its raw
logits fall apart into 240–520 components per patch at any threshold, and the layer
brings that back to 24, the true count.

**The reweighted layer trained end to end** (`--layer reweighted` in
`experiments/exp_unet_seg.py`; results `results/pannuke_reweighted/{bce,boundary}/`).
Same recipe as section 6, but the layer is an implicit solve at the annealed base
weights exp(−p c), p from 5 to 50, followed by two Cauchy reweighting steps (ε = 0.1,
unaries included) during training, five at evaluation ("fixed point"). The "limit"
row is not reported: the exact Power Watershed of the base costs is not the limit of
this layer. Training costs 50 s per epoch against 11 s for the unrolled layer.

BCE loss, all of fold 2:

| output | IoU | BF₁ | BF₂ | band acc. | soft px | edge align. | F1@0.5 | PQ | count err. |
|---|---|---|---|---|---|---|---|---|---|
| plain U-Net, thresholded at 0.5 | **0.719** | **0.652** | **0.769** | **0.807** | 15.4 % | 0.577 | **0.656** | **0.531** | 0.275 |
| unrolled layer, 20 steps (section 6) | 0.709 | 0.628 | 0.752 | 0.799 | 16.1 % | 0.579 | 0.604 | 0.482 | 0.337 |
| reweighted layer, 2 steps (as trained) | 0.708 | 0.641 | 0.759 | 0.801 | 15.5 % | 0.594 | 0.646 | 0.518 | **0.269** |
| reweighted layer, 5 steps (fixed point) | 0.682 | 0.632 | 0.743 | 0.776 | 7.7 % | **0.628** | 0.653 | **0.531** | 0.303 |

Boundary loss:

| output | IoU | BF₁ | BF₂ | band acc. | soft px | edge align. | F1@0.5 | PQ | count err. |
|---|---|---|---|---|---|---|---|---|---|
| plain U-Net, thresholded at 0.5 | **0.718** | **0.669** | **0.787** | **0.819** | 13.2 % | 0.569 | 0.286 | 0.232 | 4.42 |
| unrolled layer, 20 steps (section 7) | 0.714 | 0.656 | 0.778 | 0.816 | 13.2 % | 0.571 | 0.263 | 0.213 | 4.78 |
| reweighted layer, 2 steps | 0.706 | 0.660 | 0.778 | 0.816 | 13.0 % | 0.590 | **0.364** | **0.295** | **2.98** |
| reweighted layer, 5 steps | 0.697 | 0.662 | 0.779 | 0.807 | 3.9 % | **0.603** | 0.317 | 0.258 | 3.58 |

(Under the boundary loss every method produces many tiny components, which the
instance metrics punish; section 7 has the min-area-filtered numbers.)

- **Same verdict on pixels, better on instances.** The reweighted layer matches the
  unrolled one on IoU and boundary scores and stays 0.01 below the plain thresholded
  U-Net. Where it differs is the instance side: with two steps it reaches the U-Net's
  count error and nearly its F1 and PQ (0.646 / 0.518 against 0.656 / 0.531), well
  above the unrolled layer (0.604 / 0.482), and under the boundary loss it is the best
  method on all three instance numbers. The full fixed point has the highest edge
  alignment of anything measured on this dataset (0.628) and the U-Net's PQ, but loses
  0.03 IoU: it commits confidently, including where it is wrong, which is the rigidity
  of section 8 showing up in the metrics.
- **Piecewise constant rather than binary on real images.** Five steps leave 7.7 % soft
  pixels under BCE and 3.9 % under the boundary loss, against 0.0–0.2 % on the synthetic
  scenes. The example crops (`figures/examples_rw_learned_crop.png`; the column titled
  "layer, 20 steps" is the 2-step layer and "PW limit" the base-cost limit) show what
  these are: not ramps but plateaus, whole nuclei or clusters sitting at one
  intermediate grey level. That is the ℓ0-type energy doing exactly what it does on
  gain graphs: once the edges inside a region are reweighted to agree, the region's
  value is set by its unaries as a block, and where those are balanced the block
  settles at a fraction. More steps or a smaller ε push it further along the same
  trade-off, more edge alignment for less IoU; a final threshold at 0.5 resolves the
  plateaus one way or the other.
- **Taken together with sections 6–8:** on PanNuke a thresholded U-Net is a hard
  baseline that no variant of the layer beats at the pixel level, including with a
  tuned threshold on either side. The layer's measurable contribution is at the
  instance level, where the reweighted version is the strongest form of it, and in
  edge alignment, which is label-free. Whether that is worth a layer that costs five
  times the training time is a question for a task where touching objects matter more
  than pixel IoU.

## 10. The two untried leads: an edge target on the cost head, and a Dice-band boundary loss

Added 17 October 2026 (side session, after sections 6.1 and 9). Code: `--w-edge`,
`--edge-pos`, `--edge-seam` and `--loss boundary_dice` in `experiments/exp_unet_seg.py`,
`experiments/run_leads.sh`; tables and statistics with `compare_losses.py`,
`seam_stats.py` and `inst_minarea.py`. Raw results, per-image metrics and figures:
`results/pannuke/leads/{dice,edge_bce,edge_dice,edge_gap_p10}/`.

Of the three leads section 7 listed, the lower-p / cost-scale one was run in section 6.1
(p 2 → 10 with 8·σ edges is the best finite-p configuration, but the layer still blurs
the seams half shut and its limit is lost). The two others:

- **Edge target on the cost head** (`--w-edge 1`). Section 6.1 ended on "supervising
  the cost head directly with the seam mask". Every grid edge whose two pixels carry
  different instance ids is a positive: nucleus / background boundaries (3 % of the
  edges) and the seams between touching nuclei (0.1 %), the latter weighted ×5 on top
  of the ×10 of all positives. BCE on the edge probability σ(h) averaged onto the edge
  (the cost divided by its scale), added with weight 1 to the segmentation loss. Three
  runs: binary target at p 5 → 50 with BCE (`edge_bce`) and with the Dice-band loss
  (`edge_dice`), and the gap target at p 2 → 10 with the 8·σ learnable-scale edges of
  section 6.1 (`edge_gap_p10`), to be read against that section's run without the target.
- **Dice-band boundary loss** (`--loss boundary_dice`, `dice/`). The band-weighted BCE of
  section 7's boundary loss (×5 within 3 px of the true boundary) plus 1 − soft Dice
  restricted to that band, instead of the boundary-F surrogate: it pays for filling the
  band correctly, and a dotted contour earns nothing. Both variants, binary target,
  p 5 → 50, so the comparison with section 7 is one-for-one.

**Results on all of fold 2** (2523 patches; the PW limit on the same 307 patches as
before). Binary target, p 5 → 50, except the last block (gap target, p 2 → 10, 8·σ
learnable-scale edges), whose comparison rows are section 6.1's. Instance metrics on the
raw 4-connected components; the min-area-filtered numbers follow.

| target, p | loss / cost head | variant | output | IoU | BF₁ | BF₂ | BF₃ | band acc. | soft px | edge align. | F1@0.5 | PQ | count err. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| binary, 5 → 50 | bce (sec. 6) | unet | logits | 0.719 | 0.652 | 0.769 | 0.825 | 0.807 | 15.4 % | 0.577 | 0.656 | 0.531 | 0.275 |
| | bce (sec. 6) | rw_learned | layer, 20 steps | 0.709 | 0.628 | 0.752 | 0.813 | 0.799 | 16.1 % | 0.579 | 0.604 | 0.482 | 0.337 |
| | bce (sec. 6) | rw_learned | PW limit (307) | 0.661 | 0.591 | 0.711 | 0.768 | 0.771 | 0 | 0.577 | 0.618 | 0.490 | 0.246 |
| | boundary_dice | unet | logits | 0.697 | 0.632 | 0.737 | 0.786 | 0.836 | 14.2 % | 0.555 | 0.612 | 0.498 | 0.876 |
| | boundary_dice | rw_learned | layer, 20 steps | 0.693 | 0.621 | 0.728 | 0.778 | 0.831 | 13.6 % | 0.546 | 0.595 | 0.482 | 0.878 |
| | boundary_dice | rw_learned | converged | 0.690 | 0.621 | 0.728 | 0.778 | 0.833 | 14.3 % | 0.544 | 0.601 | 0.486 | 0.818 |
| | boundary_dice | rw_learned | PW limit (307) | 0.658 | 0.591 | 0.695 | 0.748 | 0.815 | 0 | 0.518 | 0.633 | 0.502 | 0.487 |
| | bce + edge target | rw_learned | layer, 20 steps | 0.703 | 0.630 | 0.752 | 0.813 | 0.792 | 14.1 % | 0.554 | 0.446 | 0.355 | 1.25 |
| | bce + edge target | rw_learned | converged | 0.707 | 0.635 | 0.754 | 0.814 | 0.797 | 14.1 % | 0.558 | 0.435 | 0.347 | 1.11 |
| | bce + edge target | rw_learned | PW limit (307) | 0.684 | 0.624 | 0.744 | 0.802 | 0.783 | 0 | 0.569 | 0.501 | 0.395 | 0.489 |
| | boundary_dice + edge target | rw_learned | layer, 20 steps | 0.690 | 0.608 | 0.715 | 0.767 | 0.830 | 13.9 % | 0.525 | 0.505 | 0.408 | 1.56 |
| | boundary_dice + edge target | rw_learned | PW limit (307) | 0.646 | 0.553 | 0.662 | 0.721 | 0.807 | 0 | 0.495 | 0.428 | 0.339 | 1.40 |
| gap, 2 → 10, 8·σ | bce (sec. 6.1) | unet | logits | 0.717 | 0.651 | 0.768 | 0.825 | 0.806 | 15.5 % | 0.575 | 0.667 | 0.541 | 0.296 |
| | bce (sec. 6.1) | rw_learned | layer, 20 steps | 0.712 | 0.639 | 0.759 | 0.819 | 0.796 | 14.5 % | 0.585 | 0.678 | 0.548 | 0.225 |
| | bce (sec. 6.1) | rw_learned | converged | 0.716 | 0.639 | 0.760 | 0.820 | 0.801 | 14.8 % | 0.575 | 0.680 | 0.549 | 0.226 |
| | bce (sec. 6.1) | rw_learned | PW limit (307) | 0.508 | 0.496 | 0.582 | 0.620 | 0.671 | 0 | 0.669 | 0.523 | 0.435 | 0.555 |
| | bce + edge target | rw_learned | layer, 20 steps | 0.713 | 0.649 | 0.766 | 0.822 | 0.799 | 12.5 % | 0.582 | **0.723** | **0.587** | **0.207** |
| | bce + edge target | rw_learned | converged | **0.721** | **0.655** | **0.773** | **0.829** | **0.810** | 13.2 % | 0.569 | **0.724** | **0.588** | 0.214 |
| | bce + edge target | rw_learned | PW limit (307) | 0.637 | 0.612 | 0.718 | 0.763 | 0.746 | 0 | 0.625 | 0.682 | 0.562 | 0.334 |
| | ground truth | binary / gap mask | | 1 | 1 | 1 | 1 | 1 | 0 | 0.559 | 0.913 / 0.998 | 0.883 / 0.990 | 0.088 / 0.002 |

**Instance metrics after removing components smaller than 8 px** (same filter as
section 7, `results/pannuke/leads/minarea.json`):

| target, p | loss / cost head | variant | output | IoU | F1@0.5 | PQ | count err. | components / patch (raw → filtered) |
|---|---|---|---|---|---|---|---|---|
| binary, 5 → 50 | bce (sec. 7) | unet | logits | 0.720 | 0.683 | 0.552 | 0.224 | 23.0 → 21.2 |
| | boundary (sec. 7) | unet | logits | 0.725 | 0.714 | 0.582 | 0.236 | 90.8 → 22.1 |
| | boundary_dice | unet | logits | 0.702 | 0.653 | 0.532 | 0.596 | 31.3 → 27.7 |
| | bce (sec. 7) | rw_learned | layer | 0.711 | 0.633 | 0.505 | 0.268 | 23.8 → 21.6 |
| | boundary_dice | rw_learned | layer | 0.694 | 0.627 | 0.508 | 0.682 | 31.8 → 28.9 |
| | boundary_dice | rw_learned | PW limit (307) | 0.658 | 0.633 | 0.502 | 0.487 | 26.8 → 26.8 |
| | bce + edge target | rw_learned | layer | 0.705 | 0.641 | 0.510 | 0.255 | 42.4 → 22.3 |
| | bce + edge target | rw_learned | PW limit (307) | 0.684 | 0.575 | 0.454 | 0.304 | 30.2 → 23.0 |
| | boundary_dice + edge target | rw_learned | layer | 0.695 | 0.615 | 0.497 | 0.689 | 41.2 → 29.5 |
| gap, 2 → 10, 8·σ | bce (sec. 6.1) | unet | logits | 0.719 | 0.700 | 0.567 | 0.220 | 24.0 → 21.7 |
| | bce (sec. 6.1) | rw_learned | layer | 0.714 | 0.686 | 0.555 | 0.218 | 21.5 → 21.0 |
| | bce + edge target | rw_learned | layer | 0.716 | **0.726** | **0.589** | **0.202** | 22.0 → 21.8 |
| | bce + edge target | rw_learned | PW limit (307) | 0.638 | 0.682 | 0.562 | 0.334 | 16.1 → 16.1 |

(IoU in this table is against the binary mask for every row.)


**Seam statistics** (`seam_stats.json`, `limit_seams.json`): fraction of the 142 211
seam pixels of fold 2 predicted as background / fraction of the 8999 seams entirely
background; the limit on its 307 patches, with the other outputs on the same patches
in brackets for comparison.

| target, p | run | logits | layer, 20 steps | converged | PW limit (307) [logits / layer / converged on the same 307] |
|---|---|---|---|---|---|
| binary, 5 → 50 | bce (sec. 6), unet | 15 % / 11 % | | | |
| | bce (sec. 6), rw_learned | 20 % / 11 % | 15 % / 11 % | 9 % / 8 % | 25 % / 17 % [23 / 19 / 11 %] |
| | bce + edge target | 28 % / 3 % | 21 % / 10 % | 14 % / 6 % | 23 % / 9 % [30 / 24 / 15 %] |
| | boundary_dice, unet | 13 % / 8 % | | | |
| | boundary_dice, rw_learned | 20 % / 11 % | 15 % / 9 % | 13 % / 8 % | |
| gap, 2 → 10, 8·σ | bce, unet (sec. 6.1) | 19 % / 13 % | | | |
| | bce (sec. 6.1), rw_learned | 32 % / 19 % | 20 % / 14 % | 18 % / 12 % | 57 % / 48 % [31 / 22 / 20 %] |
| | bce + edge target | 42 % / 26 % | 29 % / 19 % | 23 % / 15 % | **52 % / 34 %** [43 / 34 / 24 %] |

**Paired per-patch differences** (2523 patches, bootstrap 95 % intervals):

| comparison | IoU | BF₁ | BF₂ | band acc. | first better on |
|---|---|---|---|---|---|
| gap target, p 2 → 10, 8·σ, edge target: converged − gap U-Net | +0.004 [+0.002, +0.007] | +0.004 [+0.002, +0.007] | +0.005 [+0.003, +0.008] | +0.004 [+0.004, +0.005] | 50 % / 54 % |
| same: layer (20 steps) − gap U-Net | −0.003 [−0.006, −0.001] | −0.001 [−0.004, +0.001] | −0.002 [−0.005, +0.000] | −0.007 | 36 % / 42 % |
| same: converged, with − without the edge target (sec. 6.1) | +0.005 [+0.003, +0.007] | +0.016 [+0.013, +0.018] | +0.013 [+0.011, +0.016] | +0.009 | 58 % / 69 % |
| same: PW limit − converged (307) | −0.078 [−0.091, −0.065] | | −0.047 [−0.058, −0.036] | −0.058 | 14 % |
| binary, 5 → 50, bce + edge target: layer − U-Net (bce) | −0.015 [−0.018, −0.013] | | −0.017 [−0.020, −0.015] | −0.015 | 19 % / 23 % |
| same: PW limit − converged (307) | −0.016 [−0.020, −0.013] | | +0.002 [−0.002, +0.006] | −0.008 | 16 % / 44 % |
| same: PW limit − U-Net (bce) (307) | −0.030 [−0.039, −0.023] | | −0.020 [−0.028, −0.012] | −0.019 | 14 % / 27 % |
| binary, boundary_dice: layer − U-Net (same loss) | −0.005 [−0.007, −0.002] | | −0.009 [−0.012, −0.007] | −0.005 | 28 % / 24 % |
| binary, boundary_dice: U-Net, dice − bce | −0.021 [−0.026, −0.016] | | −0.032 [−0.037, −0.026] | +0.028 [+0.027, +0.030] | 40 % / 35 % |

Per tissue, converged edge-target solve against the gap U-Net (IoU / BF₂ / F1 / PQ):
Breast (749) 0.722 / 0.757 / 0.753 / 0.600 vs 0.720 / 0.755 / 0.704 / 0.560; Colon (468)
0.697 / 0.739 / 0.614 / 0.483 vs 0.693 / 0.737 / 0.562 / 0.444; HeadNeck (169) 0.702 /
0.777 / 0.725 / 0.590 vs 0.670 / 0.741 / 0.649 / 0.528; Adrenal (148) 0.724 / 0.785 /
0.778 / 0.654 vs 0.716 / 0.774 / 0.692 / 0.580. The converged solve has the higher IoU on
9 of the 15 tissue types with ≥ 50 patches and the higher F1 on all of them. By crowding:
+0.012 IoU on patches with fewer than 10 nuclei, +0.002 on all other bins; count error
0.50 vs 0.77 (< 10 nuclei), 0.14 vs 0.20 (10–30), equal above 30.

Figures: `results/pannuke/leads/edge_gap_p10/figures/examples_rw_learned_crop.png`
(the edge target makes the cost head a closed contour map, last column; the seams are
in it), `edge_bce/figures/examples_rw_learned_crop.png` (the same at p = 50: the logits
are now pure checkerboard and the 20-step layer shows horizontal streaks where the PCG
has not converged inside closed contours; the exact limit separates the nuclei),
`dice/figures/examples_unet_crop.png` (no dotted contours, but a softer output),
`edge_gap_p10/cmp/losses.png`, `losses.png`.

- **Honest outcome: the edge target is the missing piece, and with it the layer beats
  the U-Net on PanNuke for the first time, by a small pixel margin and a large instance
  one.** With the cost head supervised on the instance-id edges, on top of section 6.1's
  gap target, p 2 → 10 and 8·σ edges, the converged layer is above the U-Net trained on
  the same target on IoU, BF₁, BF₂, BF₃ and band accuracy, each paired interval
  excluding zero (+0.004 to +0.005), on 9 of 15 tissues, and on every tissue for instance
  F1; at the instance level it reaches F1 0.724 and PQ 0.588 against 0.667 / 0.541 (raw
  components, no post-processing), above the min-area-filtered boundary-trained U-Net of
  section 7 (0.714 / 0.582) which was the best instance segmenter so far. The 20-step
  unrolled layer, i.e. the output actually trained, is 0.003 IoU below the U-Net and
  level on BF₂; the +0.008 IoU between the two is what 20 Jacobi-PCG steps leave on
  the table at p = 10 with closed contours, so either K or a converged (implicit) layer
  at evaluation is part of the recipe. Against section 6.1's run without the edge
  target, the gain is +0.005 IoU, +0.016 BF₁ and +0.013 BF₂, paired, and F1 0.724
  against 0.680: the segmentation loss alone did not find the contour costs, the edge
  target did (last column of the crop panels: a closed, 1–2 px contour around every
  nucleus and along every seam, where section 6.1's costs were ridges inside the nuclei).
- **It cuts more seams, but it is still mostly a denoiser, and the gain is where
  objects are few.** The layer now predicts 29 % of the seam pixels as background and
  cuts 19 % of the seams entirely, against 20 % / 14 % in section 6.1 and 19 % / 13 %
  for the gap U-Net; its own logits cut 42 % / 26 %, so the solve still closes half of
  what the network opens. The IoU gain is +0.012 on the 486 patches with fewer than 10
  nuclei and +0.002 elsewhere, and the count error drops most on those patches (0.50 vs
  0.77): the layer removes spurious small components and rounds off the nuclei, the
  mechanism of section 6.1, done better because the contours are now real. The learned
  edge scale fell to 0.41 (from 8, and 4.1 in section 6.1): with a clean contour
  probability map the network wants weak cuts at p = 10, consistent with the solve
  staying a smoother that respects contours rather than a cutter.
- **The limit becomes usable again, at both p.** The edge target is the first thing that
  moves the exact Power Watershed at low p off the floor: 0.637 IoU and F1 0.682 / PQ
  0.562 on the 307 limit patches against 0.508 and 0.523 / 0.435 in section 6.1 (the
  gap U-Net on the same patches: F1 0.645 / PQ 0.520; the converged solve: 0.698 /
  0.564), with the best label-free edge alignment of any non-limit output (0.625). At
  p 5 → 50 with the binary target the limit on the supervised costs scores 0.684 IoU and
  0.744 BF₂, its price against the converged solve shrinks to −0.016 IoU and zero BF₂
  (from −0.046 / −0.034 in section 6), and the crops show it separating touching nuclei
  cleanly; but that model's finite-p output is worse than without the target (−0.006
  IoU paired, raw F1 0.45 because the closed contours leave holes and fragments at
  threshold), and the limit stays 0.030 IoU below the plain U-Net. So the edge target
  buys a deployable limit or a stronger finite-p layer depending on p, and the p 2 → 10
  solve is the better product on this data.
- **The Dice-band loss removes the dotted-contour artefact and nothing else.** Both
  models lose 0.02 IoU and 0.03 BF₂ against BCE while gaining 0.03 band accuracy: the
  band Dice rewards filling the 3-px band on average, which the models satisfy with a
  softer, wider edge (14 % soft pixels, components 31 per patch instead of 91 under the
  boundary-F surrogate, but still 8 too many). The gap between layer and U-Net is the
  same −0.005 IoU as under the boundary-F loss, reached by dragging both down. The
  boundary-F surrogate of section 7 with a minimum-area filter remains the better
  boundary loss, and adding the edge target to the Dice loss (`edge_dice`) helps neither.
- **What this does and does not establish.** One configuration, one seed, one fold
  pair, and a margin of 0.004–0.005 IoU with a bootstrap interval that clears zero but
  not by much; the instance margin (+0.06 F1, +0.05 PQ) is the robust part, and it is
  consistent across tissues. The result stands on three ingredients at once (gap target,
  low p with sharp edges, edge target), none of which helps on its own, and the
  comparison is against a U-Net that has no access to the edge supervision; a U-Net
  with a second contour head trained on the same edge target, and its contours used in a
  classical watershed post-processing, is the fair next baseline; section 10.1 runs it. The
  Pets repeat of the edge target is not possible (no instances); a boundary target from
  the trimap would be the analogue.

### 10.1 The fair baseline: a U-Net with its own contour head, and a watershed on it

Added 18 October 2026 (side session). Code: `--variant unet_edge`, `postprocess_edge`,
`--pp-tune-fold`, `--eval-only` in `experiments/exp_unet_seg.py`, `experiments/run_unet_edge.sh`,
`experiments/compare_unet_edge.py` (tables, paired statistics; numpy only); `inst_minarea.py`
now also writes the per-image counts, `seam_stats.py` and `plot_pannuke.py` know the new
outputs. Raw results, per-image metrics, figures and the full comparison:
`results/pannuke/leads/unet_edge/` (`compare.md`).

**What was run.** The U-Net of section 6.1 (gap target, same recipe, fold 1 → fold 2, 30
epochs, one seed) with three output channels like `rw_learned` but no layer: channel 0 is
the segmentation logit under BCE, channels 1–2 a per-pixel contour head trained with exactly
section 10's edge target (BCE on the edge probability averaged onto each grid edge against
the instance-id changes, positives ×10, seams ×5 on top, weight 1). It is evaluated as the
thresholded logits and after two classical post-processings of the contour map c (mean of
the two directions): (a) the segmentation with the predicted contour (c > 0.5) removed;
(b) a marker-based watershed of c inside the segmentation, seeded by the maxima of the
distance transform of the thresholded segmentation, with the watershed lines set to
background (2 px, like the seams of the gap target), so that touching nuclei are split
along the predicted contours. A second seeding, from the distance transform of (a) so that
the contour does the first split, is reported as (b′). The one hyper-parameter, the marker
spacing, was chosen by PQ on 300 patches of fold 3 (neither fold used elsewhere): 12 px for
(b), 25 px for (b′); on fold 3 the PQ of (b) goes from 0.42 at 2 px to 0.59 at 12 and 0.57
at 25, so the choice matters and is not the layer's advantage. All rows below are against
the gap target on all of fold 2, instance metrics on the raw 4-connected components; the
layer rows are section 10's `edge_gap_p10` run.

| run | output | IoU | BF₁ | BF₂ | BF₃ | band acc. | edge align. | F1@0.5 | PQ | count err. |
|---|---|---|---|---|---|---|---|---|---|---|
| U-Net, gap target (sec. 6.1) | logits | 0.717 | 0.651 | 0.768 | 0.825 | 0.806 | 0.575 | 0.667 | 0.541 | 0.296 |
| U-Net + contour head, edge target | logits | 0.719 | **0.658** | **0.774** | 0.828 | 0.809 | 0.574 | 0.682 | 0.556 | 0.303 |
| | (a) logits − contour | 0.655 | 0.495 | 0.707 | 0.811 | 0.749 | 0.512 | 0.665 | 0.492 | 0.415 |
| | (b) watershed, seg. markers (12 px) | 0.718 | **0.658** | **0.774** | **0.829** | 0.809 | 0.568 | 0.715 | 0.583 | 0.344 |
| | (b′) watershed, contour markers (25 px) | 0.717 | **0.660** | **0.775** | **0.830** | 0.808 | 0.566 | 0.693 | 0.566 | 0.416 |
| layer, edge target (sec. 10) | layer, 20 steps | 0.713 | 0.649 | 0.766 | 0.822 | 0.799 | 0.582 | 0.723 | 0.587 | **0.207** |
| | converged | **0.721** | 0.655 | 0.773 | **0.829** | **0.810** | 0.569 | **0.724** | **0.588** | 0.214 |
| | PW limit (307) | 0.637 | 0.612 | 0.718 | 0.763 | 0.746 | 0.625 | 0.682 | 0.562 | 0.334 |
| ground truth | gap mask | 1 | 1 | 1 | 1 | 1 | 0.553 | 0.998 | 0.990 | 0.002 |

**After the 8-px min-area filter** (sections 7 and 10's convention; 32 px in brackets):

| run | output | IoU | F1@0.5 | PQ | count err. | components / patch (raw → 8 px) |
|---|---|---|---|---|---|---|
| U-Net, gap target (sec. 6.1) | logits | 0.719 | 0.700 (0.715) | 0.567 (0.581) | 0.220 | 24.0 → 21.7 |
| U-Net + contour head | logits | **0.724** | 0.723 (0.738) | 0.589 (0.602) | 0.214 | 25.2 → 22.4 |
| | (b) watershed, seg. markers | 0.722 | **0.757** (0.774) | **0.618** (0.632) | 0.227 | 27.2 → 24.3 |
| | (b′) watershed, contour markers | 0.720 | 0.753 (0.777) | 0.615 (0.636) | 0.241 | 30.3 → 26.0 |
| layer, edge target (sec. 10) | layer, 20 steps | 0.716 | 0.726 (0.733) | 0.589 (0.596) | **0.202** | 22.0 → 21.8 |

**Paired per-patch differences** (2523 patches, bootstrap 95 % intervals; F1 and PQ are
dataset-level, bootstrapped over patches):

| comparison | IoU | BF₁ | BF₂ | band acc. | F1@0.5 | PQ |
|---|---|---|---|---|---|---|
| U-Net + contour head, logits − gap U-Net | +0.003 [+0.001, +0.005] | +0.007 [+0.005, +0.009] | +0.005 [+0.003, +0.007] | +0.004 | +0.015 [+0.012, +0.018] | +0.015 [+0.012, +0.017] |
| converged layer − U-Net + contour head, logits | +0.001 [−0.001, +0.004] | −0.003 [−0.005, −0.000] | −0.000 [−0.003, +0.003] | +0.001 | +0.042 [+0.039, +0.045] | +0.032 [+0.030, +0.034] |
| converged layer − (b) watershed | +0.003 [+0.000, +0.006] | −0.004 [−0.006, −0.001] | −0.001 [−0.003, +0.002] | +0.002 | +0.009 [+0.005, +0.013] | +0.005 [+0.002, +0.008] |
| layer (20 steps) − (b) watershed | −0.005 [−0.007, −0.002] | −0.009 [−0.012, −0.006] | −0.008 [−0.011, −0.005] | −0.010 | +0.008 [+0.004, +0.012] | +0.004 [+0.001, +0.007] |
| after the 8-px filter: layer (20 steps) − U-Net + contour head, logits | | | | | +0.004 [+0.001, +0.006] | +0.001 [−0.001, +0.003] |
| after the 8-px filter: layer (20 steps) − (b) watershed | | | | | −0.031 [−0.034, −0.027] | −0.028 [−0.031, −0.025] |

Per tissue, converged layer against (b) (IoU / F1 / PQ): Breast (749) 0.722 / 0.753 / 0.600
vs 0.722 / 0.757 / 0.605; Colon (468) 0.697 / 0.614 / 0.483 vs 0.691 / 0.630 / 0.497;
HeadNeck (169) 0.702 / 0.725 / 0.590 vs 0.682 / 0.688 / 0.565; Adrenal (148) 0.724 / 0.778 /
0.654 vs 0.719 / 0.712 / 0.605; the layer has the higher IoU on 9 and the higher F1 on 11 of
the 15 tissues with ≥ 50 patches. By crowding (F1 / count error): fewer than 10 nuclei,
layer 0.670 / 0.50 vs watershed 0.596 / 0.81; 10–30: 0.752 / 0.14 vs 0.719 / 0.27; 30–60:
0.718 / 0.14 vs 0.733 / 0.15; more than 60: 0.676 / 0.22 vs 0.700 / 0.13. Seam statistics
(seam pixels background / seams cut entirely): contour-head U-Net logits 22 % / 15 %,
(a) 68 % / 55 %, (b) 31 % / 17 %, (b′) 37 % / 17 %; the converged layer 23 % / 15 %, the
20-step layer 29 % / 19 %. Figures: `results/pannuke/leads/unet_edge/figures/examples_unet_edge_crop.png`
(the contour head is the same closed 2–3 px contour map as the layer's cost head; (a)
shaves every nucleus by that width; (b) splits the large blobs along the contours but
leaves merged pairs whose distance transform has a single maximum, and over-splits
elongated ones; (b′) cuts more and also along spurious contour fragments).

- **Honest outcome: the pixel-level advantage of section 10 does not survive, and the
  instance advantage survives only without post-processing.** Half of what the edge target
  gave the layer it gives the backbone: with the same contour head, the plain U-Net's
  logits gain +0.003 IoU, +0.007 BF₁ and +0.005 BF₂ over the gap U-Net, paired, which is the
  same margin section 10 attributed to the converged layer. Layer against this U-Net the
  pixel differences are zero (+0.001 IoU with an interval through zero, −0.003 BF₁, 0.000
  BF₂). At the instance level the raw converged layer is still ahead of the raw contour-head
  U-Net by 0.042 F1 and of the tuned watershed by 0.009 F1 / 0.005 PQ (intervals clear of
  zero, but small, and the 20-step layer that was actually trained is 0.005 IoU and 0.008
  BF₂ *below* the watershed output while 0.008 F1 above it); with the 8-px min-area filter
  that sections 7 and 10 apply to every method, the order flips: the watershed U-Net reaches
  F1 0.757 / PQ 0.618 against the layer's 0.726 / 0.589, −0.031 F1 paired, and the
  filtered contour-head logits alone are level with the layer (+0.004 F1, +0.001 PQ). So the
  two things the layer was doing in section 10, removing small spurious components and
  benefiting from a contour map, are each done at least as well by a min-area filter and an
  extra head; what is left to the layer is the best count error of any output (0.21 raw, 0.20
  filtered, against the watershed's 0.34 / 0.23, which over-segments: 27 components per
  patch for 23.7 nuclei), a clear advantage on sparse patches (fewer than 10 nuclei, F1 0.670
  vs 0.596, count error 0.50 vs 0.81) and on HeadNeck and Adrenal, and the fact that it is a
  single differentiable module with no post-processing hyper-parameter, where the
  watershed's marker spacing had to be tuned on a third fold and moves PQ by 0.17 across its
  range. On crowded patches (more than 30 nuclei) the watershed is the better instance
  segmenter, which is consistent with the seam statistics: the watershed cuts 31 % of the
  seam pixels where the converged layer cuts 23 %, no more than the U-Net's own logits.
- **Removing the predicted contour is not a usable post-processing.** The contour head's
  2–3 px band costs 0.064 IoU and 0.163 BF₁ when subtracted, although it cuts 55 % of the
  seams; a 1-px contour target, or a thinning step, would be needed for (a) to compete.
- **What this establishes.** With a fair U-Net the finite-p layer with the edge target is a
  competitive instance segmenter on PanNuke, not a better one: level at the pixel level,
  slightly ahead on raw components, behind once both sides are filtered, better on sparse
  patches and on counts, worse on crowded ones. The remaining arguments for the layer are
  therefore architectural (one module, trained end to end, a limit that section 10 showed
  is usable again) rather than a metric margin on this dataset. The same caveats as
  section 10 apply, one seed and one fold pair, plus the baseline's own: the simplest marker
  recipe (distance-transform maxima) with one tuned spacing; a HoVer-Net-style distance or
  gradient head would be a stronger classical baseline still.

## 11. The instances are the labels: a multi-marker layer

Added 18 October 2026 (side session), after Hugues' observation of 17 October: the Power
Watershed does not care how many labels there are (one maximum spanning forest whatever the
number of markers), the Random Walker's cost is affine in the number of labels (one matrix,
one right-hand side per label), while a U-Net needs a fixed one-hot output layout. So the
natural use of the layer on nuclei is not binary nucleus / background but one label per
nucleus, with the markers supplied per image. Code: `MultiRWLayer`, `ImplicitRWMulti`,
`label_systems`, `multi_cross_entropy`, `eroded_markers`, `pw_limit_multi_numpy` /
`power_watershed_multi` in `experiments/pw_layer.py` (self-tests in its `__main__`);
`experiments/exp_instance_pannuke.py` (model, training, evaluation), `run_instances.sh`,
`plot_instances.py`; `instance_metrics` of `seg_metrics.py` accepts a label map. Raw results,
per-image metrics, figures and the full tables: `results/pannuke_instances/`
(`figures/summary.md`, `run_instances.log`; the trained model stays on jacobian).

**The layer.** For K markers plus the background, label k gets an attachment a_k ≥ 0 per
pixel and the K + 1 systems share the matrix:

    (L(w) + diag(Σ_j a_j)) x_k = a_k,   k = 0 … K,     so that   Σ_k x_k = 1   (L 1 = 0).

x_k,i is the probability that a random forest at inverse temperature p connects pixel i to
label k. The systems of every image of a batch are stacked along the batch axis (M = Σ_b (K_b + 1)
systems, the weights gathered per image), so the PCG of section 1 runs unchanged on (M,1,H,W)
tensors, K is free per image, and the cost is affine in K with no padding. The solve is
implicit; the adjoint is one solve per label with the same matrix, dl/dw_e = −Σ_k (x_k,u −
x_k,v)(λ_k,u − λ_k,v) and dl/da_k,i = λ_k,i − Σ_j λ_j,i x_j,i (own right-hand side, shared
diagonal), which reduces to the binary formulas of section 0 for K = 1. Attachments: a_0,i =
exp(−p c0_i) everywhere, c0 = −log(1 − s) the U-Net's background cost; a_k,i = exp(−p c1_i)
on the marker pixels of label k with c1 = −log s and zero elsewhere, so the markers are soft
(their strength is the network's foreground confidence) and differentiable; the edge costs
are the learned cost head of sections 6.1 and 10 (scale · σ(h), learnable scale, edge target).

**The limit with K labels.** `power_watershed` of section 1 interpolates scalar seed values on
the plateaus it has to solve, which is the exact limit for two labels only. `power_watershed_multi`
keeps a K-vector per merged node: seeds are one-hot, a plateau that touches two distinct known
vectors is solved with K right-hand sides at once (unit-weight RW), and the argmax is taken at
the end, so it is the limit of the K systems above and not an interpolation of label indices.
Self-tests (7 × 9 grid, random costs, K = 3; 12 × 14 grid with costs quantised to 1/4 so that
large ambiguous plateaus occur): the label probabilities sum to one to 1e-14, the two-label
case equals the binary layer and the binary limit, the adjoint matches finite differences to
seven digits on every input, the argmax of the finite-p solve equals the limit's at p = 60,
and on the quantised grid the K-vector limit equals the K + 1 one-hot runs of the scalar
`power_watershed` exactly.

**Training** (fold 1 → fold 2 as before, 30 epochs, batch 16, one seed). The U-Net has four
output channels: the foreground logit (its sigmoid s gives c0 and c1), the two-channel cost
head, and a marker logit. Training markers are the ground-truth instances eroded by 2 or 3 px
(radius drawn per step; the core of a nucleus the erosion would empty is kept), the marker
head is trained with BCE against them, and the layer loss is the per-pixel cross-entropy of the
K + 1 label probabilities against the instance map (the seam pixels and their 1-px flank
weighted × 6), plus 0.5 BCE on the foreground logit and section 10's edge target (× 1) on the
cost head. p is annealed 5 → 20 (section 6.1: costs learned at low p do not transfer to p = ∞,
so both the finite-p output and the exact limit are reported). The training solve runs to a
relative residual of 1e-4 or 100 PCG iterations, evaluation to 1e-5; 290 s per epoch, 2.4 h in
all, 1 h for the evaluation (four solves per batch plus the CPU metrics).

**Test markers** are the 4-connected components of the thresholded marker map (0.5). Each
ground-truth nucleus is counted as having exactly one, none or several predicted markers (a
marker belongs to the nucleus holding the majority of its pixels), and markers in background
are counted. A second variant ("fallback") adds a marker at the distance-transform maximum of
every foreground component (s > 0.5, ≥ 16 px) that has none. The oracle row runs the same
trained costs from the ground-truth markers (eroded by 2 px): it bounds what better markers
could give.

**Baselines and controls.** The plain U-Net + connected components of section 6 (binary
target) and the contour-head U-Net with the tuned marker watershed of section 10.1 (the
strongest pipeline so far), both re-used from their per-image files; within this model, its
own foreground logits + components, the classical marker watershed (skimage) of the learned
contour map inside s > 0.5 from the same predicted markers, the converged solve and the exact
limit with image-gradient edge costs in place of the learned ones (the RMS colour difference
across each edge, scaled per patch so that its 99th percentile equals the unary clamp 8: the
marker-controlled watershed with the U-Net's background as a soft seed), and the exact
K-label limit of the learned costs on the 307 patches of section 6. Instance metrics are
computed on the label maps themselves (argmax over the K + 1 labels; one predicted instance per
label that wins at least one pixel), pixel metrics on the foreground (label > 0) against the
binary mask, so they are comparable with section 6's rows.

**Results on all of fold 2** (2523 patches; the limits on 307):

| output | IoU | BF₁ | BF₂ | band acc. | edge align. | F1@0.5 | PQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6), s > 0.5, components | **0.719** | 0.652 | 0.769 | 0.807 | 0.577 | 0.656 | 0.531 | 0.494 | **0.275** | 23.0 |
| U-Net + contour head (sec. 10.1), logits | **0.719** | **0.658** | **0.774** | **0.809** | 0.574 | 0.682 | 0.556 | 0.571 | 0.303 | 25.2 |
| U-Net + contour head, tuned marker watershed (b) | 0.718 | **0.658** | **0.774** | **0.809** | 0.568 | **0.715** | **0.583** | **0.657** | 0.344 | 27.2 |
| this model, s > 0.5, components | 0.575 | 0.408 | 0.580 | 0.691 | 0.402 | 0.024 | 0.017 | 0.168 | 52.7 | 723 |
| this model, layer, converged, predicted markers | 0.706 | 0.643 | 0.759 | 0.795 | **0.585** | 0.681 | 0.554 | 0.652 | 0.460 | 28.6 |
| this model, layer + fallback markers | 0.702 | 0.641 | 0.757 | 0.798 | 0.586 | 0.657 | 0.534 | 0.652 | 0.585 | 31.1 |
| this model, layer, image-gradient costs | 0.487 | 0.203 | 0.351 | 0.592 | 0.248 | 0.355 | 0.218 | 0.470 | 0.529 | 29.9 |
| this model, marker watershed on the contour map, same markers | 0.615 | 0.455 | 0.633 | 0.684 | 0.430 | 0.597 | 0.414 | 0.541 | 0.546 | 30.2 |
| this model, PW limit, learned costs (307) | 0.690 | 0.613 | 0.736 | 0.781 | 0.579 | 0.661 | 0.526 | 0.612 | 0.426 | 29.8 |
| this model, PW limit, image-gradient costs (307) | 0.479 | 0.202 | 0.341 | 0.589 | 0.241 | 0.335 | 0.204 | 0.451 | 0.507 | 31.5 |
| this model, layer, ground-truth markers (oracle) | 0.859 | 0.796 | 0.922 | 0.858 | 0.591 | 0.959 | 0.805 | 0.858 | 0.020 | 23.3 |
| ground truth instances | 1 | 1 | 1 | 1 | 0.559 | 1 | 1 | 1 | 0 | 23.7 |

**Marker quality.** Fold 2 has 59 872 nuclei (23.7 per patch); the marker head gives 30.5
markers per patch. 73.2 % of the nuclei get exactly one marker, 17.4 % none, 9.5 % several;
5.9 markers per patch lie in background. With the fallback: 76.3 / 13.8 / 9.9 % and 8.2
background markers per patch. By crowding (one / none / several; background markers per
patch): fewer than 10 nuclei 69 / 19 / 12 %, 2.6; 10–30: 75 / 15 / 11 %, 6.1; 30–60: 74 / 16 /
9 %, 7.9; more than 60: 69 / 26 / 6 %, 8.1.

**Paired per-patch differences** (bootstrap 95 % intervals; F1, PQ and AJI dataset-level,
bootstrapped over patches):

| comparison | IoU | BF₂ | edge align. | F1@0.5 | PQ | AJI |
|---|---|---|---|---|---|---|
| layer − U-Net (sec. 6) | −0.013 [−0.016, −0.010] | −0.011 [−0.014, −0.007] | +0.009 [+0.008, +0.010] | +0.024 [+0.019, +0.031] | +0.023 [+0.018, +0.029] | +0.158 [+0.143, +0.172] |
| layer − contour-head U-Net, watershed (b) | −0.012 [−0.015, −0.009] | −0.016 [−0.019, −0.012] | +0.018 [+0.017, +0.020] | −0.034 [−0.039, −0.030] | −0.029 [−0.033, −0.025] | −0.005 [−0.008, −0.003] |
| layer − marker watershed, same markers | +0.091 | +0.126 | +0.155 | +0.084 [+0.081, +0.087] | +0.140 | +0.111 |
| layer − layer with image-gradient costs | +0.218 | +0.407 | +0.337 | +0.325 [+0.317, +0.335] | +0.336 | +0.182 |
| layer + fallback − layer | −0.004 [−0.007, −0.001] | −0.002 | −0.001 | −0.024 [−0.025, −0.023] | −0.020 | −0.000 |
| layer, ground-truth markers − layer | +0.153 [+0.148, +0.158] | +0.163 | +0.006 | +0.278 [+0.272, +0.285] | +0.251 | +0.206 |
| 307 patches: PW limit (learned) − layer | −0.008 [−0.011, −0.005] | −0.013 [−0.016, −0.009] | −0.001 [−0.004, +0.002] | +0.007 [+0.003, +0.010] | −0.003 [−0.006, −0.000] | −0.017 [−0.020, −0.015] |
| 307 patches: PW limit (learned) − U-Net (sec. 6) | −0.024 [−0.031, −0.016] | −0.027 | +0.011 | +0.027 [+0.010, +0.043] | +0.017 [+0.003, +0.030] | +0.187 |

By crowding (F1 / PQ / count error), U-Net (sec. 6) vs watershed (b) vs layer: fewer than 10
nuclei (486 patches) 0.608 / 0.485 / 0.68 vs 0.596 / 0.479 / 0.81 vs 0.559 / 0.449 / 0.94; 10–30
(1383) 0.691 / 0.563 / 0.18 vs 0.719 / 0.591 / 0.27 vs 0.673 / 0.551 / 0.40; 30–60 (525) 0.650 /
0.524 / 0.15 vs 0.733 / 0.596 / 0.15 vs 0.696 / 0.565 / 0.24; more than 60 (129) 0.588 / 0.469 /
0.24 vs 0.700 / 0.562 / 0.13 vs **0.703 / 0.569** / 0.16. Per tissue (IoU / F1 / PQ, layer vs
watershed (b)): Breast (749) 0.710 / 0.716 / 0.569 vs 0.722 / 0.757 / 0.605; Colon (468) 0.681 /
0.570 / 0.451 vs 0.691 / 0.630 / 0.497; HeadNeck (169) 0.688 / 0.664 / 0.547 vs 0.682 / 0.688 /
0.565; Adrenal (148) **0.714 / 0.726 / 0.615** vs 0.719 / 0.712 / 0.605. Inference: U-Net 0.8 ms
per image; the converged multi-marker solve 224 ms per image on the GPU at K = 30.5 markers
(79 353 systems in 158 batches of 16, 330 PCG iterations per batch to 1e-5: the time is affine
in the number of systems, and a batch of 16 images carries 500 of them); the exact K-label
limit 0.7 s per patch on one CPU core (6043 ambiguous plateaus solved over the 307 patches),
0.8 s with image-gradient costs. Figures: `results/pannuke_instances/figures/training.png`,
`examples_crop.png` (64-px crops around the densest cluster of touching nuclei, the same eight
Colon patches as section 6: image, instances, marker map with the predicted markers outlined,
the model's own thresholded logits, the layer, the layer with fallback markers, the two limits,
the marker watershed, the oracle), `examples_full.png`.

- **Honest outcome: instances as labels give the layer a margin over the U-Net + components
  pipeline, not over the best classical pipeline.** The layer from its own markers scores
  F1 0.681 / PQ 0.554 / AJI 0.652: +0.024 F1, +0.023 PQ and +0.158 AJI over the plain U-Net of
  section 6, paired and clear of zero, with the highest edge alignment of any full-set output
  (0.585), and it is the first output in this report whose instances come from a single
  differentiable module with no post-processing at all (no threshold on the output, no
  component filter, no marker spacing). Against the contour-head U-Net with the tuned
  watershed of section 10.1 it is behind by 0.034 F1 and 0.029 PQ and level on AJI (−0.005):
  its segments are as tight (SQ 0.814 against 0.816) but it detects fewer nuclei correctly
  (DQ 0.681 against 0.715). It is also 0.013 IoU below the U-Net on the foreground, and its
  count error is the worst of the three (0.46: 28.6 predicted instances for 23.7 nuclei). On
  crowded patches (more than 60 nuclei) it is the best method, on sparse ones the worst, the
  reverse of the binary layer's pattern in section 10.1.
- **The costs are not the problem; the markers are.** With the ground-truth markers the same
  trained costs give F1 0.959 / PQ 0.805 / AJI 0.858 and 0.859 IoU, i.e. the layer assigns
  almost every pixel to the right nucleus once it knows where the nuclei are, and separates
  touching ones along the learned contours (DQ 0.959, count error 0.02; last column of
  `examples_crop.png`). The oracle leaks the ground truth (the markers are its instances
  eroded by 2 px), so 0.96 is an upper bound and not a target, but the gap to 0.681 is entirely
  the marker head: 17 % of the nuclei get no marker and vanish into the background (this is
  also where the 0.013 IoU goes: patch #4 of the crops loses half its nuclei), 10 % get several
  and are split, and 5.9 spurious markers per patch in background become small false instances
  (the count error; the layer gives them few pixels because the background attachment is
  strong there, but it does not remove them). The marker head is a one-threshold blob
  detector trained with plain BCE on eroded masks; a HoVer-Net-style distance or
  centre-vector head, or a learned threshold, is the obvious next step, and the fallback
  markers from the foreground mask are not it (−0.024 F1: the foreground head degenerated
  into speckle, see below, so its components are not nuclei).
- **The learned costs are what the layer contributes, and a classical watershed cannot use
  them as well.** The same predicted markers through the skimage marker watershed of the
  learned contour map inside s > 0.5 give F1 0.597 (−0.084 paired), partly because that mask
  is the degenerate foreground head (723 components per patch, F1 0.024, as in section 6's
  division of labour: with the background attachment taking c0 = −log(1 − s) the network only
  needs s as a soft prior and the 0.5 auxiliary BCE did not stop it). The marker-controlled
  watershed with image-gradient costs, exact (0.335 F1) or at finite p (0.355), fails on H&E
  as `rw_img` did in section 6: the colour gradient is not the nucleus boundary. So the
  classical control is far below, and the margin over it is the learned cost head plus the
  soft background seed, not the solver.
- **The limit is usable again, at p = 20.** The exact K-label Power Watershed of the learned
  costs is within 0.008 IoU and 0.013 BF₂ of the converged finite-p solve on the 307 patches,
  with +0.007 F1 and −0.003 PQ, where section 6.1's binary model trained at p ≤ 20 lost 0.2
  IoU at the limit. Two reasons: the cross-entropy over markers trains the costs to put a cut
  between every pair of neighbouring markers, which is exactly what a maximum spanning forest
  needs, and the background is a soft seed (a_0 = (1 − s)^p) rather than a competing unary
  that has to saturate. So deploy-at-the-limit costs 0.7 s per patch on one CPU core against
  224 ms per image on the GPU for the converged solve, and gives the same instances. One
  training caveat: the training solve hit its 100-iteration cap from epoch 9 (p ≈ 8) on, so
  two thirds of the training ran on a forward solve above the 1e-4 residual and an implicit
  gradient of an approximately solved system; the validation curves are flat from epoch 10,
  which is consistent with a converged model but was not checked with a higher cap. The edge
  scale went from 8 to 2.0 again (section 6.1).
- **What this says about the plan.** The multi-marker layer is the right object: one solve
  for any number of nuclei, exact limit, no post-processing hyper-parameter, and a margin of
  +0.02 F1 / PQ and +0.16 AJI over the pipeline a practitioner would build from the same
  U-Net. It does not beat a U-Net that was given a contour head and a tuned watershed, and
  the oracle says the reason is marker quality, which is a detection problem the layer does
  not touch. The same one-seed, one-fold-pair caveats as sections 10 and 10.1 apply, plus
  the marker head's untuned threshold and the capped training solve.

### 11.1 Better markers: a tuned threshold, a distance head, and a higher solver cap

Added 18–19 October 2026 (side session). Section 11 ended with the markers as the bottleneck:
the same trained costs give F1 0.959 from the ground-truth markers and 0.681 from the marker
head's. This section tries the two things it named, as options of
`experiments/exp_instance_pannuke.py` (the defaults reproduce the section 11 run): `--mk-head
dist` (a HoVer-Net-style distance head), `--tune-fold F` (the marker threshold, minimum marker
area and, for the distance head, the prominence of the maxima chosen by PQ on a held-out
fold, never on fold 2), `--load` (re-evaluate a saved model) and the existing `--maxit` of the
training solve. `run_instances_11_1.sh` launches the runs, `plot_instances.py --ref` adds the
section 11 run to every table, `compare_instances.py` (numpy only) makes the cross-run
tables. Results: `results/pannuke_instances/{bce_tuned, dist, dist_ext, maxit300,
maxit300_tuned}/` (each with `figures/summary.md` holding all the tables of section 11 plus
the tuning table, `run.log`, the per-image npz; the examples npz is kept for `dist` only), `results/pannuke_instances/compare_11_1.md`.

**Choosing the post-processing on fold 3.** `--tune-fold 3` runs the trained model on 300
evenly spaced patches of fold 3 (neither the training nor the test fold, as the marker spacing
of section 10.1), builds the markers for every setting of a grid, runs the converged layer from
them and keeps the setting with the best PQ of the layer's output; the whole table goes to the
json and to the top of `summary.md`. For the BCE head of section 11 the grid is thr ∈ {0.2 …
0.7} × min area ∈ {1, 4, 9, 16} px (24 settings; 50 min while sharing the GPU with a training
run); for the distance head the same × h ∈ {0.05, 0.1, 0.2} (72 settings, 41 min on a free GPU). The section 11 model was re-tuned this way
without retraining (`bce_tuned`: its saved `.pt` through `--eval-only --load`), to separate
the effect of the threshold from the effect of the head.

**The distance head** (`dist`). Channel 3 of the U-Net predicts, through a sigmoid, the
normalised distance transform of every instance: the Chebyshev distance to the instance
boundary (the `label_core_distance` already used for the training markers, capped at 12 px)
divided by the instance's own maximum, so every nucleus is 1 at its centre and 0 at its border
whatever its size, background 0; MSE loss with weight 2 in place of the BCE on eroded masks.
Everything else is section 11's recipe: the layer's cross-entropy from the ground-truth
markers eroded by 2–3 px, p 5 → 20, the edge target, 30 epochs, the 100-iteration training
solve. Test markers are the regional maxima of the predicted map with prominence at least h
(`skimage.morphology.h_maxima`, one seed per plateau, so saturation at 1 is harmless), grown
by a watershed of the map down to the threshold thr, basins below the minimum area dropped:
two touching nuclei whose maxima are separated by a valley deeper than h get two markers even
when the valley is above thr. Fold 3 chose thr 0.2, min area 16 px, h 0.2, both thr and h at
the edge of the grid, so the saved model was re-tuned on an extended grid (`dist_ext`: thr ∈
{0.1, 0.15, 0.2, 0.3}, h ∈ {0.2, 0.3, 0.4}, min area ∈ {9, 16}): the fold-3 PQ is a plateau
(0.646 for the first choice and for thr 0.2 / min area 9 / h 0.3, 0.640–0.645 for the eight
best settings), and the two choices give the same fold 2 result (F1 0.791 / PQ 0.641 against
0.788 / 0.641). The first choice is reported below.

**The solver cap** (`maxit300`). Section 11's training solve hit its 100-iteration cap from
epoch 9 on. The same run with `--maxit 300` (BCE head, untuned thr 0.5 as in section 11, so
the comparison is clean) never hits the cap: 112 / 215 / 227 iterations per batch over the
three ten-epoch thirds, 778 s per epoch instead of 280 (6.5 h of training). Its validation
curve (layer F1 / PQ on the first 200 test patches at epochs 4, 9, 14, 19, 24, 29, untuned
markers) is 0.696 / 0.534, 0.703 / 0.546, 0.716 / 0.563, 0.710 / 0.559, 0.730 / 0.576, 0.705 /
0.551, against section 11's 0.684 / 0.522, 0.727 / 0.571, 0.715 / 0.561, 0.738 / 0.581, 0.722 /
0.570, 0.720 / 0.564: the same curve within its epoch-to-epoch wobble, and the final losses
agree to the third digit (cross-entropy 0.0876 against 0.0909, edge scale 2.09 against 1.99).
On all of fold 2 its oracle equals section 11's (F1 0.960 / PQ 0.806 against 0.959 / 0.805,
paired +0.001) — the costs are the same — while its own markers are slightly worse (33.0 per
patch, 72 / 17 / 10 %, 7.0 in background): F1 0.658 / PQ 0.536, −0.023 F1 [−0.026, −0.019]
paired against section 11. Re-tuned on fold 3 (`maxit300_tuned`, thr 0.4, min area
16 px) it reaches F1 0.770 / PQ 0.631, +0.001 F1 [−0.001, +0.002] / +0.001 PQ [−0.000, +0.002] paired against `bce_tuned`.
So the capped solve of section 11 cost nothing: an approximate forward solve with an implicit
gradient of the approximately solved system trains the same costs as the converged one at
2.8 times the price, and the combined distance-head + 300-iteration run was not made.

**Results on all of fold 2** (2523 patches; limits on the 307 of section 6; the three rows of
section 11 repeated for reference):

| output | IoU | BF₂ | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6), s > 0.5, components | **0.719** | 0.769 | 0.577 | 0.656 | 0.531 | – | – | 0.494 | 0.275 | 23.0 |
| U-Net + contour head, tuned marker watershed (sec. 10.1 b) | 0.718 | **0.774** | 0.568 | 0.715 | 0.583 | 0.816 | 0.715 | **0.657** | 0.344 | 27.2 |
| sec. 11: layer, BCE marker head, thr 0.5, min area 1 | 0.706 | 0.759 | 0.585 | 0.681 | 0.554 | 0.814 | 0.681 | 0.652 | 0.460 | 28.6 |
| `bce_tuned`: the same model, thr 0.4, min area 16 (fold 3) | 0.708 | 0.761 | **0.587** | 0.769 | 0.630 | **0.819** | 0.769 | 0.645 | **0.208** | 21.7 |
| `dist`: distance head, h 0.2, thr 0.2, min area 16 (fold 3) | 0.707 | 0.762 | 0.580 | **0.791** | **0.641** | 0.811 | **0.791** | 0.653 | 0.239 | 24.3 |
| `dist`, + fallback markers | 0.704 | 0.760 | 0.582 | 0.776 | 0.629 | – | – | 0.652 | 0.311 | 25.7 |
| `dist`, PW limit, learned costs (307) | 0.683 | 0.728 | 0.574 | 0.758 | 0.603 | – | – | 0.611 | 0.255 | 25.0 |
| `dist`, layer, ground-truth markers (oracle) | 0.859 | 0.922 | 0.591 | 0.959 | 0.805 | – | – | 0.857 | 0.020 | 23.3 |
| `maxit300`: BCE head, 300-iteration training solve, thr 0.5, min area 1 | 0.704 | 0.757 | 0.581 | 0.658 | 0.536 | – | – | 0.652 | 0.542 | 30.2 |
| `maxit300_tuned`: the same, thr 0.4, min area 16 (fold 3) | 0.707 | 0.760 | 0.584 | 0.770 | 0.631 | 0.820 | 0.770 | 0.647 | 0.200 | 21.6 |

**Marker quality** (nuclei with exactly one / no / several predicted markers; markers in
background per patch; markers per patch for 23.7 nuclei): section 11 73.2 / 17.4 / 9.5 %, 5.9,
30.5; `bce_tuned` 77.7 / 21.1 / 1.2 %, 2.7, 21.7; `dist` 83.9 / 14.5 / 1.6 %, 3.6, 24.3 (with the
fallback 85.4 / 12.6 / 2.0 %, 5.0, 26.2); `maxit300` 72.3 / 17.4 / 10.3 %, 7.0, 33.0. By crowding
for `dist` (one / none / several, background per patch): fewer than 10 nuclei 83 / 14 / 2 %, 1.8;
10–30: 87 / 11 / 2 %, 3.5; 30–60: 84 / 14 / 2 %, 4.7; more than 60: 77 / 22 / 1 %, 6.6 (section
11: 69 / 19 / 12 %, 2.6; 75 / 15 / 11 %, 6.1; 74 / 16 / 9 %, 7.9; 69 / 26 / 6 %, 8.1).

**Paired per-patch differences** (bootstrap 95 % intervals; F1, PQ and AJI dataset-level,
bootstrapped over patches):

| comparison | IoU | BF₂ | edge align. | F1@0.5 | PQ | AJI |
|---|---|---|---|---|---|---|
| `bce_tuned` − sec. 11 layer | +0.002 [+0.000, +0.003] | +0.002 [+0.000, +0.004] | +0.002 [+0.001, +0.003] | +0.088 [+0.082, +0.094] | +0.075 [+0.071, +0.080] | −0.006 [−0.008, −0.005] |
| `dist` − sec. 11 layer | +0.001 [−0.003, +0.004] | +0.003 [−0.000, +0.007] | −0.006 [−0.007, −0.005] | +0.110 [+0.105, +0.115] | +0.087 [+0.083, +0.091] | +0.001 [−0.002, +0.003] |
| `dist` − `bce_tuned` | −0.001 [−0.004, +0.002] | +0.001 [−0.002, +0.005] | −0.008 [−0.009, −0.006] | +0.022 [+0.018, +0.025] | +0.012 [+0.009, +0.014] | +0.007 [+0.005, +0.009] |
| `bce_tuned` − contour-head U-Net, watershed (b) | −0.010 [−0.014, −0.007] | −0.013 [−0.017, −0.010] | +0.020 [+0.019, +0.022] | +0.054 [+0.050, +0.058] | +0.046 [+0.043, +0.050] | −0.012 [−0.015, −0.009] |
| `dist` − contour-head U-Net, watershed (b) | −0.011 [−0.014, −0.008] | −0.012 [−0.015, −0.009] | +0.012 [+0.010, +0.014] | +0.076 [+0.072, +0.079] | +0.058 [+0.056, +0.061] | −0.005 [−0.007, −0.002] |
| `dist` − U-Net (sec. 6) | −0.012 [−0.016, −0.009] | −0.007 [−0.011, −0.004] | +0.003 [+0.002, +0.005] | +0.134 [+0.129, +0.139] | +0.111 [+0.107, +0.114] | +0.158 [+0.143, +0.172] |
| `dist`, ground-truth markers − `dist` | +0.152 [+0.147, +0.158] | +0.160 [+0.155, +0.166] | +0.012 [+0.010, +0.014] | +0.168 [+0.164, +0.173] | +0.163 [+0.160, +0.167] | +0.205 [+0.201, +0.209] |
| `dist` oracle − sec. 11 oracle | −0.000 [−0.001, +0.001] | +0.000 [−0.001, +0.001] | +0.000 [−0.000, +0.001] | −0.000 [−0.001, +0.002] | −0.000 [−0.001, +0.001] | −0.000 [−0.001, +0.000] |
| `maxit300` − sec. 11 layer | −0.002 [−0.004, +0.001] | −0.002 [−0.004, +0.001] | −0.004 [−0.005, −0.003] | −0.023 [−0.026, −0.019] | −0.018 [−0.021, −0.015] | −0.000 [−0.002, +0.001] |
| 307 patches: `dist` PW limit − `dist` layer | −0.014 [−0.016, −0.012] | −0.020 [−0.023, −0.017] | −0.000 [−0.002, +0.001] | −0.008 [−0.010, −0.005] | −0.016 [−0.018, −0.014] | −0.018 [−0.020, −0.016] |

By crowding (F1 / PQ / count error), watershed (b) vs `bce_tuned` vs `dist`: fewer than 10
nuclei (486 patches) 0.596 / 0.479 / 0.81 vs 0.704 / 0.571 / 0.46 vs 0.689 / 0.553 / 0.64; 10–30
(1383) 0.719 / 0.591 / 0.27 vs 0.787 / 0.648 / 0.15 vs 0.802 / 0.655 / 0.16; 30–60 (525) 0.733 /
0.596 / 0.15 vs 0.778 / 0.634 / 0.13 vs 0.801 / 0.648 / 0.10; more than 60 (129) 0.700 / 0.562 /
0.13 vs 0.718 / 0.586 / 0.26 vs 0.763 / 0.615 / 0.15. Per tissue (IoU / F1 / PQ, `dist` vs
watershed (b)): Breast (749) 0.708 / **0.817 / 0.647** vs 0.722 / 0.757 / 0.605; Colon (468)
0.683 / **0.709 / 0.558** vs 0.691 / 0.630 / 0.497; HeadNeck (169) **0.701 / 0.784 / 0.647** vs
0.682 / 0.688 / 0.565; Adrenal (148) 0.709 / **0.823 / 0.696** vs 0.719 / 0.712 / 0.605.
Inference: the converged solve of `dist` takes 94 ms per image on the GPU at K = 24.3 (177 PCG
iterations per batch of 16, against 224 ms and 330 iterations at K = 30.5 in section 11: fewer
and better-placed markers also make the systems easier); the exact K-label limit stays at
0.7 s per patch on one CPU core. Figures: `results/pannuke_instances/dist/figures/training.png`,
`examples_crop.png` (the same eight Colon crops as section 11; the third column is now the
predicted distance map with the grown markers outlined: one clean maximum per nucleus, the
layer column close to the oracle's), `examples_full.png`; the same for every run.

- **Honest outcome: the gap to the best classical pipeline is closed, by the markers alone.**
  The section 11 model without retraining, with its marker threshold and minimum marker area
  chosen on fold 3 (0.4 and 16 px instead of 0.5 and 1), goes from F1 0.681 / PQ 0.554 to 0.769 /
  0.630, +0.088 F1 / +0.075 PQ paired; the distance head adds +0.022 F1 / +0.012 PQ / +0.007 AJI
  on top (0.791 / 0.641 / 0.653), every interval clear of zero. Against the contour-head U-Net
  with the tuned watershed of section 10.1, the strongest pipeline of this report, the layer
  from the distance head's markers is +0.076 F1 and +0.058 PQ, ahead on every tissue (Breast
  +0.060 F1, Colon +0.079, HeadNeck +0.096, Adrenal +0.111) and in every crowding bin, with the
  same segmentation quality (SQ 0.811 against 0.816) and far more correct detections (DQ 0.791
  against 0.715); its count error (0.24) is the best of all full-set outputs after `bce_tuned`'s
  0.21. AJI is level (−0.005) and the foreground IoU stays 0.011 below the U-Net's: what the
  layer still loses is the nuclei with no marker (14.5 %), which it gives to the background.
- **Which markers were wrong.** Section 11's 30.5 markers per patch for 23.7 nuclei were 5.9
  spurious ones in background and 9.5 % of the nuclei split by several; the tuned threshold
  removes most of both (2.7 in background, 1.2 % split) at the price of more nuclei with none
  (21 %). The distance head's normalised target makes the marker of a small nucleus as strong as
  that of a large one and separates touching nuclei by their two maxima rather than by a gap in
  a thresholded mask, so it gets both: 83.9 % of the nuclei with exactly one marker, 14.5 %
  with none, 1.6 % with several, 3.6 in background. On fold 3 the settings order the same way
  (PQ 0.646 for the distance head, 0.635 for the tuned BCE head, 0.557 for section 11's
  untuned 0.5 / 1), so the tuning fold predicted the test fold; the untuned distance head
  (0.5 / 1 / h 0.1) would have scored 0.570 on fold 3, worse than the tuned BCE head, so the
  head without its threshold is not the story either.
- **Where the remaining 0.17 F1 to the oracle is.** With the ground-truth markers the same
  costs give 0.959; the distance head leaves 14.5 % of the nuclei without a marker (22 % on the
  patches with more than 60 nuclei), and these are the whole of the gap in detections: DQ 0.791
  against the oracle's 0.959 is 0.17, and the fallback markers from the degenerate foreground
  mask do not recover them (−0.015 F1). The missed nuclei are those whose predicted distance map
  stays below 0.2 everywhere (which nuclei these are, small or faint, was not examined); the
  next step on markers is a detection objective (a focal or count-aware loss on the distance map, or the HoVer-Net
  horizontal/vertical maps whose gradient is sharp at every seam), not a lower threshold (thr
  0.1 on the extended grid leaves 14 % without a marker and adds background markers: 4.7 per
  patch, PQ 0.628).
- **The capped solve was not a problem, and the limit is still usable.** `maxit300` reproduces
  section 11's costs (oracle identical) at 2.8 times the training cost; its marker head came
  out slightly noisier (one seed, one run). The exact K-label limit of the distance-head costs
  is 0.758 F1 / 0.603 PQ on the 307 patches, −0.008 F1 / −0.016 PQ / −0.014 IoU from the
  converged solve, the same small price as in section 11, so deploy-at-the-limit on one CPU
  core still gives essentially the layer's instances.
- **What this says about the plan.** The multi-marker layer with a distance head for its
  markers is now the best nucleus instance segmenter in this report on F1 and PQ, by a margin
  (+0.076 F1 over the tuned watershed) that is larger than every other difference measured
  since section 6, with no post-processing beyond three scalars chosen on a held-out fold
  (the watershed has one), and the exact limit within 0.01 F1 of it. It remains one seed and
  one fold pair, and the contour-head U-Net was not given the distance head (a U-Net with a
  distance head + watershed on the distance map, the HoVer-Net recipe proper, is the fair next
  baseline: the oracle rows say the layer's costs are not the limiting factor, so that baseline
  may well match the layer on F1, and the comparison would then be about the solver as the
  final assignment step against a watershed of the distance map).

### 11.2 The fair baseline: a U-Net with the distance head, and a watershed on it

Added 19 October 2026 (side session). Section 11.1 ended with the baseline it had not run: the
contour-head U-Net of section 10.1 was never given the distance head, and the oracle rows said
the layer's costs were not the limiting factor, so a U-Net with its own distance head and the
HoVer-Net post-processing might match the layer on F1. This section runs it. Code:
`experiments/exp_unet_dist.py` (model, training, post-processing, tuning, evaluation; it
imports the U-Net, the edge target and `dist_target` / `markers_from_dist` of the existing
scripts, which are unchanged), `run_unet_dist.sh`, `plot_unet_dist.py` (tables and paired
statistics need numpy only; figures need matplotlib). Results: `results/pannuke_instances/
unet_dist/` (`unet_dist.json` with the tuning table, `unet_dist_perimage.npz`, `figures/summary.md`
holding every table of this section, `run.log`) and `unet_dist_ext/` (the same model re-tuned on
an extended grid); the trained model stays on jacobian.

**What was run.** The U-Net of section 6 with four output channels and no layer, trained on fold
1 with the recipe of sections 11 / 11.1 (30 epochs, batch 16, d4 augmentation, Adam 1e-3 with
cosine annealing, one seed): channel 0 the foreground logit under BCE against the binary nucleus
mask (the target of the layer's auxiliary head, not the gap target of section 10.1), channels 1–2
the contour head trained with exactly section 10's edge target (as `--variant unet_edge`:
positives ×10, seams ×5, weight 1), channel 3 the distance head with exactly the target and
loss of `--mk-head dist` (normalised Chebyshev distance to the instance boundary capped at 12 px,
MSE, weight 2). Training takes 10 s per epoch (5 min in all, against 290 s per epoch with the
layer in the loop). Post-processing, HoVer-Net style: the markers are `markers_from_dist` of the
predicted distance map (h-maxima of prominence h grown by a watershed of the map down to thr,
basins below the minimum area dropped: the layer's own marker rule), then a marker watershed
inside the thresholded foreground s > 0.5 of a relief that is the contour map c (mean of the two
directions), the negative distance map −d, or their sum c − d; foreground components with no
marker get no label, as the layer gives unmarked nuclei to the background (a variant keeps them
as instances when they have at least 16 px). The four choices thr ∈ {0.1 … 0.5}, min area ∈ {4,
9, 16}, h ∈ {0.1, 0.2, 0.3} and the relief (135 settings) were made by PQ on the same 300 patches
of fold 3 as sections 10.1 and 11.1 (5 min; the whole table is in the json and at the top of
`summary.md`), never on fold 2. Fold 3 chose thr 0.5, min area 4, h 0.2 and the relief c − d (PQ
0.662), with the three reliefs within 0.001 of each other at every marker setting and a flat
plateau between thr 0.4 and 0.5 (PQ 0.662 for the eight best settings, 0.652 at thr 0.3, 0.645 at
the layer's own setting 0.2 / 16 / 0.2, 0.641 at 0.1); since 0.5 was the edge of the grid, the saved model was re-tuned on thr ∈ {0.4, 0.5, 0.6, 0.7} × min area ∈ {4, 9, 16} × h ∈ {0.2, 0.3} (`unet_dist_ext`): PQ falls to 0.631 at thr 0.6 and 0.566 at 0.7 (31 % and 44 % of the nuclei unmarked), the choice is unchanged, and so is the fold-2 result below (identical to every digit, the settings being the same).

To isolate the final assignment step, the same script also loads the section 11.1 `dist` run (its
`.pt` and its fold-3 marker settings) and evaluates on the same fold-2 patches the 2 × 2 of markers
× assignment: the layer's markers through its converged solve (which reproduces section 11.1's
row to every digit), the layer's markers through this model's watershed (this model's
foreground and relief), the layer's markers through a watershed of the layer's own contour map
inside the layer's own output foreground (its solve's label > 0: everything held fixed except
the solve), and this model's markers through the layer's solve. The marker-quality counts of
section 11.1 are computed for both sets of markers.

**Results on all of fold 2** (2523 patches; the reference rows repeated from sections 10.1 and
11.1):

| output | IoU | BF₂ | edge align. | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred |
|---|---|---|---|---|---|---|---|---|---|---|
| U-Net (sec. 6), s > 0.5, components | 0.719 | 0.769 | 0.577 | 0.656 | 0.531 | – | – | 0.494 | 0.275 | 23.0 |
| U-Net + contour head, tuned marker watershed (sec. 10.1 b) | 0.718 | 0.774 | 0.568 | 0.715 | 0.583 | 0.816 | 0.715 | 0.657 | 0.344 | 27.2 |
| `bce_tuned` layer (sec. 11.1) | 0.708 | 0.761 | 0.587 | 0.769 | 0.630 | 0.819 | 0.769 | 0.645 | 0.208 | 21.7 |
| `dist` layer, converged (sec. 11.1) | 0.707 | 0.762 | 0.580 | 0.791 | 0.641 | 0.811 | 0.791 | 0.653 | 0.239 | 24.3 |
| `dist` layer, ground-truth markers (oracle) | 0.859 | 0.922 | 0.591 | 0.959 | 0.805 | 0.839 | 0.959 | 0.857 | 0.020 | 23.3 |
| `unet_dist`: s > 0.5, components | **0.725** | **0.777** | 0.573 | 0.664 | 0.539 | 0.813 | 0.664 | 0.501 | 0.313 | 24.1 |
| `unet_dist`: distance-head markers + watershed, tuned on fold 3 | 0.719 | 0.774 | **0.591** | **0.794** | **0.655** | **0.824** | **0.794** | 0.658 | **0.190** | 20.6 |
| `unet_dist`: the same, watershed of c / of −d | 0.719 | 0.774 | 0.591 | 0.794 | 0.654 / 0.655 | 0.824 | 0.794 | 0.658 | 0.190 | 20.6 |
| `unet_dist`: the same + unmarked components kept | 0.725 | 0.777 | 0.574 | 0.780 | 0.637 | 0.817 | 0.780 | **0.666** | 0.202 | 23.9 |
| `unet_dist`: watershed from the ground-truth markers (oracle) | 0.774 | 0.827 | 0.586 | 0.867 | 0.708 | 0.816 | 0.867 | 0.765 | 0.066 | 22.2 |
| layer's markers, `unet_dist`'s foreground + watershed | 0.726 | 0.777 | 0.575 | 0.781 | 0.639 | 0.819 | 0.781 | 0.671 | 0.196 | 23.5 |
| layer's markers, layer's own foreground + watershed of its contour map | 0.707 | 0.762 | 0.580 | 0.791 | 0.641 | 0.811 | 0.791 | 0.653 | 0.239 | 24.3 |
| `unet_dist`'s markers, layer's solve | 0.637 | 0.678 | 0.569 | 0.736 | 0.579 | 0.787 | 0.736 | 0.609 | 0.192 | 20.5 |

**Marker quality** (nuclei with exactly one / no / several markers; markers in background per
patch; markers per patch for 23.7 nuclei): `unet_dist` 76.6 / 21.8 / 1.6 %, 1.6, 20.6; the `dist`
layer 83.9 / 14.5 / 1.6 %, 3.6, 24.3 (recomputed here to the same digits); `bce_tuned` 77.7 /
21.1 / 1.2 %, 2.7, 21.7. By crowding for `unet_dist` (one / none / several, background per
patch): fewer than 10 nuclei 72 / 26 / 2 %, 0.7; 10–30: 79 / 19 / 2 %, 1.6; 30–60: 77 / 21 / 2 %,
2.3; more than 60: 70 / 29 / 1 %, 3.2 (the layer: 83 / 14 / 2 %, 1.8; 87 / 11 / 2 %, 3.5; 84 / 14 /
2 %, 4.7; 77 / 22 / 1 %, 6.6). Inference: 0.8 ms U-Net forward plus 16 ms of post-processing per
image on one CPU core (markers and all three watersheds), against 94 ms for the layer's
converged solve on the GPU.

**Paired per-patch differences** (bootstrap 95 % intervals; F1, PQ and AJI dataset-level,
bootstrapped over patches):

| comparison | IoU | BF₂ | edge align. | F1@0.5 | PQ | AJI |
|---|---|---|---|---|---|---|
| `unet_dist` watershed − `dist` layer | +0.012 [+0.008, +0.017] | +0.012 [+0.008, +0.016] | +0.012 [+0.010, +0.013] | +0.003 [+0.001, +0.006] | +0.013 [+0.011, +0.015] | +0.006 [+0.003, +0.009] |
| `unet_dist` watershed − `bce_tuned` layer | +0.011 [+0.008, +0.015] | +0.013 [+0.010, +0.017] | +0.004 [+0.002, +0.005] | +0.025 [+0.022, +0.028] | +0.025 [+0.022, +0.027] | +0.013 [+0.010, +0.016] |
| `unet_dist` watershed − contour-head U-Net, watershed (b) | +0.001 [−0.002, +0.005] | −0.000 [−0.004, +0.004] | +0.024 [+0.023, +0.026] | +0.079 [+0.075, +0.083] | +0.071 [+0.069, +0.074] | +0.001 [−0.001, +0.004] |
| `unet_dist` watershed − U-Net (sec. 6) | +0.000 [−0.003, +0.004] | +0.005 [+0.001, +0.009] | +0.015 [+0.013, +0.016] | +0.138 [+0.133, +0.142] | +0.124 [+0.120, +0.128] | +0.164 [+0.150, +0.177] |
| `unet_dist` watershed − its own logits | −0.006 [−0.009, −0.002] | −0.003 [−0.006, +0.001] | +0.019 [+0.018, +0.021] | +0.130 [+0.125, +0.135] | +0.115 [+0.111, +0.119] | +0.158 [+0.138, +0.179] |
| watershed of −d − watershed of c (same markers) | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | −0.000 [−0.001, +0.000] | +0.000 [−0.000, +0.001] | +0.000 [−0.000, +0.001] |
| + unmarked components kept − `unet_dist` watershed | +0.006 [+0.003, +0.009] | +0.002 [−0.001, +0.006] | −0.017 [−0.019, −0.016] | −0.014 [−0.016, −0.012] | −0.017 [−0.019, −0.016] | +0.007 [+0.006, +0.008] |
| `unet_dist` oracle − `unet_dist` watershed | +0.055 [+0.052, +0.059] | +0.052 [+0.049, +0.056] | −0.004 [−0.006, −0.002] | +0.073 [+0.070, +0.077] | +0.053 [+0.051, +0.056] | +0.107 [+0.103, +0.111] |
| `unet_dist` oracle − `dist` layer's oracle | −0.085 [−0.088, −0.082] | −0.095 [−0.099, −0.092] | −0.004 [−0.006, −0.003] | −0.091 [−0.095, −0.088] | −0.097 [−0.099, −0.094] | −0.092 [−0.095, −0.090] |
| layer's markers, `unet_dist` watershed − `dist` layer (same markers: watershed vs solve) | +0.019 [+0.016, +0.022] | +0.015 [+0.013, +0.018] | −0.005 [−0.007, −0.004] | −0.010 [−0.012, −0.008] | −0.002 [−0.004, −0.001] | +0.018 [+0.016, +0.019] |
| layer's markers, layer's foreground, watershed of its contour map − `dist` layer | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [−0.000, +0.000] | −0.000 [−0.000, −0.000] | −0.000 [−0.000, −0.000] |
| `unet_dist`'s markers, layer's solve − `unet_dist` watershed (same markers: solve vs watershed) | −0.082 [−0.084, −0.080] | −0.097 [−0.099, −0.094] | −0.022 [−0.024, −0.020] | −0.058 [−0.061, −0.054] | −0.075 [−0.078, −0.072] | −0.049 [−0.052, −0.046] |
| layer's markers, `unet_dist` watershed − `unet_dist` watershed (same watershed: markers swapped) | +0.007 [+0.003, +0.010] | +0.003 [−0.000, +0.006] | −0.017 [−0.018, −0.015] | −0.014 [−0.016, −0.011] | −0.016 [−0.017, −0.014] | +0.012 [+0.010, +0.014] |

By crowding (F1 / PQ / count error), `dist` layer vs `unet_dist` watershed: fewer than 10 nuclei
(486 patches) 0.689 / 0.553 / 0.64 vs 0.727 / 0.592 / 0.35; 10–30 (1383) 0.802 / 0.655 / 0.16 vs
0.809 / 0.672 / 0.15; 30–60 (525) 0.801 / 0.648 / 0.10 vs 0.803 / 0.660 / 0.14; more than 60 (129)
0.763 / 0.615 / 0.15 vs 0.754 / 0.613 / 0.23. Per tissue (IoU / F1 / PQ, `unet_dist` vs `dist`
layer): Breast (749) 0.717 / 0.825 / 0.665 vs 0.708 / 0.817 / 0.647; Colon (468) 0.696 / 0.708 /
0.564 vs 0.683 / 0.709 / 0.558; HeadNeck (169) 0.710 / 0.788 / 0.655 vs 0.701 / 0.784 / 0.647;
Adrenal (148) 0.711 / 0.824 / 0.706 vs 0.709 / 0.823 / 0.696; Lung (53) 0.657 / 0.713 / 0.580 vs
0.690 / 0.764 / 0.612; the baseline has the higher F1 on 10 and the higher PQ on 14 of the 15
tissues with at least 50 patches. Figures: `results/pannuke_instances/unet_dist/figures/training.png`
(the validation curve of the post-processed output, F1 0.73 → 0.81 on the first 200 test patches
with the untuned default thresholds, is above the layer's at every checkpoint; the logits reach
IoU 0.720 on the same patches), `examples_crop.png` (the same eight Colon crops as sections 11 and
11.1, with the distance map and its markers, the contour map, every post-processing and the four
cells of the marker × assignment square), `examples_full.png`.

- **Honest outcome: the fair baseline matches the layer on F1 and beats it on PQ, IoU and AJI.**
  A plain U-Net with the same three heads as the section 11.1 model, trained on the same targets
  with no layer in the loop, followed by the HoVer-Net post-processing with four scalars chosen
  on fold 3, reaches F1 0.794 / PQ 0.655 / AJI 0.658 on all of fold 2 against the layer's 0.791 /
  0.641 / 0.653: +0.003 F1 [+0.001, +0.006], +0.013 PQ [+0.011, +0.015], +0.006 AJI, +0.012 IoU and
  +0.012 BF₂, every interval clear of zero, the best count error of the report (0.19), and the
  higher PQ on 14 of 15 tissues. It is +0.079 F1 / +0.071 PQ over the contour-head U-Net with the
  distance-transform watershed of section 10.1, the same margin the layer had: what section 11.1
  attributed to the layer was the distance head and the tuned marker rule, which a watershed
  exploits equally well. The prediction at the end of section 11.1 was right, and slightly
  pessimistic for the layer: the baseline does not merely match it, its segmentation quality is
  higher (SQ 0.824 against 0.811), because the foreground head of the plain U-Net is the best
  of the report (IoU 0.725 for its thresholded logits, +0.006 over the section 6 U-Net and +0.018
  over the layer's output), whereas the layer's foreground head degenerated to speckle in both
  section 11 runs and its output foreground is 0.012 IoU below.
- **The solver is a watershed.** With the layer's own markers and the layer's own output
  foreground, a marker watershed of the layer's contour map reproduces the converged solve on
  every metric to three digits (differences +0.000 with intervals of width 0.000 on 2523
  patches): at p = 20 with the edge target's sharp costs, the solve assigns every pixel to the
  marker that the steepest path of the contour map reaches first, which is what the watershed
  does, as section 11.1's 0.008 F1 gap between the solve and the exact Power-Watershed limit
  already suggested. With the layer's markers inside this model's foreground the watershed is
  −0.010 F1 / −0.002 PQ and +0.019 IoU / +0.018 AJI against the solve: the markers decide the
  detections, the foreground decides the pixels, and the assignment step is immaterial. The
  reverse cell confirms it from the other side: this model's markers (compact cores above d =
  0.5) through the layer's solve lose 0.058 F1 / 0.075 PQ to the same markers through the
  watershed, because the layer's degenerate foreground head gives the background label a strong
  attachment inside the nuclei and the compact markers do not reach far enough to win the rim;
  the layer only works with markers grown down to d = 0.2 that already cover most of each
  nucleus. The relief of the watershed is immaterial too (the contour map, −d and their sum agree
  to 0.001): the markers grown by a watershed of the distance map already decide every split
  between touching nuclei, and the final watershed only distributes the rim below the threshold.
- **Two different marker operating points, the same detections.** Fold 3 chose a higher
  threshold for this model than for the layer (0.5 against 0.2), with a flat PQ plateau from 0.4
  to 0.5, so its markers are fewer and cleaner: 76.6 % of the nuclei with one marker, 21.8 % with
  none, 1.6 in background per patch, against the layer's 83.9 / 14.5 % and 3.6. The detections come
  out the same (DQ 0.794 against 0.791) because the layer's extra markers are mostly spurious
  ones; swapping the markers under the same watershed moves F1 by −0.014 in favour of this
  model's set. Keeping the unmarked foreground components as instances recovers IoU (0.725) and
  AJI (0.666) but costs 0.014 F1 / 0.017 PQ, as the layer's fallback markers did (−0.015 F1): the
  unmarked components are mostly merged clumps and fragments, not missed nuclei. On the sparse
  patches (fewer than 10 nuclei) the baseline is clearly ahead (F1 0.727 / count error 0.35
  against 0.689 / 0.64: fewer background markers), on the crowded ones (more than 60) slightly
  behind (0.754 / 0.23 against 0.763 / 0.15, with 29 % of the nuclei unmarked against 22 %).
- **The oracles are not comparable, and the remaining gap is still the markers.** With the
  ground-truth markers the watershed reaches F1 0.867 / PQ 0.708, +0.073 F1 over its predicted
  markers, where the layer's oracle reaches 0.959: the watershed is confined to the predicted
  foreground, so a marker in a nucleus that s > 0.5 missed yields nothing (count error 0.066
  against the layer oracle's 0.020), whereas the layer's marker attachment overrides its
  foreground head. The 0.073 of this model's oracle gap is the 21.8 % of the nuclei without a
  marker, as the 0.17 of the layer's was its 14.5 %: the next step on either side is a detection
  objective for the distance head, not the assignment step.
- **What this says about the plan.** On PanNuke, with a fair baseline on every count (the same
  backbone, the same three targets, post-processing tuned on a held-out fold like the layer's
  markers), the multi-marker layer is not a better nucleus instance segmenter than a U-Net with
  a HoVer-Net-style head and a 16-ms watershed: it is 0.003 F1 behind, 0.013 PQ behind, six
  times slower at inference, and its foreground head degenerates. What the layer still offers is
  architectural (one differentiable module trained end to end from the instance labels, no
  post-processing threshold on the foreground, an exact limit within 0.01 F1), plus the one
  empirical fact this section adds, that at the p it trains to its solve *is* the marker
  watershed of its learned contour map. The remaining caveats are those of sections 10.1 and
  11.1: one seed, one fold pair, the baseline's thresholds chosen on 300 patches of fold 3, and
  the foreground target of the two models identical here but different from section 10.1's gap
  target (not re-run with `--gap`).

### 11.3 Seeds, fold pairs, and a detection objective for the distance head

Added 22 October 2026 (side session, with Hugues' ruche allocation). Sections 11.1 and 11.2 left
two open items: everything was one seed on one fold pair, and the layer's oracle rows said that
its remaining gap was the 14.5 % of nuclei without a marker, which a detection objective on the
distance head might recover. This section runs both, with the fair baseline of section 11.2
beside the layer in every configuration. Code: `--w-peak` / `--peak-pool` in
`experiments/exp_instance_pannuke.py` (`peak_loss`) and `exp_unet_dist.py`; `--seed`,
`--train-fold` / `--test-fold` / `--tune-fold` already existed; `run_instances_11_3.sh` (jacobian),
`ruche_run.sh` / `ruche_submit.sh` (one SLURM job per run on the A100 partition of ruche, the
baseline as a job dependent on its layer run, the folds staged to the node-local disk);
`plot_instances.py` now runs without the fold-2 baselines of sections 6 and 10.1 (`--unet ""`) and
names its reference run (`--ref-label`); `compare_instances.py` reads the baseline runs too and
pairs only runs that share a test fold. Results: `results/pannuke_instances/{dist_s1, dist_s2,
dist_f23, dist_f31, dist_peak, dist_peak5}/` and `unet_dist_{s1, s2, f23, f31, peak5}/` (each with
`figures/summary.md`, `run.log`, the per-image npz; the examples npz only for the peak runs),
`compare_11_3_seeds_folds.md` and `compare_11_3_peak.md`.

**Seeds and fold pairs.** The section 11.1 layer (`--mk-head dist`, the recipe of section 11
otherwise) and the section 11.2 baseline (three-head U-Net + HoVer-Net-style watershed) were
retrained with seeds 1 and 2 on fold 1 → fold 2 (post-processing chosen on fold 3, as before) and
with seed 0 on the two other fold pairs, 2 → 3 (chosen on fold 1) and 3 → 1 (chosen on fold 2).
Every run chose its own post-processing on its own tuning fold; every baseline run also loads
the matching layer run for the markers × assignment 2 × 2 of section 11.2. On an A100 the layer
trains in 184 s per epoch (1.5 h; 290 s on jacobian's RTX 6000 Ada), 2.7 h per job with the tuning
and the evaluation; the baseline in 32 s per epoch, 48 min per job.

| configuration (train → test, tune) | n | layer: F1 / PQ / AJI / IoU | baseline: F1 / PQ / AJI / IoU | baseline − layer, paired: F1 / PQ / IoU | layer oracle − baseline oracle, F1 |
|---|---|---|---|---|---|
| 1 → 2, 3; seed 0 (sections 11.1 / 11.2) | 2523 | 0.791 / 0.641 / 0.653 / 0.707 | 0.794 / 0.655 / 0.658 / 0.719 | +0.003 [+0.001, +0.006] / +0.013 [+0.011, +0.015] / +0.012 | +0.091 |
| 1 → 2, 3; seed 1 | 2523 | 0.790 / 0.642 / 0.653 / 0.708 | 0.793 / 0.654 / 0.657 / 0.718 | +0.003 [+0.000, +0.006] / +0.012 [+0.009, +0.014] / +0.009 | +0.098 |
| 1 → 2, 3; seed 2 | 2523 | 0.789 / 0.642 / 0.654 / 0.707 | 0.799 / 0.656 / 0.673 / 0.727 | +0.010 [+0.007, +0.012] / +0.014 [+0.012, +0.016] / +0.020 | +0.089 |
| 2 → 3, 1; seed 0 | 2722 | 0.787 / 0.640 / 0.653 / 0.711 | 0.795 / 0.655 / 0.664 / 0.729 | +0.008 [+0.005, +0.010] / +0.015 [+0.013, +0.017] / +0.018 | +0.102 |
| 3 → 1, 2; seed 0 | 2656 | 0.787 / 0.636 / 0.655 / 0.709 | 0.797 / 0.659 / 0.661 / 0.725 | +0.011 [+0.008, +0.013] / +0.023 [+0.021, +0.026] / +0.016 | +0.093 |

Marker quality of the layer's markers (nuclei with one / none / several; markers in background
per patch): seed 1 83.5 / 14.8 / 1.7 %, 3.6; seed 2 84.3 / 13.9 / 1.7 %, 3.8; 2 → 3 84.6 / 13.3 / 2.0 %,
4.2; 3 → 1 82.9 / 15.1 / 2.1 %, 3.4 (section 11.1: 83.9 / 14.5 / 1.6 %, 3.6). The tuning folds chose the
layer's thr 0.2 / min area 16 / h 0.2 in every configuration but 3 → 1 (thr 0.3), and for the
baseline thr 0.4–0.5, min area 4–9, h 0.2–0.3 with the `both` or `dist` relief, i.e. the same two
operating points as section 11.2 (the baseline's markers: 76–81 % one, 18–22 % none, 1.6–2.2 in
background). The 2 × 2 repeats section 11.2 on every configuration: with the layer's own markers the
baseline's watershed is 0.003–0.013 F1 below the solve but 0.016–0.022 IoU above it, and with the
baseline's watershed fixed, the layer's markers are 0.013–0.021 F1 below the baseline's own: each
marker operating point suits its assignment step (the lower threshold the solve, the higher one
the watershed), and the model's markers through the layer's solve are the worst cell (0.744–0.772
F1 on the fold pairs).

**A detection objective for the distance head.** The 14.5 % of nuclei without a marker in
section 11.1 are, on the eight crowded Colon crops of `examples_crop.png`, mostly nuclei whose
predicted distance map does peak but too low (174 of the 291 unmarked nuclei there peak between
0.2 and 0.5, 61 below 0.2, 56 above 0.5 but absorbed into a neighbour's basin), and they are
smaller than average (median 107 px against 190). Under the pixel MSE a small nucleus hardly
weighs, so `--w-peak` adds a per-nucleus term: the maximum of the predicted map over every
ground-truth instance should reach the target's, loss = mean over instances of (max target −
max prediction)₊², weight 1, the MSE kept. The first form, the raw maximum (`dist_peak`), is a
failure of a kind worth recording: its gradient reaches one pixel per nucleus per step, and
after 30 epochs the map carries needle-shaped maxima everywhere (on 16 fold-3 patches 200
regional maxima per patch at h 0.2 against 24 for `dist`, 144 at h 0.3; the mean map and its
area above 0.2 are unchanged), so the h-maxima rule produces hundreds of markers, the tuning
solves spent 1516 s on their first batch and the run was stopped (`results/pannuke_instances/
dist_peak/README.md`). The second form (`dist_peak5`, `--peak-pool 5`) takes both maxima on the
5 × 5 mean-pooled maps, so a nucleus must carry a plateau; it trains normally (peak term 0.0034 at
the end, 283 s per epoch) and its untuned validation markers looked like the answer: 89 % of the
nuclei with exactly one marker and 4 % with none at epoch 29, against 80 / 18 % for `dist`. The
baseline got the same term (`unet_dist_peak5`, peak 0.0030). Both were tuned on fold 3 as before
(the layer's tuning took 6605 s against 2438 s: more markers per solve).

**Results on fold 2 for the peak-loss runs** (seed 0, the rows of section 11.1 / 11.2 for reference):

| output (fold 2) | IoU | BF₂ | F1@0.5 | PQ | SQ | DQ | AJI | count err. | n_pred | one / none / several | bg / patch |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `dist` layer (sec. 11.1; thr 0.2 / 16 / h 0.2) | 0.707 | 0.762 | 0.791 | 0.641 | 0.811 | 0.791 | 0.653 | 0.239 | 24.3 | 83.9 / 14.5 / 1.6 % | 3.6 |
| `unet_dist` baseline (sec. 11.2; thr 0.5 / 4 / h 0.2, relief c − d) | 0.719 | 0.774 | 0.794 | 0.655 | 0.824 | 0.794 | 0.658 | 0.190 | 20.6 | 76.6 / 21.8 / 1.6 % | 1.6 |
| `dist_peak5` layer (thr 0.3 / 16 / h 0.2) | 0.674 | 0.720 | 0.701 | 0.558 | 0.796 | 0.701 | 0.617 | 0.712 | 33.1 | 85.7 / 7.0 / 7.4 % | 10.0 |
| `dist_peak5` layer, ground-truth markers (oracle) | 0.859 | 0.922 | 0.958 | 0.804 | – | – | 0.857 | 0.019 | 23.3 | | |
| `dist_peak5` PW limit, learned costs (307) | 0.658 | 0.708 | 0.683 | 0.534 | – | – | 0.574 | 0.695 | 34.4 | | |
| `unet_dist_peak5` baseline (thr 0.5 / 16 / h 0.3, relief c) | 0.725 | 0.776 | 0.766 | 0.626 | 0.816 | 0.766 | 0.675 | 0.233 | 25.6 | 86.3 / 8.9 / 4.8 % | 6.8 |

Paired on fold 2: `dist_peak5` − `dist` −0.090 F1 [−0.095, −0.085], −0.083 PQ, −0.033 IoU;
`unet_dist_peak5` − `unet_dist` −0.028 F1 [−0.031, −0.025], −0.029 PQ, +0.006 IoU; `dist_peak5` −
`unet_dist_peak5` −0.065 F1, −0.067 PQ, −0.051 IoU; the oracles are unchanged (`dist_peak5` oracle −
`dist` oracle −0.001 F1). On fold 3 the tuning already said so: the best PQ of the `dist_peak5` layer
over the 72 settings is 0.560 against 0.646 for `dist`, and of `unet_dist_peak5` 0.632 against 0.662.

- **Honest outcome: section 11.2 holds on every seed and fold pair.** Across five configurations
  the baseline is level or ahead of the layer on F1 (+0.003 to +0.011, every interval at or above
  zero), ahead on PQ (+0.012 to +0.023) and IoU (+0.009 to +0.020), and the layer's advantage with
  ground-truth markers is a stable +0.09 to +0.10 F1. The spread between seeds (0.002 F1, 0.001
  PQ for the layer; 0.006 F1, 0.002 PQ for the baseline) and between fold pairs (0.004 F1, 0.005
  PQ) is smaller than the baseline-minus-layer difference on every configuration, so the
  one-seed caveat of sections 11.1 and 11.2 is lifted: the distance-head U-Net with a watershed
  is at least as good a nucleus instance segmenter as the layer with the same head, and
  slightly better on PQ, and the layer's instances remain 0.01–0.02 IoU short of the thresholded
  foreground on every fold.
- **The detection objective recovers the missed nuclei and loses more elsewhere.** The pooled
  peak loss halves the nuclei without a marker (14.5 → 7.0 % for the layer, 21.8 → 8.9 % for the
  baseline) but it does so by raising the map wherever something nucleus-like sits: markers in
  background go from 3.6 to 10.0 per patch for the layer (1.6 → 6.8 for the baseline) and nuclei
  split by several markers from 1.6 to 7.4 % (1.6 → 4.8 %), and no threshold on fold 3 trades
  these back (the chosen thr 0.3 against 0.2). The net effect is −0.090 F1 / −0.083 PQ for the
  layer and −0.028 / −0.029 for the baseline, with the oracle unchanged (the costs are the same):
  under the layer every spurious marker becomes an instance, since the solve has no mechanism to
  discard a label, while the watershed's foreground mask and minimum area absorb part of them,
  which is why the baseline loses a third as much. The raw-maximum form was worse still (needle
  peaks, hundreds of markers). So the lever that the oracle rows pointed at, the markers, does not
  move with a per-nucleus objective of this kind: what is needed is a marker head that is
  precise as well as sensitive (a detection loss with explicit negatives, or HoVer-Net's gradient
  term that penalises spurious maxima), and that improvement would go to the baseline's watershed
  as much as to the layer.
- **What this says about the plan.** With the one-seed caveat lifted, the record on PanNuke is: the multi-marker
  layer with the distance head is a strong instance segmenter (F1 0.787–0.791, PQ 0.636–0.642 on
  three fold pairs), the plain three-head U-Net with a watershed on the same head is at least as
  good on F1 and 0.012–0.023 PQ better, the layer's costs are 0.09–0.10 F1 better than the
  baseline's with perfect markers, and the first attempt at better markers helped neither. The
  layer's case therefore rests on what the oracle measures, the quality of its learned costs
  given the markers, which only pays off with a marker head that does not exist yet, and on its
  structural properties (one differentiable module, the exact limit at 0.7 s per patch, no
  post-processing beyond three scalars). The ruche cluster makes the next sweep cheap: a 3 × 3
  seeds × fold-pairs grid of the two models is 18 jobs, one afternoon on the A100 partition.

### 11.4 A marker head that is precise as well as sensitive? Hard negatives and the gradient term

Added 22 October 2026 (side session; eight jobs on ruche's A100 partition, one afternoon). Section
11.3 ended with the peak loss raising sensitivity and precision together in the wrong direction:
fewer nuclei without a marker, many more markers in background and inside nuclei. This section
adds the two counterweights it named, as options of both scripts (`peak_loss`, `neg_loss`,
`grad_loss` in `experiments/exp_instance_pannuke.py`, imported by `exp_unet_dist.py`): `--w-neg`,
hard negatives, the mean of the 256 largest values of the pooled prediction over the background
pixels of every image, squared (a spurious maximum in background costs directly); and `--w-grad`,
HoVer-Net's gradient term, the MSE of the horizontal and vertical finite differences of prediction
and target over all pixels (a nucleus should carry one smooth peak, the background none). Four
variants, each for the layer and for the fair baseline, seed 0, fold 1 → fold 2, post-processing
chosen on fold 3 as before: the gradient term alone (`dist_grad`, weight 2), the pooled peak loss of
section 11.3 with the gradient term (`dist_peakgrad`), with hard negatives (`dist_peakneg`, weight
1), and with both (`dist_det`); `unet_dist_*` the same for the baseline, each loading its layer run
for the 2 × 2. Results: `results/pannuke_instances/{dist,unet_dist}_{grad,peakgrad,peakneg,det}/`,
`compare_11_4.md` (which also carries the `peak5` pair of section 11.3). The training scripts also
gained `--tb` (TensorBoard scalars under `<outdir>/tb`, on by default in the run scripts) and an
`--examples diverse` selection with `--examples-only` (one patch per tissue type for the eight most
frequent types, run from the saved model: `figures/examples_diverse_{crop,full}.png` next to the
touching-cluster figures of sections 11–11.2, for the `dist`, `bce_tuned`, section 11 and
`unet_dist` runs; PanNuke's variability, sparse mucosa to elongated stromal nuclei, is visible there
where the eight densest Colon patches hid it).

**Results on fold 2** (layer / baseline; the plain distance head of sections 11.1 / 11.2 and the
pooled peak loss of 11.3 for reference; markers = nuclei with one / none / several, background
markers per patch; fold 3 = the best PQ of the tuning table):

| marker-head loss | layer F1 / PQ / IoU | layer markers | fold 3 | baseline F1 / PQ / IoU | baseline markers | fold 3 |
|---|---|---|---|---|---|---|
| MSE only (11.1 / 11.2) | **0.791 / 0.641 / 0.707** | 84 / 14 / 2 %, 3.6 | 0.646 | 0.794 / 0.655 / 0.719 | 77 / 22 / 2 %, 1.6 | 0.662 |
| + gradient | 0.789 / 0.641 / 0.709 | 85 / 14 / 2 %, 3.9 | 0.646 | **0.796 / 0.657 / 0.720** | 77 / 22 / 1 %, 1.6 | 0.663 |
| + pooled peak (11.3) | 0.701 / 0.558 / 0.674 | 86 / 7 / 7 %, 10.0 | 0.560 | 0.766 / 0.626 / 0.725 | 86 / 9 / 5 %, 6.8 | 0.632 |
| + pooled peak + gradient | 0.717 / 0.572 / 0.677 | 86 / 8 / 6 %, 9.3 | 0.578 | 0.768 / 0.627 / 0.725 | 87 / 9 / 4 %, 6.5 | 0.636 |
| + pooled peak + hard negatives | 0.674 / 0.527 / 0.600 | 70 / 25 / 5 %, 1.5 | 0.537 | 0.751 / 0.613 / 0.704 | 70 / 25 / 6 %, 1.5 | 0.620 |
| + pooled peak + negatives + gradient | 0.658 / 0.510 / 0.621 | 81 / 12 / 8 %, 4.5 | 0.517 | 0.775 / 0.631 / 0.716 | 77 / 18 / 4 %, 2.2 | 0.637 |

Paired on fold 2 against the MSE-only run of the same model (F1 / PQ / IoU, bootstrap intervals in
`compare_11_4.md`): gradient −0.002 / 0.000 / +0.002 for the layer and +0.002 / +0.002 / +0.002 for
the baseline, every interval crossing zero; peak + gradient −0.074 / −0.069 / −0.030 and −0.026 /
−0.027 / +0.006; peak + negatives −0.117 / −0.115 / −0.106 and −0.043 / −0.042 / −0.015; all three
−0.132 / −0.132 / −0.086 and −0.019 / −0.024 / −0.003. The oracles with ground-truth markers are
unchanged in every run (layer 0.956–0.959 F1, baseline 0.861–0.870): the costs and the foreground
are not what these losses change. Training cost: the gradient term is free; the hard negatives
make the fold-3 tuning slow because the maps carry many candidate maxima at low thresholds
(20 205 s for `dist_peakneg` against 2438 s for `dist`), and the chosen thresholds move to the top of
the grid (0.7 for `dist_peakneg`).

- **Honest outcome: none of the four variants improves the markers, and the ranking is the same for
  both models.** The gradient term is neutral (±0.003 on every metric, the marker counts unchanged):
  it penalises wiggles but creates or removes no maxima by itself, and the MSE-trained map was
  already smooth. Every variant with the peak loss is worse than MSE alone, on fold 3 as on fold 2,
  for the layer (−0.074 to −0.132 F1) and for the baseline (−0.019 to −0.043). The gradient term
  recovers a little of the peak loss's damage (+0.016 F1 for the layer against `peak5`), the hard
  negatives none.
- **Hard negatives fail for a reason that is specific to the pooled design, and instructive.** They
  do what they are asked, background markers fall from 10.0 to 1.5 per patch, but the nuclei
  without a marker come back (25 %) and the layer's foreground IoU falls to 0.600, the lowest of
  any full-set output since section 6. The negatives are taken on the 5 × 5 mean-pooled map over the
  pixels outside every instance, so a background pixel next to a nucleus carries nuclear pixels in
  its window and is pushed down together with the nucleus's edge, in exactly the band the layer's
  markers are grown into (thr 0.2); the peak term pulls the other way inside, and the fold-3
  tuning ends at thr 0.7 with small markers and a shrunken foreground. A background eroded by the
  pooling radius would remove the conflict; whether it would also remove the false markers the peak
  loss creates (which sit on nucleus-like stroma, not next to nuclei) is open, and was not run.
- **The layer pays for every spurious marker, the watershed does not.** The spread between the two
  models is the same lesson as section 11.3: with the same head and the same loss, the baseline
  loses a third to a quarter of what the layer loses (−0.026 against −0.074 with the gradient term,
  −0.019 against −0.132 with all three), because the watershed's foreground mask and minimum area
  absorb markers that the solve must turn into instances. A marker head good enough to help the
  layer would have to be more precise than the watershed needs.
- **What this says about the plan.** Two rounds (11.3, 11.4) of objectives on the distance head,
  six variants, have not moved the layer's markers past the MSE-trained map of section 11.1, and the
  one neutral change (the gradient term) is neutral for the baseline too. The lever is not the loss
  on the map but what the costs are trained with: the solve has only ever been trained from
  ground-truth markers (section 11's recipe), so it has never learned to confine a spurious label or
  to do without a missing one, and at test time it meets both. Training the solve from the
  predicted markers for part of the schedule, with the cross-entropy still against the true
  instances, is the experiment that addresses the mismatch directly; it is the next one if this
  thread continues. Everything here remains one seed on one fold pair.

### 11.5 Training the solve from the model's own markers

Added 23 October 2026 (side session; three jobs on ruche's A100 partition, run overnight). Section
11.4 ended on the diagnosis that the lever was not the loss on the marker map but what the solve is
trained with: in every run since section 11 the training markers were the ground-truth instances
eroded by 2–3 px, so the costs never met a spurious marker or a missing one, while at test time
14.5 % of the nuclei have no marker and 3.6 markers per patch sit in background. This section
closes that mismatch. Code: `--mk-sched E0 E1` in `experiments/exp_instance_pannuke.py`: from
epoch E0 on, every training image draws, with probability (ep − E0 + 1) / (E1 − E0 + 1) rising to 1
at E1, the markers that `predicted_markers` extracts from the current distance head (no gradient
through the extraction, which runs in a process pool; thresholds `--mk-train-thr 0.2`,
`--mk-train-min-area 16`, `--mk-train-h 0.2`, the fold-3 choice of section 11.1) in place of the
eroded ground truth (`mixed_label_systems`). The cross-entropy stays against the true instance map
(`mapped_cross_entropy`): the target of a predicted label is the ground-truth nucleus holding the
majority of its marker pixels (the owner rule of `marker_quality`), so a marker in background has no
pixel to win and its label is penalised wherever it wins; a nucleus with several markers keeps all
of them, the probability of the target being their sum, so the loss does not force a split; the
pixels of a nucleus without a marker can be right under no label and get zero weight (they stay in
the denominator; `--mk-unmarked bg` makes the background label their target instead: the solve is
then asked to hand an unmarked nucleus to the background rather than to a neighbour). The per-epoch log carries the schedule probability, the share of images on predicted
markers, the quality of those markers on the training batches and the share of unreachable pixels
(`sched_*`, `train_mk_*`, `train_unreach`, also on TensorBoard). Two schedules, the section 11.1
recipe otherwise (`--mk-head dist --w-mk 2`, p 5 → 20, edge target, 30 epochs, seed 0, fold 1 →
fold 2, post-processing chosen on fold 3): `dist_sched10` (`--mk-sched 10 15`: predicted markers
from epoch 10, all of them from epoch 15, i.e. half the training) and `dist_sched20` (`--mk-sched
20 25`: the last third, as a fine-tuning phase), then the first schedule with the background rule
(`dist_sched10_bg`, `--mk-unmarked bg`). The fair baseline of section 11.2 has no solve to train
and is unchanged (`unet_dist`). Results: `results/pannuke_instances/{dist_sched10, dist_sched20,
dist_sched10_bg}/` (each with `figures/summary.md`, `training.png`, `examples_{crop,full}.png`,
`run.log`), `compare_11_5.md` (the five runs, paired bootstraps); `.pt` files on ruche and jacobian.
Cases `dist_sched10` / `dist_sched20` / `dist_sched10_bg` in `ruche_run.sh` and
`run_instances_11_3.sh`; `compare_instances.py` gained a "training markers" column. The `bg` job
died of a CUDA error on its node during the tuning, after the model was saved: the script now
writes the arguments and the training log to the json right after training, `--eval-only` rebuilds
the log from the TensorBoard events when no json exists (`log_from_tb`), and `ruche_run.sh` has an
`eval_<run>` case that reruns the tuning and the evaluation from a saved model (used here).

**What the solve was trained on.** On the training batches the predicted markers are, from the
first scheduled epoch, what the test fold sees: 79 % of the nuclei with one marker, 19 % with none,
4.1 per patch in background at epoch 10, 84 / 14 / 3.8 from epoch 15 on (test fold in section 11.1:
83.9 / 14.5 / 3.6), 1.3 % → 0.8 % of the pixels unreachable. The marker extraction costs 20 s per
epoch with 8 workers. The cross-entropy rises from 0.094 to 0.137–0.142 the moment the predicted
markers come in and stays there (the 11.1 run ends at 0.089): against an imperfect marker set the
pixels a spurious label wins and the nuclei a neighbour's label invades are errors by construction.
The epochs took 340–400 s against 184 s in section 11.3, which is the node, not the schedule: all
three training jobs landed on ruche-gpu16, `dist_sched20` is as slow before epoch 20 as after it,
the same converged solve takes 158 ms per image there and 90 ms on ruche-gpu18 at the same PCG
iteration count (the `bg` evaluation), and the node threw a CUDA error on the third job.

**Results on fold 2** (the section 11.1 layer and the section 11.2 baseline for reference; markers
= nuclei with one / none / several, background markers per patch; the oracle with ground-truth
markers; the exact Power Watershed limit of the learned costs on the 307 limit patches):

| run | training markers | F1 / PQ / AJI / IoU | count err. | markers (fold-3 choice) | oracle F1 / PQ | limit F1 / PQ (307) |
|---|---|---|---|---|---|---|
| `dist` (11.1) | ground truth | 0.791 / 0.641 / 0.653 / 0.707 | 0.239 | 83.9 / 14.5 / 1.6 %, 3.6 (thr 0.2, area 16, h 0.2) | 0.959 / 0.805 | 0.758 / 0.603 |
| `dist_sched10` | predicted from epoch 10 (all from 15) | 0.792 / 0.645 / 0.666 / 0.717 | 0.186 | 85.6 / 12.8 / 1.6 %, 4.3 (thr 0.2, area 1, h 0.2) | 0.877 / 0.725 | 0.694 / 0.558 |
| `dist_sched20` | predicted from epoch 20 (all from 25) | 0.792 / 0.645 / 0.663 / 0.714 | 0.197 | 85.7 / 12.6 / 1.7 %, 4.3 (thr 0.2, area 1, h 0.2) | 0.902 / 0.745 | 0.719 / 0.576 |
| `dist_sched10_bg` | as `sched10`, unmarked nuclei → background | **0.795 / 0.649 / 0.668 / 0.715** | **0.182** | 85.5 / 12.7 / 1.8 %, 4.3 (thr 0.2, area 4, h 0.2) | 0.872 / 0.723 | 0.700 / 0.564 |
| `unet_dist` (11.2) | – (watershed) | 0.794 / 0.655 / 0.658 / 0.719 | 0.190 | 76.6 / 21.8 / 1.6 %, 1.6 | 0.867 / 0.708 | – |

Paired on fold 2 (F1 / PQ / AJI / IoU, bootstrap intervals in `compare_11_5.md`): `dist_sched10` −
`dist` +0.002 [−0.001, +0.004] / +0.004 [+0.002, +0.006] / +0.013 [+0.012, +0.016] / +0.010 [+0.007,
+0.013]; `dist_sched20` − `dist` +0.002 [−0.000, +0.004] / +0.004 [+0.002, +0.005] / +0.011 / +0.007;
`dist_sched10` − `dist_sched20` 0.000 / 0.000 / +0.003 / +0.003; `dist_sched10_bg` − `dist` +0.005
[+0.002, +0.007] / +0.008 [+0.006, +0.010] / +0.015 [+0.013, +0.017] / +0.009 [+0.005, +0.012], and
`dist_sched10_bg` − `dist_sched10` +0.003 [+0.001, +0.005] / +0.004 [+0.002, +0.005] / +0.002 /
−0.001. Against the baseline, `unet_dist` − `dist_sched10` = +0.002 [−0.001, +0.004] / +0.009 [+0.007,
+0.011] / −0.008 [−0.010, −0.005] / +0.002 [−0.001, +0.005], and `unet_dist` − `dist_sched10_bg` =
−0.001 [−0.004, +0.002] / +0.005 [+0.003, +0.007] / −0.009 [−0.012, −0.007] / +0.004 [+0.001, +0.007].
On the oracles, `dist_sched10` − `dist` = −0.081 F1 / −0.079 PQ, `dist_sched20` − `dist` = −0.057 /
−0.060 and `dist_sched10_bg` − `dist` = −0.086 / −0.082; on the limit patches −0.065 / −0.044, −0.040
/ −0.027 and −0.058 / −0.039.

- **The mismatch was real but small: closing it gains 0.004 PQ, 0.013 AJI, 0.010 IoU and a fifth of
  the count error, and nothing on F1.** Both schedules land on the same output (0.792 / 0.645), the
  longer one marginally ahead on AJI and IoU. The gains are where the diagnosis placed them: the
  solve now copes with the markers it is given. The fold-3 tuning table is flat in the minimum
  area (PQ 0.651 at 1, 4, 9 and 16 px, where the 11.1 model went 0.640 → 0.646), so the tuning keeps
  the tiny markers and the test fold gets 4.3 background markers per patch instead of 3.6 at a
  lower count error (0.186 against 0.239); the fallback markers of section 11, which cost the 11.1
  model 0.015 F1, now cost 0.002; and the sparse patches, where a spurious marker is a large share
  of the count, move most (< 10 nuclei: F1 0.689 → 0.704, PQ 0.553 → 0.568, count error 0.64 →
  0.44; the three crowded bins within +0.007). A background marker still becomes an instance at
  test time, but a smaller and better-confined one.
- **Giving the unmarked nuclei to the background is the better rule.** With `--mk-unmarked bg`
  the pixels of a nucleus without a marker are no longer skipped but asked of the background label,
  so a neighbour's label is penalised for invading them and the foreground cost is pushed down
  there. It adds +0.003 F1 / +0.004 PQ / +0.002 AJI over the ignore rule (every interval clear of
  zero but AJI's), for +0.005 F1 / +0.008 PQ / +0.015 AJI / +0.009 IoU over the 11.1 run, the first
  schedule whose F1 gain is clear of zero; the count error reaches 0.182, the lowest of the report.
  The gain is again largest on the sparse patches (< 10 nuclei: F1 0.716, PQ 0.576, count error
  0.42, from 0.689 / 0.553 / 0.64 in 11.1) and +0.003–0.004 F1 on the three crowded bins. The
  cross-entropy sits higher still (0.146 against 0.136), as the unmarked nuclei now count. The
  oracle (0.872) and the limit (0.700) are those of the ignore rule within 0.006: the mechanism
  below is the same. The foreground head does not pay: IoU is 0.715 against 0.717.
- **The layer now matches the baseline on F1 and AJI leads it, with PQ 0.005 behind.** `unet_dist` −
  `dist_sched10_bg` is −0.001 F1 (interval across zero), +0.005 PQ, −0.009 AJI, +0.004 IoU, and the
  count errors are equal (0.182 against 0.190). The remaining PQ margin is the segmentation
  quality of the matched nuclei, not their detection: SQ 0.816 for the layer against 0.824 for the
  baseline at equal DQ (0.795 / 0.794); the 11.1 run had SQ 0.811. The watershed's boundaries on
  the contour map are tighter than the softened solve's, which is the price of the hedging
  described next. The 2 × 2 of section 11.2 was not rerun: the baseline's watershed and markers
  are unchanged, and the layer's own markers are the same map at a different minimum area.
- **The oracle falls from 0.959 to 0.877 / 0.902, and that is the mechanism, not a side effect.**
  Trained on perfect markers, the costs could trust every marker: the marker attachment overrode
  the foreground everywhere (oracle count error 0.020, soft pixels 6.8 %). Trained on its own
  markers, the solve learns to veto a marker through the unary costs where the foreground is weak
  and to hedge between neighbours: with ground-truth markers it now drops 11 % of them (20.7
  instances per patch for 23.3 nuclei, count error 0.129) and 12.8 % of the pixels are soft, the
  learned edge scale ends at 1.84 instead of 2.14, and the converged solve needs 263–300 PCG
  iterations per batch instead of 177 (158–189 ms per image instead of 94). The exact Power
  Watershed limit of the same costs drops by 0.065 F1 (the hedging lives in the finite-p
  smoothing, which the limit removes), so this model is further from a watershed than any in
  section 11, and its oracle advantage over the baseline's watershed oracle shrinks from +0.09 to
  +0.01 (`sched10`, `sched10_bg`) / +0.03 (`sched20`). The "0.17 F1 between the layer and its oracle" of sections
  11.1–11.4 was therefore mostly a property of the ground-truth-marker training, not headroom the
  markers could unlock: the oracle measured a solve that assumed its markers were true.
- **Validation during training is noisy at this scale.** The 200-patch curve dips at epoch 19 for
  all three schedules (0.698–0.723 F1 against 0.760 at epochs 14 and 24), for `dist_sched20` before
  its schedule has begun (its random stream differs from `dist`'s from epoch 0, since the schedule
  draws a Bernoulli per image at every step, so its permutations differ), so the dip is the
  untuned-marker validation, not the switch; the 11.1 run itself ends at 0.739 there and 0.791 on
  the full fold.
- **What this says about the plan.** The last structural mismatch of the recipe is removed and the
  layer is, on this benchmark, a different model from the watershed (softer, marker-vetoing,
  further from its own limit) at the same F1, a higher AJI and a PQ 0.005 lower, with the lowest
  count error of the report. The recipe going forward is `--mk-sched 10 15 --mk-unmarked bg`
  (the default of `--mk-unmarked` stays `ignore` so that the first two runs' records read as
  run). The baseline remains the stronger segmenter per matched nucleus (SQ), which is where the
  solve's hedging costs. What the schedule did not touch is the 12.6–12.8 % of nuclei without a
  marker, which neither model recovers and which sections 11.3–11.4 showed the map losses cannot
  buy. If this thread continues, the open items are seeds and fold pairs for the `bg` recipe (the
  section 11.3 grid, four jobs), and a schedule whose training-time thresholds follow the tuning
  (the markers are extracted at the fixed 11.1 thresholds, while the final tuning now prefers a
  minimum area of 1–4). One seed, one fold pair.

## 12. Check of our Power Watershed limit against the authors' reference code

Our exact limit (`power_watershed` in `pw_conditioning.py`, `power_watershed_multi` in
`pw_layer.py`: a NumPy/SciPy re-implementation of Algorithm 1 of Couprie, Grady, Najman and
Talbot, PAMI 2011) had only been validated against finite-p Random Walker solutions and against
itself. It was checked against the authors' C/C++ implementation, `PW_1.0.1` from
https://sourceforge.net/projects/powerwatershed (Camille Couprie, Sept 2010; PINK + CSparse), on
the same problems. Harness and build notes: `experiments/pwref/` (README), records:
`results/pwref/`.

**What the reference program does.** `powerwatsegm -a 2 -i image.pgm -s seeds.pgm` (or `-m` for
a multi-label seed image, values 1..K) builds the 4-connected grid, weights w = 255 − |I_u − I_v|
(8-bit grey images; colour images use the maximum over channels), then *reconstructs* the weights
geodesically from the seeds (`grey_weights_PW`: the dilation of the seed-adjacent weights under
the weights in the line graph, i.e. every edge's weight is lowered to the bottleneck of the best
path that connects it to a seed), and runs `PowerWatershed_q2` with the reconstructed weights
for the plateau ordering and the original weights inside a plateau. A plateau is the grid-connected
set of edges of equal reconstructed weight around the current maximum; inside it the edges whose
original weight is higher are merged first (Kruskal, never two known nodes), and the unit-weight
Random Walker is solved by a CSparse LU on the edges at the level, between merged nodes, with the
seeds and the previously solved nodes as boundary. Potentials are stored in single precision. It
writes `mask.pgm` (label of the largest potential; at exactly 0.5 the first label, the
foreground), and `proba.pgm` = 255 − 255·P(label 1) truncated to a byte. With `-g 1` the
reconstructed weights replace the weights altogether (a different problem).

**Why the reconstruction is the algorithm, not a heuristic.** The plateau of Algorithm 1 lives in
the merged graph: two equal-weight edges that touch the same merged node belong to one plateau
even when they share no pixel. A breadth-first search over grid-adjacent edges of equal *raw*
weight splits such a plateau into pieces that are then solved one after the other, and the
result depends on the order in which equal weights are sorted. The reconstruction lowers every
interior edge of a region that is cut off from the seeds above level t to exactly t, so the
reconstructed plateau at level t is grid-connected through those interior edges and is the
merged-graph plateau (split at most at known nodes, which does not couple anything); the interior
edges are then merged first, and the solve runs on the level-t edges between merged nodes. That is
what our code does directly with a union-find over merged nodes. Both readings were verified
(`check_recon.py` reproduces the reconstructed weights of the dump exactly on 30 cases;
`order_dependence.py` runs the reference under three seeds of its unseeded `rand()`).

**Set-up.** A replacement `main` (`pwref_wrap.cpp`) calls the reference's own functions in the
program's order, because the third-party option parser of the release miscompiles on current
clang; the released executable built on jacobian (gcc 13) gives masks identical to the wrapper's
on the three 512² cases it was run on (`proba.pgm` differs by ±1 byte on a few hundred pixels,
single-precision rounding across compilers). The float potentials come from a six-line dump
patch at the end of `PowerWatershed_q2`. Both codes get the identical graph (the reference's own
edge order), the identical integer weights (our costs are 255 − w = |I_u − I_v|, read back from
the reference's dump; the squared cost of the rest of the report is a monotone transform with the
same ties, hence the same limit, and the 2⁻²⁰ quantisation of `pw_limit_numpy` plays no role with
8-bit costs) and the identical seeds. Cases: 80 random 24 × 24 images with four grey levels
(plateaus everywhere; 40 two-label with three seed pixels per label, 40 with 3–5 labels), the
512² cases of section 1 (synthetic σ = 0.05 / 0.1 with seeds eroded by 5 and 30 px and scribbles,
camera and astronaut eroded by 5 and 30 px), and three multi-label 512² cases (the synthetic
shapes as four labels, camera and astronaut in three intensity classes, all eroded by 5 px).

**Result: the two codes agree.** Released mode against ours on the raw weights:

| cases | pixels | potentials, max abs. difference | labels (reference rule, ≥ 0.5 → label 1) | pixels exactly at 0.5 / tied |
|---|---|---|---|---|
| 80 random 24², 2–5 labels | 46 080 | 6.1e-8 | 0 differ | 3 at 0.5, 25 tied (same in both) |
| 10 two-label 512² | 2.6 M | 6.0e-8 | 0 differ | 0 (clean synthetic), 77–817 per noisy / natural case |
| 3 multi-label 512² (K = 3, 4) | 0.8 M | 4.6e-8 | 11 differ, all on tied top-two probabilities (gap < 1e-15) | 0 / 765 / 680 tied |

- The potentials agree to single precision everywhere (the reference's `float`), on the plateau
  pixels included (6 % to 36 % of the pixels are solved on a plateau in the natural-image cases).
- The only label differences are tie-breaks. With our strict rule (x > 0.5 → foreground) the
  pixels at exactly 0.5 go to the background, with the reference's to the foreground: 85 / 627 /
  559 pixels on the noisy synthetic cases, 77 / 122 on camera, 761 / 817 on astronaut
  (0.03–0.3 % of the pixels, none on the clean synthetic image); both codes have exactly the same
  set of 0.5 pixels. In the multi-label cases the 11 differing pixels have two labels at the
  same probability to 1e-15 and the reference's single-precision sum picks the other one.
- Our K-vector multi-label solve equals K one-hot runs of the scalar code to 1e-15, and the
  two-label case of the multi-label code equals the scalar code, on every case.
- The reference run with `-g 1` is also reproduced by our code on the reconstructed weights (no
  label difference, 6e-8 on the potentials).
- Fed the raw weights for both arguments (not reachable from the program), the reference
  disagrees with ours on 0–91 347 pixels per 512² case and with itself across `rand()` seeds
  (9 387 label changes over 40 random cases, none in the released mode): the no-reconstruction
  variant is not the limit. Its bucket-sort option (`quicksort = true`, hard-wired off in the
  program) returns positions instead of edge indices inside a plateau and yields potentials
  outside [0, 1]; irrelevant to the released program.
- Timings (Mac, Apple M-series, 512², 262 144 pixels, 523 264 edges): the reference's
  `PowerWatershed_q2` call takes 0.04–0.07 s, 0.11–0.17 s with its weights and reconstruction
  (0.17–0.22 s for the whole released executable on jacobian); ours takes 0.40–0.84 s for the
  scalar code and 0.43–1.0 s for the K-vector code, on at most 256 cost levels. Our general path
  per level (union-find compression, a sparse graph and its connected components over the whole
  image) is what costs; a C implementation of the same plateau-by-plateau scheme is an order of
  magnitude faster, as expected.

**What it changes.** Nothing in the code or the results: no bug was found, and every "limit" row
of this report (sections 1–3, the PW-limit evaluations of sections 6–11, the K-label limits of
section 11) stands as the exact p → ∞ limit as the authors compute it. The one convention to keep
in mind when reading those rows is the tie at exactly 0.5, which our label maps resolve to the
background and the reference to the first label; on the 8-bit cases above it touches at most
0.3 % of the pixels, and in the learned-cost experiments, where the costs are continuous, it
cannot occur outside symmetric plateaus.

### 12.1 A Numba back end for the limit, bit-for-bit

The profile of the NumPy limit code explains the 10× gap to the C reference: the plateau solves
are negligible (a few milliseconds of the 0.6 s on camera at 512²); on 8-bit costs the time is
the whole-image passes repeated at each of the ~180 cost levels (union-find compression, a sparse
graph and its connected components, `np.unique`), and on continuous learned costs quantised to
2⁻²⁰ (246 000 plateaus on a 256² graph) it is the Python edge loop of the scalar union-find. 
`pw_fast.py` compiles exactly that bookkeeping with Numba (one sorted-edge pass, path-compressed
union-find over merged nodes, the components of each level in the merged graph, the merges of the
unambiguous components) and hands the ambiguous plateaus back to the same NumPy/SciPy solve
code as before: the same dense solve per component on levels of at most 64 edges, the same single
block LU on larger levels, the same unknown ordering, the same accumulation order of the
right-hand sides and the same representatives of merged components. The results are therefore
identical to the bit, ties at exactly 0.5 included, which `experiments/pwref/validate_fast.py`
checks with `np.array_equal`: 400 random coarse 24² cases (two labels and 3–5 labels, with the
small-plateau path on and off), the ten 512² cases of section 1 (scalar and as a two-label
K-vector solve), and the learned-cost regime on the label-augmented 256² graph at three
quantisations (scalar, and 40 markers): 0 mismatches on the Mac (Python 3.14, Numba 0.68) and on
jacobian (3.12), the reference-harness records of section 12 are unchanged under the new back
end, and the self-tests of `pw_layer.py` print the same limit lines under both.
`power_watershed` and `power_watershed_multi` pick the back end automatically (`backend=None`:
Numba when importable, else NumPy; `PW_BACKEND=numpy|numba` overrides), so `pw_limit_numpy` and
`pw_limit_multi_numpy` and every evaluation script get it without change; the first call per
process compiles for about 1.5 s and the compiled code is cached on disk.

| regime | NumPy | Numba | reference C (section 12) |
|---|---|---|---|
| 8-bit costs, 512², clean synthetic | 0.40–0.53 s | 0.065–0.08 s | 0.05–0.06 s |
| 8-bit costs, 512², noisy / camera / astronaut | 0.55–0.8 s | 0.075–0.12 s | 0.05–0.07 s |
| continuous costs at 2⁻²⁰, 256² augmented graph, two labels | 0.70 s | 0.048 s | — |
| same, 40 markers (K-vector solve) | 0.31 s | 0.032 s | — |
| continuous costs at 2⁻⁸ (many large plateaus), two labels / 40 markers | 0.77 / 0.99 s | 0.08 / 0.08 s | — |

(Mac timings; jacobian is 20–30 % slower on both.) What remains is dominated by the argsort of
the edges and by the solves themselves, so the limit now costs about what the authors' C code
costs, and a 256² learned-cost patch goes from a second to 50 ms: cheap enough to be an
inference-time operator, or to evaluate the limit on a whole fold in a minute instead of in a
process pool. The NumPy version stays as the fallback and as the definition.
