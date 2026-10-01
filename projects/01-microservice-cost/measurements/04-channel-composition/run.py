#!/usr/bin/env python3
"""Run every composition at every sweep point, gate on the checksum, record.

Usage: ./run.py sweep.toml [--quick]

Each binary prints one RESULT line. A row is a distribution over repetitions:
the recorded table carries low, median, high and spread of ns_per_tick, and the
detail table beneath it carries the median residence-time and scheduler columns,
which are what separate queueing from work. Every composition and every
repetition at one sweep point must fold to the same checksum or nothing is
printed at all.
"""

import argparse
import statistics
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3]))

import bench  # noqa: E402  the harness: pinning, the checksum gate, the record

DETAIL = [
    ("msgs_per_tick", "msgs/tick"),
    ("p50_ns", "p50"),
    ("p99_ns", "p99"),
    ("p999_ns", "p99.9"),
    ("max_ns", "max"),
    ("cpu_cores", "cores"),
    ("spawned", "goroutines"),
    ("sched_p50_ns", "sched p50"),
    ("sched_p99_ns", "sched p99"),
    ("alloc_mb", "alloc MB"),
]


def measure(comp, flags, cores):
    """One run of one composition, pinned by the harness, parsed."""
    out = bench.run([str(HERE / "bin" / comp), *flags], cores=cores)
    for line in out.splitlines():
        if line.startswith("RESULT "):
            row = dict(kv.split("=", 1) for kv in line.split()[1:])
            row["msgs_per_tick"] = float(row["msgs"]) / float(row["ticks"])
            return row
    sys.exit(f"no RESULT line from {comp}")


def detail_table(detail, reps):
    head = " | ".join(h for _, h in DETAIL)
    lines = ["", f"Medians over {reps} repetitions. `direct` is the pure-work row:",
             "every other row minus it is the composition's overhead, and",
             "`sched p99` is the runtime's own queueing, measured off my clock.", "",
             f"| row | {head} |", "|---|" + "---:|" * len(DETAIL)]
    for label, cells in detail.items():
        lines.append(f"| {label} | " + " | ".join(f"{cells[k]:.1f}" for k, _ in DETAIL) + " |")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="the sweep TOML")
    parser.add_argument("--quick", action="store_true", help="one small point, gate only")
    args = parser.parse_args()
    with open(args.config, "rb") as handle:
        cfg = tomllib.load(handle)

    graph, run = cfg["graph"], cfg["run"]
    points, reps = cfg["sweep"]["points"], run["reps"]
    if args.quick:
        points, reps = [cfg["quick"]], cfg["quick"]["reps"]
    cores = run["cores"]

    machine: dict = {}
    if not args.quick:
        machine = bench.claim(cores, lambda: bench.run(["make", "-C", str(HERE), "build"]))
    rows, detail, agreed = {}, {}, {}
    for point in points:
        flags = [f"-depth={graph['depth']}", f"-width={graph['width']}",
                 f"-fanout={graph['fanout']}", f"-work={point['work']}",
                 f"-ticks={point['ticks']}", f"-sample-every={run['sample_every']}",
                 f"-buffer={run['buffer']}", f"-batch={run['batch']}"]
        checksums = {}
        for comp in cfg["experiment"]["variants"]:
            label = f"{comp} work={point['work']}"
            print(f"# {label}: warm-up + {reps} reps", file=sys.stderr)
            if not args.quick:
                measure(comp, flags, cores)  # discarded warm-up repetition
            measured = [measure(comp, flags, cores) for _ in range(reps)]
            rows[label] = bench.summarise([float(r["ns_per_tick"]) for r in measured])
            detail[label] = {k: statistics.median(float(r[k]) for r in measured)
                             for k, _ in DETAIL}
            for i, r in enumerate(measured):
                checksums[f"{comp}#{i}"] = r["checksum"]
        at = f"work={point['work']}"
        agreed[at] = bench.gate(checksums)
        print(f"# {at}: {len(checksums)} runs, checksum {agreed[at]}", file=sys.stderr)

    if args.quick:
        print(f"every composition folded to the same checksum at work={points[0]['work']}")
        return

    bench.record(HERE / "results", cfg["experiment"]["name"], rows, cores,
                 sources=["variants/go", "sweep.toml", "QUESTION.md"], before=machine,
                 checksums=agreed, detail=detail_table(detail, reps))


if __name__ == "__main__":
    main()
