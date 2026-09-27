#!/usr/bin/env python3
"""Build both sides, run each case with warm-up, report medians.

Usage: make test | make bench, or ./run.py [--reps N] [--cases A,B,C]
                                           [--quick] [--no-build]
Every binary prints one RESULT line (key=value pairs); this script discards
one warm-up run, keeps `reps` measured runs, verifies the checksums of every
row sharing a workload match across ALL runs (proof they did identical work),
and prints a markdown table where each cell is the per-metric median across the
measured runs (runs are deterministic in work, so metrics are independently
comparable; tails especially need per-metric medians).

Case C's rows come from sweep.toml, so the swept contention level lives in one
place. --no-build exists because the measured run is started under `sudo chrt
-f 80 taskset -c 2,3` and must not compile anything as root.
"""

import argparse
import os
import statistics
import subprocess
import sys
import tomllib

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.join(HERE, "bin")
GO = os.path.join(HERE, "variants", "go")
RUST = os.path.join(HERE, "variants", "rust")
GO_BINARIES = ("casea", "caseb", "casec", "pingpong", "sleepers")
RUST_BINARIES = ("casea", "caseb", "pingpong", "sleepers")  # case C has no Rust twin

# (case, label, binary, extra env). Cases A and B are the inherited
# cross-language rows and their operating points are fixed here; case C is
# swept and comes from sweep.toml.
DEFAULT_MATRIX = [
    ("A", "go @3 bursts", "go-casea", {}),
    ("A", "rust(tokio) @3 bursts", "rust-casea", {}),
    ("A", "rust(tokio+block_in_place) @3", "rust-casea", {"BENCH_MITIGATE": "1"}),
    ("A", "go @6 bursts", "go-casea", {"BENCH_HEAVY_EVERY": "833"}),
    ("A", "rust(tokio) @6 bursts", "rust-casea", {"BENCH_HEAVY_EVERY": "833"}),
    ("A", "rust(tokio+block_in_place) @6", "rust-casea", {"BENCH_HEAVY_EVERY": "833", "BENCH_MITIGATE": "1"}),
    ("B", "go", "go-caseb", {}),
    ("B", "go GOGC=1000", "go-caseb", {"GOGC": "1000"}),
    ("B", "rust(threads)", "rust-caseb", {}),
    ("P1", "go", "go-pingpong", {}),
    ("P1", "rust(tokio)", "rust-pingpong", {}),
    ("P2", "go", "go-sleepers", {}),
    ("P2", "rust(tokio)", "rust-sleepers", {}),
]

COLUMNS = [
    ("thr_ops_s", "thr ops/s"),
    ("p50_ns", "p50"),
    ("p99_ns", "p99"),
    ("p999_ns", "p99.9"),
    ("max_ns", "max"),
    ("rss_peak_mb", "peak RSS"),
    ("cpu_cores", "cores used"),
]

REQUESTS_PER_S = 50_000  # the driver's fixed arrival rate, for burst-rate labels


def sweep():
    with open(os.path.join(HERE, "sweep.toml"), "rb") as handle:
        return tomllib.load(handle)


def case_c_matrix(spec, quick):
    """One row per width per swept contention level.

    Quick mode is one value off the sweep entirely, chosen so the burst path
    fires often inside a short run. It proves the widths agree; it measures
    nothing.
    """
    values = [spec["run"]["quick_heavy_every"]] if quick else spec["sweep"]["values"]
    rows = []
    for every in values:
        for variant in spec["variants"]:
            label = f"{variant['label']} @{REQUESTS_PER_S // every} bursts/s"
            rows.append(("C", label, variant["binary"],
                         {"BENCH_WIDTH": variant["width"], "BENCH_HEAVY_EVERY": str(every)}))
    return rows


def require_pinned_toolchain():
    """Case C imports simd, which go1.27 compiles only under GOEXPERIMENT=simd.

    mk/measurement.mk exports that and the toolchain pin. Raising here rather
    than supplying a default keeps one source of truth: a runner that quietly
    built a different binary depending on how it was invoked is exactly the
    failure this repository exists to catch.
    """
    if "simd" not in os.environ.get("GOEXPERIMENT", "").split(","):
        sys.exit("GOEXPERIMENT=simd is unset; run via make, which pins it (mk/measurement.mk)")


def build(matrix):
    require_pinned_toolchain()
    subprocess.run(["go", "build", "-o", BIN + "/", "./..."], cwd=GO, check=True)
    for name in GO_BINARIES:
        src = os.path.join(BIN, name)
        if os.path.exists(src):
            os.replace(src, os.path.join(BIN, "go-" + name))
    # Go's own documented remedy for an SSE2-only build on a box whose
    # GOAMD64 default is v1. Same source, one build flag; the binary reports
    # its own GOAMD64, so the row cannot be mislabelled in the table.
    subprocess.run(
        ["go", "build", "-o", os.path.join(BIN, "go-casec-v3"), "./casec"],
        cwd=GO, env=dict(os.environ, GOAMD64="v3"), check=True,
    )
    if not any(binary.startswith("rust-") for _, _, binary, _ in matrix):
        return
    subprocess.run(["cargo", "build", "--release", "--quiet"], cwd=RUST, check=True)
    for name in RUST_BINARIES:
        src = os.path.join(RUST, "target", "release", name)
        if os.path.exists(src):
            subprocess.run(["cp", src, os.path.join(BIN, "rust-" + name)], check=True)


