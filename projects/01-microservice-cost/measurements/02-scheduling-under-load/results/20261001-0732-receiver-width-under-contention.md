---
title: receiver-width-under-contention
date: 2026-10-01
status: structure
host: AMD Ryzen 9 5950X 16-Core Processor
cpus: 2
kernel: 6.1.0-43-amd64
governor: unreadable
turbo: unknown
busy_on_pinned_cores_at_start: 100.0%
busy_limit: 10%
pinned_cores: [0, 1]
host_load_at_start: 9.83
host_load_at_end: 62.49 76.53 59.74
toolchains:
  gcc: gcc (Debian 12.2.0-14+deb12u1) 12.2.0
  go: go version go1.27.1 linux/amd64
  java: absent
  node: v22.23.2
  python: Python 3.11.2
  rustc: rustc 1.97.1 (8bab26f4f 2026-07-14)
go_env:
  GOAMD64: v1
  GOEXPERIMENT: simd
  GOTOOLCHAIN: absent
checksums:
  C heavy_every=12500: 7369685be5888d8b
  C heavy_every=2500: 9f975b12b6815708
  C heavy_every=25000: 9f9016c9896e1d94
  C heavy_every=3125: 5fdc496c2563917
  C heavy_every=4166: 5554f908803a220f
  C heavy_every=6250: da9395e7ee20b8eb
sources:
  - variants/go
  - sweep.toml
  - notes/design.md
---

# receiver-width-under-contention

| variant | samples | low | median | high | spread |
|---|---:|---:|---:|---:|---:|
| C scalar v1 @2 bursts/s p99 us | 5 | 83658.406 | 86459.717 | 92518.612 | 8860.206 |
| C scalar v3 @2 bursts/s p99 us | 5 | 80416.422 | 89787.569 | 96136.006 | 15719.584 |
| C simd @2 bursts/s p99 us | 5 | 1171.671 | 1393.114 | 1424.792 | 253.121 |
| C scalar v1 @4 bursts/s p99 us | 5 | 245755.837 | 332393.975 | 457365.077 | 211609.240 |
| C scalar v3 @4 bursts/s p99 us | 5 | 291377.460 | 379253.292 | 419531.820 | 128154.360 |
| C simd @4 bursts/s p99 us | 5 | 39576.586 | 40950.816 | 43070.683 | 3494.097 |
| C scalar v1 @8 bursts/s p99 us | 5 | 1134866.496 | 1271108.243 | 1323190.475 | 188323.979 |
| C scalar v3 @8 bursts/s p99 us | 5 | 1188879.371 | 1372075.140 | 1643513.118 | 454633.747 |
| C simd @8 bursts/s p99 us | 5 | 54609.250 | 56961.475 | 60811.547 | 6202.297 |
| C scalar v1 @12 bursts/s p99 us | 5 | 2880928.509 | 3750122.521 | 4279047.162 | 1398118.653 |
| C scalar v3 @12 bursts/s p99 us | 5 | 3970960.365 | 4086523.645 | 4294967.294 | 324006.929 |
| C simd @12 bursts/s p99 us | 5 | 121262.306 | 127484.646 | 158057.025 | 36794.719 |
| C scalar v1 @16 bursts/s p99 us | 5 | 4294967.294 | 4294967.294 | 4294967.294 | 0.000 |
| C scalar v3 @16 bursts/s p99 us | 5 | 4294967.294 | 4294967.294 | 4294967.294 | 0.000 |
| C simd @16 bursts/s p99 us | 5 | 180555.088 | 191194.089 | 206754.317 | 26199.229 |
| C scalar v1 @20 bursts/s p99 us | 5 | 4294967.294 | 4294967.294 | 4294967.294 | 0.000 |
| C scalar v3 @20 bursts/s p99 us | 5 | 4294967.294 | 4294967.294 | 4294967.294 | 0.000 |
| C simd @20 bursts/s p99 us | 5 | 295812.872 | 344593.583 | 390215.324 | 94402.452 |

Medians over 5 measured repetitions, one warm-up discarded.
p99 is the recorded distribution above; these are the rest.

