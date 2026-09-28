# Finding — a boundary costs less than folklore says, and less than the far side's own code

**Partly answered.** All four measurements have run and each has its own
`FINDING.md`. What is missing is named at the bottom rather than rounded into a
conclusion.

Every number below is `status: structure` except measurement 04's baseline. This
box is a two-core slice of a shared Ryzen 9 5950X with an unreadable governor, so
the orderings are the result and the absolute figures are not.

## The main question

> Every call that used to be a jump now serialises, copies, queues, traverses a
> socket, and schedules on the far side. How much does that cost at the worst
> end and at the medium-effort end, where does it stop mattering, and how much
> comes back without changing language?

**At the worst end to the best end the whole ladder spans 8.67x** — Python over
HTTP written the obvious way at 316.6 µs against tuned Go over UDP at 36.5 µs,
at a 128-byte payload. Not the two orders of magnitude the choice is usually
argued with.

**2.42x comes back without changing language or transport.** Enabling
keep-alives in Go's standard-library HTTP is the single largest lever in the
whole table — larger than any one step of the ladder. The recoverable fraction
runs from 1.04x (`go-udp`, whose remedy is inside the noise) to 2.42x.

**It stops mattering as soon as the far side is busy.** Measurement 02 moves the
receiver's p50 by 514x across a capacity knee by changing the width of one loop.
A 36.5 µs crossing is not the number that decides a latency budget when the same
request meets a receiver whose p50 is 588 µs or 326 ms depending on that loop.

## The four questions the prediction asked

**"Which is larger: worst-to-medium inside one stack, or two adjacent stacks at
the same effort?"** They are the same size. Tuning spans 1.04x to 2.42x;
adjacent stacks span 1.15x to 1.76x. The largest single gap in the table is a
tuning gap, not a stack gap. **This is the project's most useful number**: it
says the honest first answer is "tune it", not "rewrite it".

**"At what payload does serialisation overtake transport?"** Between 8 KiB and
32 KiB for tuned gRPC, which flips from second-fastest to last. Between 2 KiB and
8 KiB for the untuned Python WebSocket row, where deflate over incompressible
bytes is the cost. Plain UDP never flips with anything: 36.5 µs to 48.4 µs
across a 256x payload range.

**"Does the channel structure cost or save, and does the sign hold across three
languages?"** In Go it saves 1.81x to 1.98x in wall-clock time and saves nothing
at all per core — 0.95x to 1.11x against a single-threaded walk. The structure
buys the second core, never cheaper work, and charges 236x to 466x in residence
latency. **The three-language question is unanswered**: only the Go rung exists.

**"How many multiples separate Python over HTTP from `rsx-cast`?"** Unanswered.
`rsx-cast` was never measured, so rung 3 here is plain UDP and the floor the
project was aimed at is still missing.

## What the four measurements contribute

| # | measurement | what it established |
|---|---|---|
| 01 | in-process coordination | the unit: one `float64` divide is 1.0 ns scalar, 0.46 ns vectorised, and vectorising only pays between 8 and about 1M elements |
| 02 | scheduling under load | the far side's own width moves p50 by 514x across a knee that a crossing cost cannot reach |
| 03 | transport ladder | the ladder spans 8.67x; language beats wire 2.64x to 1.87x; tuning beats both |
| 04 | channel composition | the channel structure converts cores into throughput and never makes work cheaper |

The unit from 01 is what makes the rest legible. A 36.5 µs crossing at the floor
of the ladder buys about 36,000 scalar divides. That is the exchange rate, and
it says a boundary is expensive in work terms however well it is built — which
is the opposite conclusion from "8.67x is not much", and both are true at once.

## What is still missing

- **`rsx-cast` and the specialist transports.** MoldUDP64, SoupBinTCP, KCP and
  Aeron were to be priced beside it. None exist here.
- **Group B in Python and Rust.** Measurement 04 is Go only, so whether the sign
  holds across runtimes is not answered.
- **Measurement 02's cross-language rows.** Cases A, B, P1 and P2 need the Rust
  binaries the rsx lift dropped; the checksum gate now refuses them rather than
  passing them on one row.
- **A quiet box.** Only measurement 04 has a baseline taken under the load limit.
  01 has two runs that agree on its lower crossover and disagree on its upper
  one; 02 and 03 have one run each.
- **Half of measurement 02's sweep**, which exceeds a `uint32` nanosecond
  latency field. `BUGS.md` carries the choice between a wider field and a
  shorter sweep.

None of these change the three answers above. They bound how far the ladder
reaches at the bottom and whether Group B generalises.
