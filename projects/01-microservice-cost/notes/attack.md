# The strongest case that this project is worthless

Written before publishing, against the project's own results. Each measurement
carries its own version of this for its own axis; this one attacks the theme.
What survives is answered in the project `FINDING.md` or conceded here.

## 1. "It measures an echo, not a service boundary." — SURVIVES

This is the strongest attack and it is correct.

Measurement 03 is a strict ping-pong: one request in flight, a payload of
`splitmix64` bytes, no marshalling of a real object, no TLS, no service
discovery, no connection-pool contention, no retries, no concurrent clients. A
real service boundary has all of those, and several of them cost more than the
socket does.

**Conceded, and the project's language has to change.** What these numbers price
is the *floor* of a crossing — the least a boundary can cost once you have
decided to have one. The number is a lower bound, not an estimate. A boundary
built the way people actually build them is somewhere above it, and this project
does not say how far above.

The floor is still worth having, because an argument for a boundary that fails
at its own floor fails everywhere. But a reader who takes 36.5 µs as "what a
microservice call costs" has been misled, and the earlier wording invited that.

## 2. "Every number is from a contended two-core slice." — SURVIVES, partly

True. Only measurement 04 has a run started under the load limit, and its pinned
cores were still 31.5% busy. Everything else is `status: structure`.

The defence is that the findings are orderings and ratios taken inside one run,
that the checksum gate proves identical work across rows, and that the
per-measurement files say which claims survive a second run and which do not —
measurement 01's upper crossover is withheld for exactly this reason.

**The part that survives the defence:** contention does not hit all rows
equally. The slow rows hold more cores (`py-http` and the scalar receiver run at
1.7-1.9 of 2.0; `go-udp` and the simd receiver run well under 1.0), so a
neighbour steals proportionally more from them. **That biases the ladder's 8.67x
spread upward.** On a quiet machine the spread is probably smaller, not larger,
and the project's headline is therefore a ceiling on the ratio as well as a
floor on the cost. This has to be stated, not buried.

## 3. "The ladder confounds language with transport." — ANSWERED

Deliberate, and the reason is in `QUESTION.md`: nobody picks Python and then
writes a custom UDP transport, so the confounded ladder is how the choice
actually arrives. The `go-http` control holds the language fixed across
transports and the transport fixed across languages, and it works: 2.64x for the
runtime, 1.87x for the wire, at 128 B and medium effort.

Without that row this would be a language benchmark wearing an architecture
label. With it, the split is measured rather than asserted.

## 4. "There are a hundred HTTP-versus-gRPC benchmarks already." — ANSWERED

There are, and most of them do not pin cores, do not gate on a checksum, and do
not carry the losing side's documented remedy. This project does not claim a new
fact about gRPC.

What it claims is the *paired* comparison — the same stack twice, once written
the obvious way and once with its own platform's documented fix — reported
beside the stack-to-stack gap. That pairing is the finding, and it is what makes
"tune it" versus "rewrite it" an answerable question instead of a preference.
No claim of novelty is made beyond the method, because none was checked.

## 5. "'Medium effort' is a judgement call." — CONCEDED

It is. Keep-alives, `compression=None`, HTTP/1.1, a connected UDP socket and the
gRPC options are each documented by their own platform, which is the rule the
project set itself. A different engineer with a different afternoon picks a
different set and gets a different number.

The mitigation is that every remedy is named in the variant source and the
effort row is a build flag, not a rewrite, so a reader can disagree with the
choice and see exactly what was chosen. The 2.42x for Go stdlib keep-alives is
reproducible or refutable in one line of code.

## 6. "The headline rests on one payload, one percentile, one run." — SURVIVES

8.67x is 128 B, p50, worst against medium, from a single run of measurement 03.
That is a narrow base for the number the project leads with.

**Fixed by reporting the range rather than the point**, and by a replication. The
spread across the five payload sizes and across two runs belongs in the finding,
not one cell of it.

## 7. "The per-core figure in measurement 04 is a metric you invented." — CONCEDED

`ns_per_tick` multiplied by `cpu_cores` is CPU-nanoseconds per tick, and
`cpu_cores` comes from `getrusage` over the whole measured pass, so it includes
the composition's setup and teardown as well as its steady state. It is a
derived quantity and an approximation.

It is the right one to derive — a wall-clock win bought with a second core is
not the same thing as cheaper work, and no single recorded column says so — but
it should be labelled as derived, which `FINDING.md` now does.

## 8. "rsx-cast, the floor the project was aimed at, is missing." — CONCEDED

Stated in `FINDING.md`. Rung 3 is plain UDP at 36.5 µs; `rsx-cast` at 8.80 µs
and the specialist transports beside it were never measured here. The ladder
does not reach its own intended bottom.

## What changed because of this document

- The project `FINDING.md` says the crossing figures are a **floor**, and names
  what a real boundary adds on top.
- It reports the ladder spread as a range across payloads, not one cell.
- It says contention biases the spread upward, so the ratio is a ceiling.
- The per-core figure is labelled derived.
