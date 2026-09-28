---
title: transport-ladder-rtt-us
date: 2026-09-28
status: structure
host: AMD Ryzen 9 5950X 16-Core Processor
cpus: 2
kernel: 6.1.0-43-amd64
governor: unreadable
turbo: unknown
load_at_start: 48.91
load_limit: 1.6
load_at_end: 19.78 44.36 43.77
busy_on_pinned_cores_at_start: 26.4%
pinned_cores: [0, 1]
sources:
  - variants/go
  - variants/python
  - sweep.toml
  - notes/design.md
---

# transport-ladder-rtt-us

| variant | samples | low | median | high | spread |
|---|---:|---:|---:|---:|---:|
| 1a py-http worst @128B | 4500 | 273.717 | 316.547 | 4465.792 | 4192.075 |
| 1a py-http worst @512B | 4500 | 252.326 | 312.489 | 1365.875 | 1113.549 |
| 1a py-http worst @2048B | 4500 | 281.711 | 314.513 | 4529.792 | 4248.081 |
| 1a py-http worst @8192B | 4500 | 278.806 | 327.186 | 3744.961 | 3466.155 |
| 1a py-http worst @32768B | 4500 | 293.884 | 334.079 | 2156.687 | 1862.803 |
| 1a py-http medium @128B | 4500 | 139.183 | 179.979 | 844.743 | 705.560 |
| 1a py-http medium @512B | 4500 | 127.601 | 172.215 | 876.222 | 748.621 |
| 1a py-http medium @2048B | 4500 | 154.943 | 183.737 | 752.759 | 597.816 |
| 1a py-http medium @8192B | 4500 | 147.978 | 189.647 | 782.926 | 634.948 |
| 1a py-http medium @32768B | 4500 | 163.368 | 199.236 | 1895.134 | 1731.766 |
| 1b py-ws worst @128B | 4500 | 89.157 | 119.074 | 4500.958 | 4411.801 |
| 1b py-ws worst @512B | 4500 | 93.436 | 123.723 | 1818.450 | 1725.014 |
| 1b py-ws worst @2048B | 4500 | 100.780 | 155.673 | 1334.276 | 1233.496 |
| 1b py-ws worst @8192B | 4500 | 283.985 | 331.475 | 1660.031 | 1376.046 |
| 1b py-ws worst @32768B | 4500 | 895.488 | 991.881 | 6225.971 | 5330.483 |
| 1b py-ws medium @128B | 4500 | 76.565 | 102.143 | 3960.979 | 3884.414 |
| 1b py-ws medium @512B | 4500 | 68.028 | 96.812 | 520.101 | 452.073 |
| 1b py-ws medium @2048B | 4500 | 78.448 | 98.185 | 502.418 | 423.970 |
| 1b py-ws medium @8192B | 4500 | 76.174 | 100.960 | 523.157 | 446.983 |
| 1b py-ws medium @32768B | 4500 | 78.518 | 124.514 | 933.029 | 854.511 |
| 2 go-grpc worst @128B | 4500 | 74.581 | 89.729 | 1550.905 | 1476.324 |
| 2 go-grpc worst @512B | 4500 | 83.107 | 94.819 | 569.944 | 486.837 |
| 2 go-grpc worst @2048B | 4500 | 77.446 | 88.868 | 544.756 | 467.310 |
| 2 go-grpc worst @8192B | 4500 | 77.035 | 96.772 | 521.905 | 444.870 |
| 2 go-grpc worst @32768B | 4500 | 192.433 | 244.692 | 1890.765 | 1698.332 |
| 2 go-grpc medium @128B | 4500 | 46.489 | 59.593 | 644.726 | 598.237 |
| 2 go-grpc medium @512B | 4500 | 46.236 | 61.256 | 477.089 | 430.853 |
| 2 go-grpc medium @2048B | 4500 | 48.662 | 58.842 | 397.910 | 349.248 |
| 2 go-grpc medium @8192B | 4500 | 52.639 | 63.470 | 475.927 | 423.288 |
| 2 go-grpc medium @32768B | 4500 | 160.212 | 202.321 | 1983.911 | 1823.699 |
| 3 go-udp worst @128B | 4500 | 17.993 | 38.122 | 479.283 | 461.290 |
| 3 go-udp worst @512B | 4500 | 21.861 | 41.389 | 238.510 | 216.649 |
| 3 go-udp worst @2048B | 4500 | 23.504 | 38.664 | 148.851 | 125.347 |
| 3 go-udp worst @8192B | 4500 | 23.364 | 40.146 | 231.657 | 208.293 |
| 3 go-udp worst @32768B | 4500 | 33.283 | 49.864 | 212.321 | 179.038 |
| 3 go-udp medium @128B | 4500 | 20.308 | 36.518 | 310.226 | 289.918 |
| 3 go-udp medium @512B | 4500 | 16.653 | 38.372 | 1632.669 | 1616.016 |
| 3 go-udp medium @2048B | 4500 | 15.901 | 37.951 | 627.674 | 611.773 |
| 3 go-udp medium @8192B | 4500 | 23.484 | 40.617 | 210.637 | 187.153 |
| 3 go-udp medium @32768B | 4500 | 32.602 | 48.362 | 304.895 | 272.293 |
| C go-http worst @128B | 4500 | 143.560 | 165.492 | 725.309 | 581.749 |
| C go-http worst @512B | 4500 | 143.911 | 167.667 | 722.101 | 578.190 |
| C go-http worst @2048B | 4500 | 141.376 | 164.941 | 637.793 | 496.417 |
| C go-http worst @8192B | 4500 | 146.906 | 169.438 | 567.450 | 420.544 |
| C go-http worst @32768B | 4500 | 160.043 | 193.606 | 4183.319 | 4023.276 |
| C go-http medium @128B | 4500 | 58.621 | 68.298 | 1316.382 | 1257.761 |
| C go-http medium @512B | 4500 | 58.160 | 69.541 | 1632.960 | 1574.800 |
| C go-http medium @2048B | 4500 | 60.263 | 73.108 | 517.977 | 457.714 |
| C go-http medium @8192B | 4500 | 66.837 | 81.283 | 2164.231 | 2097.394 |
| C go-http medium @32768B | 4500 | 72.847 | 96.262 | 1149.367 | 1076.520 |

