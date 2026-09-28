# 03 — the transport ladder

**What a crossing costs across three realistic stacks**, each at worst case and
at medium effort.

| rung | stack | why it is here |
|---|---|---|
| 1 | Python to Python, HTTP then WebSocket | the default reach |
| 2 | Go to Go, gRPC wired the quick way | the common professional answer |
| 3 | Go to Go, raw UDP | the floor: no framing, one copy each way |

**Axis:** the stack. It confounds language with transport on purpose, because
that is how the choice arrives — nobody picks Python then writes a custom UDP
transport. A control holds Go fixed across transports, and holds stdlib HTTP
fixed across the two languages, so the ladder splits into the part that is the
language and the part that is the wire.

**Effort rows:** obvious code, then a working afternoon with the platform's own
documented remedies. The gap between the two rows is the recoverable cost, and
it is the number that decides "tune it" against "rewrite it". Every remedy is
cited in `notes/design.md`.

**Sweep:** payload size, 128 B to 32 KiB, to find where per-byte work overtakes
the fixed cost of a crossing. It stops at 32 KiB because 8+32768 has to fit in
one UDP datagram.

**Same work, proved:** every row computes one IEEE CRC-32 over the same payload
and folds the answer into a checksum. The runner refuses to report unless all
ten rows agree on it at every payload size — one gate across two languages and
four transports.

## What this does not take from rsx

Rung 3 was drawn up around `rsx-cast` and its 8.80 µs p50 RTT at 128 B. That
transport is not in this repo, so rung 3 measures the raw-UDP floor it sits on
rather than quoting a number from somewhere else. The rsx comparison set —
MoldUDP64, SoupBinTCP, KCP, Aeron — is not reproduced here for the same reason.
What is adopted from rsx is method, not figures: core pinning, payload
alignment, the checksum gate and the loser's-fix rule.

## Running

```sh
make -C ../../../.. build   # dist/fingerprint, which every result carries
make prepare                # go mod download, and a venv with websockets
make build
sudo chrt -f 80 taskset -c 0,1 make bench
```

`make bench` compiles nothing, on purpose: under `sudo` the pinned toolchain
cannot resolve from root's HOME and `go` silently falls back to the system
go1.19.8. It writes the machine fingerprint and the starting load into the
result file through the repo's `bench.py`, which is the only place a result
file comes from.

## Results

Dated files under `results/`. The question and the prediction are in
`QUESTION.md`, the reasoning in `notes/design.md`.

`20260928-transport-ladder-rtt-us.md` — `structure`, one run. All ten rows fold
one checksum per payload size across two languages and four transports.
`FINDING.md` has the two crossovers and the language-against-wire split.
