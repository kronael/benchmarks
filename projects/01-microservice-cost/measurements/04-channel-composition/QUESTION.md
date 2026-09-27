# 04 — is a channel-composed calculation graph worth having?

**Axis:** the composition, and nothing else. One computation, one runtime, one
input, one machine. It is written twice: once as a direct call graph walked in
topological order, once as one goroutine per node wired with channels and a
module-level graph that recomputes on every invalidation. Same kernel, same
graph, same tick stream, same checksum.

The question is not what a channel handoff costs — that is published and is
tens of nanoseconds. It is whether the *structure* pays for itself once the
whole graph is composed out of it, and at what per-node work it starts to.

## The computation

A module-level derived-value graph over a tick stream, which is the shape that
turns up in market data and in any incremental recalculation engine: a tick
arrives, the nodes that depend on it recompute, the graph settles, the next
tick arrives.

- Level 0 is the source: one tick index fans out to `width` seed values.
- Levels 1..`depth`: `width` nodes each, every node joining `fanout` parents
  from the level below as a sliding stencil, `parent(n, j) = (n + j) mod width`.
- Level `depth+1` is the sink: it joins all `width` outputs of the last level
  and folds them into the checksum.
- Every node carries state across ticks, so a tick's value depends on the whole
  history. That is what makes this propagation rather than a pure walk.

At the default shape — `depth 6`, `width 4`, `fanout 2` — the graph is 26 nodes
and the channel composition moves 52 messages per tick.

The node kernel is `work` iterations of an integer EMA step (`s += (x-s)>>5`)
mixed with MMIX's LCG. It is iteration-bounded, never wall-clock-bounded, so a
descheduled node sheds no work, and its result feeds the checksum so it cannot
be optimised away. `work` is the swept parameter.

## The four rows: two structures, both effort rows

| structure | worst case | medium effort |
|---|---|---|
| direct call graph | `direct` — one goroutine, topological walk | `direct-parallel` — per-level parallel-for, `go` + `WaitGroup` |
| channel graph | `channel` — goroutine per node, unbuffered, one tick per message | `channel-batched` — buffered channels, `batch` ticks per message |

The effort rows are not a second axis. This project measures every crossing
twice by construction (see `../../QUESTION.md`), and CLAUDE.md requires the
losing side's own documented remedy to stay in the table. Here each structure
gets its own remedy: the channel graph gets buffering and batching, which is
the documented fix for per-item channel cost; the direct graph gets the only
parallelism its shape allows, which is a parallel-for across each level with a
re-synchronisation at every level boundary, because ticks are serially
dependent through node state and cannot be parallelised across.

## Identical work is proved

Every node folds its parents in fixed index order with an order-sensitive FNV
mix, so a join that arrives out of order changes the checksum instead of
passing quietly. Each composition folds every sink value and every node's final
state into one 64-bit checksum, and `run.py` refuses to print a table when two
compositions or two repetitions disagree.

The fan-in nodes therefore receive from their input channels in fixed index
order rather than with `select`. That is also what forces the send order in the
channel compositions: a producer emits to its consumers in ascending input
index, which is the order that cannot deadlock against consumers reading in the
same order on unbuffered channels.

## Telling queueing apart from work

Channels make the scheduler part of the program, and an unpinned run reports
thread migration as if it were protocol cost. Five separate readings keep the
two halves apart, and they are in every result row:

1. **`direct` at the same `work` is the pure-work reference.** One goroutine,
   no handoff, no parking: its `ns_per_tick` is the work and nothing else. Any
   other row minus that row is the composition's overhead.
2. **`/sched/latencies:seconds` from `runtime/metrics`**, snapshotted before the
   measured pass and differenced after it. This is the runtime's own histogram
   of runnable-to-running delay — queueing measured by something other than my
   own clock. `direct` should sit near zero on it; a channel row that does not
   is queueing, not work.
3. **CPU time against wall time.** `cpu_cores` is utime+stime over wall from
   `/proc/self/stat`. Work is CPU; parking is wall that is not CPU.
4. **The spread of the residence-time distribution.** Work per tick is nearly
   constant, so p50 is work-dominated and p999/max are queueing-dominated.
   Residence time is sampled every `sample_every` ticks, not every tick, so the
   two clock reads cost under 1% even at `work = 1`, where they would otherwise
   be the measurement.
5. **`channel` against `channel-batched`.** Same messages, same values, one
   with a rendezvous per tick and one with a buffer: the difference isolates
   parking from the channel operation itself.

`gomaxprocs` and `goroutines` are printed in every row, so the pinning can be
checked from the result file rather than trusted. Allocation is reported too
(`alloc_mb`, `numgc`), because messages are the other thing channels cost.

Residence time in the batched row includes the wait for a tick's batch to
close. That delay is a real cost of the remedy, so it is counted rather than
subtracted out.

