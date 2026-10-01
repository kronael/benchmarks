---
title: transport-ladder-rtt-us
date: 2026-10-01
status: structure
host: AMD Ryzen 9 5950X 16-Core Processor
cpus: 2
kernel: 6.1.0-43-amd64
governor: unreadable
turbo: unknown
busy_on_pinned_cores_at_start: 99.5%
busy_limit: 10%
pinned_cores: [0, 1]
host_load_at_start: 7.13
host_load_at_end: 24.10 16.81 9.86
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
  @128B: e22e5ac4e65ffd75
  @512B: b6d0def9cf75df48
  @2048B: d3aaf9ca327f0eaa
  @8192B: 5badd276b106bedc
  @32768B: fa7ed117324fd46b
sources:
  - variants/go
  - variants/python
  - sweep.toml
  - notes/design.md
---

# transport-ladder-rtt-us

| variant | samples | low | median | high | spread |
|---|---:|---:|---:|---:|---:|
| 1a py-http worst @128B | 4500 | 277.483 | 311.136 | 4712.286 | 4434.803 |
| 1a py-http worst @512B | 4500 | 275.029 | 305.698 | 5544.014 | 5268.985 |
| 1a py-http worst @2048B | 4500 | 275.088 | 312.219 | 5199.584 | 4924.496 |
| 1a py-http worst @8192B | 4500 | 289.025 | 330.203 | 6292.816 | 6003.791 |
| 1a py-http worst @32768B | 4500 | 293.443 | 329.452 | 4923.983 | 4630.540 |
| 1a py-http medium @128B | 4500 | 154.271 | 180.180 | 1826.794 | 1672.523 |
| 1a py-http medium @512B | 4500 | 150.763 | 179.036 | 1730.884 | 1580.121 |
| 1a py-http medium @2048B | 4500 | 150.022 | 179.288 | 1369.042 | 1219.020 |
| 1a py-http medium @8192B | 4500 | 154.582 | 186.642 | 1756.882 | 1602.300 |
| 1a py-http medium @32768B | 4500 | 166.764 | 201.369 | 764.551 | 597.787 |
| 1b py-ws worst @128B | 4500 | 93.536 | 116.069 | 1641.726 | 1548.190 |
| 1b py-ws worst @512B | 4500 | 93.617 | 120.537 | 766.454 | 672.837 |
| 1b py-ws worst @2048B | 4500 | 100.520 | 158.339 | 3093.081 | 2992.561 |
| 1b py-ws worst @8192B | 4500 | 296.839 | 333.249 | 1244.817 | 947.978 |
| 1b py-ws worst @32768B | 4500 | 899.986 | 981.932 | 4829.046 | 3929.060 |
| 1b py-ws medium @128B | 4500 | 76.503 | 97.414 | 4394.526 | 4318.023 |
| 1b py-ws medium @512B | 4500 | 77.967 | 99.859 | 1825.803 | 1747.836 |
| 1b py-ws medium @2048B | 4500 | 79.290 | 94.769 | 512.215 | 432.925 |
| 1b py-ws medium @8192B | 4500 | 83.337 | 107.222 | 549.205 | 465.868 |
| 1b py-ws medium @32768B | 4500 | 104.757 | 135.826 | 889.838 | 785.081 |
| 2 go-grpc worst @128B | 4500 | 77.977 | 92.855 | 1769.537 | 1691.560 |
| 2 go-grpc worst @512B | 4500 | 74.702 | 89.829 | 1894.132 | 1819.430 |
| 2 go-grpc worst @2048B | 4500 | 75.021 | 88.227 | 549.146 | 474.125 |
| 2 go-grpc worst @8192B | 4500 | 80.001 | 100.390 | 652.020 | 572.019 |
| 2 go-grpc worst @32768B | 4500 | 197.173 | 236.617 | 1065.089 | 867.916 |
| 2 go-grpc medium @128B | 4500 | 46.709 | 57.328 | 665.134 | 618.425 |
| 2 go-grpc medium @512B | 4500 | 46.619 | 58.120 | 1671.002 | 1624.383 |
| 2 go-grpc medium @2048B | 4500 | 48.461 | 60.585 | 429.409 | 380.948 |
| 2 go-grpc medium @8192B | 4500 | 52.970 | 63.379 | 536.411 | 483.441 |
| 2 go-grpc medium @32768B | 4500 | 158.930 | 194.346 | 4295.759 | 4136.829 |
| 3 go-udp worst @128B | 4500 | 21.590 | 37.241 | 165.882 | 144.292 |
| 3 go-udp worst @512B | 4500 | 19.386 | 36.540 | 198.474 | 179.088 |
| 3 go-udp worst @2048B | 4500 | 20.508 | 39.744 | 687.476 | 666.968 |
| 3 go-udp worst @8192B | 4500 | 23.584 | 41.750 | 391.538 | 367.954 |
| 3 go-udp worst @32768B | 4500 | 30.287 | 48.731 | 549.998 | 519.711 |
| 3 go-udp medium @128B | 4500 | 12.794 | 35.266 | 448.545 | 435.751 |
| 3 go-udp medium @512B | 4500 | 15.780 | 35.005 | 292.903 | 277.123 |
| 3 go-udp medium @2048B | 4500 | 21.380 | 39.425 | 575.364 | 553.984 |
| 3 go-udp medium @8192B | 4500 | 22.943 | 38.402 | 164.239 | 141.296 |
| 3 go-udp medium @32768B | 4500 | 31.479 | 47.249 | 506.335 | 474.856 |
| C go-http worst @128B | 4500 | 144.012 | 162.395 | 718.845 | 574.833 |
| C go-http worst @512B | 4500 | 144.412 | 166.364 | 721.411 | 576.999 |
| C go-http worst @2048B | 4500 | 143.430 | 168.799 | 759.432 | 616.002 |
| C go-http worst @8192B | 4500 | 146.065 | 172.506 | 1839.530 | 1693.465 |
| C go-http worst @32768B | 4500 | 153.560 | 182.554 | 1304.699 | 1151.139 |
| C go-http medium @128B | 4500 | 57.027 | 67.477 | 1678.615 | 1621.588 |
| C go-http medium @512B | 4500 | 57.449 | 69.211 | 622.263 | 564.814 |
| C go-http medium @2048B | 4500 | 59.372 | 71.585 | 557.751 | 498.379 |
| C go-http medium @8192B | 4500 | 68.029 | 83.577 | 2209.196 | 2141.167 |
| C go-http medium @32768B | 4500 | 68.088 | 85.581 | 496.517 | 428.429 |

