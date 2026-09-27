# 01 — in-process coordination

**The floor.** The price of talking to yourself, with no boundary yet. Every
crossing in this project is reported as a difference from here.

**Axis:** whether the per-item work unit is vectorised, and nothing else. Same
kernel, same input bytes, same process, same core. The kernel is gonum's
element-wise `float64` divide, `floats.DivTo`, once as gonum's own portable loop
and once with Go 1.27's `simd` package. `QUESTION.md` has the axis, the
provenance and the prediction.

**Sweep:** elements in one work unit, 1 to 4M — one vector at the bottom, DRAM at
the top, with L1, L2 and L3 bracketed in between. See `sweep.toml`.

**Effort rows:** the build the box gives you (`GOAMD64=v1`, SSE2 for the scalar
loop), then Go's own documented remedy (`GOAMD64=v3`). Both variants at both, so
no row is a strawman.

## Prediction

In `QUESTION.md`, written before the first run.

## Running

Wait for the box to be quiet, then take the core:

```sh
sudo chrt -f 80 taskset -c 1 make bench
```

`make bench` builds the four binaries, disassembles each one to check the row
actually contains the instructions it claims, runs the sweep pinned, refuses to
report if the two kernels folded different checksums, and writes one dated file
under `results/`. It needs `dist/fingerprint` from the repo root, which `make
build` there produces. A run started above the load limit in `sweep.toml` is
recorded as `status: structure`, never as a baseline.

## Results

Dated files under `results/`. Numbers quoted here cite the file they came from;
nothing is inlined without one. Not run yet.
