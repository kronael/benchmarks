# CLAUDE.md

# benchmarks

All benchmarks you always wanted to run. An experiment log, not a product and
not a curriculum. There is no learner here and no gate to pass.

## The unit is a project

A **project** has one main question, and that question is its theme. Nothing in
the project exists except to answer it.

The question is answered by a series of **submeasurements**. Each one is a
**benchmark with real code** — twin implementations doing byte-identical work,
never a sketch and never a quoted figure from somewhere else.

A submeasurement follows one axis: one thing differs, everything else is
pinned — same algorithm, same input, same machine, same session. Varying two
things at once measures neither.

The project's `FINDING.md` answers the main question. A measurement's own
`FINDING.md` answers only its axis, and says what it contributes to the
theme.

## Sweep until the ordering flips

The finding is the crossover, never the single number. Ask at what size, arity,
depth or core count the winner changes. If nothing flips across the whole
sweep, that is also a finding and it is worth one sentence in `FINDING.md`.

A measurement with `results/` and no `FINDING.md` is unfinished, and a project
whose measurements do not add up to an answer is still open. Say so rather
than rounding it into a conclusion.

**Prove identical work.** Twin implementations emit a checksum over the work
they did, and the runner refuses to report when the checksums differ. Identical
work is proved, never assumed.

**Show the loser's documented fix.** When one side loses, the tuned row using
that side's own official remedy stays in the table. A comparison that omits it
is a strawman, not a measurement.

## Every result carries its fingerprint

CPU model, core count, governor, turbo state, kernel, toolchain versions and
the date go into every result file, written by the runner and never by hand.
Compare inside one fingerprint. Comparing across machines or across a governor
change is not a comparison.

Frequency scaling and thermal drift move numbers more than most code changes.
A run on a contended host is filed as structure, never as a baseline, and the
file says so.

## Reporting

- A result is a distribution. Report the median and the spread, never a mean
  alone, and say how many samples.
- An ordering that is not stable across runs is NOT quotable. Saying it is
  unstable is the honest finding.
- Write the prediction into `QUESTION.md` before the run. A prediction that
  was right for the wrong reason is worth more than a number.
- Separate warmup from steady state wherever a JIT is in play.

## Layout

```text
projects/NN-slug/
  QUESTION.md         the main question, which is the theme
  FINDING.md          the answer, assembled from the measurements
  measurements/NN-slug/
    QUESTION.md       this axis, and the prediction written before the run
    variants/         twin implementations, real code, mirrored 1:1
    sweep.toml        the swept parameter and its range
    results/          raw, append-only, never edited by hand
    FINDING.md        where it flipped, and what it gives the theme
fingerprint/          Go: records the machine into every result
analysis/             Python: reads results, finds the crossover
```

## Languages

Go for the runner and anything that keeps time under load. Python for the
analysis and the reports. A variant is written in whatever language the
question is about.

## Config

First CLI argument is a TOML file. Generated input is the default.
