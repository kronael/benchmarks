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
make bench
```

`make bench` is the whole run. It builds the four binaries and disassembles each
one to check the row actually contains the instructions it claims, writing that
trace to `bin/regime.txt`. It then re-executes itself under `sudo chrt -f 80
taskset -c 1`, reads the trace, runs the sweep, refuses to report if the kernels
folded different checksums, and writes one dated file under `results/` with the
trace in its `sources`.

Everything compiles before that escalation, on purpose. Under `sudo` the pinned
toolchain cannot resolve from root's HOME and `go` silently falls back to the
system go1.19.8, so the measured pass invokes no toolchain at all. The
toolchain versions it did build with are recorded in the result file. A run
started above `bench.QUIET_LOAD_15` is recorded as `status: structure`, never as
a baseline.

## Results

Dated files under `results/`. Numbers quoted here cite the file they came from;
nothing is inlined without one.

Two runs, both `status: structure` — each started above the load limit, so the
absolute ns/element figures are not a baseline. They agree that the vector
kernel loses below 8 elements and wins by 2.0x to 2.5x above it, and they
disagree about the top of the sweep. `FINDING.md` says which claims survive
that disagreement.
