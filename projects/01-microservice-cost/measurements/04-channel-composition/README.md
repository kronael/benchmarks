# 04 — does structuring computation as channels work?

Not what a crossing costs, but whether composing the work as channels and a
module-level graph calculation is a structure worth having once you know.

**Answer so far (Go rung only):** in wall-clock time the batched channel graph
wins the whole sweep by 1.81x to 1.98x. Multiplied by the cores each row used it
is level with the single-threaded walk, 0.95x to 1.11x. The structure buys the
second core, not cheaper work, and it costs 236x to 466x in residence latency.
`FINDING.md` has the crossovers and the evidence.

**Axis:** the structure. The same computation written as an ordinary call graph
in the same language is the control, so the runtime is held fixed and only the
shape changes.

**Ladder:** Python, then Go, then Rust. Each at both effort rows.

**What makes it non-trivial:** a graph deep and wide enough that scheduling and
allocation decide the answer, not a three-node toy. The graph recomputes on
invalidation, so the measurement includes the propagation, not just the walk.

**Built so far:** the Go rung only, as four rows — `direct` and
`direct-parallel` for the call graph at worst case and at medium effort,
`channel` and `channel-batched` for the channel graph at the same two efforts.
The Python and Rust rungs do not exist, so nothing here can yet say whether the
sign holds across runtimes.

## Prediction

In `QUESTION.md`, written before the first run, with the one parameter a
plumbing smoke check corrected recorded beside the superseded figure rather than
in place of it.

## Running

Wait for the box to be quiet, then take the cores:

```sh
make bench
```

`make bench` is the whole run. It builds `dist/fingerprint` and the variants,
then re-executes itself under `sudo chrt -f 80 taskset` on the cores named in
`sweep.toml`. Everything compiles before that escalation, on purpose: under
`sudo` the pinned toolchain cannot resolve from root's HOME and `go` silently
falls back to the system go1.19.8, so the measured pass invokes no toolchain at
all. The toolchain versions it did build with are recorded in the result file.

This container's cpuset is 0-1 host-wide, so CLAUDE.md's `-c 2,3` is refused
here. The cores come from `sweep.toml` rather than from the command line, so the
documented command cannot name a core this box does not have. A run started with
the pinned cores busier than `bench.QUIET_CORES` is filed as `structure` rather
than as a baseline, and the file says which. The busy fraction of those two
cores is what decides it, because the host load average counts sixteen CPUs this
cpuset cannot use and says nothing about the slice.

`make test` runs every composition once at a small shape and checks that all
four fold to the same checksum. It takes about three seconds and measures
nothing.

## Results

Dated files under `results/`. Numbers quoted here cite the file they came from;
nothing is inlined without one.

- `20260928-1201-channel-composition.md` — `verified`, 15-minute load 1.26, pinned
  cores 31.5% busy. The baseline.
- `20260927-1341-channel-composition.md` — `structure`, load 2.67. Kept beside it:
  the two agree on the winner at all eight sweep points and their checksums
  match, which is what makes the ordering quotable.

## Notes

`notes/design.md` has the case against the measurement, the published figures it
was checked against, and the provenance.
