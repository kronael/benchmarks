# Why this ladder, and the case that it is worthless

## The strongest case against it

**"You measured Python against Go and called it transport."** True of rungs 1
to 3 taken alone, and the reason rung C exists. Rung C is Go on the same stdlib
HTTP as rung 1a with the same two configurations, so rung 1a ÷ rung C is the
language at fixed wire and rung C ÷ rungs 2 and 3 is the wire at fixed language.
What the ladder still cannot do is put Python on UDP, which would complete the
2×2; that row is left out because the README asks for one control, and the
decomposition above is enough to answer the objection.

**"Nobody serves Python HTTP with `http.server`."** This one survives. CPython's
own docs say `http.server` "is not recommended for production. It only
implements basic security checks"
(https://docs.python.org/3/library/http.server.html). Rung 1a therefore prices
the stdlib and the client-side connection discipline, and the honest reading of
the worst row is "what the obvious code costs", not "what Python costs". An
`http.server` versus uvicorn row would vary the server framework, which is a
second axis, so it is named as future work rather than folded in here. The
client half generalises further than the server half: a bare `requests.post`
call with no `Session` opens a fresh connection exactly as the worst row does,
and that is extremely common code.

**"Somebody already did this."** Not this combination. `grpc_bench`
(https://github.com/LesnyRumcajs/grpc_bench) compares gRPC across languages but
has no plain HTTP, no WebSocket and no raw-UDP leg and no payload sweep;
gRPC's own dashboards (https://grpc.io/docs/guides/benchmarking/) compare gRPC
scenarios against each other, not against raw sockets; matheusd's Go RPC
benchmarks (https://matheusd.com/post/go-rpc-benchmarks/) are Go-only. No
published figure was found for the payload size at which per-byte work overtakes
the fixed crossing cost on Linux loopback, so that part of the sweep is new
ground rather than a confirmation.

**"A closed-loop ping-pong is the easy case."** Deliberately. Queueing is
measurement 02's axis. One request outstanding means no row can hide latency
behind a queue, and it is also the shape in which rung 3's reference figure was
taken.

**"Random payloads make deflate look bad."** They do, and that is the point of
keeping the row. The library's own compression page says the bandwidth saving
"is usually worth the additional memory and CPU cost"
(https://websockets.readthedocs.io/en/stable/topics/compression.html) — which is
a claim about compressible traffic. A binary payload is the case where the
default is pure cost, and it is the case the docs answer with `compression=None`.
The result is a fact about incompressible payloads, and the file says so rather
than generalising it to JSON.

## What is pinned, and why each one had to be

- **The service fragment.** IEEE CRC-32 over the payload, so `zlib.crc32` and
  `hash/crc32.ChecksumIEEE` compute the same number over the same bytes. That is
  what lets one checksum span two languages and four transports.
- **The payload.** One splitmix64 stream, identical constants on both sides,
  seeded from the slot and the size. Verified: the 64-payload fold is
  byte-identical in Go and Python at every swept size.
- **The timed loop.** `benchwire.Drive` and `benchwire.drive` own the sampling,
  the warmup cut and the fold. A row can only differ in its `Exchange`, so two
  rows cannot differ because one of them measured differently.
- **Nagle, off everywhere.** This one is not cosmetic. `http.client` sets
  `TCP_NODELAY` itself (CPython `Lib/http/client.py`, from bpo-23302) but
  `socketserver.StreamRequestHandler` leaves `disable_nagle_algorithm = False`,
  so an accepted `http.server` socket keeps Nagle on; Go's `net` package
  disables it on both ends by default (`go.dev/src/net/tcpsockopt_posix.go`).
  Left alone, rung 1a against rung C would have measured a kernel default and
  been reported as a language difference.
- **One core each for client and server.** Two processes on one core measure the
  context switch between them. `bench.py` refuses to run unpinned at all, and
  `run.py` refuses if `taskset` is missing rather than falling back.
- **The payload ceiling.** 32768, because 8+32768 has to fit in one UDP
  datagram. The maximum is 65507 bytes of UDP data: RFC 791's 16-bit total
  length, less a 20-byte IPv4 header, less RFC 768's 8-byte UDP header. Linux
  loopback MTU is 65536, so the ceiling is the IP length field and not the
  interface.

## The documented remedy behind every medium row

Each one is the platform's own advice, so the losing side's fix is in the table
rather than left out.

- **py-http.** `protocol_version = "HTTP/1.1"`. CPython: "If set to
  `'HTTP/1.1'`, the server will permit HTTP persistent connections; however,
  your server must then include an accurate `Content-Length` header ... For
  backwards compatibility, the setting defaults to `'HTTP/1.0'`"
  (https://docs.python.org/3/library/http.server.html). Both rows send
  `Content-Length`, so the handler body does not change with the row.
- **py-ws.** `compression=None`
  (https://websockets.readthedocs.io/en/stable/topics/compression.html).
- **go-grpc.** A bidirectional stream instead of a unary call per message:
  "Use streaming RPCs when handling a long-lived logical flow of data"
  (https://grpc.io/docs/guides/performance/). Plus
  `WithInitialWindowSize`/`WithInitialConnWindowSize` at 1 MiB, above the 64 KiB
  floor the option documents, and `WithReadBufferSize`/`WithWriteBufferSize` at
  64 KiB, above the documented 32 KiB default
  (https://github.com/grpc/grpc-go/blob/master/dialoptions.go). The server gets
  the matching `grpc.InitialWindowSize`, `grpc.ReadBufferSize` and
  `grpc.WriteBufferSize`.
- **go-udp.** `DialUDP` instead of an unconnected socket, so the destination is
  resolved once by `connect(2)` rather than per datagram, plus `SetReadBuffer`
  and `SetWriteBuffer` at 1 MiB (`SO_RCVBUF`/`SO_SNDBUF`). The kernel doubles
  the request for bookkeeping and clamps it at `net.core.rmem_max`
  (https://man7.org/linux/man-pages/man7/socket.7.html), so the row is "asked
  for a megabyte", not "got a megabyte".
- **go-http.** Keep-alives on with one idle connection retained, the mirror of
  py-http's remedy.

## Rung 3 is raw UDP, measured, not `rsx-cast`, quoted

The README's rung 3 was written around `rsx-cast` and its 8.80 µs p50 RTT at
128 B. That transport is not in this repo and is not on this host, so the choice
was between quoting the figure and measuring the thing it is a figure for. Raw
UDP over loopback is the floor `rsx-cast` sits on, so rung 3 measures that
floor with Go's `net` package and the rsx number stays out of the results table.
The comparison set the README mentions — MoldUDP64, SoupBinTCP, KCP, Aeron — is
likewise not reproduced, because none of it is here to run.

## Regenerating the protobuf code

The generated files in `variants/go/ladderpb/` are committed, so building this
measurement needs no protoc. To regenerate, with `protoc` on the path and the
two plugins installed:

```sh
go install google.golang.org/protobuf/cmd/protoc-gen-go@v1.36.11
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@v1.6.0
cd variants/go/ladderpb && protoc --proto_path=. \
  --go_out=. --go_opt=paths=source_relative \
  --go-grpc_out=. --go-grpc_opt=paths=source_relative ladder.proto
```

Generated with protoc 33.1, protoc-gen-go 1.36.11, protoc-gen-go-grpc 1.6.0.

## Prior art the numbers should be read against

- lmbench's `lat_udp` quotes 650 µs for UDP latency on localhost
  (https://lmbench.sourceforge.net/man/lat_udp.8.html). That is a figure from a
  much older machine and scheduler; it is listed because it is the only
  published loopback UDP RTT found, not because it is a target.
- gRPC's mobile benchmarks report gRPC 5–10x faster than HTTP/JSON up to the
  95th percentile, and note streaming calls were "over 2x faster than the unary
  calls" in that harness (https://grpc.io/blog/mobile-benchmarks/). That is the
  published basis for expecting go-grpc medium to beat go-grpc worst by more
  than the tuning options alone would give.
- Barroso et al., "Attack of the Killer Microseconds"
  (https://cacm.acm.org/research/attack-of-the-killer-microseconds/), is the
  standard citation for why microsecond-scale fixed costs dominate this regime
  and are easy to under-measure.
- No published p50/p99 figure was found for CPython `http.server` with and
  without keep-alive, for `websockets` with and without permessage-deflate, or
  for grpc-go unary against streaming on loopback at a stated payload size.
  Those four are the gaps this measurement fills.
