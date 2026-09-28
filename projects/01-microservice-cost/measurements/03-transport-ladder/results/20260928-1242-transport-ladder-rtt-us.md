---
title: transport-ladder-rtt-us
date: 2026-09-28
status: structure
host: AMD Ryzen 9 5950X 16-Core Processor
cpus: 2
kernel: 6.1.0-43-amd64
governor: unreadable
turbo: unknown
load_at_start: 30.42
load_limit: 1.6
load_at_end: 15.86 15.28 27.87
busy_on_pinned_cores_at_start: 85.9%
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
| 1a py-http worst @128B | 4500 | 275.430 | 316.758 | 4329.836 | 4054.406 |
| 1a py-http worst @512B | 4500 | 274.978 | 312.699 | 21197.273 | 20922.295 |
| 1a py-http worst @2048B | 4500 | 278.084 | 317.759 | 2764.182 | 2486.098 |
| 1a py-http worst @8192B | 4500 | 278.815 | 330.794 | 2824.386 | 2545.571 |
| 1a py-http worst @32768B | 4500 | 287.543 | 333.149 | 4291.012 | 4003.469 |
| 1a py-http medium @128B | 4500 | 147.228 | 181.082 | 2104.528 | 1957.300 |
| 1a py-http medium @512B | 4500 | 147.888 | 187.463 | 1620.787 | 1472.899 |
| 1a py-http medium @2048B | 4500 | 129.234 | 162.337 | 1741.896 | 1612.662 |
| 1a py-http medium @8192B | 4500 | 151.516 | 187.914 | 1683.945 | 1532.429 |
| 1a py-http medium @32768B | 4500 | 148.119 | 195.369 | 743.983 | 595.864 |
| 1b py-ws worst @128B | 4500 | 91.974 | 125.357 | 3998.780 | 3906.806 |
| 1b py-ws worst @512B | 4500 | 90.180 | 124.464 | 2018.937 | 1928.757 |
| 1b py-ws worst @2048B | 4500 | 85.311 | 144.312 | 1791.809 | 1706.498 |
| 1b py-ws worst @8192B | 4500 | 283.825 | 327.358 | 2285.380 | 2001.555 |
| 1b py-ws worst @32768B | 4500 | 903.054 | 991.000 | 4582.561 | 3679.507 |
| 1b py-ws medium @128B | 4500 | 75.723 | 98.566 | 662.800 | 587.077 |
| 1b py-ws medium @512B | 4500 | 71.475 | 98.836 | 529.368 | 457.893 |
| 1b py-ws medium @2048B | 4500 | 70.122 | 96.211 | 481.729 | 411.607 |
| 1b py-ws medium @8192B | 4500 | 72.096 | 102.223 | 3599.368 | 3527.272 |
| 1b py-ws medium @32768B | 4500 | 97.955 | 129.074 | 583.320 | 485.365 |
| 2 go-grpc worst @128B | 4500 | 76.835 | 92.885 | 535.940 | 459.105 |
| 2 go-grpc worst @512B | 4500 | 74.150 | 96.702 | 738.413 | 664.263 |
| 2 go-grpc worst @2048B | 4500 | 74.951 | 93.817 | 768.770 | 693.819 |
| 2 go-grpc worst @8192B | 4500 | 77.477 | 100.730 | 616.963 | 539.486 |
| 2 go-grpc worst @32768B | 4500 | 192.262 | 236.216 | 1722.498 | 1530.236 |
| 2 go-grpc medium @128B | 4500 | 46.999 | 59.451 | 630.931 | 583.932 |
| 2 go-grpc medium @512B | 4500 | 46.477 | 59.181 | 447.784 | 401.307 |
| 2 go-grpc medium @2048B | 4500 | 47.789 | 60.144 | 424.511 | 376.722 |
| 2 go-grpc medium @8192B | 4500 | 51.848 | 62.609 | 458.815 | 406.967 |
| 2 go-grpc medium @32768B | 4500 | 163.037 | 183.726 | 620.951 | 457.914 |
| 3 go-udp worst @128B | 4500 | 22.051 | 37.961 | 197.131 | 175.080 |
| 3 go-udp worst @512B | 4500 | 13.897 | 38.833 | 142.618 | 128.721 |
| 3 go-udp worst @2048B | 4500 | 20.098 | 40.346 | 317.318 | 297.220 |
| 3 go-udp worst @8192B | 4500 | 24.286 | 40.337 | 410.165 | 385.879 |
| 3 go-udp worst @32768B | 4500 | 32.261 | 45.455 | 299.104 | 266.843 |
| 3 go-udp medium @128B | 4500 | 18.875 | 35.317 | 1709.324 | 1690.449 |
| 3 go-udp medium @512B | 4500 | 15.150 | 38.011 | 161.364 | 146.214 |
| 3 go-udp medium @2048B | 4500 | 17.483 | 40.506 | 585.994 | 568.511 |
| 3 go-udp medium @8192B | 4500 | 23.755 | 40.146 | 478.402 | 454.647 |
| 3 go-udp medium @32768B | 4500 | 29.996 | 45.246 | 278.024 | 248.028 |
| C go-http worst @128B | 4500 | 136.458 | 163.769 | 1639.341 | 1502.883 |
| C go-http worst @512B | 4500 | 138.601 | 170.141 | 1740.582 | 1601.981 |
| C go-http worst @2048B | 4500 | 140.594 | 166.013 | 1449.092 | 1308.498 |
| C go-http worst @8192B | 4500 | 145.154 | 175.792 | 619.507 | 474.353 |
| C go-http worst @32768B | 4500 | 152.137 | 185.530 | 1258.504 | 1106.367 |
| C go-http medium @128B | 4500 | 57.949 | 70.794 | 525.340 | 467.391 |
| C go-http medium @512B | 4500 | 59.773 | 69.441 | 1914.921 | 1855.148 |
| C go-http medium @2048B | 4500 | 57.448 | 71.604 | 417.768 | 360.320 |
| C go-http medium @8192B | 4500 | 63.981 | 84.750 | 3416.282 | 3352.301 |
| C go-http medium @32768B | 4500 | 70.363 | 86.012 | 342.705 | 272.342 |

