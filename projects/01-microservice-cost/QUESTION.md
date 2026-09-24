# What does a service boundary cost?

The theme. Everything in this project exists to answer it, and a measurement
that does not feed it belongs in another project.

## The main question

A microservices architecture buys deployment independence, team autonomy and
blast-radius control. It pays for them in crossings: every call that used to
be a jump now serialises, copies, queues, traverses a socket, and schedules on
the far side.

**How much does that cost, where does it stop mattering, and how much of it
comes back without changing language?**

The second clause is the one usually skipped. "Rewrite it in Rust" is offered
as the answer to a cost that same-language work often removes for free, so
every measurement here carries a same-language tuned row beside the
cross-language one.

## The series

Each step adds exactly one crossing to the step before it, so the cost of that
crossing is the difference and nothing else.

1. **In-process coordination** — the floor. Inline serial work against a
   channel handoff against a mutex. No boundary yet, only the price of talking
   to yourself.
2. **Cross-task under load** — the same handoff when the scheduler is
   contended, where tail latency rather than throughput decides. This is where
   a runtime's preemption policy starts to show.
3. **Same-host IPC** — a Unix domain socket, and the serialisation the wire
   now demands. The first real boundary.
4. **Loopback RPC** — TCP and a production codec, still one machine, so the
   network is excluded and only the stack is measured.
5. **Same-language speedup** — how much of the accumulated cost each side
   recovers using its own documented remedies, nothing exotic.

## The axes

Two, and they are kept apart. The **crossing** axis is steps 1 to 4. The
**language** axis is Go against Rust at each step. Reporting them mixed is how
a language argument gets made out of an architecture measurement.

## The prediction

Write it before the first run, then leave it alone.

- At what payload size does serialisation dominate the crossing?
- Which step's cost is largest, and is it the one you would have guessed?
- Does the Go/Rust ordering hold across all five steps, or flip somewhere?
- How much of step 4's cost does step 5 give back, per language?

## Provenance

Steps 2 and 5 start from `bench/go-vs-rust` in `github.com/kronael/rsx`, the
same author's exchange. That harness already proves identical work with a
cross-language checksum gate, drives arrivals open-loop so queueing is counted,
and keeps a tuned row for the losing side's official fix. Those three rules
are adopted here rather than reinvented, and the lifted cases are cited where
they are used.
