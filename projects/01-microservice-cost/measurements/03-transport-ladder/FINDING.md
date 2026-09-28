# Finding — the language costs more than the wire, and tuning costs more than either

`status: structure` (`results/20260928-transport-ladder-rtt-us.md`). The host's
15-minute load average read 48.91 at the start while the pinned cores were only
26.4% busy, so the two gates disagree completely about this run. The load average
is the host's and counts CPUs this cpuset cannot use; `BUGS.md` carries the
proposal to gate on the pinned cores instead. **One run**, three measured
repetitions per cell plus a discarded warm-up.

All ten rows fold **one checksum per payload size**, across two languages and
four transports. Identical work is proved rather than assumed.

## The ladder, p50 µs, worst / medium effort

| row | 128 B | 512 B | 2 KiB | 8 KiB | 32 KiB |
|---|---|---|---|---|---|
| py-http | 316.6 / 180.0 | 312.5 / 172.2 | 314.5 / 183.7 | 327.2 / 189.7 | 334.1 / 199.2 |
| py-ws | 119.1 / 102.1 | 123.7 / 96.8 | 155.7 / 98.2 | 331.5 / 101.0 | 991.9 / 124.5 |
| go-grpc | 89.7 / 59.6 | 94.8 / 61.3 | 88.9 / 58.8 | 96.8 / 63.5 | 244.7 / 202.3 |
| go-udp | 38.1 / 36.5 | 41.4 / 38.4 | 38.7 / 38.0 | 40.1 / 40.6 | 49.9 / 48.4 |
| go-http (control) | 165.5 / 68.3 | 167.7 / 69.5 | 164.9 / 73.1 | 169.4 / 81.3 | 193.6 / 96.3 |

**The whole ladder spans 8.67x**, from Python over HTTP written the obvious way
to `go-udp` tuned, at 128 B. That is not the two orders of magnitude the choice
is usually argued with.

## The control splits the ladder, and the language is the larger half

`go-http` exists to hold the language fixed across transports and the transport
fixed across languages. At 128 B and medium effort:

- Same transport, Python to Go — `py-http` against `go-http`: **2.64x**.
- Same language, HTTP to UDP — `go-http` against `go-udp`: **1.87x**.

**Changing language is worth more than changing transport.** Without this row
the ladder reads as a transport result, and it is mostly a runtime result.

## Tuning one stack is worth as much as moving a rung

This is the project's own question — which gap is larger, worst-to-medium inside
one stack, or stack-to-stack at the same effort — and the answer at 128 B is that
they are the same size.

| worst to medium, same stack | | adjacent stacks, medium |  |
|---|---:|---|---:|
| go-http | **2.42x** | py-ws to py-http | 1.76x |
| py-http | 1.76x | go-udp to go-grpc | 1.63x |
| go-grpc | 1.51x | go-http to py-ws | 1.50x |
| py-ws | 1.17x | go-grpc to go-http | 1.15x |
| go-udp | 1.04x | | |

**The largest single lever in the table is not a transport at all.** Enabling
keep-alives in Go's standard-library HTTP server and client is worth 2.42x, more
than any one step of the ladder. `go-udp`'s remedy is worth 4%, inside the noise,
because a strict ping-pong never queues and the buffers have nothing to absorb.

## Where the ordering flips

**At medium effort, `go-grpc` flips from second-fastest to last between 8 KiB
and 32 KiB** — 63.5 µs at 8 KiB, 202.3 µs at 32 KiB, behind even `py-http` at
199.2. Its per-byte cost is the worst of the medium rows: 3.2x over the last
4x of payload, against 1.19x for `go-udp`.

**At worst effort, `py-ws` flips from third to last between 2 KiB and 8 KiB** —
155.7 µs at 2 KiB, 331.5 µs at 8 KiB against `py-http`'s 327.2, and 991.9 µs at
32 KiB. The mechanism is deflate over an incompressible splitmix64 payload,
which buys no bytes and costs CPU on both sides. Turning it off is worth 7.97x
at 32 KiB, and that is the one place a remedy attacks the per-byte slope rather
than the fixed cost.

`go-udp` never flips with anything. It has the smallest fixed cost and the
smallest per-byte cost, 36.5 µs to 48.4 µs across a 256x payload range.

## Prediction, written before the run

Seven predictions in `QUESTION.md`, built on a Hockney `T(m) = α + β·m` model.

**Held, including the mechanism.** Prediction 3 put a flip inside rung 1 —
`py-ws` worst against `py-http` worst — "at about 8 KiB", from `Δα/Δβ`, because
deflate on incompressible bytes is β-dominated. The rows cross between 2 KiB and
8 KiB and are within 1.3% of each other at 8 KiB. Prediction 5 said `go-grpc`
worst loses to `go-http` medium at every size, and that `go-grpc` medium "loses
above about 8 KiB". Both hold at all five payloads. The model earned those.

**Wrong.** Prediction 1 put rung 1 worst against rung 3 medium at 15-25x at
128 B; it is 8.67x, so the fixed cost of the Python stack is smaller than the
model allowed. Prediction 2 said nothing flips between rungs anywhere in the
sweep — `go-grpc` medium falls behind `py-http` medium at 32 KiB, which is a
rung-to-rung flip. Prediction 6 said the recoverable fraction is largest for
`py-http`; it is largest for `go-http`, at 2.42x against 1.76x.

**Half right.** Prediction 4 said the rung-to-rung gap beats the worst-to-medium
gap at 128 B, and the reverse inside rung 1b at 32 KiB. The second half holds
(7.97x from one remedy). The first half does not: `go-http`'s 2.42x already
exceeds every rung-to-rung gap at 128 B.

The α/β model predicted the two crossovers and their causes correctly and got
the absolute fixed costs too high. That is the better half to be right about.

## What this gives the theme

Group A asked what the crossing costs at the worst end and at the medium-effort
end, and how much comes back without changing language. The answers:

- The worst end to the best end is **8.67x**, not 100x.
- **2.42x of that comes back without changing language or transport**, from the
  documented remedy on the stack you already have.
- The remaining gap splits 2.64x language against 1.87x transport, so a rewrite
  in another runtime buys more than a change of wire.
- A crossing of 36.5 µs at best is still about 36,000 scalar divides from
  measurement 01, so the boundary is expensive in work terms however it is
  built.

Unmeasured: `rsx-cast` at 8.80 µs, the floor this ladder was meant to reach, and
MoldUDP64, SoupBinTCP, KCP and Aeron beside it. Rung 3 here is plain UDP.
