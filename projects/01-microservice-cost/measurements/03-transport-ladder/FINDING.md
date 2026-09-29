# Finding — the language costs more than the wire, and tuning costs more than either

Two runs, `results/20260928-1233-transport-ladder-rtt-us.md` and
`results/20260928-1242-transport-ladder-rtt-us.md`, both `status: structure`.
They were taken under sharply different contention — the pinned cores were 26.4%
busy at the start of the first and **85.9%** at the start of the second — so
agreement between them is a strong test of whether an ordering is a property of
the code or of the load. Three measured repetitions per cell plus a discarded
warm-up in each.

All ten rows fold **one checksum per payload size**, across two languages and
four transports, in both runs. Identical work is proved rather than assumed.

The host's 15-minute load average read 48.91 and 30.42 at the two starts, in the
opposite order to the actual core contention. It is the host's average and counts
CPUs this cpuset cannot use; `BUGS.md` carries the proposal to gate on the pinned
cores instead.

## The ladder, p50 µs at medium effort, run 1 / run 2

| row | 128 B | 512 B | 2 KiB | 8 KiB | 32 KiB |
|---|---|---|---|---|---|
| go-udp | 36.5 / 35.3 | 38.4 / 38.0 | 38.0 / 40.5 | 40.6 / 40.1 | 48.4 / 45.2 |
| go-grpc | 59.6 / 59.5 | 61.3 / 59.2 | 58.8 / 60.1 | 63.5 / 62.6 | 202.3 / 183.7 |
| go-http (control) | 68.3 / 70.8 | 69.5 / 69.4 | 73.1 / 71.6 | 81.3 / 84.8 | 96.3 / 86.0 |
| py-ws | 102.1 / 98.6 | 96.8 / 98.8 | 98.2 / 96.2 | 101.0 / 102.2 | 124.5 / 129.1 |
| py-http | 180.0 / 181.1 | 172.2 / 187.5 | 183.7 / 162.3 | 189.7 / 187.9 | 199.2 / 195.4 |

**The whole ladder spans 7x to 9x** — Python over HTTP written the obvious way
against tuned Go over UDP, across the five payload sizes and both runs
(6.91x to 8.97x). Not the two orders of magnitude the choice is usually argued
with.

## The control splits the ladder, and the language is the larger half

`go-http` holds the language fixed across transports and the transport fixed
across languages. Comparing at medium effort:

- Same transport, Python to Go: **2.07x to 2.70x**.
- Same language, HTTP to UDP: **1.77x to 2.11x**.

**Language is the larger half at all five payload sizes in both runs** — ten
comparisons out of ten. The margin narrows as the payload grows (2.6x against
1.9x at 128 B, 2.2x against 1.9x at 32 KiB), because per-byte work is where the
two runtimes differ least.

Without this row the ladder reads as a transport result, and it is mostly a
runtime result.

## Tuning one stack is worth as much as moving a rung

The project's own question is which gap is larger: worst-to-medium inside one
stack, or stack-to-stack at the same effort. They are the same size.

**The largest single lever in the table is not a transport.** Enabling
keep-alives in Go's standard-library HTTP is worth **2.01x to 2.45x** across
payloads and runs — more than any one step of the ladder, and the most stable
number in this measurement. `go-udp`'s remedy is worth 0.99x to 1.08x, inside
the noise, because a strict ping-pong never queues and the buffers have nothing
to absorb.

## Where the ordering flips

**The rung-1 crossover is at 8 KiB, and the two runs place it to within 1%.**
Untuned `py-ws` against untuned `py-http`, as a ratio:

| payload | 128 B | 512 B | 2 KiB | 8 KiB | 32 KiB |
|---|---:|---:|---:|---:|---:|
| run 1 | 0.38 | 0.40 | 0.49 | **1.01** | 2.97 |
| run 2 | 0.40 | 0.40 | 0.45 | **0.99** | 2.97 |

At 8 KiB the two rows are within 1% of each other and the two runs order them
oppositely. That is not instability in the finding — **it is the crossover
itself**, located to a single sweep point by two independent runs. The mechanism
is deflate over an incompressible `splitmix64` payload, which buys no bytes and
costs CPU on both sides. Turning it off is worth 7.97x and 7.68x at 32 KiB in the two runs, the one place
a remedy attacks the per-byte slope rather than the fixed cost.

**Tuned gRPC collapses between 8 KiB and 32 KiB**, from 63.5/62.6 µs to
202.3/183.7 µs — a factor of 3.2 and 2.9 over a 4x payload step, against 1.19x
and 1.13x for `go-udp`. Both runs agree it falls from second-fastest to below
`go-http` and `py-ws`. **Whether it also falls below `py-http` is not stable**:
it lands within 6% of that row and the two runs order them oppositely. The
collapse is quotable; the final position is not.

`go-udp` never flips with anything, in either run.

## Prediction, written before the run

Seven predictions in `QUESTION.md`, built on a Hockney `T(m) = α + β·m` model.

**Held, including the mechanism and the location.** Prediction 3 put a flip
inside rung 1 — `py-ws` worst against `py-http` worst — "at about 8 KiB", from
`Δα/Δβ`, because deflate on incompressible bytes is β-dominated. It is at 8 KiB,
to within 1%, in two runs. Prediction 5 said `go-grpc` worst loses to `go-http`
medium at every size and that `go-grpc` medium "loses above about 8 KiB". Both
hold at all five payloads in both runs. The model earned those.

**Wrong.** Prediction 1 put rung 1 worst against rung 3 medium at 15-25x at
128 B; it is 8.67x and 8.97x, so the Python stack's fixed cost is smaller than
the model allowed. Prediction 6 said the recoverable fraction is largest for
`py-http`; it is largest for `go-http`, 2.01-2.45x against `py-http`'s
1.67-1.96x.

**Half right.** Prediction 2 said nothing flips between rungs anywhere in the
sweep. `go-grpc` medium does fall past `py-ws` medium at 32 KiB, which is a
rung-to-rung flip, though its claimed fall past `py-http` is the part that did
not replicate. Prediction 4 said the rung-to-rung gap beats the worst-to-medium
gap at 128 B and the reverse inside rung 1b at 32 KiB. The second half holds
(7.97x from one remedy); the first does not, because `go-http`'s 2.0-2.4x
already exceeds every rung-to-rung gap.

The α/β model predicted both crossovers and their causes correctly and put every
absolute fixed cost too high. That is the better half to be right about.

## What this gives the theme

Group A asked what a crossing costs at the worst end and at the medium-effort
end, and how much comes back without changing language:

- Worst end to best end is **7x to 9x**, not 100x.
- **About 2.2x comes back without changing language or transport**, from the
  documented remedy on the stack you already have.
- The rest splits roughly 2.3x language against 1.9x wire, so a change of
  runtime buys more than a change of wire — at every payload, in both runs.

These are ping-pong round trips, not service calls. `notes/attack.md` at the
project level says what that excludes and why the figures are a floor.

Unmeasured: `rsx-cast` at 8.80 µs, the floor this ladder was meant to reach, and
MoldUDP64, SoupBinTCP, KCP and Aeron beside it. Rung 3 here is plain UDP.
