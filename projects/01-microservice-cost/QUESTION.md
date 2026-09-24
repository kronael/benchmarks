# What does a service boundary cost?

The theme. Everything in this project exists to answer it, and a measurement
that does not feed it belongs in another project.

## The benefits are real, and they are not measured here

Splitting a program into services buys deployment independence, team autonomy,
blast-radius control, independent scaling, and the freedom to replace one part
without touching the rest. Those are genuine and often worth the price.

This project does not argue against them and does not measure them. It prices
the other side of the trade, because that side is usually asserted rather than
measured. A cost you have measured is a cost you can decide to pay.

## The main question

Every call that used to be a jump now serialises, copies, queues, traverses a
socket, and schedules on the far side.

**How much does that cost at the worst end and at the medium-effort end, where
does it stop mattering, and how much comes back without changing language?**

## Two axes, and they are kept apart

**The crossing** — how far the call travels, from an inline jump to a socket.

**The effort** — every crossing is measured twice. The **worst case** is what
you get by reaching for the obvious tool and writing the obvious code. The
**medium-effort best case** is what you get from a working afternoon and the
platform's own documented remedies. Not a heroic tuning campaign; the fix a
competent team would actually apply.

The gap between those two rows is the most useful number in the project. It is
the cost that is recoverable, and it is the number that decides whether the
honest answer is "tune it" rather than "rewrite it".

## Group A — the transport ladder

Three realistic stacks, worst case and medium-effort each:

1. **Python to Python over HTTP, and over a WebSocket.** The default reach.
2. **Go to Go over gRPC**, wired the quick way. The common professional answer.
3. **`rsx-cast`.** The floor: 8.80 µs p50 RTT at 128 B, measured at raw UDP,
   with MoldUDP64, SoupBinTCP, KCP and Aeron priced beside it.

**These stacks confound language with transport on purpose**, because that is
how the choice actually arrives — nobody picks Python and then reaches for a
custom UDP transport. To keep the result defensible, one control holds the
language fixed across transports, so the ladder can be split into the part
that is the language and the part that is the wire. Without that control this
group produces a language argument, not an architecture measurement.

## Group B — does structuring computation as channels work?

The next level, and a different question: not what a crossing costs, but
whether composing the work as channels and a module-level graph calculation is
a structure worth having once the cost is known.

Same ladder, same two effort rows: **Python**, then **Go**, then **Rust**. The
comparison is against the same computation written as an ordinary call graph
in the same language, so the axis is the structure and not the runtime.

## The measurements

| # | measurement | what it adds |
|---|---|---|
| 01 | in-process coordination | the floor: the price of talking to yourself |
| 02 | scheduling under load | the cost of being queued behind someone else |
| 03 | transport ladder | Group A: the wire, three stacks, two effort rows |
| 04 | channel composition | Group B: is the structure worth having |

Measurement 01 is the zero of both groups. Every crossing above is reported as
a difference from it.

## The prediction

Write it before the first run, then leave it alone.

- How many multiples separate Python over HTTP from `rsx-cast`?
- Which is larger: the gap between worst and medium-effort in one stack, or
  the gap between two adjacent stacks at the same effort?
- At what payload size does serialisation overtake transport?
- Does the channel structure in Group B cost or save, and does the sign hold
  across all three languages?

## Provenance

`rsx-cast` and `bench/go-vs-rust` come from `github.com/kronael/rsx`, the same
author's exchange. Three rules are adopted from that harness rather than
reinvented: twin implementations prove identical work with a cross-language
checksum gate, arrivals are open-loop so queueing is counted, and the losing
side's own documented fix stays in the results table.
