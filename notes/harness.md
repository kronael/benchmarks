# Why the harness does each of these things

`bench.py` says only what each function does. The reasoning is
here, because the repository's docs split puts the numbers in `results/`, what
this is in `README.md`, and the reasoning in `notes/`. Moved out of the
docstrings on 2026-09-30; the wording is unchanged.

## Pinning raises rather than running unpinned — `run()`

Pinning is not tuning. Unpinned threads report their own migration as the thing
under test: in rsx that alone moved a transport's high tail by 21% and reversed
the published conclusion. An absent `taskset` raises rather than running
unpinned, because an unpinned run looks identical afterwards.

## The busy fraction is sampled before the run — `contention()`

`/proc/loadavg` is the host's and counts CPUs this cpuset cannot use, so it is
not commensurable with a two-core slice. Measured here: a host load of 36 over
pinned cores that were 17% idle, of which the benchmark itself held 14% and a
neighbour 69%. Per-CPU time is commensurable, and sampled before the benchmark
starts it measures the neighbours rather than the benchmark.

`claim()` takes that sample as its very first act, before it builds anything.
It did not at first, and the first run under the new harness recorded the
pinned cores as 99.5% busy on a box measured at 25-38% busy moments earlier:
the sample had caught `claim()`'s own compile. A reading taken after the
harness starts working describes the harness.

## The count is gated as well as the value — `gate()`

One row satisfies any equality test while comparing nothing, and a comparison of
one row is the quiet failure this harness exists to catch.

## The file is named for the minute — `record()`

A second run on the same day stands beside the first instead of replacing it: a
superseded number has to remain auditable next to the one that replaced it.

## The machine readings come from before the run — `claim()`, `record()`

A quiet start that ends loud is still a baseline, and a loaded start is structure
however quiet the finish. `QUIET_CORES` is the one limit for the whole
repository, so no measurement can set itself an easier one.

The status decides on the busy fraction of the pinned cores, not on the host
load average. `/proc/loadavg` is not namespaced: it counts runnable tasks across
all sixteen host CPUs while a measurement runs inside a two-CPU cpuset. Measured
together, a host load of 26.3 sat beside pinned cores that were 63.5% idle, and
a host load of 36.2 beside cores with zero steal. The host figure is kept in
every result as `host_load_at_start`, because it describes the machine the slice
lives on, but it decides nothing.

## The toolchains are read before the escalation — `claim()`, `record()`

`record()` runs in the measured pass, which is root, and under root's HOME
`GOTOOLCHAIN` cannot resolve the pinned toolchain, so `go` there is the system
go1.19.8. A toolchain version read at that point would describe root rather than
the compiler that built the binaries. `claim()` therefore writes the reading to
`dist/toolchains.json` while it is still unprivileged, and `record()` copies that
file into the result.

## The agreed checksum goes into the file — `gate()`, `record()`

`gate()` returns the value it accepted so the runner can collect one per swept
point and hand the set to `record()`. The gate already refuses a mismatch; the
reason to write the value down is that a console nobody kept is not evidence. A
claim that two runs did identical work is then checkable from the two files.

## Low, median, high, never a mean alone — `summarise()`

The spread is itself a finding, and a wide one usually names the scheduler rather
than the code.
