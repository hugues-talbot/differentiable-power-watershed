# Check of `power_watershed` against Couprie's reference implementation (PW_1.0.1)

Reference: https://sourceforge.net/projects/powerwatershed (PW_1.0.1.tar.gz, Sept 2010, CeCILL;
C/C++, PINK + CSparse). Not included here: download it into an empty directory of its own.
`src/powerwatsegm.c` is the program (`-a 2` = Power Watershed q = 2), `src/MSF_RW.c` holds
`PowerWatershed_q2`, the plateau algorithm, `src/cccodimage.c` the weights
(`grey_weights_PW`: w = 255 - |I_u - I_v| on the 4-connected grid, plus their geodesic
reconstruction from the seeds), `src/random_walker.c` the plateau solve (CSparse LU).

Building on macOS (clang 17) and Ubuntu 24.04 (gcc 13): the `#define epsilon` of
`include/powerwatsegm.h` clashes with `std::numeric_limits::epsilon()`; pre-include the C++ math
headers so that they are parsed first:

    make FLAGS="-g -Wall -include math.h" CCFLAGS="-g -O2 -Wno-int-conversion -Wno-implicit-function-declaration -Wno-implicit-int"   # macOS
    make CXXFLAGS="-g -O2 -Wno-deprecated -include cmath -include limits" CCFLAGS="-g -O2"   # Ubuntu / gcc 13

On macOS the third-party option parser (`argv/argv.c`) miscompiles and the executable segfaults
before reading anything; on Linux it runs. `pwref_wrap.cpp` is a replacement `main` that does
what `powerwatsegm.c` does for `-a 2` (same seed-image conventions, `compute_edges`,
`grey_weights_PW`, `PowerWatershed_q2`), lets one choose which weights go to the plateau
routine (`prog`: the program's default, plateaus on the reconstructed weights and the original
weights inside; `geod`: `-g 1`; `raw`: original weights for both), seeds the stochastic quicksort,
and dumps the mask, the 8-bit potential map and the edge weights as raw arrays. The float
potentials come from `MSF_RW_dump_proba.patch` (six lines at the end of `PowerWatershed_q2`,
active only when `PW_DUMP_PROBA` is set; the diff is against the CRLF-stripped original).
Compile against the objects of a patched copy:

    g++ -O2 -include math.h -I$P/include -I$P/PINK -I$P/CSparse/Include pwref_wrap.cpp $(ls $P/objects/*.o | grep -v argv.o) -o pwref_wrap

Scripts (numpy, scipy, scikit-image; no torch needed, `power_watershed_multi` is lifted out of
`pw_layer.py` by `ast`):

- `pwref_compare.py --repo <ell-zero> --wrap ./pwref_wrap --out <dir>`: the comparison on 80
  random coarsely quantised 24 x 24 images (two-label and 3-5 labels) and on the 512^2 cases of
  `pw_conditioning.make_cases` plus three multi-label cases; one JSON record per case.
- `order_dependence.py`: the reference under three seeds of `rand()`, per mode.
- `check_recon.py`: a 20-line re-implementation of the geodesic reconstruction against the dump.
- `ties_and_timing.py`: the remaining label differences are ties; the timing table.
- `make_pgms.py`: PGMs of three cases for the released executable (run on jacobian).
- `validate_fast.py`: bit-for-bit validation of the Numba back end (`../pw_fast.py`) against the
  NumPy code on random coarse images (both plateau paths), the 512^2 cases and the learned-cost
  regime, with timings; run from `unrolling/experiments`.

Results: `unrolling/results/pwref/` (JSON lines of both runs and the log of the 512^2 run);
write-up: section 12 of `unrolling/finishing-layer-experiments.md`.
