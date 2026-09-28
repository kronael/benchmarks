# Finding — vectorising the work unit pays only inside a band

Two runs, `results/20260927-1339-scalar-vs-simd-divto.md` and
`results/20260928-1201-scalar-vs-simd-divto.md`. **Both are `status: structure`**
— each started above the 1.6 load limit — so the absolute ns/element figures are
not a baseline. The pinned cores were 34.3% busy at the start of the second, and
the two runs agree on the ordering everywhere it matters, which is what this
file claims. Both binaries' disassembly is in each result's `sources`.

## The lower flip is at 8 elements, and it is stable

Ratio is `scalar / simd` per element at `GOAMD64=v1`: above 1.00 the vector
kernel wins. Four readings, two runs by two estimators.

| elements | run1 median | run2 median | run1 low | run2 low |
|---:|---:|---:|---:|---:|
| 1 | 0.25 | 0.26 | 0.25 | 0.26 |
| 4 | 0.75 | 0.68 | 0.71 | 0.74 |
| 5 | 0.42 | 0.43 | 0.41 | 0.43 |
| 8 | 0.97 | 1.39 | 1.08 | 1.19 |
| 16 | 1.36 | 1.63 | 1.45 | 1.60 |
| 1024 | 2.15 | 2.51 | 2.27 | 2.36 |
| 262144 | 2.15 | 2.31 | 2.18 | 2.23 |
| 1048576 | 1.82 | 2.20 | 1.85 | 2.12 |
| 4194304 | 1.01 | 1.17 | 1.08 | 1.25 |

**Three of the four readings put the flip at 8 elements and the fourth puts it
at 16.** Below it the vector kernel loses by up to 4x: at one element it costs
about 10 ns against 2.6 ns. In the band above it the win is 2.0x to 2.5x.

## The upper flip is NOT established, and that is the honest answer

At 4,194,304 elements the first run reads 1.01 and 1.08 — a tie — and the second
reads 1.17 and 1.25 — still a win. **The two runs disagree about whether the
ordering has flipped at the top of the sweep, so it is not quotable.** What both
runs do show is the advantage shrinking there, from about 2.2x at 262k to 1.0-1.2x
at 4M, as three `float64` arrays at 24 bytes per element reach 96 MB and leave
the 16 MB L3.

The sweep does not bracket the upper crossover. Answering it needs sizes past 4M
and a quiet box, and this measurement has neither.

## A partial vector costs more than the elements it saves

At 4 elements the ratio is 0.68-0.75. At 3 and at 5 it falls to 0.33-0.43. Four
`float64` lanes are exactly one 256-bit AVX2 register, so 4 is the only small
size needing no mask. A masked tail is dearer than the scalar loop it replaces,
and 5 elements — one full vector plus a masked tail — is worse than 4. Both runs
agree on this at every one of those three sizes.

## GOAMD64=v3 does not close the gap

Go's documented remedy for an SSE2-only default is in the table and it buys the
scalar row between 1% and 9% depending on the run. It never approaches the 2.1x
the vector kernel takes.

The `v3` scalar row is the steadier of the two across runs — 1.003/1.004 at 1024
elements, 1.002/1.005 at 16384 — while the `v1` scalar row moves (1.011/1.088,
1.011/1.034), so most of that 1-9% spread is the `v1` row's noise on a contended
box rather than a gain from `v3`.

The disassembly says why the remedy cannot help: both scalar binaries hold
`DIVSD=5 DIVPD=0` and both vector binaries hold `DIVSD=4 DIVPD=6` at either
level. `GOAMD64=v3` does not auto-vectorise this loop, which is the reason gonum
ships hand-written assembly for it.

## What this gives the theme

This measurement is the zero of both groups and sets the unit the rest of the
project is priced in. One element-wise `float64` divide costs about 1.0 ns
scalar and 0.46 ns vectorised inside the band. A crossing priced at 8.8 µs
therefore buys roughly 8,800 scalar divides or 19,000 vectorised ones, and that
is the exchange rate every rung above is reported against.

It also bounds when an in-process optimisation can answer a crossing at all:
below 8 elements vectorising makes the work 4x *worse*, and past L3 it stops
paying. Outside that band the work unit is not the thing to fix.

## Prediction, written before the run

Six predictions in `QUESTION.md`. Four hold, one holds in shape but not in size,
one is wrong in absolute terms and right in ratio.

**Held.** The lower flip was predicted at 4 elements "or at 8 if that tail costs
more than one scalar iteration". It is at 8, so the conditional branch was the
right one and the reason it named is the reason measured. The in-cache win was
predicted at "about 2x, not the 4x the lane count suggests, because Zen 3's
floating-point divider is 128 bits wide and a 256-bit `VDIVPD` is two passes
through it" — measured 2.0 to 2.5x, so that model of the divider stands. The
`v3` rows were predicted to move nothing and they move under 10%. Five elements
was predicted to be worse per element than 8 if the portable tail is the cause,
and it is.

**Held in shape, wrong in size.** The top end was predicted to shrink "once the
working set leaves L2" and to be "inside the spread by 1M elements", with the
expected wording "the ordering does not reverse at the top end, it ties". The
shape is right — it shrinks and does not reverse. The size is not: the win
survives L2 intact (2.1x at 16384, where the working set is 393 KB) and is still
1.8-2.2x at 1M. The bandwidth argument was applied to the wrong cache level, and
whether it reaches a tie at 4M is the thing the two runs disagree about.

**Wrong in absolute terms.** At 1024 elements the prediction was scalar
1.1-1.3 ns/element and vector 0.55-0.70. Measured: 1.011-1.088 and 0.433-0.470.
Both sides are faster than the whole predicted range, so the ratio was right for
the wrong absolute numbers.
