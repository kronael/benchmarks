# Why case C is worth running, argued against itself first

The strongest case that case C is worthless, written before it ran, and what
the design does about whatever survived.

`design.md` is the inherited reasoning for cases A and B and is not restated
here.

## 1. The result is already published as theory

Delimitrou and Kozyrakis, [Amdahl's Law for Tail Latency][amdahl] (CACM 2018),
show from queueing models that improving a system's queueing behaviour usually
buys more than reducing its service-time tail, and that optimising for a tail
makes Amdahl's Law more consequential than optimising for a mean. Case C's
headline claim — cheaper work per request leaves scheduling a larger share of
what a request waits — is that result. Predicting it is not a contribution.

**Survives, and it fixes what the measurement is for.** The direction is taken
from the published model rather than discovered; what is not published is how
much of a *specific* 4x service-time win survives at p99.9 on the Go runtime
with asynchronous preemption, at what offered load it stops being visible, and
whether Go's own `GOAMD64` remedy closes the gap first. So `QUESTION.md` commits
to magnitudes and to a convergence band, not to the direction. The run can only
be wrong about the part that is not already known.

## 2. The reduce is not real code somebody else wrote

`CLAUDE.md` asks for code collected from the wild. The contention machinery is:
it is case A's driver verbatim, lifted from `bench/go-vs-rust` in
`github.com/kronael/rsx`. The reduce is not. A threshold-weighted sum over a
decoded payload is the shape a receiver actually runs, and it is the shape the
`simd` API is built around — relational operator to mask, `IfElse` to select,
`MulAdd` to accumulate — but it was written here.

**Survives. It is the measurement's weakest point and is recorded as such.** The
mitigation is external: measurement 01 in this project prices the same
scalar-against-vector width question on a third-party kernel (gonum's
`floats.DivTo`) with no contention at all. If case C's uncontended width ratio
disagrees with 01's, the probe is wrong and the tail result is not quotable.

## 3. The scalar row is a strawman

`go env GOAMD64` is `v1` on this box, so the stock scalar row is compiled
SSE2-only, and its select is a data-dependent branch on PRNG-derived data — as
close to unpredictable as a branch gets. Both flatter the vector row.

**Answered.** A scalar row built at `GOAMD64=v3` — Go's own documented remedy —
stays in the table whatever it shows, and each binary reports its own `GOAMD64`
from `debug.ReadBuildInfo()` so a row cannot be mislabelled. `QUESTION.md`
states that the measured gap is width and branch elimination together and does
not quote it as a lanes-per-cycle ratio; the v3 row is the probe that separates
them.

## 4. The vector row is a strawman in the other direction

Published measurements of the Go 1.27 `simd` package report that it still trails
hand-written AVX-512 assembly on long vectors and on horizontal reductions, and
that below one vector's worth of data the fixed setup cost makes it slower
outright ([Gorse][gorse]). Case C ends its reduce in exactly such a horizontal
reduction.

**Survives as a stated limit.** The SIMD row is a floor on what vectorising this
fragment buys, not a ceiling, and the finding must say so. It does not bite hard
here: a window is 8192 elements, so the setup cost amortises over 2048 vectors
and the horizontal reduction runs once per 8192 elements. That is the regime the
same published benchmarks say the package does win in.

## 5. Two cores cannot show an eight-worker scheduling effect

Case A was designed for eight cores. On this box its default `heavy_every` of
1666 puts 175% of capacity on two cores, which is sustained overload, not
scheduling policy — and the `uint32` nanosecond latency field saturates at
4.29 s well before the run ends.

**Survives, and it is why case C sweeps rather than inheriting.** The range in
`sweep.toml` is derived from an offered-load calculation for two cores, not from
rsx's operating points, and it stops at about 125% of capacity. The program
counts clamped samples and reports the count, so saturation is visible in the
record rather than inferred from a suspicious maximum.

## 6. A checksum cannot gate across widths, because float addition is not associative

A lane-partitioned vector sum and a sequential scalar sum normally differ in the
low bits, so there could be no cross-width proof of identical work — and a
comparison of widths without that proof is not a measurement.

**Answered by construction.** Payload elements are `splitmix64` output masked to
20 bits, weights are 1 and 3, and a window is 8192 elements, so every partial
sum is an integer below 2^35. `float64` addition and multiplication over such
values do not round, so all three widths must agree bit for bit — and for the
same reason `GOAMD64=v3` cannot break the gate by contracting `x*w + acc` into
an FMA. Verified both ways: the three widths fold to one checksum, and changing
one row's weight from 3 to 4 makes the run exit non-zero with no table printed.

## 7. Nothing will flip, so there is no finding

`simd` will lead p50 at every point in the sweep and no ordering will reverse.

**Answered by the house rule.** No flip across the whole sweep is a finding
worth one sentence. The quantity case C is for is not a reversal but the load at
which the three rows' tails become indistinguishable within run-to-run spread —
the point past which a 4x cheaper receiver buys nothing a latency budget can
feel.

## What would make the run unquotable

- `simd.Emulated()` true, or `vector_bits` under 256: the program refuses to
  start in the first case and records both in every row.
- `clamped` greater than zero: the latency field saturated and the tail is a
  floor, not a number.
- Throughput spread above 15%: the ordering at that point names the scheduler,
  and saying so is the finding.
- Any run at all on this box, as a baseline. It is a two-core slice of a
  Ryzen 9 5950X carrying other work with an unreadable governor, so every
  result is filed `status: structure`.

[amdahl]: https://people.csail.mit.edu/delimitrou/papers/2018.cacm.amdahlsTail.pdf
[gorse]: https://gorse.io/posts/go-simd-benchmark
