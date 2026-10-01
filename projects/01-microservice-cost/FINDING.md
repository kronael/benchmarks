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

**The box is a contended two-core slice** of a shared Ryzen 9 5950X with an
unreadable governor, so the question is how much that moves the spread. The
answer is: less than expected, and three runs now say so. The ladder ran with
the pinned cores 26.4%, 85.9% and 99.5% busy at the start, and the full-ladder
spread at 128 B read 8.67x, 8.97x and 8.82x. A 3.8x change in neighbour load
moved it 3.5%, and both ends of the ladder held their identity: `py-http`
untuned slowest at 316.6, 316.8 and 311.1 µs, `go-udp` tuned fastest at 36.5,
35.3 and 35.3 µs.

**No result here is `verified`.** Every run carries `status: structure` under the
gate as it now stands, which judges the busy fraction of the pinned cores
against a 10% limit. Those cores have not been under 25% busy at any point when
a run was started, so this box cannot certify a baseline at all. Earlier files
labelled `verified` were judged by the superseded load-average gate and that
label does not mean what it says; `BUGS.md` records the change and why the
reason first given for it was wrong.

An earlier version of this file claimed the slow rows hold more cores and so
lose more to a neighbour, quoting per-row core figures. **Measurement 03 records
no per-row core usage at all** — its columns are rung, row, effort, payload and
the three percentiles. Those figures were measurement 02's, about a receiver
rather than a transport, and they did not belong here.

The orderings are the result; the absolute figures are not.

## The main question

> Every call that used to be a jump now serialises, copies, queues, traverses a
> socket, and schedules on the far side. How much does that cost at the worst
> end and at the medium-effort end, where does it stop mattering, and how much
> comes back without changing language?

**Worst end to best end, the ladder spans 7x to 9x** — Python over HTTP written
the obvious way against tuned Go over UDP, across five payload sizes and three
runs (6.91x to 8.97x). Not the two orders of magnitude the choice is usually
argued with. The three runs put the 128 B figure at 8.67x, 8.97x and 8.82x
while the neighbour load on the pinned cores moved 3.8x, so this is the most
replicated number in the project.

**Between nothing and 8x comes back without changing language or transport**,
depending on which default was wrong. Keep-alives in Go's standard-library HTTP
are worth 2.01x to 2.45x; turning off WebSocket compression over incompressible
bytes is worth 7.97x at 32 KiB. At the other end `go-udp`'s own remedy is worth
0.99x to 1.08x, inside the noise.

**It stops mattering as soon as the far side is busy.** Measurement 02 moves the
receiver's p50 by two orders of magnitude across a capacity knee by changing the
width of one loop, and both runs agree the knee sits between 4 and 8 bursts per
second. A 36.5 µs crossing is not what decides a latency budget when the same
request meets a receiver whose p50 is 588 µs or 326 ms depending on that loop.

## The four questions the prediction asked

**"Which is larger: worst-to-medium inside one stack, or two adjacent stacks at
the same effort?"** Tuning wins, and by more than expected. Across both runs and
all five payloads, applying a stack's own documented fix spans **0.99x to 7.97x**;
stepping to the next stack along at the same effort never exceeds **1.99x**. The
two largest levers in the whole table are both tuning fixes: turning deflate off
in the Python WebSocket row (7.97x at 32 KiB) and turning on keep-alives in Go's
standard-library HTTP (up to 2.45x). **This is the project's most useful
result**: the first answer is "tune it", not "rewrite it".

**"At what payload does serialisation overtake transport?"** At 8 KiB inside
rung 1, and both runs place it to within 1% — untuned `py-ws` against untuned
`py-http` reads 1.01 and 0.99 there. The cause is deflate over incompressible
bytes. Tuned gRPC also collapses between 8 KiB and 32 KiB, by 3.2x and 2.9x over
a 4x payload step; how far it falls is not stable and the claim is withdrawn.
Plain UDP never flips with anything, in either run.

**"Does the channel structure cost or save, and does the sign hold across three
languages?"** In Go it saves 1.81x to 2.10x in wall-clock time and saves nothing
per core — 0.95x to 1.11x against a single-threaded walk, over two runs. The
structure buys the second core, never cheaper work, and charges 200x to 544x in
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
- **Group B in Python and Rust.** Measurement 04 has a Python rung in
  `variants/python` but no run that includes it, so whether the sign holds
  across runtimes is still unanswered.
- **Measurement 02's cross-language rows.** The Rust twins for cases A and B
  exist in `variants/rust/src/bin`, but `BUGS.md` records that case A's
  operating points exceed this box, so `make bench` runs case C only.
- **A quiet box, and this one is not it.** No run has ever started with the
  pinned cores under 25% busy, against a 10% limit, so nothing here is
  `verified` and nothing can be until the box is quiet or the neighbours stop.
  Measurement 01's runs agree on its lower crossover and disagree on its upper
  one, so the upper one is not claimed.
- **Half of measurement 02's sweep**, which exceeds a `uint32` nanosecond
  latency field. `BUGS.md` carries the choice between a wider field and a
  shorter sweep.

None of these change the three answers above. They bound how far the ladder
reaches at the bottom and whether Group B generalises.
