# Finding — the receiver's own width decides whether it stays inside capacity

Two runs, `results/20260928-1230-receiver-width-under-contention.md` and
`results/20260928-1307-receiver-width-under-contention.md`, both
`status: structure`. They were taken with the pinned cores **24.5%** and
**81.7%** busy at the start, so agreement between them tests whether the effect
belongs to the code or to the load. Five measured repetitions per row in each,
one discarded warm-up.

Each of the six workloads gated across all fifteen runs on one checksum, in both
runs, so the three widths provably did identical work.

## Only the bottom half of the sweep is quotable, and the instrument says so

The latency field is `uint32` nanoseconds and saturates at 4,294,967,295 ns.
Each row reports how many of its 600,000 requests hit that ceiling:

| bursts/s | scalar v1 clamped, run 1 / run 2 | simd clamped |
|---:|---:|---:|
| 2, 4, 8 | 0 / 0 | 0 |
| 12 | 2 / 1 | 0 |
| 16 | 228,886 / 91,006 | 0 |
| 20 | 268,836 / 276,497 | 0 |

The clamp count itself moves with the load — 228,886 against 91,006 at 16
bursts/s — which is a second reason those points cannot be compared.

At 16 and 20 bursts/s more than a third of the scalar samples are the clamp
rather than a latency, and the `spread: 0.0` on those rows is the ceiling, not
precision. **Everything at 12 bursts/s and above is unquotable for the scalar
rows.** The simd row never clamps anywhere in the sweep, which is itself a
result.

## The knee is between 4 and 8 bursts/s, and only the scalar rows cross it

Within the unsaturated range, `scalar v1` divided by `simd`, run 1 / run 2:

| bursts/s | p50 | cores used, scalar / simd |
|---:|---:|---|
| 2 | 2.0x / 2.0x | 1.67 / 0.35 and 1.66 / 0.33 |
| 4 | 6.1x / 6.0x | 1.81 / 0.54 and 1.81 / 0.53 |
| 8 | 514x / 392x | 1.89 / 0.80 and 1.89 / 0.76 |

The two low points reproduce to within 0.1x and the cores column to within 0.04
across a 3.3x change in neighbour load. At 8 bursts/s the ratio is **about 400x
to 500x** — past the knee the number is large and not precise, and it should be
quoted as two orders of magnitude rather than as a figure.

Between 4 and 8 bursts/s the scalar row's p50 goes from 3.56 ms to 326 ms in the
first run and 3.47 ms to 241 ms in the second — a factor of 92 and of 70. Over
the same step the simd row's p50 goes from 588 µs to 635 µs and from 578 µs to
616 µs, a factor of 1.1 in both. **That is the crossover this measurement is for: not an
ordering flip, but the offered load at which one configuration leaves its
capacity while the other does not.** The scalar receiver crosses between 4 and 8
bursts/s. The simd receiver has not crossed by 20 bursts/s, the top of the
sweep.

The mechanism is in the two columns beside the latencies. The scalar row is
already holding 1.67 of the 2.0 available cores at the lightest contention level
and 1.89 by 8 bursts/s, so it has no headroom to absorb a burst; the simd row
holds 0.35 and 0.80. Peak RSS is the queue made visible: the scalar row grows to
161 MB at 8 bursts/s and 607 MB at 20, against 33 MB and 71 MB for simd, because
the requests that cannot be served are goroutines that still exist.

Both rows serve the full 0.05M ops/s up to 8 bursts/s. Above the knee the scalar
rows drop to 0.03M, so past that point they are not slower at the same job —
they are failing to do it.

## GOAMD64=v3, the loser's documented fix, does not help

It is in the table because leaving it out would be a strawman, and it changes
nothing: p99 of 87.17 ms against 87.42 ms at 2 bursts/s, and 477.77 ms against
398.76 ms at 4 bursts/s, where the remedy is 20% **worse**. Measurement 01
reaches the same conclusion on a different kernel, and its disassembly says why:
`GOAMD64=v3` does not auto-vectorise these loops at all.

## Prediction, written before the run

Six predictions in `QUESTION.md`. One holds, one is right for the wrong reason,
and the central model of the axis is reversed.

**Held.** Prediction 2, that `GOAMD64=v3` buys the scalar row under 15%: it buys
nothing and sometimes loses. Prediction 5's first half, that nothing flips and
simd leads p50 at every point: it does, at all six.

**Right for the wrong reason.** Prediction 6 said the overloaded end is not
quotable, because throughput spread above 105% offered load would exceed 15%.
The conclusion is correct and the reason is not: measured throughput spread is
0-2% at every point. The top of the sweep is unquotable because the instrument
saturates, which is an instrument limit rather than a noise limit, and the
prediction did not anticipate it.

**Reversed.** Prediction 4 said simd's p50 advantage "stays near 4x across the
whole sweep" and its p99.9 advantage "falls monotonically and is under 1.3x by
105% offered load", on the grounds that above the knee a light request waits
behind a burst identical in all three rows. The opposite happens on both counts:
the p50 advantage rises from 2.0x to about 400-500x and the p99.9 advantage
rises from 2.5x to 17.8x. The reasoning fails because it assumed all three rows reach the
knee together. They do not — the width of the light path is what decides which
row reaches it, so above the knee the comparison is between a system inside its
capacity and a system outside it, not between two queues behind one burst.

**Wrong.** Prediction 1 put the uncontended p50 advantage at 3.5x to 5x, above
the 4x lane ratio. At the lightest contention level it is 2.0x. Prediction 3
said `p99.9 / p50` rises with vectorisation at every contention level; it falls
at 2 bursts/s (120x scalar against 98x simd) and at 4, and only rises from 8
onward. Prediction 5's second half expected the three rows to become
indistinguishable on p99.9 between 85% and 105% offered load; they diverge
instead.

## What this gives the theme

The project prices a service boundary, and this measurement says what the far
side's own code does to that price. Inside capacity the receiver's width is
worth 2x to 6x on p50, and both runs agree to within 0.1x. Across the knee it is
worth two orders of magnitude,
because it decides whether the far side is queueing at all.

A crossing budget therefore cannot be written against a service time. The same
8.8 µs crossing lands on a receiver whose p50 is 588 µs or 326 ms depending on
one loop's width, and the 8.8 µs is not the number that matters in either case.

Unmeasured here: cases A, B, P1 and P2, the inherited cross-language rows. The
rsx lift never brought the Rust binaries across, so the gate now refuses those
cases rather than passing them on one row (`BUGS.md`).
