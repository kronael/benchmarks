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
- **Make the machine quiet before you measure.** Stop the other tenants; do
  not nice around them. Only when the box cannot be quieted does the run get
  `status: structure` rather than a baseline, and the file says which it is.
  The load average at start goes in the frontmatter either way.
- **Prove the regime under test was actually entered.** Enough warmup rounds,
  and an independent trace showing the thing happened — the JIT optimised, the
  cache filled, the path went hot. A number from a run that never reached the
  regime measures something else entirely.
- **Record the commit that changed the method and keep the superseded numbers
  beside the new ones**, so a correction can be audited instead of believed.
- **Prove identical work.** Variants fold their work into a checksum and the
  run refuses to report when the checksums differ.
- **Keep the loser's documented fix in the table.** A comparison that omits
  the other side's official remedy is a strawman, not a measurement.

## What makes a comparison honest

- **Same fragment, two configurations.** The pair is the benchmark: the same
  code once without the thing and once with it. Two different programs are a
  demo, not a measurement.
- **Use real code somebody else wrote.** Collect it from the wild and run on
  it. A synthetic case dressed as a real one is the commonest way to be wrong
  and look thorough.
- **A null result from a badly chosen probe is a fact about the probe.** If
  nobody would write the case you measured, the zero says nothing about the
  system. Fix the probe before reporting the finding.
- **Fix only real findings.** Not everything a tool flags is a defect, and
  chasing the rest buys nothing.

## Attack it before you publish it

Write the strongest case that the measurement is worthless — the design is
pointless, the number proves nothing, somebody already did it better — then
design around whatever survives. Do this in writing, and research it against
what is actually published online.

Strawmanning yourself first is the whole discipline. It is also why the
opponent's own documented fix stays in the results table: having attacked
your own case that hard, leaving theirs weak is indefensible.

## Writing a result down

**State the result as a fact, and say why it can be trusted.** Never narrate
the investigation. A result file is not a diary of what you tried; it is the
number, the conditions that make it defensible, and nothing else.

Ground every claim in something real. A design worth measuring is one that
turns up in practice and can be corroborated against a published source —
not one invented because it was convenient to measure.

Docs split by the question they answer: `README.md` says what this is and why
you would care, in the first screen; `notes/` explains the reasoning; results
carry the numbers. Plain engineering language, no fluff.

## Config

First CLI argument is a TOML file. Generated input is the default.

## Where these rules came from

Two sources, and they are not the same weight.

**The author's own steering**, across the turbo, turbocharge and jitmax work:
make the machine quiet, prove the regime was entered, same fragment in two
configurations, real code from the wild, a bad probe's null result, fix only
real findings, attack it before publishing, and state results as facts rather
than as an investigation diary.

**rsx's committed artifacts** — `facts/cast-vs-udp-overhead.md` and
`bench/go-vs-rust/notes/design.md` — supply core pinning, payload alignment,
the checksum gate, open-loop arrivals and the loser's-fix rule. Those files
are real and their evidence is real, but they were written during a sprint
whose reasoning is not recoverable, so they are cited as artifacts rather
than as doctrine handed down.
