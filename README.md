# benchmarks

All benchmarks you always wanted to run. Each project asks one question you
cannot look up, and answers it by running real code twice.

## What a service boundary costs

The first project's question: every call that used to be a jump now serialises,
copies, queues, traverses a socket and schedules on the far side — how much does
that cost, and how much comes back without changing language?

**The first answer is "tune it", not "rewrite it".** Applying a stack's own
documented fix spans 0.99x to 7.97x. Stepping to the next stack along at the
same effort never exceeds 1.99x. The two largest levers in the whole table are
both configuration: turning deflate off in a Python WebSocket over
incompressible bytes is worth 7.97x at 32 KiB, and turning on keep-alives in
Go's standard-library HTTP is worth 2.01x to 2.45x.

**The whole ladder spans 7x to 9x**, Python over HTTP written the obvious way
against tuned Go over UDP — not the two orders of magnitude the choice is
usually argued with.

**It stops mattering as soon as the far side is busy.** A 36.5 µs crossing does
not decide a latency budget when the same request meets a receiver whose p50 is
588 µs or 326 ms depending on the width of one loop.

[Read the finding](projects/01-microservice-cost/FINDING.md), including the four
attacks on it that survived.

## Read this before quoting a number

**Nothing here is a baseline.** The box is a contended two-core slice of a
shared Ryzen 9 5950X with an unreadable governor, and every result is
`status: structure` except one. The orderings are the result; the absolute
figures are not.

**These are ping-pong round trips, not service calls** — one request in flight,
no marshalling of a real object, no TLS, no service discovery, no retries, no
concurrent clients. Every crossing figure is a floor, not an estimate. The floor
still earns its place, because an argument for a boundary that fails at its own
floor fails everywhere.

## Why the numbers are worth reading anyway

A benchmark fails quietly. An unpinned thread, a stale binary or two variants
doing slightly different work all produce a number that looks fine forever. So:

- **Twin implementations fold their work into a checksum**, and the run refuses
  to report when they disagree. Identical work is proved, never assumed.
- **A missing `taskset` raises** rather than running unpinned. Thread migration
  once moved a transport's high tail by 21% and reversed a published conclusion.
- **Everything compiles before the run takes the cores**, so the measured pass
  invokes no toolchain, and the versions that did build are in the result file.
- **A run started on a loud box is filed as `structure`**, never as a baseline,
  and the file says which.
- **Sweep until the ordering flips.** One number is a scoreboard and it rots.
  The crossover is the finding: at what payload, arity or core count the winner
  changes. If nothing flips, that is the finding and it says so.
- **The loser's documented fix stays in the table.** A comparison that omits the
  other side's official remedy is a strawman.

## Projects

| project | main question | state |
|---|---|---|
| [01-microservice-cost](projects/01-microservice-cost/FINDING.md) | What does a service boundary cost, and how much comes back without changing language? | partly answered |

## Layout

```text
projects/NN-slug/
  QUESTION.md         the main question, which is the theme
  FINDING.md          the answer, assembled from the measurements
  measurements/NN-slug/
    QUESTION.md       this axis, and the prediction written before the run
    variants/         twin implementations, mirrored 1:1
    sweep.toml        the swept parameter and its range
    results/          raw, append-only, never edited by hand
    FINDING.md        where it flipped, and what it gives the theme
```

## Running

```sh
make                  build, vet and test the harness
make fingerprint      print this machine as JSON
make clean            remove dist/fingerprint
```

One measurement is one command, run from its own directory so its `sweep.toml`,
variants and results stay together:

```sh
make -C projects/01-microservice-cost/measurements/04-channel-composition bench
```

That builds the variants, then re-executes itself under `sudo chrt -f 80
taskset` on the cores named in `sweep.toml`, and writes one dated file under
`results/` carrying the machine, the toolchains, the starting load and the
checksums its rows agreed on.

## Licence

GPL-3.0-or-later. See [LICENSE](LICENSE).
