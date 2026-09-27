# Why this pair, and the case against it

The pair is one calculation graph written twice. `direct` walks it in
topological order in one goroutine; `channel` gives every node its own goroutine
and every edge its own channel. Each structure then gets its own documented
remedy, so the table has four rows and no strawman in it. The kernel, the
topology, the input and the checksum are one copy of one file, shared by all
four, which is the only reason the difference can be attributed to the
composition.

## The strongest case that this is worthless

**"It measures Go's channel implementation, not a structural question."** Partly
true and it survives. The answer is per-runtime, which is exactly why
`README.md` asks for the same pair in Python and Rust: the useful result is
whether the *sign* holds across three runtimes. Only the Go rung exists, so
anything written down here is a Go finding and has to say so.

**"Two cores cap the upside at 2×, so the outcome is decided in advance."** Real.
The ceiling is stated up front rather than discovered. What survives the cap is
the crossover: the work per node at which the structure stops costing depends on
handoff cost against per-node work, not on how many cores are available, so the
number is checkable on a wider box by anyone who disagrees with it. The
smoke check already shows both structures holding about one core at small work,
which means the cap is not what decides the small end.

**"Nobody writes a 26-node lockstep dataflow graph out of channels."** They write
the shape — incremental derived-value graphs over a tick stream are what market
data systems, spreadsheet engines and reactive libraries are. What is less
common is the *lockstep*, and this is the objection that survives hardest. See
below.

**"Channel benchmarks are everywhere; this is already done."** The cost of one
channel operation is published and is not in dispute. What is not published is
the composition-level crossover with both sides' own remedies in the same table:
the search turns up per-op ping-pong numbers and pipeline tutorials, not a
priced comparison against the same computation written as calls.

**"The kernel is synthetic."** Partly true. It is two published algorithms, it is
iteration-bounded so identical work can be proved, and its cost is the swept
parameter rather than a fixed number the finding depends on. A synthetic kernel
whose only job is to be a knob is not the failure mode the rule is about; a
synthetic *case* dressed as a real one is, and the case here is a derived-value
graph, which is real.

## The objection that survives: the deterministic join

Every fan-in node receives its parents in fixed index order, and never with
`select`. That is what makes the checksum provable — the fold is order-sensitive
on purpose, so a join out of order fails the gate rather than passing quietly —
and it is a per-tick barrier the channel structure would not otherwise need.
Go's own pipeline pattern does the opposite: a stage there is a group of
goroutines and the documented fan-in explicitly does not preserve order.

So the measurement prices the channel structure **under a correctness constraint
that a real system may not have**. A graph that tolerates out-of-order arrival
can use `select`, drop the barrier, and do better than the rows here. The
finding must be stated as the price of a deterministic recomputation, not as the
price of channels in general. The alternative is worse: dropping the barrier
makes the work unprovable, and an unproved comparison is not a measurement.

## What is published, and what this adds

A public ping-pong benchmark puts an unbuffered channel volley at about 232 ns
and finds a buffered volley no faster; the commonly cited figure for the channel
operation itself is about 70 ns on top of the goroutine park and ready. The
smoke check here reads 270 ns per message on a contended two-core slice, the
same order of magnitude and two to three times higher, which is what a loaded
box with 26 goroutines should look like. Those numbers corroborate the
per-message cost; none of them answers whether the structure built out of it
pays, which is what the four rows are for.

## Provenance

- The channel pipeline shape — a stage per derived value, connected by channels
  — is Go's own documented pattern: Sameer Ajmani, *Go Concurrency Patterns:
  Pipelines and cancellation*, 13 March 2014, <https://go.dev/blog/pipelines>.
  The deterministic join is this measurement's constraint, not the article's.
- The per-message figures above: <https://github.com/tamnd/burrow-bench/pull/23>
  and <https://dev.to/gabrielanhaia/go-channels-arent-free-heres-the-real-cost-56eg>.
  Blog and benchmark-repo quality, cited for magnitude only.
- The kernel's LCG constants are MMIX's (Knuth, *TAOCP* vol. 2). The integer EMA
  step is ordinary fixed-point practice.
- `Splitmix64`, the nearest-rank percentile and the single-RESULT-line protocol
  mirror measurement 02's `benchutil`, which came from
  `github.com/kronael/rsx`. The checksum gate and the loser's-fix rule come from
  the same place.
- Queueing is read from the Go runtime's own `/sched/latencies:seconds`
  histogram, available since Go 1.20, differenced across the measured pass.

## Two things this deliberately does not vary

**The kernel's width.** Vectorising it would move every row along the sweep's own
axis and prove nothing the sweep does not already show, while the identical-work
proof would have to be rebuilt on both sides. If it is worth asking it is its
own measurement, with the composition pinned and the kernel width swept.

**Pinning.** `bench.py` refuses to run unpinned, so there is no unpinned row
here. This container's cpuset is 0-1 host-wide, so pinning cannot reserve a core
from anything — it only forbids a migration the process could not make anyway.
That is why a run above the quiet-load threshold is filed as `structure` and not
as a baseline.
