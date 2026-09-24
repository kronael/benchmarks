# benchmarks

All benchmarks you always wanted to run.

Not a benchmark suite for one project. A place to ask a measurable question,
run it across the variants that matter, and keep what you learned.

## The unit is a project

A project has one main question, and that question is its theme. The question
is answered by a series of submeasurements, and each submeasurement is a
benchmark with real code — twin implementations doing byte-identical work,
proved by a checksum, never a sketch.

A submeasurement follows one axis. Everything else is pinned. A benchmark that
varies the language and the architecture at once has measured neither.

## The house rule

**Sweep until the ordering flips.** One number is a scoreboard and it rots. The
crossover is the finding: at what buffer size, what arity, what core count does
the winner change. An experiment with results and no `FINDING.md` is unfinished.

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

## Projects

| project | main question | state |
|---|---|---|
| [01-microservice-cost](projects/01-microservice-cost/QUESTION.md) | What does a service boundary cost, and how much comes back without changing language? | open |

## Running

```sh
make fingerprint   record this machine into results/
make               format, build, lint, fast test
make bench         run a measurement: make -C projects/<p>/measurements/<m> bench
make clean         remove generated artifacts
```

## Why the fingerprint comes first

A number without its machine is dead weight in six months. Frequency scaling
and thermal drift move results more than most code changes, so every result
file carries the CPU, the governor, the turbo state, the kernel, the toolchain
versions and the date. Compare within a fingerprint, never across one.

## Reporting

A result is a distribution, not a mean. An ordering that flips between runs is
not quotable, and saying so is the finding.
