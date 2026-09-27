# Does vectorising the work unit pay, and where does it stop paying?

## The axis

One thing differs: whether the per-item work unit runs scalar or vectorised.
Same kernel, same input bytes, same process, same core, same session. The swept
parameter is the element count of one work unit (`sweep.toml`).

The kernel is gonum's element-wise `float64` divide, `floats.DivTo`:

    for i, v := range s {
        dst[i] = v / t[i]
    }

`Scalar` is that loop unchanged, from gonum's portable implementation
(`internal/asm/f64/stubs_noasm.go`). `Vector` is the same loop with Go 1.27's
`simd` package. gonum ships hand-written amd64 assembly for this same function
(`internal/asm/f64/divto_amd64.s`), which is the evidence that vectorising this
exact loop is work somebody outside this repo chose to do.

Everything else is one shared file, `variants/go/divto/divto.go`: the input, the
timing loop, the checksum fold, the output format. The two binaries cannot
differ anywhere but the kernel, because there is only one copy of the rest.

### Why a map and not a dot product

A reduction reassociates when it is vectorised: four partial sums do not give
the bits one running sum gives, so the two sides would fold different checksums
and the gate would refuse the run for a reason that has nothing to do with the
axis. An element-wise map is bit-identical per element at any lane count. A
multiply-add kernel fails the same test a second way, because a fused `MulAdd`
rounds once where a separate multiply and add round twice. Both operands are
drawn from [1, 2), so every quotient is normal and the divider never sees an
operand whose timing might differ.

## The effort rows

`go env GOAMD64` is `v1` on this box, so the scalar loop is built for SSE2 while
the `simd` package dispatches on the hardware and takes AVX2 regardless. Go's
own documented remedy for that is `GOAMD64=v3`, and it is in the table as its
own row for both sides: `scalar@v1`, `simd@v1`, `scalar@v3`, `simd@v3`. A table
without the v3 rows is a strawman.

## What this contributes to the theme

The project prices a service boundary. This measurement is the floor's
denominator: how much in-process work one call actually carries. A crossing that
costs 10 us is twice as damaging if the work it interrupts can be made twice as
fast, and the size at which vectorising stops paying is also the size at which
the work unit stops being the thing that matters.

## The prediction

Written before any run of this measurement. The first three items are not
predictions — they are disassembly and runtime facts, checked on this box with
this toolchain, and they are what the numeric predictions are reasoned from.

**Checked before the run** (`go tool objdump`, `GOEXPERIMENT=simd`, go1.27.1):

- The scalar loop compiles to scalar `DIVSD` at both `GOAMD64=v1` and `v3`. Go
  1.27 does not auto-vectorise it at either level.
- `Vector` emits 256-bit `VDIVPD` even when built at `GOAMD64=v1`, and reports
  `VectorBitSize()=256`, `Emulated()=false`, 4 `float64` lanes. The `simd`
  package dispatches on the hardware, not on `GOAMD64` ([go.dev][blog]).
- The two kernels fold identical checksums at lengths that exercise the tail.

**Predicted:**

1. Below one full vector the ordering favours scalar. At 1, 2 and 3 elements the
   vector path runs only its masked tail and pays a masked load, a divide and a
   masked store where scalar pays one `DIVSD`. The flip is at 4 elements, or at
   8 if that tail costs more than one scalar iteration.
2. In cache, 8 to ~20k elements, vectorising wins about 2x — not the 4x the lane
   count suggests, because Zen 3's floating-point divider is 128 bits wide and a
   256-bit `VDIVPD` is two passes through it. A measured 4x means that model of
   the divider is wrong. A measured 1.3x means the loop is limited by its loads
   and stores rather than by the divider.
3. The win shrinks once the working set leaves L2 and is inside the spread by 1M
   elements. Three arrays of `float64` is 24 bytes per element: 64 KiB L1d at
   ~2.7k elements, 512 KiB L2 at ~21k, 16 MiB L3 at ~700k. Scalar at ~4.5
   cycles/element already asks for ~21 GB/s, which is near what one core of this
   slice can pull, so the two should meet at the bandwidth limit rather than at
   the divider. Expected wording of the finding: the ordering does not reverse
   at the top end, it ties.
4. The v3 rows move nothing on either side, because the instruction in the loop
   is the same one. Go's documented remedy does not close this gap, which is why
   gonum writes the assembly.
5. At 1024 elements: scalar 1.1-1.3 ns/element, vector 0.55-0.70.
6. Sizes that are not a multiple of 4 (3, 5) cost the vector side an extra
   masked iteration, and its padded lanes divide zero by zero because
   `LoadFloat64sPart` fills with zero. If 5 elements is worse per element than
   8, that is the portable API's tail and not the hardware.

## The strongest case that this measurement is worthless

- **"SIMD is lanes-times faster; this is a textbook exercise."** The lane count
  is not the answer: 4 lanes, and the prediction is 2x. The number worth having
  is where the win disappears, and that is a property of this slice's cache and
  bandwidth rather than of the instruction set.
- **"Somebody already did it better."** [gorse.io][gorse] measured Go 1.27's
  portable `simd` against scalar Go and against generated AVX512 on an
  i7-11370H, with `DivTo` among six kernels, at vector lengths 16 to 128 —
  `float32`, all of it inside L1. That is the prior art for the kernel and this
  measurement claims nothing new about the kernel. What is missing there is the
  sweep past cache, which is where the ordering changes, and the `GOAMD64` row.
- **"Divide is a strawman; nobody divides in a hot loop."** gonum ships assembly
  for exactly this loop. A cheaper op is bandwidth-bound at every size on this
  box, so its flat result would be a fact about bandwidth rather than about
  vectorising. Divide is where the arithmetic can dominate, which is what makes
  a crossover visible at all.
- **"`simd` is an experiment, so this measures a moving target."** It does,
  which is why the toolchain and `GOEXPERIMENT` go into the record, and why the
  emitted instructions are checked per row instead of assumed.
- **"The box is a contended 2-core slice with an unreadable governor."** True.
  The 15-minute load average goes into the frontmatter and a run above the
  threshold in `sweep.toml` is filed `status: structure`, never a baseline.

## Not this axis

- The coordination mechanism — inline call, channel handoff, mutex — is a
  separate axis and does not share this table; varying two things at once
  measures neither. It is still to be built.
- Portable `simd` against `archsimd`, or against gonum's own assembly, is a
  third axis. The published 1.8x gap at length 128 ([gorse.io][gorse]) says it
  deserves its own measurement rather than a row here.
- `GODEBUG=simd=128` narrows the vector at run time and would separate "wider
  vectors" from "vectors at all". Also its own axis.

[blog]: https://go.dev/blog/simd-experiment
[gorse]: https://gorse.io/posts/go-simd-benchmark
