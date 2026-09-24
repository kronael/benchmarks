# 01 — in-process coordination

**The floor.** The price of talking to yourself, with no boundary yet. Every
crossing in this project is reported as a difference from here.

**Axis:** the coordination mechanism, nothing else. Same kernel, same input,
same process. `serial` inline, `channel` handoff, `mutex` shared lock.

**Sweep:** work per item, from trivial to substantial, wide enough to cross
the point where coordination stops losing. See `sweep.toml`.

**Effort rows:** obvious code, then the documented remedy — buffered channel,
batched handoff, lock held for less.

## Prediction

Write it here before the first run, then leave it alone. Where do you expect
the ordering to flip, and how far apart are the variants at the small end?

## Running

```sh
make bench
```

## Results

Dated files under `results/`. Numbers quoted here cite the file they came
from; nothing is inlined without one. Not run yet.
