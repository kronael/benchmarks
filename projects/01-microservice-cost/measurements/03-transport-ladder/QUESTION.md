# What does a crossing cost across three realistic stacks?

## The axis

**The stack a crossing goes through.** Nothing else varies.

Pinned across every row: the service fragment is one IEEE CRC-32 over the
payload; the payload is the same 64 payloads from one splitmix64 stream; the
application messages are the same 8+N bytes out and 12 bytes back; arrivals are
closed-loop with exactly one request outstanding; the client and the server get
one core each on the same host in the same session; Nagle is off on every TCP
row; and the timed loop is one function, `Drive` in Go and `drive` in Python,
which every row calls.

The stack confounds language with transport on purpose, because that is how the
choice arrives — nobody picks Python and then writes a custom UDP transport.
Rung C is the control that splits it: Go over the same stdlib HTTP as rung 1a,
configured identically, so rung 1a against rung C is the language and rung C
against rungs 2 and 3 is the wire.

| rung | row | transport | worst case | medium effort |
|---|---|---|---|---|
| 1a | py-http | CPython stdlib HTTP/1.1 | `protocol_version` left at HTTP/1.0, a fresh connection per crossing | HTTP/1.1 and one persistent connection |
| 1b | py-ws | `websockets` sync API | `compression="deflate"`, the library default | `compression=None` |
| 2 | go-grpc | grpc-go | one unary RPC per crossing, stock client | one bidirectional stream, tuned windows and buffers |
| 3 | go-udp | Go `net` UDP | unconnected socket, destination named per send | `DialUDP` connected socket, enlarged socket buffers |
| C | go-http | Go stdlib `net/http` | `DisableKeepAlives`, server closes after each response | keep-alives on, one idle connection held |

Every medium row is the platform's own documented remedy, cited in
`notes/design.md`. None of them is a trick.

## The sweep

Payload bytes: 128, 512, 2048, 8192, 32768. The question the sweep asks is
where per-byte work overtakes the fixed per-crossing cost, and whether the
ranking of the rungs changes when it does.

The range stops at 32768 because 8+32768 must fit in one UDP datagram. The
ceiling is 65507 bytes of UDP data, and above it rung 3 would be measuring
fragmentation rather than a crossing. A row that fails is not a slower row, so
the sweep stops below the cliff and this sentence records where the cliff is.

## The prediction

Written before the first run. The model is the Hockney form, `T(m) = α + β·m`,
with α the fixed cost of one crossing and β the per-byte cost; the crossover
between two rows sits near `Δα / Δβ`.

Estimated α, on this two-core host under its usual load:

| row | α | β |
|---|---|---|
| go-udp medium | 15–25 µs | ~0.5 ns/B |
| go-udp worst | 15–25 µs | ~0.5 ns/B |
| go-http medium | 50–80 µs | ~1 ns/B |
| go-grpc medium | 60–100 µs | ~1.5 ns/B |
| go-grpc worst | 80–120 µs | ~1.5 ns/B |
| py-ws medium | 90–130 µs | ~2 ns/B |
| go-http worst | 150–250 µs | ~1 ns/B |
| py-http medium | 150–200 µs | ~2 ns/B |
| py-ws worst | 100–140 µs | ~10 ns/B |
| py-http worst | 300–450 µs | ~2 ns/B |

1. **Rung 1 worst to rung 3 medium is 15–25x at 128 B, not the 100x the
   folklore suggests.** Most of rung 1's cost is the fresh TCP connection and
   the fresh server thread, not the interpreter.

2. **Nothing flips between the three rungs anywhere in the sweep.** Rung 3 has
   both the smallest α and the smallest β — one copy each way and no framing —
   so no crossover with it exists inside 128 B–32 KiB. The ratio rung 1 : rung 3
   collapses as the payload grows, from 15–25x at 128 B to 4–8x at 32 KiB, but
   the order holds. If that is what the run shows, the absence of a flip is the
   finding and not a failed sweep.

3. **One flip is predicted, and it is inside rung 1: py-http worst against
   py-ws worst, at about 8 KiB.** py-http worst is α-dominated (a connection
   and a thread per crossing) and py-ws worst is β-dominated (deflate over an
   incompressible splitmix64 payload, which buys no bytes and costs CPU both
   ways). py-ws worst is the faster row at 128 B and the slower row at 32 KiB.
   `Δα / Δβ` with the numbers above puts the crossing between 4 KiB and 16 KiB.

4. **At 128 B the rung-to-rung gap is larger than the worst-to-medium gap; at
   32 KiB, inside rung 1b, it is the other way round.** Turning deflate off is
   worth more at 32 KiB than any change of transport, because it is the only
   row where the remedy attacks β rather than α.

5. **go-grpc worst loses to go-http medium at every size**, because a unary RPC
   per crossing pays HTTP/2 framing and a new stream on top of the same socket
   that HTTP/1.1 keep-alive reuses for free. go-grpc medium beats go-http medium
   below about 2 KiB and loses above about 8 KiB.

6. **The recoverable fraction is largest for py-http and smallest for go-udp.**
   Connection reuse should halve py-http. A connected socket and larger buffers
   should be worth under 15% on go-udp, and may be inside the noise: a strict
   ping-pong never queues, so the buffers have nothing to absorb.

7. **Where this prediction could be right for the wrong reason.** If py-ws worst
   never overtakes py-http worst, the likely cause is that zlib's deflate on
   incompressible bytes is cheaper than 10 ns/B, or that the library declines to
   compress small frames — not that the transport ranking is different from the
   claim. That distinction has to be checked against the per-byte slope, not
   against the ordering.

## What would make this measurement worthless

The full case is argued in `notes/design.md`. The three objections that survive
it and are therefore stated as limits rather than answered:

- **`http.server` is not what anyone serves production Python with.** Rung 1a
  prices the CPython stdlib and the client-side connection discipline, not
  Flask or uvicorn. A server-framework row is a different axis.
- **This host is a two-core slice under real load.** The 15-minute load average
  was 3.37 when the variants were written. A run started there is filed
  `status: structure` by the runner, never as a baseline.
- **Rung 3 is Go's `net` UDP, not `rsx-cast`.** The rsx transport is not present
  in this repo and a figure copied from its notes would be a quotation rather
  than a measurement. Raw UDP is the floor rung 3 was meant to establish, and
  it is measured here rather than cited.
