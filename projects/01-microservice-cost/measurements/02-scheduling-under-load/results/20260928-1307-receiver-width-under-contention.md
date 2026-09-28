---
title: receiver-width-under-contention
date: 2026-09-28
status: structure
host: AMD Ryzen 9 5950X 16-Core Processor
cpus: 2
kernel: 6.1.0-43-amd64
governor: unreadable
turbo: unknown
load_at_start: 27.79
load_limit: 1.6
load_at_end: 56.71 69.41 56.44
busy_on_pinned_cores_at_start: 81.7%
pinned_cores: [0, 1]
sources:
  - variants/go
  - sweep.toml
  - notes/design.md
---

# receiver-width-under-contention

| variant | samples | low | median | high | spread |
|---|---:|---:|---:|---:|---:|
| C scalar v1 @2 bursts/s p99 us | 5 | 82708.759 | 85515.915 | 95660.460 | 12951.701 |
| C scalar v3 @2 bursts/s p99 us | 5 | 82356.203 | 86089.976 | 97875.466 | 15519.263 |
| C simd @2 bursts/s p99 us | 5 | 2181.146 | 2412.388 | 3305.642 | 1124.496 |
| C scalar v1 @4 bursts/s p99 us | 5 | 377184.945 | 401811.386 | 415872.122 | 38687.177 |
| C scalar v3 @4 bursts/s p99 us | 5 | 366626.708 | 433698.751 | 614561.004 | 247934.296 |
| C simd @4 bursts/s p99 us | 5 | 41676.842 | 42374.836 | 51535.015 | 9858.173 |
| C scalar v1 @8 bursts/s p99 us | 5 | 1289069.540 | 1403861.939 | 1583802.790 | 294733.250 |
| C scalar v3 @8 bursts/s p99 us | 5 | 1555877.530 | 1653939.547 | 1750640.742 | 194763.212 |
| C simd @8 bursts/s p99 us | 5 | 53669.410 | 58255.192 | 62988.379 | 9318.969 |
| C scalar v1 @12 bursts/s p99 us | 5 | 3072917.076 | 4134001.701 | 4204196.370 | 1131279.294 |
| C scalar v3 @12 bursts/s p99 us | 5 | 4119868.072 | 4259834.997 | 4294967.294 | 175099.222 |
| C simd @12 bursts/s p99 us | 5 | 124373.819 | 142945.397 | 187727.422 | 63353.603 |
| C scalar v1 @16 bursts/s p99 us | 5 | 4294967.294 | 4294967.294 | 4294967.294 | 0.000 |
| C scalar v3 @16 bursts/s p99 us | 5 | 4294967.294 | 4294967.294 | 4294967.294 | 0.000 |
| C simd @16 bursts/s p99 us | 5 | 189439.838 | 196219.153 | 258618.442 | 69178.604 |
| C scalar v1 @20 bursts/s p99 us | 5 | 4294967.294 | 4294967.294 | 4294967.294 | 0.000 |
| C scalar v3 @20 bursts/s p99 us | 5 | 4294967.294 | 4294967.294 | 4294967.294 | 0.000 |
| C simd @20 bursts/s p99 us | 5 | 299406.888 | 369614.400 | 443445.535 | 144038.647 |

Medians over 5 measured repetitions, one warm-up discarded.
p99 is the recorded distribution above; these are the rest.

