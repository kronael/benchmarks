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

## Plumbing

**None of this is new doctrine. It is the boring-code baseline applied to
measurement**, and it is written down only because a benchmark fails quietly
where ordinary code fails loudly.

`bench.py` is the whole harness: run pinned, gate on the checksum, summarise,
write the record. One file, standard library only, `uv run bench.py`. The
benchmark programs do the measuring — if the harness grows past one screen,
something that belongs in a variant has leaked into it.

Make is the uniform interface and never the logic: `make bench` means the same
thing in every measurement, and a recipe is one command that calls Python. The
moment a recipe wants an `if`, a loop or a pipe, it belongs in Python. **No
bash scripts.**

Go for anything that must keep time under load. A variant is written in
whatever language the question is about.

## Rules that decide whether a number is real

- **Pin the cores, or you measured the scheduler.** Not a tuning option. In
  rsx, pinning alone cut a transport's high tail from 17.3 to 13.6 µs and its
  spread by 38%, which reversed the published conclusion — the original
  "casting adds 8 µs of protocol work" was thread migration. `bench.py` raises
  rather than running unpinned, because an unpinned run looks identical after
  the fact.
- **Align the payload across the whole comparison set**, so the table is
  apples to apples rather than one row measuring a different thing.
- **Low, median and high. Never a mean alone.** The spread is itself a
  finding, and a wide one usually names the scheduler rather than the code.
- **A contended host produces `status: structure`, never a baseline**, and the
  file says which it is. The load average at start goes in the frontmatter.
- **Record the commit that changed the method and keep the superseded numbers
  beside the new ones**, so a correction can be audited instead of believed.
- **Prove identical work.** Variants fold their work into a checksum and the
  run refuses to report when the checksums differ.
- **Keep the loser's documented fix in the table.** A comparison that omits
  the other side's official remedy is a strawman, not a measurement.

## Config

First CLI argument is a TOML file. Generated input is the default.
