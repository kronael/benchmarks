# benchmarks

All benchmarks you always wanted to run.

Not a benchmark suite for one project. A place to ask a measurable question,
run it across the variants that matter, and keep what you learned.

## The unit

One question, one axis, N variants. The axis is the single thing that differs;
everything else is pinned. A lab that varies the language and the algorithm at
once has measured nothing.

## The house rule

**Sweep until the ordering flips.** One number is a scoreboard and it rots. The
crossover is the finding: at what buffer size, what arity, what core count does
the winner change. An experiment with results and no `FINDING.md` is unfinished.

## An experiment

```text
experiments/NN-slug/
  QUESTION.md   the ask, the axis, and your prediction written before the run
  variants/     one directory per implementation
  sweep.toml    the swept parameter and its range
  results/      raw, append-only, never edited by hand
  FINDING.md    where it flipped, and why
```

## Running

```sh
make fingerprint   record this machine into results/
make               format, build, lint, fast test
make bench         run an experiment: make bench EXP=01-channel-vs-serial
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
