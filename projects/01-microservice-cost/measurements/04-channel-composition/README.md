# 03 — does structuring computation as channels work?

Not what a crossing costs, but whether composing the work as channels and a
module-level graph calculation is a structure worth having once you know.

**Axis:** the structure. The same computation written as an ordinary call graph
in the same language is the control, so the runtime is held fixed and only the
shape changes.

**Ladder:** Python, then Go, then Rust. Each at both effort rows.

**What makes it non-trivial:** a graph deep and wide enough that scheduling and
allocation decide the answer, not a three-node toy. The graph recomputes on
invalidation, so the measurement includes the propagation, not just the walk.

## Prediction

Does the channel structure cost or save, and does the sign hold across all
three languages? If it flips, at what graph depth or fan-out?

## Running

```sh
make bench
```

## Results

Dated files under `results/`. Not run yet.
