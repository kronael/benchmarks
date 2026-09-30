#!/usr/bin/env python3
"""Run the ladder: one server and one client process per row, each on its own core.

Usage: ./run.py [sweep.toml] [--quick] [--rows go-udp,go-http]

Every client prints one RESULT line. This runner discards one warm-up rep,
keeps `reps` measured reps, takes the per-metric median across them, and refuses
to report if the ten rows disagree on the checksum at any payload size — that
gate spans two languages and four transports, so identical work is proved rather
than assumed. The result file and its machine fingerprint come from the repo's
bench.py, which is the only place a result is allowed to be written from.
"""

from __future__ import annotations

import argparse
import os
import shutil
import statistics
import subprocess
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
import bench  # noqa: E402  the repo harness; ROOT has to be on the path first

VENV = HERE / "variants" / "python" / ".venv" / "bin" / "python"
PYDIR = HERE / "variants" / "python"
DIST = HERE / "dist"

# (rung, row, effort, server program, client program, tuned)
MATRIX = [
    ("1a", "py-http", "worst", PYDIR / "httpsrv.py", PYDIR / "httpcli.py", False),
    ("1a", "py-http", "medium", PYDIR / "httpsrv.py", PYDIR / "httpcli.py", True),
    ("1b", "py-ws", "worst", PYDIR / "wssrv.py", PYDIR / "wscli.py", False),
    ("1b", "py-ws", "medium", PYDIR / "wssrv.py", PYDIR / "wscli.py", True),
    ("2", "go-grpc", "worst", DIST / "grpcsrv", DIST / "grpccli", False),
    ("2", "go-grpc", "medium", DIST / "grpcsrv", DIST / "grpccli", True),
    ("3", "go-udp", "worst", DIST / "udpsrv", DIST / "udpcli", False),
    ("3", "go-udp", "medium", DIST / "udpsrv", DIST / "udpcli", True),
    ("C", "go-http", "worst", DIST / "httpsrv", DIST / "httpcli", False),
    ("C", "go-http", "medium", DIST / "httpsrv", DIST / "httpcli", True),
]

METRICS = ["min_ns", "p50_ns", "p99_ns", "p999_ns", "max_ns"]


def argv_for(program: Path, core: int) -> list[str]:
    """Pin the program to one core. An unpinned run is not comparable, so no fallback."""
    taskset = shutil.which("taskset")
    if taskset is None:
        raise RuntimeError("taskset not found; an unpinned run is not comparable")
    launcher = [str(VENV)] if program.suffix == ".py" else []
    if launcher and not VENV.exists():
        raise RuntimeError(f"{VENV} missing; run make prepare first")
    if not launcher and not program.exists():
        raise RuntimeError(f"{program} missing; run make build first")
    return [taskset, "-c", str(core), *launcher, str(program)]


