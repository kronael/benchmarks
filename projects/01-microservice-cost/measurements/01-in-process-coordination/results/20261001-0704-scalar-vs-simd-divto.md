---
title: scalar-vs-simd-divto
date: 2026-10-01
status: structure
host: AMD Ryzen 9 5950X 16-Core Processor
cpus: 1
kernel: 6.1.0-43-amd64
governor: unreadable
turbo: unknown
busy_on_pinned_cores_at_start: 99.0%
busy_limit: 10%
pinned_cores: [1]
host_load_at_start: 6.74
host_load_at_end: 21.13 11.94 7.15
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
  n=1: f59fb8a85738ad30
  n=2: e58f95a9ad85813f
  n=3: 52c6a2048bbce95a
  n=4: 90449d83cd0fb407
  n=5: a960c073b42158a7
  n=8: 69c7d50bd32b74ff
  n=16: 9ed1d68f719f3e80
  n=64: c3c861e6e2c15307
  n=256: 592d9132774d6007
  n=1024: f719a533eedb7eff
  n=4096: b5fc8004f372a693
  n=16384: 4e3e4e02e147d557
  n=65536: 1fb1e5b61cf70a54
  n=262144: 67b63e34f620bc54
  n=1048576: d6326408a162d9fd
  n=4194304: 91cd041af180b099
sources:
  - kernel, gonum floats.DivTo: https://github.com/gonum/gonum/blob/master/internal/asm/f64/stubs_noasm.go
  - its assembly twin: https://github.com/gonum/gonum/blob/master/internal/asm/f64/divto_amd64.s
  - the simd package: https://go.dev/blog/simd-experiment
  - prior art, DivTo at lengths 16-128 on an i7-11370H: https://gorse.io/posts/go-simd-benchmark
  - regime at build time, scalar@v1: DIVSD=5 DIVPD=0
  - regime at build time, simd@v1: DIVSD=4 DIVPD=6
  - regime at build time, scalar@v3: DIVSD=5 DIVPD=0
  - regime at build time, simd@v3: DIVSD=4 DIVPD=6
---

# scalar-vs-simd-divto

