# The Power Watershed as a differentiable segmentation layer

Code, result tables, figures and the complete experimental record for

> G. R. Akl, L. Najman, H. Talbot, *The Power Watershed as a Differentiable Segmentation
> Layer*, submitted to DGMM 2027.

The Power Watershed (PW) is the p → ∞ limit of the seeded Random Walker (RW) with edge
weights raised to the power p. At every finite p the segmentation solves a sparse
positive-definite linear system, exactly differentiable through one adjoint solve; the
limit is the watershed itself, evaluated exactly by a maximum spanning forest for any
number of labels. This repository contains the layer, the studies of the paper and the
long-form record of every run, negative results included.

## Layout

| Path | Contents |
|---|---|
| `experiments/pw_layer.py` | The differentiable RW/PW layer (dense shifted-grid operators, unrolled Jacobi-PCG, implicit adjoint, fixed-point reweighting, multi-marker form) and the exact PW limit on the label-augmented graph. Run it for the self-tests. |
| `experiments/pw_conditioning.py`, `pw_fast.py` | Exact Power Watershed (plateau algorithm of Couprie et al. 2011, NumPy; Numba back end) and the conditioning study. |
| `experiments/exp_*.py` | The experiments: synthetic softmax, reweighting, U-Net + layer on Oxford-IIIT Pet and PanNuke (binary), multi-marker instance segmentation, baselines. `run_*.sh`, `ruche_*.sh` are the launchers used. |
| `experiments/seg_metrics.py`, `plot_*.py`, `compare_*.py` | Metrics (boundary F, instance F1 / PQ / AJI, edge alignment), figures and comparison tables. |
| `experiments/pwref/` | Harness that checks our PW limit against the authors' reference implementation (PW_1.0.1, sourceforge.net/projects/powerwatershed): identical to single precision. |
| `results/` | Metrics (JSON), summary tables (Markdown) and figures of every run. Per-image arrays and trained weights are not included (size). |
| `finishing-layer-experiments.md` | The experimental record, sections 1–12, written as the work progressed. |
| `pw_unrolling_note.tex` | The feasibility note that started the project. |

## Running

Python ≥ 3.12 with `numpy`, `scipy`, `torch` (CUDA build for the GPU runs), `scikit-image`,
`matplotlib`, optionally `numba`. Each script has a docstring with its usage. Data: Oxford-IIIT
Pet is downloaded by `torchvision`; PanNuke (CC BY-NC-SA, Gamper et al.) must be obtained from
the authors and converted once with `experiments/convert_pannuke.py`. The experiments were run
on one NVIDIA RTX 6000 Ada and on A100 nodes.

## Citation

Until the proceedings appear, please cite the arXiv / HAL version (to come) or this repository.

## Licence

The code (`experiments/`) is released under the BSD-3-Clause licence (`LICENSE`); the
report, the note, the result tables and the figures under CC BY-SA 4.0 (`LICENSE-CC-BY-SA`).
Copyright 2026 Galia R. Akl, Laurent Najman, Hugues Talbot.