| case | impl | thr ops/s | p50 | p99 | p99.9 | max | peak RSS | cores used | thr spread |
|---|---|---|---|---|---|---|---|---|---|
| C | scalar v1 @2 bursts/s | 0.05M | 1.11ms | 86.46ms | 126.73ms | 148.76ms | 30MB | 1.65 | 0% |
| C | scalar v3 @2 bursts/s | 0.05M | 1.11ms | 89.79ms | 111.86ms | 151.92ms | 32MB | 1.66 | 0% |
| C | simd @2 bursts/s | 0.05M | 560.4us | 1.39ms | 51.73ms | 60.45ms | 28MB | 0.33 | 0% |
| C | scalar v1 @4 bursts/s | 0.05M | 3.24ms | 332.39ms | 370.39ms | 540.38ms | 53MB | 1.80 | 1% |
| C | scalar v3 @4 bursts/s | 0.05M | 3.42ms | 379.25ms | 419.14ms | 521.39ms | 53MB | 1.80 | 1% |
| C | simd @4 bursts/s | 0.05M | 570.8us | 40.95ms | 62.82ms | 68.27ms | 32MB | 0.51 | 0% |
| C | scalar v1 @8 bursts/s | 0.05M | 174.87ms | 1271.11ms | 1284.51ms | 2100.09ms | 130MB | 1.89 | 1% |
| C | scalar v3 @8 bursts/s | 0.05M | 246.86ms | 1372.08ms | 1389.55ms | 2598.36ms | 140MB | 1.89 | 3% |
| C | simd @8 bursts/s | 0.05M | 615.9us | 56.96ms | 87.52ms | 139.24ms | 32MB | 0.74 | 0% |
| C | scalar v1 @12 bursts/s | 0.04M | 1904.55ms | 3750.12ms | 3822.65ms | 4294.97ms | 352MB | 1.90 | 2% |
| C | scalar v3 @12 bursts/s | 0.04M | 1476.24ms | 4086.52ms | 4101.14ms | 4294.97ms | 368MB | 1.90 | 4% |
| C | simd @12 bursts/s | 0.05M | 761.2us | 127.48ms | 181.92ms | 251.12ms | 45MB | 1.07 | 0% |
| C | scalar v1 @16 bursts/s | 0.03M | 3186.65ms | 4294.97ms | 4294.97ms | 4294.97ms | 490MB | 1.90 | 3% |
| C | scalar v3 @16 bursts/s | 0.03M | 2893.39ms | 4294.97ms | 4294.97ms | 4294.97ms | 479MB | 1.90 | 1% |
| C | simd @16 bursts/s | 0.05M | 997.9us | 191.19ms | 232.63ms | 385.05ms | 54MB | 1.36 | 0% |
| C | scalar v1 @20 bursts/s | 0.03M | 4151.55ms | 4294.97ms | 4294.97ms | 4294.97ms | 599MB | 1.90 | 1% |
| C | scalar v3 @20 bursts/s | 0.03M | 4013.78ms | 4294.97ms | 4294.97ms | 4294.97ms | 592MB | 1.90 | 1% |
| C | simd @20 bursts/s | 0.05M | 36.88ms | 344.59ms | 398.59ms | 605.71ms | 61MB | 1.61 | 1% |
- C scalar v1 @2 bursts/s: numgc=11.0 gc_pause_total_ms=0.9 gogc=100.0
- C scalar v1 @2 bursts/s: width=scalar goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=25000 clamped=0
- C scalar v3 @2 bursts/s: numgc=11.0 gc_pause_total_ms=0.9 gogc=100.0
- C scalar v3 @2 bursts/s: width=scalar goamd64=v3 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=25000 clamped=0
- C simd @2 bursts/s: numgc=12.0 gc_pause_total_ms=0.7 gogc=100.0
- C simd @2 bursts/s: width=simd goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=25000 clamped=0
- C scalar v1 @4 bursts/s: numgc=11.0 gc_pause_total_ms=1.0 gogc=100.0
- C scalar v1 @4 bursts/s: width=scalar goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=12500 clamped=0
- C scalar v3 @4 bursts/s: numgc=11.0 gc_pause_total_ms=1.2 gogc=100.0
- C scalar v3 @4 bursts/s: width=scalar goamd64=v3 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=12500 clamped=0
- C simd @4 bursts/s: numgc=12.0 gc_pause_total_ms=0.7 gogc=100.0
- C simd @4 bursts/s: width=simd goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=12500 clamped=0
- C scalar v1 @8 bursts/s: numgc=9.0 gc_pause_total_ms=1.0 gogc=100.0
- C scalar v1 @8 bursts/s: width=scalar goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=6250 clamped=0
- C scalar v3 @8 bursts/s: numgc=9.0 gc_pause_total_ms=0.8 gogc=100.0
- C scalar v3 @8 bursts/s: width=scalar goamd64=v3 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=6250 clamped=0
- C simd @8 bursts/s: numgc=13.0 gc_pause_total_ms=0.7 gogc=100.0
- C simd @8 bursts/s: width=simd goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=6250 clamped=0
- C scalar v1 @12 bursts/s: numgc=7.0 gc_pause_total_ms=0.8 gogc=100.0
- C scalar v1 @12 bursts/s: width=scalar goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=4166 clamped=1
- C scalar v3 @12 bursts/s: numgc=7.0 gc_pause_total_ms=0.9 gogc=100.0
- C scalar v3 @12 bursts/s: width=scalar goamd64=v3 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=4166 clamped=2
- C simd @12 bursts/s: numgc=9.0 gc_pause_total_ms=0.8 gogc=100.0
- C simd @12 bursts/s: width=simd goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=4166 clamped=0
- C scalar v1 @16 bursts/s: numgc=7.0 gc_pause_total_ms=0.8 gogc=100.0
- C scalar v1 @16 bursts/s: width=scalar goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=3125 clamped=225999
- C scalar v3 @16 bursts/s: numgc=7.0 gc_pause_total_ms=1.1 gogc=100.0
- C scalar v3 @16 bursts/s: width=scalar goamd64=v3 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=3125 clamped=247769
- C simd @16 bursts/s: numgc=9.0 gc_pause_total_ms=0.9 gogc=100.0
- C simd @16 bursts/s: width=simd goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=3125 clamped=0
- C scalar v1 @20 bursts/s: numgc=6.0 gc_pause_total_ms=0.8 gogc=100.0
- C scalar v1 @20 bursts/s: width=scalar goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=2500 clamped=268934
- C scalar v3 @20 bursts/s: numgc=7.0 gc_pause_total_ms=0.8 gogc=100.0
- C scalar v3 @20 bursts/s: width=scalar goamd64=v3 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=2500 clamped=258400
- C simd @20 bursts/s: numgc=9.0 gc_pause_total_ms=0.9 gogc=100.0
- C simd @20 bursts/s: width=simd goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=2500 clamped=0
