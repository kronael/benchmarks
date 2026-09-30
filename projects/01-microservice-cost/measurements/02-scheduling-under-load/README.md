# 02 — scheduling under load

**When the far side is contended, who pays?** A crossing is cheap until the
receiving side is busy. This measures the cost of being queued behind someone
else's work, which is the cost a latency budget actually feels.

**Axes:** three. Case A varies the runtime's preemption policy, Go against Rust.
Case B varies the memory reclamation policy. Case C varies the width of the
receiver's own work under a pinned contention source. `QUESTION.md` states case
C's axis and its prediction; `notes/design.md` is the inherited reasoning for A
and B, and `notes/simd-axis.md` is the case against C.

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

**Case C — does a cheaper receiver help once the far side is contended?** Case
A's driver verbatim, with the light request's work replaced by something a
vector unit can do: a threshold-weighted reduction over a payload window, run
once scalar and once through Go 1.27's `simd` package. The contention source is
pinned and scalar in every row, so only the receiver's work width moves. Three
rows — stock scalar, scalar at `GOAMD64=v3`, and vector — and the swept
parameter is the contention level. Go only: case C has no Rust twin, and its
checksum gates widths rather than languages.

**The finding that matters** is not which language won. It is that the
crossover is a load threshold — the probability that concurrent bursts reach
the worker count — and not a language property. Below it work stealing rescues
tokio; above it the light requests stall.

## Fairness rules, kept

- Every spin is iteration-bounded, never wall-clock-bounded, so a preempted
  goroutine cannot silently shed work.
- Each spin's fold feeds a checksum over every row sharing a workload. `run.py`
  refuses to report when they differ, so identical work is proved. Case C's
  payload values are exact integers, which is what makes one checksum able to
  gate a scalar and a vector reduction at all.
- Every side gets a tuned row using its own documented fix: `block_in_place` for
  tokio, `GOGC` for Go in case B, `GOAMD64=v3` for the scalar row in case C. A
  table without the loser's remedy is a strawman.
- Case C's rows report `vector_bits`, `lanes`, `emulated` and their own
  `GOAMD64`, so a row cannot claim a regime it did not run in. The program
  refuses to start as the vector row if `simd` is emulated.

## Running

```sh
make prepare       # go mod download, cargo fetch
make build lint test
```

Then wait for the box to be quiet — check the 15-minute load average first — and
take the cores:

```sh
make bench
```

`make bench` runs `--cases C --no-build` and writes the result file itself
through the repo's `bench.py`, with the machine fingerprint and the starting
load in it. It compiles nothing because the pinned run is started under `sudo`,
where the pinned toolchain cannot resolve from root's HOME and `go` silently
falls back to the system go1.19.8; `make build` has already filled `bin/`.

`CLAUDE.md` prescribes `taskset -c 2,3`. That fails on this box:
`/sys/devices/system/cpu/possible` is `0-1`, so CPUs 2 and 3 do not exist and
there is nothing to isolate from. Pinning still holds a thread on one core, which
is the part that moved rsx's numbers, but it reserves nothing — another reason
every result here is `status: structure`.

Cases A, B, P1 and P2 now have their Rust twins, and every case gates
cross-language: A folds `e9d272bd58d6e9a5` across Go, Rust and Rust with
`block_in_place`; B folds `e8b7b9a2853cabc5` across Go, Go at `GOGC=1000` and
Rust; P1 and P2 fold `989680` and `bb212550014be0f0`. `make bench` still runs
case C only, because case A's inherited operating points ask for more cores than
this box has (`BUGS.md`).

## Results

Dated files under `results/`. Numbers quoted here cite the file they came from.

Two runs of case C, both `structure`, taken with the pinned cores 24.5% and
81.7% busy. Each of the six workloads gated across fifteen runs on one checksum,
in both. The two low contention levels reproduce to within 0.1x and the
cores-used column to within 0.04.

`FINDING.md` has the capacity knee and says why the top half of the sweep is not
quotable: the latency field saturates, and the clamp count itself moves with the
load.

## Provenance

Lifted from `bench/go-vs-rust` in `github.com/kronael/rsx`, same author.
`notes/design.md` is that harness's own reasoning, including why the folklore
cases were rejected. The three fairness rules above are its rules, adopted
repository-wide in `CLAUDE.md` rather than restated per measurement.
