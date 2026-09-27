# 04 — does structuring computation as channels work?

Not what a crossing costs, but whether composing the work as channels and a
module-level graph calculation is a structure worth having once you know.

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

`dist/fingerprint` has to exist, because every result file carries the machine:

```sh
make -C ../../../.. build
sudo chrt -f 80 taskset -c 0,1 make bench
```

This container's cpuset is 0-1 host-wide, so CLAUDE.md's `-c 2,3` is refused
here. `run.py` pins every child to the cores in `sweep.toml` itself, so plain
`make bench` is also pinned; the `chrt` wrapper only adds priority. A run above
`quiet_load_15` is filed as `structure` rather than as a baseline, and the file
says which.

`make test` runs every composition once at a small shape and checks that all
four fold to the same checksum. It takes about three seconds and measures
nothing.

## Results

Dated files under `results/`. Numbers quoted here cite the file they came from;
nothing is inlined without one. Not run yet.

## Notes

`notes/design.md` has the case against the measurement, the published figures it
was checked against, and the provenance.
