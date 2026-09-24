# CLAUDE.md

# benchmarks

All benchmarks you always wanted to run. An experiment log, not a product and
not a curriculum. There is no learner here and no gate to pass.

## The unit

One question, one axis, N variants. The axis is the single thing that differs.
Pin everything else — same algorithm, same input, same machine, same session.
Varying two things at once measures neither.

## Sweep until the ordering flips

The finding is the crossover, never the single number. Ask at what size, arity,
depth or core count the winner changes. If nothing flips across the whole
sweep, that is also a finding and it is worth one sentence in `FINDING.md`.

An experiment with `results/` and no `FINDING.md` is unfinished. Treat it the
way a lab with no scale target is treated: not done.

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
experiments/NN-slug/
  QUESTION.md   the ask, the axis, the prediction
  variants/     one directory per implementation
  sweep.toml    the swept parameter and its range
  results/      raw, append-only, never edited by hand
  FINDING.md    where it flipped, and why
fingerprint/    Go: records the machine into every result
analysis/       Python: reads results, finds the crossover
```

## Languages

Go for the runner and anything that keeps time under load. Python for the
analysis and the reports. A variant is written in whatever language the
question is about.

## Config

First CLI argument is a TOML file. Generated input is the default.
