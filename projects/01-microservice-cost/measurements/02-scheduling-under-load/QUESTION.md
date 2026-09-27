# 02 — scheduling under load

**When the far side is contended, who pays?** A crossing is cheap until the
receiving side is busy. This measures the cost of being queued behind someone
else's work, which is the cost a latency budget actually feels.

The measurement carries three axes. Two are inherited from
`bench/go-vs-rust` in `github.com/kronael/rsx` and are described in
`notes/design.md`: case A varies the runtime's preemption policy (Go against
Rust) and case B varies the memory reclamation policy. Case C is added here and
is the axis this file predicts.

## The axis (case C)

**The width of the receiver's own work, under a pinned contention source.**

One program, one driver, one payload. Three rows differ in exactly one thing —
how the light request's reduction over its payload is executed:

| row | build | the reduce |
|---|---|---|
| `scalar v1` | stock (`GOAMD64=v1` is this box's default) | one `float64` accumulator, one element per add |
| `scalar v3` | `GOAMD64=v3` | the same source, Go's own documented remedy |
| `simd` | stock, `GOEXPERIMENT=simd` | `simd.Float64s`, one vector per add |

The contention source is pinned across all three rows and is byte-identical to
case A's: 1-in-`heavy_every` requests run an 80M-iteration splitmix64 chain
(~100 ms), scalar in every row. Only the light path's width moves.

`scalar v3` is in the table because omitting it would be a strawman. `go env
GOAMD64` is `v1` on this box, so the stock scalar row is compiled SSE2-only,
which flatters the vector row. Go's documented answer to that is to raise
`GOAMD64`, so the raised row stays in the table whatever it shows.

### Why case C and not a third mode inside case A

Case A's light path is a splitmix64 chain: each step depends on the previous
state, so it cannot be vectorised without changing the work. Case A is also
the cross-language row against the Rust twin, and altering its fragment would
invalidate that comparison. Case C keeps case A's driver verbatim — same
batch, same 1 ms tick, same open-loop arrivals, same latency-against-intended-
tick accounting, same burst — and replaces only the light request's work with
something a vector unit can actually do.

### The receiver work, and why one checksum can gate three widths

A filter-and-reduce over a payload window: for each element, add it once if it
is below a threshold and three times if it is not. This is what a receiver does
to a decoded message, and it is the shape people vectorise.

Floating-point addition is not associative, so a lane-partitioned vector sum
and a sequential scalar sum normally differ in the low bits — which would make
a cross-width checksum gate impossible. It is made possible by keeping every
value an exactly-representable integer: payload elements are `splitmix64`
output masked to 20 bits, multipliers are 1 and 3, and the window is 8192
elements, so every partial sum is an integer below 2^35 and far below 2^53.
Addition and multiplication of such values are exact, so all three widths must
produce bit-identical results. They are gated on it, and the gate is the reason
the rows can be compared at all.

### What this axis cannot separate

The scalar rows evaluate a data-dependent branch that the vector rows replace
with a mask. The payload is PRNG-derived and the threshold is its midpoint, so
that branch is close to maximally unpredictable. The measured gap is therefore
width **and** branch elimination together. That is honestly what vectorising
this fragment buys — the vector unit supplies both and the scalar loop can have
neither — but the number is not a pure lanes-per-cycle ratio and is not quoted
as one. `scalar v3` is the probe that separates them: if raising `GOAMD64`
closes most of the gap, the win was the branch.

Measurement 01 in this project prices the same scalar-against-vector width
question on a third-party kernel with no contention at all. If case C's
uncontended width ratio disagrees with 01's, this probe is wrong and its tail
result is not quotable. `notes/simd-axis.md` is the full case against case C.

### Why offered load differs between rows on purpose

Making the light path cheaper lowers total utilisation at the same burst rate.
That is not a confound, it is the mechanism under test. The contention source
is pinned in rate and in cost; the receiver's work width is the axis; and the
utilisation it implies is the consequence being measured.

## The sweep

The swept parameter is the contention level, as `heavy_every` — one burst per
that many requests, at 50k req/s. `sweep.toml` holds the range. On two cores a
100 ms burst is expensive, so the range is chosen to cross capacity:

| `heavy_every` | bursts/s | offered cores, scalar | offered cores, simd |
|---:|---:|---:|---:|
| 25000 | 2 | 0.68 | 0.32 |
| 12500 | 4 | 0.88 | 0.52 |
| 6250 | 8 | 1.28 | 0.92 |
| 4166 | 12 | 1.68 | 1.32 |
| 3125 | 16 | 2.08 | 1.72 |
| 2500 | 20 | 2.48 | 2.12 |

Capacity is 2.0 cores. The range spans roughly 35% to 125% of it, which puts
the knee inside the sweep rather than at its edge. It stops at 125% because the
latency field is `uint32` nanoseconds and clamps at 4.29 s; the program counts
clamped samples and reports the count, so a saturated row is visible rather
than inferred.

## The prediction

Written before any run. Left alone afterwards.

**The hardware ceiling is 4x.** `simd.VectorBitSize()` is 256 and
`simd.Emulated()` is false on this box at every usable `GOAMD64` level —
`GOAMD64=v4` aborts, because a 5950X is Zen 3 and has no AVX-512. So four
`float64` lanes, and the reduce's dependent-add critical path shortens by at
most 4x.

1. **Uncontended p50: `simd` beats `scalar v1` by 3.5x to 5x.** Above the 4x
   lane ratio, because the scalar row additionally pays the mispredicted
   select.

2. **`GOAMD64=v3` buys the scalar row under 15%.** `gc` does not auto-vectorise
   this loop and does not fuse `x*sel + acc` into an FMA on amd64. v3 supplies
   VEX encodings and possibly a `cmov` for the select; neither shortens the
   4-cycle dependent-add chain that sets the loop's cost. The loser's
   documented fix does not close the gap. If it does close it, the finding is
   about Go's codegen and branch prediction, not about SIMD.

3. **The headline claim holds as a ratio and fails as an absolute.**
   `p99.9 / p50` rises with vectorisation at every contention level: cheaper
   service time leaves queueing as a larger share of what a request waits. But
   absolute `p99.9` still improves or ties — vectorising does not make the tail
   worse.

4. **`simd`'s advantage decays in the tail as contention rises.** Its p50
   advantage stays near 4x across the whole sweep. Its p99.9 advantage falls
   monotonically and is under 1.3x by 105% offered load, because above the knee
   a light request's latency is the burst it is queued behind, and that burst is
   identical in all three rows.

5. **Nothing flips, and that is the finding.** `simd` leads p50 at every point.
   On p99.9 the three rows become indistinguishable within run-to-run spread
   somewhere between 85% and 105% offered load; that convergence is the
   crossover this measurement is for. A strict flip would need wider live vector
   state to make Go's async preemption more expensive, and on Zen 3 a YMM save
   is cheap against a ~10 ms preemption interval, so I predict no strict flip.

6. **The overloaded end is not quotable.** Throughput spread above 105% offered
   load exceeds 15%, because a 1 ms generator tick and 100 ms bursts on two
   cores interact more than the code does. Any ordering read off those rows is
   structure.

## Status of any run made here

This box is a two-core slice of a Ryzen 9 5950X carrying other work, and the
governor is unreadable. Every result from it is filed `status: structure`,
never a baseline, and the load average at start goes into the frontmatter so
the claim can be checked later.

## What this contributes to the theme

The project asks what a service boundary costs and how much comes back without
changing language. Case C prices one specific answer to "how much comes back":
making the receiver's own work several times cheaper. If the prediction holds,
that recovery is real at the median and nearly absent at the tail once the far
side is contended — which is an argument for spending the afternoon on the
scheduling shape before spending it on the kernel.