| rung | row | effort | payload | p50 µs | p99 µs | p99.9 µs | checksum |
|---|---|---|---:|---:|---:|---:|---|
| 1a | py-http | worst | 128 | 311.14 | 527.04 | 1057.33 | e22e5ac4e65ffd75 |
| 1a | py-http | worst | 512 | 305.70 | 462.19 | 1128.09 | b6d0def9cf75df48 |
| 1a | py-http | worst | 2048 | 312.22 | 496.32 | 1134.44 | d3aaf9ca327f0eaa |
| 1a | py-http | worst | 8192 | 330.20 | 494.66 | 2111.43 | 5badd276b106bedc |
| 1a | py-http | worst | 32768 | 329.45 | 494.66 | 834.25 | fa7ed117324fd46b |
| 1a | py-http | medium | 128 | 180.18 | 249.15 | 506.01 | e22e5ac4e65ffd75 |
| 1a | py-http | medium | 512 | 179.04 | 269.36 | 630.83 | b6d0def9cf75df48 |
| 1a | py-http | medium | 2048 | 179.29 | 249.18 | 568.68 | d3aaf9ca327f0eaa |
| 1a | py-http | medium | 8192 | 186.64 | 281.43 | 604.83 | 5badd276b106bedc |
| 1a | py-http | medium | 32768 | 201.37 | 299.75 | 619.13 | fa7ed117324fd46b |
| 1b | py-ws | worst | 128 | 116.07 | 180.78 | 314.01 | e22e5ac4e65ffd75 |
| 1b | py-ws | worst | 512 | 120.54 | 213.58 | 540.70 | b6d0def9cf75df48 |
| 1b | py-ws | worst | 2048 | 158.34 | 225.74 | 1606.82 | d3aaf9ca327f0eaa |
| 1b | py-ws | worst | 8192 | 333.25 | 431.51 | 635.99 | 5badd276b106bedc |
| 1b | py-ws | worst | 32768 | 981.93 | 1556.75 | 2262.69 | fa7ed117324fd46b |
| 1b | py-ws | medium | 128 | 97.41 | 171.58 | 423.79 | e22e5ac4e65ffd75 |
| 1b | py-ws | medium | 512 | 99.86 | 172.83 | 391.12 | b6d0def9cf75df48 |
| 1b | py-ws | medium | 2048 | 94.77 | 139.70 | 228.85 | d3aaf9ca327f0eaa |
| 1b | py-ws | medium | 8192 | 107.22 | 155.59 | 331.94 | 5badd276b106bedc |
| 1b | py-ws | medium | 32768 | 135.83 | 225.10 | 629.34 | fa7ed117324fd46b |
| 2 | go-grpc | worst | 128 | 92.86 | 204.12 | 492.66 | e22e5ac4e65ffd75 |
| 2 | go-grpc | worst | 512 | 89.83 | 195.75 | 447.33 | b6d0def9cf75df48 |
| 2 | go-grpc | worst | 2048 | 88.23 | 157.87 | 447.75 | d3aaf9ca327f0eaa |
| 2 | go-grpc | worst | 8192 | 100.39 | 249.35 | 473.45 | 5badd276b106bedc |
| 2 | go-grpc | worst | 32768 | 236.62 | 469.75 | 741.99 | fa7ed117324fd46b |
| 2 | go-grpc | medium | 128 | 57.33 | 104.91 | 274.31 | e22e5ac4e65ffd75 |
| 2 | go-grpc | medium | 512 | 58.12 | 105.34 | 301.52 | b6d0def9cf75df48 |
| 2 | go-grpc | medium | 2048 | 60.59 | 107.15 | 255.94 | d3aaf9ca327f0eaa |
| 2 | go-grpc | medium | 8192 | 63.38 | 162.40 | 330.66 | 5badd276b106bedc |
| 2 | go-grpc | medium | 32768 | 194.35 | 404.36 | 666.02 | fa7ed117324fd46b |
| 3 | go-udp | worst | 128 | 37.24 | 59.84 | 85.44 | e22e5ac4e65ffd75 |
| 3 | go-udp | worst | 512 | 36.54 | 61.83 | 106.55 | b6d0def9cf75df48 |
| 3 | go-udp | worst | 2048 | 39.74 | 70.27 | 168.45 | d3aaf9ca327f0eaa |
| 3 | go-udp | worst | 8192 | 41.75 | 76.24 | 233.88 | 5badd276b106bedc |
| 3 | go-udp | worst | 32768 | 48.73 | 95.73 | 243.96 | fa7ed117324fd46b |
| 3 | go-udp | medium | 128 | 35.27 | 60.51 | 127.95 | e22e5ac4e65ffd75 |
| 3 | go-udp | medium | 512 | 35.01 | 58.55 | 107.84 | b6d0def9cf75df48 |
| 3 | go-udp | medium | 2048 | 39.42 | 79.98 | 129.75 | d3aaf9ca327f0eaa |
| 3 | go-udp | medium | 8192 | 38.40 | 65.60 | 143.40 | 5badd276b106bedc |
| 3 | go-udp | medium | 32768 | 47.25 | 86.57 | 210.02 | fa7ed117324fd46b |
| C | go-http | worst | 128 | 162.40 | 279.14 | 484.79 | e22e5ac4e65ffd75 |
| C | go-http | worst | 512 | 166.36 | 294.38 | 560.09 | b6d0def9cf75df48 |
| C | go-http | worst | 2048 | 168.80 | 307.03 | 539.85 | d3aaf9ca327f0eaa |
| C | go-http | worst | 8192 | 172.51 | 313.82 | 653.68 | 5badd276b106bedc |
| C | go-http | worst | 32768 | 182.55 | 350.59 | 682.36 | fa7ed117324fd46b |
| C | go-http | medium | 128 | 67.48 | 108.70 | 265.24 | e22e5ac4e65ffd75 |
| C | go-http | medium | 512 | 69.21 | 128.66 | 321.75 | b6d0def9cf75df48 |
| C | go-http | medium | 2048 | 71.58 | 123.17 | 296.76 | d3aaf9ca327f0eaa |
| C | go-http | medium | 8192 | 83.58 | 166.85 | 385.87 | 5badd276b106bedc |
| C | go-http | medium | 32768 | 85.58 | 180.96 | 303.71 | fa7ed117324fd46b |

reps: 3 measured plus one discarded, ops 5000, warmup 500; every cell is the median across reps.
One checksum per payload size across all ten rows: identical work is gated, not assumed.
