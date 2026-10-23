| variant | output | n | IoU | BF 1px | BF 2px | band acc | soft frac |
|---|---|---|---|---|---|---|---|
| unet | logits | 3669 | 0.842 | 0.364 | 0.503 | 0.685 | 0.187 |
| rw_learned | logits | 3669 | 0.817 | 0.211 | 0.310 | 0.670 | 0.222 |
| rw_learned | layer | 3669 | 0.844 | 0.359 | 0.498 | 0.678 | 0.178 |
| rw_learned | converged | 3669 | 0.845 | 0.369 | 0.506 | 0.688 | 0.195 |
| rw_learned | limit | 200 | 0.795 | 0.296 | 0.412 | 0.637 | 0.000 |