| variant | samples | low | median | high | spread |
|---|---:|---:|---:|---:|---:|
| n=1 scalar@v1 | 11 | 2.669 | 2.792 | 3.335 | 0.667 |
| n=1 simd@v1 | 11 | 9.251 | 9.714 | 12.667 | 3.416 |
| n=1 scalar@v3 | 11 | 2.328 | 2.445 | 5.725 | 3.397 |
| n=1 simd@v3 | 11 | 9.742 | 10.103 | 13.037 | 3.296 |
| n=2 scalar@v1 | 11 | 1.522 | 1.660 | 4.580 | 3.058 |
| n=2 simd@v1 | 11 | 4.817 | 4.940 | 8.475 | 3.658 |
| n=2 scalar@v3 | 11 | 1.372 | 1.447 | 1.505 | 0.133 |
| n=2 simd@v3 | 11 | 4.719 | 4.854 | 7.987 | 3.267 |
| n=3 scalar@v1 | 11 | 1.127 | 1.240 | 1.608 | 0.481 |
| n=3 simd@v1 | 11 | 3.026 | 3.135 | 3.962 | 0.936 |
| n=3 scalar@v3 | 11 | 1.045 | 1.093 | 1.681 | 0.637 |
| n=3 simd@v3 | 11 | 3.159 | 3.366 | 6.407 | 3.248 |
| n=4 scalar@v1 | 11 | 0.999 | 1.015 | 1.033 | 0.035 |
| n=4 simd@v1 | 11 | 1.390 | 1.455 | 1.948 | 0.557 |
| n=4 scalar@v3 | 11 | 1.073 | 1.179 | 4.516 | 3.444 |
| n=4 simd@v3 | 11 | 1.330 | 1.384 | 1.508 | 0.179 |
| n=5 scalar@v1 | 11 | 1.005 | 1.049 | 1.236 | 0.232 |
| n=5 simd@v1 | 11 | 2.498 | 2.530 | 2.978 | 0.480 |
| n=5 scalar@v3 | 11 | 1.065 | 1.079 | 1.141 | 0.076 |
| n=5 simd@v3 | 11 | 2.434 | 2.511 | 3.356 | 0.921 |
| n=8 scalar@v1 | 11 | 1.020 | 1.125 | 4.218 | 3.198 |
| n=8 simd@v1 | 11 | 0.884 | 0.934 | 1.060 | 0.176 |
| n=8 scalar@v3 | 11 | 1.032 | 1.053 | 1.105 | 0.073 |
| n=8 simd@v3 | 11 | 0.903 | 0.975 | 1.377 | 0.474 |
| n=16 scalar@v1 | 11 | 1.013 | 1.026 | 1.065 | 0.052 |
| n=16 simd@v1 | 11 | 0.661 | 0.700 | 1.420 | 0.759 |
| n=16 scalar@v3 | 11 | 1.023 | 1.036 | 1.060 | 0.038 |
| n=16 simd@v3 | 11 | 0.656 | 0.667 | 0.821 | 0.164 |
| n=64 scalar@v1 | 11 | 1.010 | 1.050 | 1.099 | 0.089 |
| n=64 simd@v1 | 11 | 0.501 | 0.514 | 0.609 | 0.108 |
| n=64 scalar@v3 | 11 | 1.013 | 1.019 | 3.949 | 2.937 |
| n=64 simd@v3 | 11 | 0.484 | 0.499 | 3.662 | 3.178 |
| n=256 scalar@v1 | 11 | 1.016 | 1.038 | 1.101 | 0.085 |
| n=256 simd@v1 | 11 | 0.474 | 0.513 | 0.603 | 0.129 |
| n=256 scalar@v3 | 11 | 0.991 | 1.016 | 1.038 | 0.047 |
| n=256 simd@v3 | 11 | 0.484 | 0.492 | 0.501 | 0.018 |
| n=1024 scalar@v1 | 11 | 1.055 | 1.079 | 4.411 | 3.356 |
| n=1024 simd@v1 | 11 | 0.448 | 0.451 | 0.645 | 0.197 |
| n=1024 scalar@v3 | 11 | 0.997 | 1.023 | 1.129 | 0.132 |
| n=1024 simd@v3 | 11 | 0.451 | 0.457 | 0.490 | 0.039 |
| n=4096 scalar@v1 | 11 | 0.990 | 1.028 | 1.213 | 0.223 |
| n=4096 simd@v1 | 11 | 0.464 | 0.467 | 0.494 | 0.031 |
| n=4096 scalar@v3 | 11 | 0.985 | 1.008 | 1.115 | 0.130 |
| n=4096 simd@v3 | 11 | 0.439 | 0.492 | 0.579 | 0.140 |
| n=16384 scalar@v1 | 11 | 0.987 | 1.000 | 1.030 | 0.043 |
| n=16384 simd@v1 | 11 | 0.441 | 0.466 | 0.494 | 0.053 |
| n=16384 scalar@v3 | 11 | 0.990 | 1.015 | 4.189 | 3.199 |
| n=16384 simd@v3 | 11 | 0.475 | 0.490 | 0.495 | 0.020 |
| n=65536 scalar@v1 | 11 | 0.991 | 1.006 | 1.020 | 0.029 |
| n=65536 simd@v1 | 11 | 0.434 | 0.457 | 3.889 | 3.455 |
| n=65536 scalar@v3 | 11 | 0.991 | 1.017 | 1.046 | 0.056 |
| n=65536 simd@v3 | 11 | 0.478 | 0.520 | 0.806 | 0.329 |
| n=262144 scalar@v1 | 11 | 0.992 | 1.006 | 3.952 | 2.960 |
| n=262144 simd@v1 | 11 | 0.456 | 0.495 | 0.576 | 0.121 |
| n=262144 scalar@v3 | 11 | 1.005 | 1.009 | 1.021 | 0.016 |
| n=262144 simd@v3 | 11 | 0.477 | 0.577 | 0.832 | 0.355 |
| n=1048576 scalar@v1 | 11 | 1.096 | 1.167 | 1.295 | 0.199 |
| n=1048576 simd@v1 | 11 | 0.495 | 0.546 | 0.719 | 0.224 |
| n=1048576 scalar@v3 | 11 | 1.038 | 1.051 | 1.067 | 0.029 |
| n=1048576 simd@v3 | 11 | 0.566 | 0.616 | 0.843 | 0.276 |
| n=4194304 scalar@v1 | 11 | 1.371 | 1.396 | 1.494 | 0.122 |
| n=4194304 simd@v1 | 11 | 1.159 | 1.580 | 1.867 | 0.709 |
| n=4194304 scalar@v3 | 11 | 1.279 | 1.320 | 1.445 | 0.166 |
| n=4194304 simd@v3 | 11 | 1.192 | 1.333 | 1.526 | 0.334 |