| rung | row | effort | payload | p50 µs | p99 µs | p99.9 µs | checksum |
|---|---|---|---:|---:|---:|---:|---|
| 1a | py-http | worst | 128 | 316.76 | 505.82 | 1783.06 | e22e5ac4e65ffd75 |
| 1a | py-http | worst | 512 | 312.70 | 480.99 | 1841.55 | b6d0def9cf75df48 |
| 1a | py-http | worst | 2048 | 317.76 | 479.01 | 1816.77 | d3aaf9ca327f0eaa |
| 1a | py-http | worst | 8192 | 330.79 | 514.60 | 1087.38 | 5badd276b106bedc |
| 1a | py-http | worst | 32768 | 333.15 | 533.77 | 1090.52 | fa7ed117324fd46b |
| 1a | py-http | medium | 128 | 181.08 | 270.54 | 642.69 | e22e5ac4e65ffd75 |
| 1a | py-http | medium | 512 | 187.46 | 270.69 | 456.09 | b6d0def9cf75df48 |
| 1a | py-http | medium | 2048 | 162.34 | 238.00 | 425.87 | d3aaf9ca327f0eaa |
| 1a | py-http | medium | 8192 | 187.91 | 262.08 | 592.23 | 5badd276b106bedc |
| 1a | py-http | medium | 32768 | 195.37 | 312.94 | 599.20 | fa7ed117324fd46b |
| 1b | py-ws | worst | 128 | 125.36 | 195.22 | 312.41 | e22e5ac4e65ffd75 |
| 1b | py-ws | worst | 512 | 124.46 | 242.99 | 657.13 | b6d0def9cf75df48 |
| 1b | py-ws | worst | 2048 | 144.31 | 248.00 | 588.34 | d3aaf9ca327f0eaa |
| 1b | py-ws | worst | 8192 | 327.36 | 550.76 | 1777.11 | 5badd276b106bedc |
| 1b | py-ws | worst | 32768 | 991.00 | 1473.27 | 2262.73 | fa7ed117324fd46b |
| 1b | py-ws | medium | 128 | 98.57 | 151.01 | 368.52 | e22e5ac4e65ffd75 |
| 1b | py-ws | medium | 512 | 98.84 | 156.66 | 401.61 | b6d0def9cf75df48 |
| 1b | py-ws | medium | 2048 | 96.21 | 155.56 | 312.04 | d3aaf9ca327f0eaa |
| 1b | py-ws | medium | 8192 | 102.22 | 152.62 | 389.13 | 5badd276b106bedc |
| 1b | py-ws | medium | 32768 | 129.07 | 195.49 | 421.34 | fa7ed117324fd46b |
| 2 | go-grpc | worst | 128 | 92.89 | 178.90 | 446.51 | e22e5ac4e65ffd75 |
| 2 | go-grpc | worst | 512 | 96.70 | 239.36 | 494.07 | b6d0def9cf75df48 |
| 2 | go-grpc | worst | 2048 | 93.82 | 182.65 | 492.06 | d3aaf9ca327f0eaa |
| 2 | go-grpc | worst | 8192 | 100.73 | 255.67 | 487.86 | 5badd276b106bedc |
| 2 | go-grpc | worst | 32768 | 236.22 | 432.74 | 643.02 | fa7ed117324fd46b |
| 2 | go-grpc | medium | 128 | 59.45 | 104.70 | 371.63 | e22e5ac4e65ffd75 |
| 2 | go-grpc | medium | 512 | 59.18 | 97.00 | 318.14 | b6d0def9cf75df48 |
| 2 | go-grpc | medium | 2048 | 60.14 | 102.60 | 253.92 | d3aaf9ca327f0eaa |
| 2 | go-grpc | medium | 8192 | 62.61 | 143.48 | 317.09 | 5badd276b106bedc |
| 2 | go-grpc | medium | 32768 | 183.73 | 359.82 | 488.33 | fa7ed117324fd46b |
| 3 | go-udp | worst | 128 | 37.96 | 67.90 | 137.63 | e22e5ac4e65ffd75 |
| 3 | go-udp | worst | 512 | 38.83 | 69.06 | 98.87 | b6d0def9cf75df48 |
| 3 | go-udp | worst | 2048 | 40.35 | 72.82 | 115.24 | d3aaf9ca327f0eaa |
| 3 | go-udp | worst | 8192 | 40.34 | 74.16 | 128.96 | 5badd276b106bedc |
| 3 | go-udp | worst | 32768 | 45.45 | 84.40 | 171.23 | fa7ed117324fd46b |
| 3 | go-udp | medium | 128 | 35.32 | 58.12 | 101.54 | e22e5ac4e65ffd75 |
| 3 | go-udp | medium | 512 | 38.01 | 69.26 | 107.00 | b6d0def9cf75df48 |
| 3 | go-udp | medium | 2048 | 40.51 | 77.34 | 173.77 | d3aaf9ca327f0eaa |
| 3 | go-udp | medium | 8192 | 40.15 | 75.01 | 164.61 | 5badd276b106bedc |
| 3 | go-udp | medium | 32768 | 45.25 | 76.46 | 135.78 | fa7ed117324fd46b |
| C | go-http | worst | 128 | 163.77 | 302.69 | 595.65 | e22e5ac4e65ffd75 |
| C | go-http | worst | 512 | 170.14 | 360.43 | 709.79 | b6d0def9cf75df48 |
| C | go-http | worst | 2048 | 166.01 | 290.94 | 621.01 | d3aaf9ca327f0eaa |
| C | go-http | worst | 8192 | 175.79 | 311.39 | 531.20 | 5badd276b106bedc |
| C | go-http | worst | 32768 | 185.53 | 347.44 | 630.35 | fa7ed117324fd46b |
| C | go-http | medium | 128 | 70.79 | 122.92 | 307.51 | e22e5ac4e65ffd75 |
| C | go-http | medium | 512 | 69.44 | 124.53 | 300.60 | b6d0def9cf75df48 |
| C | go-http | medium | 2048 | 71.60 | 142.04 | 345.35 | d3aaf9ca327f0eaa |
| C | go-http | medium | 8192 | 84.75 | 169.48 | 416.98 | 5badd276b106bedc |
| C | go-http | medium | 32768 | 86.01 | 179.81 | 299.63 | fa7ed117324fd46b |

reps: 3 measured plus one discarded, ops 5000, warmup 500; every cell is the median across reps.
One checksum per payload size across all ten rows: identical work is gated, not assumed.
