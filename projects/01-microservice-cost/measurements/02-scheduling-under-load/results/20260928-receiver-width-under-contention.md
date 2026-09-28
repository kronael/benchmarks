---
title: receiver-width-under-contention
date: 2026-09-28
status: structure
host: AMD Ryzen 9 5950X 16-Core Processor
cpus: 2
kernel: 6.1.0-43-amd64
governor: unreadable
turbo: unknown
load_at_start: 3.07
load_limit: 1.6
load_at_end: 61.55 67.57 49.64
busy_on_pinned_cores_at_start: 24.5%
pinned_cores: [0, 1]
sources:
  - variants/go
  - sweep.toml
  - notes/design.md
---

# receiver-width-under-contention

| variant | samples | low | median | high | spread |
|---|---:|---:|---:|---:|---:|
| C scalar v1 @2 bursts/s p99 us | 5 | 84862.401 | 87419.314 | 96759.712 | 11897.311 |
| C scalar v3 @2 bursts/s p99 us | 5 | 79448.579 | 87167.318 | 94595.769 | 15147.190 |
| C simd @2 bursts/s p99 us | 5 | 1323.115 | 2162.538 | 2409.126 | 1086.011 |
| C scalar v1 @4 bursts/s p99 us | 5 | 356341.327 | 398763.757 | 443610.207 | 87268.880 |
| C scalar v3 @4 bursts/s p99 us | 5 | 399057.150 | 477770.297 | 559096.015 | 160038.865 |
| C simd @4 bursts/s p99 us | 5 | 41376.897 | 43728.679 | 44799.657 | 3422.760 |
| C scalar v1 @8 bursts/s p99 us | 5 | 1512671.821 | 1602706.274 | 1654195.961 | 141524.140 |
| C scalar v3 @8 bursts/s p99 us | 5 | 1376698.589 | 1576781.792 | 1843211.197 | 466512.608 |
| C simd @8 bursts/s p99 us | 5 | 60465.503 | 61705.433 | 71311.545 | 10846.042 |
| C scalar v1 @12 bursts/s p99 us | 5 | 3722578.820 | 4294967.294 | 4294967.294 | 572388.474 |
| C scalar v3 @12 bursts/s p99 us | 5 | 3692666.113 | 4251150.537 | 4294967.294 | 602301.181 |
| C simd @12 bursts/s p99 us | 5 | 125860.380 | 135212.753 | 141991.962 | 16131.582 |
| C scalar v1 @16 bursts/s p99 us | 5 | 4294967.294 | 4294967.294 | 4294967.294 | 0.000 |
| C scalar v3 @16 bursts/s p99 us | 5 | 4294967.294 | 4294967.294 | 4294967.294 | 0.000 |
| C simd @16 bursts/s p99 us | 5 | 173236.575 | 189203.578 | 195324.956 | 22088.381 |
| C scalar v1 @20 bursts/s p99 us | 5 | 4294967.294 | 4294967.294 | 4294967.294 | 0.000 |
| C scalar v3 @20 bursts/s p99 us | 5 | 4294967.294 | 4294967.294 | 4294967.294 | 0.000 |
| C simd @20 bursts/s p99 us | 5 | 346095.122 | 422595.265 | 465623.238 | 119528.116 |

Medians over 5 measured repetitions, one warm-up discarded.
p99 is the recorded distribution above; these are the rest.

