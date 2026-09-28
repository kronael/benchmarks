# Finding — the channel structure buys cores, never cheaper work

`status: verified` (`results/20260928-channel-composition.md`, 15-minute load
1.26, pinned cores 31.5% busy at the start). A second run under contention
(`20260927`, load 2.67) is kept beside it: the two agree on the winner at all
eight sweep points and on every per-core ratio to within 0.10, so the ordering
below is stable and quotable. 28 runs per sweep point fold one checksum, and the
checksums match across the two runs.

## The ordering, and the one number that reverses it

Median ns per tick, then the same figure multiplied by the cores the row actually
used. The graph is 26 nodes, depth 6, width 4, fanout 2.

| work | direct | direct-parallel | channel | channel-batched |
|---:|---:|---:|---:|---:|
| 1 | 231 / **231** | 7949 / 14308 | 6818 / 13636 | **124** / 248 |
| 16 | 515 / **515** | 8579 / 15442 | 7118 / 14236 | **285** / 569 |
| 256 | 6474 / **6474** | 18843 / 33918 | 11799 / 23598 | **3485** / 6971 |
| 1024 | 25023 / **25023** | 47022 / 84640 | 20210 / 40421 | **12860** / 25721 |
| 4096 | 100969 / **100969** | 92660 / 166788 | 64343 / 128686 | **51057** / 102114 |
| 16384 | 402096 / 402096 | 256867 / 488047 | 237098 / 474197 | **211303** / **422606** |

**In wall-clock time `channel-batched` wins at every point in the sweep, by
1.81x to 1.98x, and nothing ever overtakes it.** There is no flip on this axis.

**Per core it never wins at all.** Against `direct` it measures 0.95x to 1.11x
across the whole sweep over both runs, and the two runs never differ by more than
0.10 at a point — the same work for the same CPU, inside the noise everywhere. The entire wall-clock win is the second core, and the
ceiling of 1.9x is what two cores allow. `direct` uses 1.0 cores and every other
row uses 1.8 to 2.0.

So the answer to this measurement's axis is that composing the work as channels
does not make the computation cheaper. It makes the computation *parallel*, and
it is an efficient way to spend a second core — 5% overhead against a
single-threaded walk — where the obvious alternative is not.

## Where the orderings flip

- **`channel-batched` against `direct`, wall clock: no flip.** It leads from one
  kernel iteration per node upward. Per core: no flip either, because the two
  are level everywhere.
- **`channel` against `direct`, wall clock: flips between work 256 and 1024.**
  At 256 the plain channel row is 1.82x slower; at 1024 it is 1.24x faster. Both
  runs place the flip in the same interval. That is where per-node work — about
  1.6 µs at work 1024 — exceeds the 52 unbuffered rendezvous per tick it has to
  cover.
- **`channel` against `direct`, per core: never flips.** It converges from 59x
  worse at work 1 to 1.18x worse at work 16384 and stops there. An unbuffered
  rendezvous per message cannot be amortised by making the message do more work;
  it can only be made a smaller fraction of it.
- **`direct-parallel` against `direct`: flips between work 1024 and 4096** in
  wall clock, and never per core.

## What each remedy costs

Batching is the channel structure's documented remedy and it is paid for in
residence time, not in CPU. Batch 32 cuts channel traffic from 52 messages per
tick to 1.6, and the tick that enters the graph waits for its batch and its
buffer:

| work | direct p50 | channel-batched p50 | cost |
|---:|---:|---:|---:|
| 1 | 260 ns | 121 µs | 466x |
| 16384 | 385 µs | 90.8 ms | 236x |

`direct-parallel` is the direct structure's own documented remedy and its cost is
visible in one column: at work 1 it spawns **1,572,864 goroutines** and allocates
**264 MB** in a pass, against 25 goroutines and 0.1 MB for either channel row.
Twenty-four spawns per tick is more traffic than 52 handoffs per tick, and the
prediction had it the other way round.

## The tail is tighter in the channel rows, not wider

Residence p99.9 divided by p50, at work 1: `direct` 20.2x, `direct-parallel`
8.2x, `channel` 2.1x, `channel-batched` 1.6x. The runtime's own
runnable-to-running p99 is 0 ns in `direct` and 3.6 µs in `channel`.

The direct walk has the best p50 by two orders of magnitude and the worst
relative tail, because a 260 ns p50 turns any interruption into a 20x outlier.
The channel rows are already dominated by queueing, so an interruption is lost
inside it. A latency budget written against a p99.9 will prefer the structure
with the slower median.

## Prediction, written before any run

`QUESTION.md` holds a prediction and an amendment made after a plumbing smoke
check. Both are wrong about the crossover and the amendment is wrong in the same
direction as the original.

**Wrong.** The crossover for `channel-batched` was predicted "between work = 512
and 2048, most likely at 1024", then amended to "work 16 to 64". There is no
crossover: the batched row leads from work 1. `channel` was predicted to "never
overtake `direct` anywhere in the sweep" — it overtakes at work 1024 in wall
clock. `direct-parallel` was predicted to be "the fastest row at the top of the
sweep, ahead of `channel-batched`" on the grounds that 24 spawns beat 52
handoffs; it is the slowest of the three remedies at the top, and the goroutine
count says why.

**Wrong, and reversed.** The tail was predicted as "residence p999 at least 5x
p50 in the channel rows and under 2x in `direct`". Measured: 1.6-2.1x in the
channel rows and 20.2x in `direct`. The prediction had the right idea that the
channel rows queue and got the consequence backwards.

**Right.** The ceiling was predicted at "about 1.8x, because two cores", and it
is 1.81-1.98x. `direct` at work 1 was predicted at 150-250 ns/tick and measured
231. The stated conclusion — "the channel composition is not worth having *for
its speed*" — holds per core, though not for the reason given: it is not that
the direct structure's own remedy wins by more, because it does not.

The prediction said the crossover point was the thing that mattered. The
measurement says the axis that matters is whether you normalise by CPU, because
that is what turns a 1.9x win into a tie.

## What this gives the theme

Group B asked whether structuring computation as channels is worth having once
the cost of a crossing is known. On this shape and this box the answer is that
the structure is not a performance technique. It is a way to use cores you
already have, at about 5% overhead over a single-threaded walk once batched, and
it costs 236x to 466x in residence latency to get there.

That matters for the project's main question because it removes an argument for
the service boundary. If channels inside one process do not make the work
cheaper — only more parallel — then neither does moving the same graph across a
socket, and the crossing's cost is added to an unchanged amount of work rather
than traded against a saving.

Unmeasured: the same comparison in Python and in Rust. `QUESTION.md`'s theme asks
whether the sign holds across three languages, and one language cannot answer it.