Every measured pass is preceded by a discarded warmup pass over `ticks/8` ticks
that builds and tears down the same goroutines and channels, and the measured
pass starts from fresh node state, so warmup cannot change the checksum.

## The sweep

`work`, the per-node kernel iterations, from 1 to 16384 — see `sweep.toml`. One
iteration is roughly 1.6 ns on this class of core, so the sweep runs a node from
about 5 ns of work to about 26 µs, which brackets the handoff cost from both
sides. Ticks per point fall as work rises so that a repetition stays near a
third of a second at every point.

If the ordering never flips, that is the finding and it gets one sentence.

## Prediction, written before any run

Per-tick times at the default shape, on two pinned cores of this box.

- `work = 1`: `direct` at 150–250 ns/tick. `channel` 75–250× worse than that —
  52 rendezvous per tick at 250 ns to 1 µs each, so 13–50 µs/tick.
  `direct-parallel` also loses badly here, 10–20 µs/tick, because 24 goroutine
  spawns and 6 barriers per tick cost more than the whole graph's work. Both
  remedies are worse than doing nothing at the small end.
- **`channel-batched` overtakes `direct` between `work = 512` and `work = 2048`,
  most likely at 1024.** That is where per-node work (about 1.6 µs) exceeds the
  handoff it has to amortise. Its ceiling is about 1.8×, because two cores.
- **`channel` (unbuffered) never overtakes `direct` anywhere in the sweep.** It
  reaches parity at best, at `work` 4096 or above. Its rendezvous per message
  cannot be amortised by anything.
- **`direct-parallel` overtakes `direct` around `work = 256`–1024 and is the
  fastest row at the top of the sweep**, ahead of `channel-batched`: 24 spawns
  per tick is less traffic than 52 handoffs per tick, and it needs no buffers.
- So the expected answer to the theme is that the channel composition is not
  worth having *for its speed* at this shape on this box: it is 2 orders of
  magnitude behind at small work, and where it finally wins against the naive
  walk, the direct structure's own remedy wins by more.
- On the tail: `/sched/latencies` p99 at or above 10 µs in both channel rows and
  near zero in `direct`; residence p999 at least 5× p50 in the channel rows and
  under 2× in `direct`.

The prediction that matters most is the crossover point, and the reason given
for it — handoff cost against per-node work — is checkable independently of
whether 1024 is the right number.

## Amendment, after the plumbing smoke check

The prediction above was written before any code ran and stays as written. One
of its parameters is wrong, and the correction is recorded here rather than
edited into it.

Proving the RESULT line was populated needed a smoke run: every composition
once, `work = 8`, 2048 ticks, on a box at 15-minute load 3.4. That is a
plumbing check and not a result — one point, far too short, a contended host —
but it is real information and it contradicts the prediction.

Observed ns/tick: `direct` 386, `channel-batched` 510, `direct-parallel` 8450,
`channel` 14024. Observed residence p50: `direct` 400 ns, `channel` 22 µs,
`channel-batched` 456 µs.

- The unbuffered row landed where predicted. 52 rendezvous per tick totalling
  14 µs is 270 ns a handoff, inside the 250 ns-1 µs band the prediction used.
- Batching removes far more of the handoff than the prediction allowed. Batch 32
  turns 52 messages per tick into 1.6 and cuts per-tick cost 27×, to within 1.3×
  of the direct walk at `work = 8`. **The revised crossover for
  `channel-batched` against `direct` is `work` 16 to 64, not 512 to 2048.** The
  superseded figure stays above so the error can be audited instead of believed.
- Both of those rows read about 1.0 cores, so neither is holding the second core
  at the small end. The parallelism the prediction leaned on has to appear
  further up the sweep or the crossover arrives for the wrong reason.
- The batched row's residence p50 is roughly 900× its per-tick cost. A buffer of
  8 batches of 32 across 6 levels is up to 1536 ticks in flight, so its
  residence time is queue depth rather than work. The remedy buys throughput by
  spending latency, and how much of each is the finding this measurement is
  shaped to produce.

## Not in this measurement

**Python and Rust.** `README.md` asks for the same pair at three runtimes so the
*sign* of the answer can be checked across them. Only the Go rung exists. Until
the other two are built, any finding here is a Go finding and must say so.

**SIMD.** Vectorising the kernel would change the cost of a node, which is
exactly what the sweep already varies: every row would slide along the existing
axis and nothing new would be learned, while the identical-work proof would have
to be rebuilt on both sides. If it is worth asking, it is a separate measurement
whose axis is the kernel width with the composition pinned.

**Unpinned.** Pinning is not a row here. If the pinned-against-unpinned gap is
wanted, it is its own axis with the composition held fixed.

## Running

Not run yet. See `README.md` for the command.