| case | impl | thr ops/s | p50 | p99 | p99.9 | max | peak RSS | cores used | thr spread |
|---|---|---|---|---|---|---|---|---|---|
| C | scalar v1 @2 bursts/s | 0.05M | 1.12ms | 85.52ms | 114.65ms | 128.15ms | 32MB | 1.66 | 0% |
| C | scalar v3 @2 bursts/s | 0.05M | 1.12ms | 86.09ms | 132.12ms | 160.79ms | 33MB | 1.65 | 0% |
| C | simd @2 bursts/s | 0.05M | 559.5us | 2.41ms | 57.67ms | 66.35ms | 30MB | 0.33 | 0% |
| C | scalar v1 @4 bursts/s | 0.05M | 3.47ms | 401.81ms | 432.71ms | 573.84ms | 54MB | 1.81 | 1% |
| C | scalar v3 @4 bursts/s | 0.05M | 3.50ms | 433.70ms | 458.52ms | 630.90ms | 59MB | 1.81 | 1% |
| C | simd @4 bursts/s | 0.05M | 578.4us | 42.37ms | 66.47ms | 71.90ms | 30MB | 0.53 | 0% |
| C | scalar v1 @8 bursts/s | 0.05M | 241.40ms | 1403.86ms | 1441.97ms | 2399.21ms | 144MB | 1.89 | 1% |
| C | scalar v3 @8 bursts/s | 0.05M | 292.73ms | 1653.94ms | 1701.43ms | 2828.51ms | 166MB | 1.89 | 1% |
| C | simd @8 bursts/s | 0.05M | 616.3us | 58.26ms | 87.12ms | 113.94ms | 32MB | 0.76 | 0% |
| C | scalar v1 @12 bursts/s | 0.04M | 1760.88ms | 4134.00ms | 4180.38ms | 4294.97ms | 371MB | 1.90 | 1% |
| C | scalar v3 @12 bursts/s | 0.04M | 1656.99ms | 4259.83ms | 4294.97ms | 4294.97ms | 385MB | 1.90 | 2% |
| C | simd @12 bursts/s | 0.05M | 767.8us | 142.95ms | 182.18ms | 253.47ms | 45MB | 1.08 | 0% |
| C | scalar v1 @16 bursts/s | 0.03M | 3126.88ms | 4294.97ms | 4294.97ms | 4294.97ms | 493MB | 1.90 | 2% |
| C | scalar v3 @16 bursts/s | 0.03M | 2824.06ms | 4294.97ms | 4294.97ms | 4294.97ms | 480MB | 1.90 | 1% |
| C | simd @16 bursts/s | 0.05M | 1.05ms | 196.22ms | 249.09ms | 398.23ms | 57MB | 1.38 | 0% |
| C | scalar v1 @20 bursts/s | 0.03M | 4230.50ms | 4294.97ms | 4294.97ms | 4294.97ms | 608MB | 1.90 | 1% |
| C | scalar v3 @20 bursts/s | 0.03M | 4294.97ms | 4294.97ms | 4294.97ms | 4294.97ms | 606MB | 1.90 | 1% |
| C | simd @20 bursts/s | 0.05M | 42.06ms | 369.61ms | 440.28ms | 753.71ms | 69MB | 1.64 | 1% |
- C scalar v1 @2 bursts/s: numgc=11.0 gc_pause_total_ms=0.9 gogc=100.0
- C scalar v1 @2 bursts/s: width=scalar goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=25000 clamped=0
- C scalar v3 @2 bursts/s: numgc=12.0 gc_pause_total_ms=0.9 gogc=100.0
- C scalar v3 @2 bursts/s: width=scalar goamd64=v3 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=25000 clamped=0
- C simd @2 bursts/s: numgc=12.0 gc_pause_total_ms=0.7 gogc=100.0
- C simd @2 bursts/s: width=simd goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=25000 clamped=0
- C scalar v1 @4 bursts/s: numgc=11.0 gc_pause_total_ms=1.0 gogc=100.0
- C scalar v1 @4 bursts/s: width=scalar goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=12500 clamped=0
- C scalar v3 @4 bursts/s: numgc=11.0 gc_pause_total_ms=1.0 gogc=100.0
- C scalar v3 @4 bursts/s: width=scalar goamd64=v3 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=12500 clamped=0
- C simd @4 bursts/s: numgc=12.0 gc_pause_total_ms=0.6 gogc=100.0
- C simd @4 bursts/s: width=simd goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=12500 clamped=0
- C scalar v1 @8 bursts/s: numgc=9.0 gc_pause_total_ms=1.1 gogc=100.0
- C scalar v1 @8 bursts/s: width=scalar goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=6250 clamped=0
- C scalar v3 @8 bursts/s: numgc=8.0 gc_pause_total_ms=0.9 gogc=100.0
- C scalar v3 @8 bursts/s: width=scalar goamd64=v3 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=6250 clamped=0
- C simd @8 bursts/s: numgc=13.0 gc_pause_total_ms=0.9 gogc=100.0
- C simd @8 bursts/s: width=simd goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=6250 clamped=0
- C scalar v1 @12 bursts/s: numgc=7.0 gc_pause_total_ms=0.9 gogc=100.0
- C scalar v1 @12 bursts/s: width=scalar goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=4166 clamped=1
- C scalar v3 @12 bursts/s: numgc=7.0 gc_pause_total_ms=0.7 gogc=100.0
- C scalar v3 @12 bursts/s: width=scalar goamd64=v3 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=4166 clamped=1973
- C simd @12 bursts/s: numgc=9.0 gc_pause_total_ms=0.7 gogc=100.0
- C simd @12 bursts/s: width=simd goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=4166 clamped=0
- C scalar v1 @16 bursts/s: numgc=6.0 gc_pause_total_ms=0.8 gogc=100.0
- C scalar v1 @16 bursts/s: width=scalar goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=3125 clamped=91006
- C scalar v3 @16 bursts/s: numgc=7.0 gc_pause_total_ms=0.8 gogc=100.0
- C scalar v3 @16 bursts/s: width=scalar goamd64=v3 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=3125 clamped=158649
- C simd @16 bursts/s: numgc=9.0 gc_pause_total_ms=1.0 gogc=100.0
- C simd @16 bursts/s: width=simd goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=3125 clamped=0
- C scalar v1 @20 bursts/s: numgc=7.0 gc_pause_total_ms=0.8 gogc=100.0
- C scalar v1 @20 bursts/s: width=scalar goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=2500 clamped=276497
- C scalar v3 @20 bursts/s: numgc=6.0 gc_pause_total_ms=0.8 gogc=100.0
- C scalar v3 @20 bursts/s: width=scalar goamd64=v3 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=2500 clamped=202000
- C simd @20 bursts/s: numgc=9.0 gc_pause_total_ms=1.0 gogc=100.0
- C simd @20 bursts/s: width=simd goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=2500 clamped=0