| case | impl | thr ops/s | p50 | p99 | p99.9 | max | peak RSS | cores used | thr spread |
|---|---|---|---|---|---|---|---|---|---|
| C | scalar v1 @2 bursts/s | 0.05M | 1.14ms | 87.42ms | 137.21ms | 173.40ms | 31MB | 1.67 | 0% |
| C | scalar v3 @2 bursts/s | 0.05M | 1.14ms | 87.17ms | 116.32ms | 170.05ms | 31MB | 1.66 | 0% |
| C | simd @2 bursts/s | 0.05M | 563.4us | 2.16ms | 55.17ms | 63.78ms | 29MB | 0.35 | 0% |
| C | scalar v1 @4 bursts/s | 0.05M | 3.56ms | 398.76ms | 433.66ms | 563.60ms | 51MB | 1.81 | 1% |
| C | scalar v3 @4 bursts/s | 0.05M | 3.74ms | 477.77ms | 532.16ms | 583.05ms | 62MB | 1.83 | 1% |
| C | simd @4 bursts/s | 0.05M | 588.0us | 43.73ms | 66.04ms | 72.61ms | 29MB | 0.54 | 0% |
| C | scalar v1 @8 bursts/s | 0.05M | 326.16ms | 1602.71ms | 1626.73ms | 2840.63ms | 161MB | 1.89 | 1% |
| C | scalar v3 @8 bursts/s | 0.05M | 389.89ms | 1576.78ms | 1602.83ms | 2268.30ms | 155MB | 1.89 | 2% |
| C | simd @8 bursts/s | 0.05M | 634.6us | 61.71ms | 91.20ms | 111.58ms | 33MB | 0.80 | 0% |
| C | scalar v1 @12 bursts/s | 0.04M | 1695.18ms | 4294.97ms | 4294.97ms | 4294.97ms | 382MB | 1.90 | 2% |
| C | scalar v3 @12 bursts/s | 0.04M | 1538.92ms | 4251.15ms | 4277.05ms | 4294.97ms | 377MB | 1.90 | 2% |
| C | simd @12 bursts/s | 0.05M | 763.9us | 135.21ms | 182.72ms | 283.13ms | 44MB | 1.08 | 0% |
| C | scalar v1 @16 bursts/s | 0.03M | 3242.45ms | 4294.97ms | 4294.97ms | 4294.97ms | 504MB | 1.90 | 2% |
| C | scalar v3 @16 bursts/s | 0.03M | 3492.27ms | 4294.97ms | 4294.97ms | 4294.97ms | 517MB | 1.90 | 2% |
| C | simd @16 bursts/s | 0.05M | 1.03ms | 189.20ms | 247.95ms | 331.26ms | 53MB | 1.37 | 0% |
| C | scalar v1 @20 bursts/s | 0.03M | 4006.85ms | 4294.97ms | 4294.97ms | 4294.97ms | 607MB | 1.90 | 2% |
| C | scalar v3 @20 bursts/s | 0.03M | 4232.02ms | 4294.97ms | 4294.97ms | 4294.97ms | 602MB | 1.90 | 1% |
| C | simd @20 bursts/s | 0.05M | 38.93ms | 422.60ms | 483.49ms | 741.57ms | 71MB | 1.62 | 1% |
- C scalar v1 @2 bursts/s: numgc=11.0 gc_pause_total_ms=0.8 gogc=100.0
- C scalar v1 @2 bursts/s: width=scalar goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=25000 clamped=0
- C scalar v3 @2 bursts/s: numgc=11.0 gc_pause_total_ms=0.9 gogc=100.0
- C scalar v3 @2 bursts/s: width=scalar goamd64=v3 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=25000 clamped=0
- C simd @2 bursts/s: numgc=12.0 gc_pause_total_ms=0.7 gogc=100.0
- C simd @2 bursts/s: width=simd goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=25000 clamped=0
- C scalar v1 @4 bursts/s: numgc=10.0 gc_pause_total_ms=1.2 gogc=100.0
- C scalar v1 @4 bursts/s: width=scalar goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=12500 clamped=0
- C scalar v3 @4 bursts/s: numgc=10.0 gc_pause_total_ms=0.9 gogc=100.0
- C scalar v3 @4 bursts/s: width=scalar goamd64=v3 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=12500 clamped=0
- C simd @4 bursts/s: numgc=11.0 gc_pause_total_ms=0.7 gogc=100.0
- C simd @4 bursts/s: width=simd goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=12500 clamped=0
- C scalar v1 @8 bursts/s: numgc=8.0 gc_pause_total_ms=0.9 gogc=100.0
- C scalar v1 @8 bursts/s: width=scalar goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=6250 clamped=0
- C scalar v3 @8 bursts/s: numgc=8.0 gc_pause_total_ms=0.7 gogc=100.0
- C scalar v3 @8 bursts/s: width=scalar goamd64=v3 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=6250 clamped=0
- C simd @8 bursts/s: numgc=12.0 gc_pause_total_ms=1.0 gogc=100.0
- C simd @8 bursts/s: width=simd goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=6250 clamped=0
- C scalar v1 @12 bursts/s: numgc=7.0 gc_pause_total_ms=0.8 gogc=100.0
- C scalar v1 @12 bursts/s: width=scalar goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=4166 clamped=2
- C scalar v3 @12 bursts/s: numgc=7.0 gc_pause_total_ms=0.9 gogc=100.0
- C scalar v3 @12 bursts/s: width=scalar goamd64=v3 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=4166 clamped=17953
- C simd @12 bursts/s: numgc=9.0 gc_pause_total_ms=0.7 gogc=100.0
- C simd @12 bursts/s: width=simd goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=4166 clamped=0
- C scalar v1 @16 bursts/s: numgc=7.0 gc_pause_total_ms=0.9 gogc=100.0
- C scalar v1 @16 bursts/s: width=scalar goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=3125 clamped=228886
- C scalar v3 @16 bursts/s: numgc=7.0 gc_pause_total_ms=0.9 gogc=100.0
- C scalar v3 @16 bursts/s: width=scalar goamd64=v3 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=3125 clamped=104488
- C simd @16 bursts/s: numgc=9.0 gc_pause_total_ms=1.0 gogc=100.0
- C simd @16 bursts/s: width=simd goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=3125 clamped=0
- C scalar v1 @20 bursts/s: numgc=7.0 gc_pause_total_ms=0.9 gogc=100.0
- C scalar v1 @20 bursts/s: width=scalar goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=2500 clamped=268836
- C scalar v3 @20 bursts/s: numgc=7.0 gc_pause_total_ms=0.7 gogc=100.0
- C scalar v3 @20 bursts/s: width=scalar goamd64=v3 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=2500 clamped=267091
- C simd @20 bursts/s: numgc=9.0 gc_pause_total_ms=0.9 gogc=100.0
- C simd @20 bursts/s: width=simd goamd64=v1 goexperiment=simd vector_bits=256 lanes=4 emulated=false heavy_every=2500 clamped=0