def run_row(row: tuple, payload: int, run_cfg: dict) -> dict[str, str]:
    """Start the server, wait for READY, run the client once, return its RESULT fields."""
    _, _, _, server_program, client_program, tuned = row
    env = dict(
        os.environ,
        BENCH_ADDR="127.0.0.1:0",
        BENCH_PAYLOAD_BYTES=str(payload),
        BENCH_OPS=str(run_cfg["ops"]),
        BENCH_WARMUP=str(run_cfg["warmup"]),
        BENCH_TUNED="1" if tuned else "0",
        PYTHONPATH=str(PYDIR),
    )
    server = subprocess.Popen(
        argv_for(server_program, run_cfg["server_core"]), env=env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    try:
        hello = server.stdout.readline()
        if not hello.startswith("READY "):
            raise RuntimeError(f"{server_program} never bound: {server.stderr.read().strip()}")
        env["BENCH_ADDR"] = hello.split(maxsplit=1)[1].strip()
        done = subprocess.run(
            argv_for(client_program, run_cfg["client_core"]), env=env,
            capture_output=True, text=True, check=False,
        )
        if done.returncode != 0:
            raise RuntimeError(f"{client_program} exited {done.returncode}\n{done.stderr.strip()}")
        for line in done.stdout.splitlines():
            if line.startswith("RESULT "):
                return dict(pair.split("=", 1) for pair in line.split()[1:])
        raise RuntimeError(f"no RESULT line from {client_program}")
    finally:
        server.terminate()
        server.wait(timeout=10)


def measure(row: tuple, payload: int, run_cfg: dict, warm: bool) -> dict[str, float | str]:
    """One cell: reps measured runs plus a discarded warm-up, median per metric."""
    if warm:
        run_row(row, payload, run_cfg)
    runs = [run_row(row, payload, run_cfg) for _ in range(run_cfg["reps"])]
    checksums = {run["checksum"] for run in runs}
    if len(checksums) > 1:
        raise RuntimeError(f"{row[1]} {row[2]} @{payload} differs across reps: {checksums}")
    cell: dict[str, float | str] = {"checksum": runs[0]["checksum"], "samples": int(runs[0]["samples"])}
    for metric in METRICS:
        cell[metric] = statistics.median(float(run[metric]) for run in runs)
    return cell


def load(config_path: Path, quick: bool) -> tuple[list[int], dict]:
    config = tomllib.loads(config_path.read_text())
    run_cfg = dict(config["run"])
    values = config["sweep"]["values"]
    if quick:
        run_cfg.update({k: v for k, v in config["quick"].items() if k != "values"})
        values = config["quick"]["values"]
    return values, run_cfg


def report(cells: dict, values: list[int], run_cfg: dict, quick: bool,
           wanted: list[str], machine: dict[str, float]) -> None:
    """Print the ladder, then write the dated result file through bench.py."""
    matrix = [row for row in MATRIX if row[1] in wanted]
    header = "| rung | row | effort | " + " | ".join(f"{v}B p50/p99 µs" for v in values) + " |"
    print("\n" + header)
    print("|" + "---|" * (len(values) + 3))
    for rung, name, effort, *_ in matrix:
        line = f"| {rung} | {name} | {effort} |"
        for payload in values:
            cell = cells[(name, effort, payload)]
            line += f" {cell['p50_ns'] / 1000:.2f} / {cell['p99_ns'] / 1000:.2f} |"
        print(line)

    if quick:
        print("\nquick run: checksums agree across all rows, numbers are not a measurement")
        return

    rows = {}
    for rung, name, effort, *_ in matrix:
        for payload in values:
            cell = cells[(name, effort, payload)]
            rows[f"{rung} {name} {effort} @{payload}B"] = {
                "samples": cell["samples"],
                "low": cell["min_ns"] / 1000,
                "median": cell["p50_ns"] / 1000,
                "high": cell["max_ns"] / 1000,
                "spread": (cell["max_ns"] - cell["min_ns"]) / 1000,
            }
    out = bench.record(
        HERE / "results", "transport-ladder-rtt-us", rows,
        [run_cfg["server_core"], run_cfg["client_core"]],
        sources=["variants/go", "variants/python", "sweep.toml", "notes/design.md"],
        before=machine,
    )
    tail = ["", "| rung | row | effort | payload | p50 µs | p99 µs | p99.9 µs | checksum |",
            "|---|---|---|---:|---:|---:|---:|---|"]
    for rung, name, effort, *_ in matrix:
        for payload in values:
            cell = cells[(name, effort, payload)]
            tail.append(f"| {rung} | {name} | {effort} | {payload} | {cell['p50_ns'] / 1000:.2f} "
                        f"| {cell['p99_ns'] / 1000:.2f} | {cell['p999_ns'] / 1000:.2f} "
                        f"| {cell['checksum']} |")
    tail += ["", f"reps: {run_cfg['reps']} measured plus one discarded, ops {run_cfg['ops']}, "
             f"warmup {run_cfg['warmup']}; every cell is the median across reps.",
             "One checksum per payload size across all ten rows: identical work is gated, "
             "not assumed."]
    with out.open("a") as handle:
        handle.write("\n".join(tail) + "\n")
    print(f"\nwrote {out}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("config", nargs="?", default=str(HERE / "sweep.toml"))
    parser.add_argument("--quick", action="store_true", help="the make test run: no warm-up rep")
    parser.add_argument("--rows", default="", help="comma-separated row names, default all")
    args = parser.parse_args()
    values, run_cfg = load(Path(args.config), args.quick)
    wanted = args.rows.split(",") if args.rows else [row[1] for row in MATRIX]

    cores = [run_cfg["server_core"], run_cfg["client_core"]]
    if not args.quick:
        bench.claim(cores, lambda: bench.run(["make", "-C", str(HERE), "build"]))
    machine = bench.before(cores)
    cells = {}
    for payload in values:
        for row in MATRIX:
            if row[1] not in wanted:
                continue
            print(f"# {row[1]} {row[2]} @{payload}B", file=sys.stderr, flush=True)
            cells[(row[1], row[2], payload)] = measure(row, payload, run_cfg, not args.quick)
        bench.gate({f"{row[1]} {row[2]} @{payload}B": cells[(row[1], row[2], payload)]["checksum"]
                    for row in MATRIX if row[1] in wanted})
    report(cells, values, run_cfg, args.quick, wanted, machine)


if __name__ == "__main__":
    main()
