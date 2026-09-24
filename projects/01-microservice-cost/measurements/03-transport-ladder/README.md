# 02 — the transport ladder

**What a crossing costs across three realistic stacks**, each at worst case and
at medium effort.

| rung | stack | why it is here |
|---|---|---|
| 1 | Python to Python, HTTP then WebSocket | the default reach |
| 2 | Go to Go, gRPC wired the quick way | the common professional answer |
| 3 | `rsx-cast` | the floor: 8.80 µs p50 RTT at 128 B, at raw UDP |

**Axis:** the stack. It confounds language with transport on purpose, because
that is how the choice arrives — nobody picks Python then writes a custom UDP
transport. A control holds one language fixed across transports so the ladder
splits into the part that is the language and the part that is the wire.

**Effort rows:** obvious code, then a working afternoon with the platform's own
documented remedies. The gap between the two rows is the recoverable cost, and
it is the number that decides "tune it" against "rewrite it".

**Sweep:** payload size, to find where serialisation overtakes transport.

## Drawn from rsx

`rsx-cast` supplies rung 3 and its comparison set — MoldUDP64, SoupBinTCP, KCP,
Aeron, raw UDP — already measured on one harness. Provenance is marked as rsx
marks it: `[our]`, `[lib]`, `[reimpl]`.

## Prediction

How many multiples separate rung 1 from rung 3? Is the worst-to-medium gap
inside one rung larger than the gap between two adjacent rungs?

## Running

```sh
make prepare   # toolchains and the cast crate
make bench
```

## Results

Dated files under `results/`. Not run yet.
