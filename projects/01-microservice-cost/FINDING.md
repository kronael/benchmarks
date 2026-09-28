# Finding — a boundary costs less than folklore says, and less than the far side's own code

**Partly answered.** All four measurements have run, three of them twice, and
each has its own `FINDING.md`. What is missing is named at the bottom rather
than rounded into a conclusion.

`notes/attack.md` is the case that this project is worthless. Four of its
attacks survived and are answered here rather than buried.

## Read this before quoting a number

**These are ping-pong round trips, not service calls.** One request in flight, a
payload of `splitmix64` bytes, no marshalling of a real object, no TLS, no
service discovery, no connection-pool contention, no retries, no concurrent
clients. A real boundary has all of those, and several cost more than the socket
does.

Every crossing figure here is therefore a **floor** — the least a boundary can
cost once you have decided to have one — not an estimate of what a real one
costs. The floor is still worth having, because an argument for a boundary that
fails at its own floor fails everywhere.

**And the ratios are a ceiling.** This box is a contended two-core slice of a
shared Ryzen 9 5950X with an unreadable governor. Contention does not hit all
rows equally: the slow rows hold more cores (`py-http` and the scalar receiver
run at 1.7-1.9 of 2.0, `go-udp` and the simd receiver well under 1.0), so a
neighbour steals proportionally more from them. On a quiet machine the ladder is
probably flatter, not steeper.

Every result is `status: structure` except measurement 04's baseline. The
orderings are the result; the absolute figures are not.

## The main question

> Every call that used to be a jump now serialises, copies, queues, traverses a
> socket, and schedules on the far side. How much does that cost at the worst
> end and at the medium-effort end, where does it stop mattering, and how much
> comes back without changing language?

**Worst end to best end, the ladder spans 7x to 9x** — Python over HTTP written
the obvious way against tuned Go over UDP, across five payload sizes and two
runs (6.91x to 8.97x). Not the two orders of magnitude the choice is usually
argued with.

**About 2.2x comes back without changing language or transport.** Keep-alives in
Go's standard-library HTTP are worth 2.01x to 2.45x — the single largest lever
in the table and more than any one step of the ladder. The recoverable fraction
runs from 0.99x (`go-udp`, inside the noise) to 2.45x.

**It stops mattering as soon as the far side is busy.** Measurement 02 moves the
receiver's p50 by two orders of magnitude across a capacity knee by changing the
width of one loop, and both runs agree the knee sits between 4 and 8 bursts per
second. A 36.5 µs crossing is not what decides a latency budget when the same
request meets a receiver whose p50 is 588 µs or 326 ms depending on that loop.

## The four questions the prediction asked

**"Which is larger: worst-to-medium inside one stack, or two adjacent stacks at
the same effort?"** They are the same size. Tuning spans 0.99x to 2.45x;
adjacent stacks span 1.15x to 1.76x. The largest single gap in the table is a
tuning gap, not a stack gap. **This is the project's most useful number**: the
honest first answer is "tune it", not "rewrite it".

**"At what payload does serialisation overtake transport?"** At 8 KiB inside
rung 1, and both runs place it to within 1% — untuned `py-ws` against untuned
`py-http` reads 1.01 and 0.99 there. The cause is deflate over incompressible
bytes. Tuned gRPC also collapses between 8 KiB and 32 KiB, by 3.2x and 2.9x over
a 4x payload step; how far it falls is not stable and the claim is withdrawn.
Plain UDP never flips with anything, in either run.

**"Does the channel structure cost or save, and does the sign hold across three
languages?"** In Go it saves 1.81x to 1.98x in wall-clock time and saves nothing
per core — 0.95x to 1.11x against a single-threaded walk, over two runs. The
structure buys the second core, never cheaper work, and charges 236x to 466x in
residence latency. **The three-language question is unanswered**: only the Go
rung exists.

**"How many multiples separate Python over HTTP from `rsx-cast`?"** Unanswered.
`rsx-cast` was never measured, so rung 3 here is plain UDP and the floor the
project was aimed at is still missing.

## What the four measurements contribute

| # | measurement | runs | what it established |
|---|---|---|---|
| 01 | in-process coordination | 2 | the unit: one `float64` divide is 1.0 ns scalar, 0.46 ns vectorised, and vectorising only pays above 8 elements |
| 02 | scheduling under load | 2 | the far side's own width moves p50 by two orders of magnitude across a knee a crossing cost cannot reach |
| 03 | transport ladder | 2 | the ladder spans 7-9x; language beats wire at all five payloads in both runs; tuning beats both |
| 04 | channel composition | 2 | the channel structure converts cores into throughput and never makes work cheaper |

The unit from 01 is what makes the rest legible. A 36.5 µs crossing at the floor
of the ladder buys about 36,000 scalar divides. That is the exchange rate, and
it says a boundary is expensive in work terms however well it is built — which
is the opposite conclusion from "7-9x is not much spread", and both are true at
once.

## What is still missing

- **`rsx-cast` and the specialist transports.** MoldUDP64, SoupBinTCP, KCP and
  Aeron were to be priced beside it. None exist here.
- **Group B in Python and Rust.** Measurement 04 is Go only, so whether the sign
  holds across runtimes is not answered.
- **Measurement 02's cross-language rows.** Cases A, B, P1 and P2 need the Rust
  binaries the rsx lift dropped; the checksum gate now refuses them rather than
  passing them on one row.
- **A quiet box.** Only measurement 04 has a run started under the load limit.
  Measurement 01's two runs agree on its lower crossover and disagree on its
  upper one, so the upper one is not claimed.
- **Half of measurement 02's sweep**, which exceeds a `uint32` nanosecond
  latency field. `BUGS.md` carries the choice between a wider field and a
  shorter sweep.

None of these change the three answers above. They bound how far the ladder
reaches at the bottom and whether Group B generalises.
