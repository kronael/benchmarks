# benchmarks

All benchmarks you always wanted to run. Each project asks one question you
cannot look up, and answers it by running real code twice.

## What a service boundary costs

The first project's question: every call that used to be a jump now serialises,
copies, queues, traverses a socket and schedules on the far side — how much does
that cost, and how much comes back without changing language?

**No figure from this repository is quotable, and none appears on this page.**
Every run is taken on a two-CPU slice of a Ryzen 9 5950X with an unreadable
governor and neighbours that never stop. The runner judges a baseline on the
busy fraction of the pinned cores against a 10% limit, and those cores have
never been under 25% busy when a run started, so every result carries
`status: structure`. This box cannot certify a baseline at all.

What survives is the ordering, and it survives well. The transport ladder has
run three times with the pinned cores 26.4%, 85.9% and 99.5% busy at the start,
and its headline spread moved 3.5% across that 3.8x change in neighbour load,
with both ends of the ladder keeping their identity. Three orderings hold across
repeated runs:

- **Tuning beats stepping.** Applying a stack's own documented fix moves the
  number further than moving to the next stack along at the same effort. The two
  largest levers in the whole table are both configuration, not architecture.
  The first answer is "tune it", not "rewrite it".
- **The ladder is far shorter than the folklore.** Worst end to best end does
  not reach the two orders of magnitude the choice is usually argued with.
- **It stops mattering as soon as the far side is busy.** The crossing does not
  decide a latency budget when the same request meets a receiver whose own p50
  moves by orders of magnitude on the width of one loop.

[Read the finding](projects/01-microservice-cost/FINDING.md) for the figures,
each beside the conditions that qualify it, and the four attacks on it that
survived.

## Read this before quoting a number

**These are ping-pong round trips, not service calls** — one request in flight,
no marshalling of a real object, no TLS, no service discovery, no retries, no
concurrent clients. Every crossing figure is a floor, not an estimate. The floor
still earns its place, because an argument for a boundary that fails at its own
floor fails everywhere.

**A quotable set needs a quiet box, and the reruns have been done.** All four
measurements ran again on 2026-10-01 under one command each, and all four came
back `structure`. Quotable numbers now wait on the machine, not on the work: the
neighbours here are five containers holding about a third of one core between
them, and nothing below 25% busy has ever been observed at a run's start.

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
