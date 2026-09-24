# 02 — scheduling under load

**When the far side is contended, who pays?** A crossing is cheap until the
receiving side is busy. This measures the cost of being queued behind someone
else's work, which is the cost a latency budget actually feels.

**Axis:** the runtime's preemption policy. Go against Rust, twin programs,
byte-identical work.

## The essence

Cooperative schedulers only reschedule at yield points, and pure computation
has none. A tokio worker that enters a long compute loop is gone for its
duration, and every task queued behind it waits. Go took the other branch: its
runtime preempts a goroutine asynchronously, so no cooperation is needed.

**Case A — tail latency under unpredictable CPU bursts.** Open-loop arrivals,
one task per request, a small fraction of requests running a long pure-CPU
chain. Latency is measured against the *intended* arrival tick, so queueing
during a block-out is counted in full and coordinated omission cannot hide it.

**Case B — CPU and allocation throughput and tail.**

**The finding that matters** is not which language won. It is that the
crossover is a load threshold — the probability that concurrent bursts reach
the worker count — and not a language property. Below it work stealing rescues
tokio; above it the light requests stall.

## Fairness rules, kept

- Every spin is iteration-bounded, never wall-clock-bounded, so a preempted
  goroutine cannot silently shed work.
- Each spin's fold feeds a cross-language checksum. `run.py` refuses to report
  when the Go and Rust checksums differ, so identical work is proved.
- Both sides get a tuned row using their own documented fix: `block_in_place`
  for tokio, `GOGC` for Go. A table without the loser's remedy is a strawman.

## Running

```sh
make prepare
make test      # ./run.py --quick, checksums must match
make bench
```

## Results

Dated files under `results/`. Numbers quoted here cite the file they came
from. Not yet run in this repository.

## Provenance

Lifted from `bench/go-vs-rust` in `github.com/kronael/rsx`, same author.
`notes/design.md` is that harness's own reasoning, including why the folklore
cases were rejected. The three fairness rules above are its rules, adopted
repository-wide in `CLAUDE.md` rather than restated per measurement.