def run_once(binary, extra_env):
    env = dict(os.environ, **extra_env)
    out = subprocess.run(
        [os.path.join(BIN, binary)], env=env, check=True,
        capture_output=True, text=True,
    ).stdout
    result, regime = None, ""
    for line in out.splitlines():
        if line.startswith("RESULT "):
            result = dict(kv.split("=", 1) for kv in line.split()[1:])
        elif line.startswith("REGIME "):
            regime = line[len("REGIME "):]
    if result is None:
        sys.exit(f"no RESULT line from {binary}")
    return result, regime


def fmt_ns(ns):
    ns = float(ns)
    if ns >= 1e6:
        return f"{ns / 1e6:.2f}ms"
    if ns >= 1e3:
        return f"{ns / 1e3:.1f}us"
    return f"{ns:.0f}ns"


def fmt(key, value):
    if key.endswith("_ns"):
        return fmt_ns(value)
    if key == "thr_ops_s":
        return f"{float(value) / 1e6:.2f}M"
    if key == "rss_peak_mb":
        return f"{float(value):.0f}MB"
    if key == "cpu_cores":
        return f"{float(value):.2f}"
    return str(value)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reps", type=int, default=5)
    parser.add_argument("--cases", default="A,B")
    parser.add_argument("--quick", action="store_true", help="1 rep, no warm-up, short workload")
    parser.add_argument("--no-build", action="store_true", help="run the binaries already in bin/")
    parser.add_argument("--build-only", action="store_true", help="fill bin/ and stop")
    args = parser.parse_args()
    cases = args.cases.split(",")
    reps = 1 if args.quick else args.reps

    spec = sweep()
    matrix = [m for m in DEFAULT_MATRIX if m[0] in cases]
    if "C" in cases:
        matrix += case_c_matrix(spec, args.quick)
    # Quick mode shrinks the workload for every row that reads these; the
    # inherited cases ignore them and stay at their fixed operating points.
    short = {"BENCH_TOTAL": str(spec["run"]["quick_total"]),
             "BENCH_HEAVY_ITERS": str(spec["run"]["quick_heavy_iters"])} if args.quick else {}

    os.makedirs(BIN, exist_ok=True)
    if not args.no_build:
        build(matrix)
    if args.build_only:
        return

    rows = []
    checksums = {}
    for case, label, binary, extra_env in matrix:
        extra_env = dict(short, **extra_env)
        print(f"# {case} {label}: warm-up + {reps} reps", file=sys.stderr)
        if not args.quick:
            run_once(binary, extra_env)  # discarded warm-up run
        runs = [run_once(binary, extra_env) for _ in range(reps)]
        regime = runs[-1][1]
        runs = [r for r, _ in runs]
        median = dict(runs[0])
        for key in runs[0]:
            try:
                median[key] = statistics.median(float(r[key]) for r in runs)
            except ValueError:
                pass  # non-numeric fields (lang, checksum) keep the first run's value
        thrs = [float(r["thr_ops_s"]) for r in runs]
        spread = (max(thrs) - min(thrs)) / statistics.median(thrs) * 100
        rows.append((case, label, median, spread, regime))
        workload = (case, extra_env.get("BENCH_HEAVY_EVERY", ""))
        for r in runs:
            checksums.setdefault(workload, set()).add(r["checksum"])

    for workload, sums in checksums.items():
        if len(sums) > 1:
            sys.exit(f"CHECKSUM MISMATCH in {workload}: {sums} — implementations diverge")

    print("\n| case | impl | " + " | ".join(h for _, h in COLUMNS) + " | thr spread |")
    print("|" + "---|" * (len(COLUMNS) + 3))
    for case, label, median, spread, _ in rows:
        cells = " | ".join(fmt(k, median[k]) for k, _ in COLUMNS)
        print(f"| {case} | {label} | {cells} | {spread:.0f}% |")
    print("\nchecksums per workload:", {w: sorted(s) for w, s in checksums.items()})
    for case, label, median, _, regime in rows:
        if "numgc" in median:
            print(f"  {case} {label}: numgc={median['numgc']} "
                  f"gc_pause_total_ms={median['gc_pause_total_ms']} gogc={median['gogc']}")
        if regime:
            print(f"  {case} {label}: {regime}")


if __name__ == "__main__":
    main()