| rung | row | effort | payload | p50 µs | p99 µs | p99.9 µs | checksum |
|---|---|---|---:|---:|---:|---:|---|
| 1a | py-http | worst | 128 | 316.55 | 545.63 | 961.17 | e22e5ac4e65ffd75 |
| 1a | py-http | worst | 512 | 312.49 | 429.42 | 679.98 | b6d0def9cf75df48 |
| 1a | py-http | worst | 2048 | 314.51 | 464.31 | 1017.73 | d3aaf9ca327f0eaa |
| 1a | py-http | worst | 8192 | 327.19 | 519.33 | 977.28 | 5badd276b106bedc |
| 1a | py-http | worst | 32768 | 334.08 | 587.07 | 1325.38 | fa7ed117324fd46b |
| 1a | py-http | medium | 128 | 179.98 | 243.79 | 482.81 | e22e5ac4e65ffd75 |
| 1a | py-http | medium | 512 | 172.22 | 250.90 | 553.14 | b6d0def9cf75df48 |
| 1a | py-http | medium | 2048 | 183.74 | 268.65 | 621.86 | d3aaf9ca327f0eaa |
| 1a | py-http | medium | 8192 | 189.65 | 256.43 | 561.23 | 5badd276b106bedc |
| 1a | py-http | medium | 32768 | 199.24 | 336.58 | 631.36 | fa7ed117324fd46b |
| 1b | py-ws | worst | 128 | 119.07 | 180.49 | 1736.49 | e22e5ac4e65ffd75 |
| 1b | py-ws | worst | 512 | 123.72 | 183.65 | 292.45 | b6d0def9cf75df48 |
| 1b | py-ws | worst | 2048 | 155.67 | 248.92 | 465.98 | d3aaf9ca327f0eaa |
| 1b | py-ws | worst | 8192 | 331.48 | 548.63 | 860.38 | 5badd276b106bedc |
| 1b | py-ws | worst | 32768 | 991.88 | 1581.67 | 3121.78 | fa7ed117324fd46b |
| 1b | py-ws | medium | 128 | 102.14 | 184.27 | 555.06 | e22e5ac4e65ffd75 |
| 1b | py-ws | medium | 512 | 96.81 | 140.76 | 382.00 | b6d0def9cf75df48 |
| 1b | py-ws | medium | 2048 | 98.19 | 139.43 | 309.25 | d3aaf9ca327f0eaa |
| 1b | py-ws | medium | 8192 | 100.96 | 136.96 | 294.75 | 5badd276b106bedc |
| 1b | py-ws | medium | 32768 | 124.51 | 205.59 | 482.92 | fa7ed117324fd46b |
| 2 | go-grpc | worst | 128 | 89.73 | 175.83 | 472.34 | e22e5ac4e65ffd75 |
| 2 | go-grpc | worst | 512 | 94.82 | 176.16 | 433.40 | b6d0def9cf75df48 |
| 2 | go-grpc | worst | 2048 | 88.87 | 148.03 | 419.69 | d3aaf9ca327f0eaa |
| 2 | go-grpc | worst | 8192 | 96.77 | 229.08 | 434.24 | 5badd276b106bedc |
| 2 | go-grpc | worst | 32768 | 244.69 | 497.08 | 867.90 | fa7ed117324fd46b |
| 2 | go-grpc | medium | 128 | 59.59 | 114.30 | 308.05 | e22e5ac4e65ffd75 |
| 2 | go-grpc | medium | 512 | 61.26 | 128.48 | 345.40 | b6d0def9cf75df48 |
| 2 | go-grpc | medium | 2048 | 58.84 | 91.92 | 250.02 | d3aaf9ca327f0eaa |
| 2 | go-grpc | medium | 8192 | 63.47 | 135.96 | 281.18 | 5badd276b106bedc |
| 2 | go-grpc | medium | 32768 | 202.32 | 423.60 | 643.71 | fa7ed117324fd46b |
| 3 | go-udp | worst | 128 | 38.12 | 85.60 | 119.17 | e22e5ac4e65ffd75 |
| 3 | go-udp | worst | 512 | 41.39 | 81.72 | 113.84 | b6d0def9cf75df48 |
| 3 | go-udp | worst | 2048 | 38.66 | 87.49 | 101.65 | d3aaf9ca327f0eaa |
| 3 | go-udp | worst | 8192 | 40.15 | 63.76 | 106.07 | 5badd276b106bedc |
| 3 | go-udp | worst | 32768 | 49.86 | 83.04 | 145.41 | fa7ed117324fd46b |
| 3 | go-udp | medium | 128 | 36.52 | 83.90 | 104.33 | e22e5ac4e65ffd75 |
| 3 | go-udp | medium | 512 | 38.37 | 70.06 | 107.54 | b6d0def9cf75df48 |
| 3 | go-udp | medium | 2048 | 37.95 | 69.32 | 126.52 | d3aaf9ca327f0eaa |
| 3 | go-udp | medium | 8192 | 40.62 | 67.24 | 121.14 | 5badd276b106bedc |
| 3 | go-udp | medium | 32768 | 48.36 | 79.76 | 153.33 | fa7ed117324fd46b |
| C | go-http | worst | 128 | 165.49 | 298.26 | 511.72 | e22e5ac4e65ffd75 |
| C | go-http | worst | 512 | 167.67 | 354.81 | 564.08 | b6d0def9cf75df48 |
| C | go-http | worst | 2048 | 164.94 | 279.87 | 486.34 | d3aaf9ca327f0eaa |
| C | go-http | worst | 8192 | 169.44 | 299.49 | 451.05 | 5badd276b106bedc |
| C | go-http | worst | 32768 | 193.61 | 404.72 | 715.89 | fa7ed117324fd46b |
| C | go-http | medium | 128 | 68.30 | 124.48 | 322.17 | e22e5ac4e65ffd75 |
| C | go-http | medium | 512 | 69.54 | 120.12 | 291.12 | b6d0def9cf75df48 |
| C | go-http | medium | 2048 | 73.11 | 133.62 | 329.71 | d3aaf9ca327f0eaa |
| C | go-http | medium | 8192 | 81.28 | 152.20 | 348.60 | 5badd276b106bedc |
| C | go-http | medium | 32768 | 96.26 | 246.44 | 357.14 | fa7ed117324fd46b |

reps: 3 measured plus one discarded, ops 5000, warmup 500; every cell is the median across reps.
One checksum per payload size across all ten rows: identical work is gated, not assumed.
