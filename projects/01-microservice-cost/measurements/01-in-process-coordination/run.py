#!/usr/bin/env python3
"""Build the pair, prove the regime, gate on the checksum, record the sweep.

    ./run.py [sweep.toml] [--build] [--clean] [--quick]

The two Go binaries do the measuring. This reads the matrix out of the TOML,
refuses to report when the two kernels folded different checksums or when a
binary does not contain the instructions its row claims, and hands the
distribution to bench.py, which writes it down beside the machine.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tomllib
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BIN = HERE / "bin"
GO = HERE / "variants" / "go"

sys.path.insert(0, str(ROOT))
import bench  # noqa: E402  the harness: pinning, the gate, the summary, the record

SOURCES = [
    "kernel, gonum floats.DivTo: https://github.com/gonum/gonum/blob/master/internal/asm/f64/stubs_noasm.go",
    "its assembly twin: https://github.com/gonum/gonum/blob/master/internal/asm/f64/divto_amd64.s",
    "the simd package: https://go.dev/blog/simd-experiment",
    "prior art, DivTo at lengths 16-128 on an i7-11370H: https://gorse.io/posts/go-simd-benchmark",
]


def matrix(cfg: dict) -> list[tuple[str, str, str]]:
    """(row label, variant, GOAMD64) for every cell of the comparison set."""
    return [(f"{v}@{a}", v, a)
            for a in cfg["experiment"]["goamd64"]
            for v in cfg["experiment"]["variants"]]


def build(cfg: dict) -> None:
    """One binary per cell. GOAMD64 is the only difference between builds."""
    BIN.mkdir(exist_ok=True)
    for _, variant, amd64 in matrix(cfg):
        subprocess.run(["go", "build", "-o", str(BIN / f"{variant}-{amd64}"), f"./{variant}"],
                       cwd=GO, env=dict(os.environ, GOAMD64=amd64), check=True)


def regime(binary: Path, packed_wanted: bool) -> str:
    """Refuse a row whose binary does not hold the instructions it claims.

    Each binary links only the kernel it calls; the other is dead code. A scalar
    row containing a packed divide, or a vector row containing none, is not the
    row it says it is, and its number would be unattributable afterwards.
    """
    out = subprocess.run(["go", "tool", "objdump", "-s", r"divto\.", str(binary)],
                         capture_output=True, text=True, check=True).stdout
    packed, scalar = out.count("DIVPD"), out.count("DIVSD")
    if packed_wanted and packed == 0:
        raise RuntimeError(f"{binary.name}: no packed divide in the kernel")
    if not packed_wanted and packed:
        raise RuntimeError(f"{binary.name}: {packed} packed divides in a scalar row")
    return f"DIVSD={scalar} DIVPD={packed}"


def measure(binary: Path, cfg: dict, sizes: list[int]) -> dict[int, dict[str, str]]:
    """Run one binary over the whole sweep, pinned, and return its RESULT lines."""
    out = bench.run([str(binary),
                     "-sizes", ",".join(str(n) for n in sizes),
                     "-visits", str(cfg["run"]["element_visits"]),
                     "-samples", str(cfg["run"]["samples"]),
                     "-warmup", str(cfg["run"]["warmup_samples"])],
                    cores=cfg["run"]["cores"])
    rows = {}
    for line in out.splitlines():
        if line.startswith("RESULT "):
            fields = dict(kv.split("=", 1) for kv in line.split()[1:])
            rows[int(fields["elements"])] = fields
    if len(rows) != len(sizes):
        raise RuntimeError(f"{binary.name} reported {len(rows)} sizes, expected {len(sizes)}")
    return rows


def crossover(sizes: list[int], summary: dict[str, dict[int, dict]], cfg: dict) -> None:
    """Print the ordering as the size grows, so the flip needs no second pass."""
    labels = [label for label, _, _ in matrix(cfg)]
    plain, vector = cfg["experiment"]["variants"]
    levels = cfg["experiment"]["goamd64"]
    print("\n| elements | " + " | ".join(labels) + " | "
          + " | ".join(f"{plain}/{vector}@{a}" for a in levels) + " |")
    print("|" + "---|" * (len(labels) + len(levels) + 1))
    for n in sizes:
        med = {label: summary[label][n]["median"] for label in labels}
        ratios = [med[f"{plain}@{a}"] / med[f"{vector}@{a}"] for a in levels]
        cells = " | ".join(f"{med[label]:.3f}" for label in labels)
        print(f"| {n} | {cells} | " + " | ".join(f"{r:.2f}x" for r in ratios) + " |")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", nargs="?", default="sweep.toml", help="the sweep TOML")
    parser.add_argument("--build", action="store_true", help="build the binaries and stop")
    parser.add_argument("--clean", action="store_true", help="remove the binaries")
    parser.add_argument("--quick", action="store_true", help="the small sizes only, as a smoke test")
    args = parser.parse_args()
    cfg = tomllib.loads((HERE / args.config).read_text())
    plain, vector = cfg["experiment"]["variants"]
    if "simd" not in os.environ.get("GOEXPERIMENT", ""):
        raise SystemExit("GOEXPERIMENT=simd is required; make exports it, so run make bench")

    if args.clean:
        for _, variant, amd64 in matrix(cfg):
            (BIN / f"{variant}-{amd64}").unlink(missing_ok=True)
        return
    build(cfg)
    if args.build:
        return

    sizes = cfg["sweep"]["values"]
    if args.quick:
        sizes = sizes[:6]
        cfg["run"] = dict(cfg["run"], element_visits=100_000, samples=3, warmup_samples=1)
    # Read before measuring: the load that decides whether this is a baseline is
    # the load the run started under, not the one it leaves behind.
    load15 = float(Path("/proc/loadavg").read_text().split()[2])

    summary: dict[str, dict[int, dict]] = {}
    checksums: dict[int, dict[str, str]] = {n: {} for n in sizes}
    for label, variant, amd64 in matrix(cfg):
        binary = BIN / f"{variant}-{amd64}"
        print(f"# {label}: {regime(binary, variant == vector)}", file=sys.stderr)
        measured = measure(binary, cfg, sizes)
        summary[label] = {}
        for n, fields in measured.items():
            if fields["goamd64"] != amd64 or fields["kernel"] != variant:
                raise RuntimeError(f"{binary.name} reports {fields['kernel']}@{fields['goamd64']}")
            summary[label][n] = bench.summarise([float(v) for v in fields["ns_per_elem"].split(",")])
            checksums[n][label] = fields["checksum"]

    rows = {}
    for n in sizes:
        bench.gate(checksums[n])
        for label in summary:
            rows[f"n={n} {label}"] = summary[label][n]

    status = "verified" if load15 <= cfg["run"]["max_load_15m"] else "structure"
    title = f"{cfg['experiment']['name']}-{datetime.now(timezone.utc):%H%M}"
    out = bench.record(HERE / "results", title, rows, cfg["run"]["cores"], SOURCES, status)
    crossover(sizes, summary, cfg)
    print(f"\nwrote {out} as {status}, 15-minute load {load15} against a limit of "
          f"{cfg['run']['max_load_15m']}")


if __name__ == "__main__":
    main()
