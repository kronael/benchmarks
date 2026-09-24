# Step 1 — does a Go channel ever beat an inline serial loop?

## The axis

The coordination mechanism, and nothing else. Same kernel, same input, same
process, same machine. Three variants:

- `serial` — the work inline in one goroutine, no coordination at all
- `channel` — the work handed between goroutines over a buffered channel
- `mutex` — the work behind a shared lock, as the control that is neither

## The sweep

Work per item, from trivial to substantial. The prediction is that coordination
loses at the small end and wins at the large end, so the sweep must cross the
point where it flips. `sweep.toml` holds the range.

## The prediction

Write it here BEFORE the first run, with the reasoning, then do not edit it.

- Where do you expect the ordering to flip, and why?
- How far apart are the variants at the small end?
- Does buffering the channel move the crossover, or only the slope?

A prediction that was right for the wrong reason is worth more than a number.

## What it gives the theme

Step 1 of five. This is the floor the other four are measured against: the
price of talking to yourself, with no boundary yet. Every later step adds one
crossing, so its cost is the difference from the step before — and all of them
are differences from this one.

It needs no toolchain beyond Go and no second language, so it proves the
harness before the question gets hard.
