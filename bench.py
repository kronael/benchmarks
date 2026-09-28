# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Everything a measurement needs from the harness, and nothing else.

The benchmark programs do the measuring. This only runs them on the cores you
chose, refuses to report when they did different work, and writes the result
down with the machine beside it. If it grows past one screen, something that
belongs in a variant has leaked into here.

    uv run bench.py fingerprint
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from statistics import median

ROOT = Path(__file__).parent

QUIET_LOAD_15 = 1.6


def run(command: list[str], cwd: Path | None = None, cores: list[int] | None = None,
        env: dict[str, str] | None = None) -> str:
    """Run a command, pinned when cores are given, and return its stdout.

    Pinning is not tuning. Unpinned threads report their own migration as the
    thing under test: in rsx that alone moved a transport's high tail by 21%
    and reversed the published conclusion. An absent taskset raises rather
    than running unpinned, because an unpinned run looks identical afterwards.
    """
    if cores:
        taskset = shutil.which("taskset")
        if taskset is None:
            raise RuntimeError("taskset not found; an unpinned run is not comparable")
        command = [taskset, "-c", ",".join(str(c) for c in cores), *command]
    done = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True,
                          check=False)
    if done.returncode != 0:
        raise RuntimeError(f"{' '.join(command)} exited {done.returncode}\n{done.stderr.strip()}")
    return done.stdout


def load15() -> float:
    """The 15-minute load average. Read it before the run it judges, never after."""
    return os.getloadavg()[2]


def _jiffies(cores: list[int]) -> tuple[int, int]:
    """Busy and total jiffies across the named CPUs, from /proc/stat."""
    wanted = {f"cpu{c}" for c in cores}
    busy = idle = 0
    for line in Path("/proc/stat").read_text().splitlines():
        fields = line.split()
        if fields[0] in wanted:
            values = [int(v) for v in fields[1:]]
            idle += values[3] + values[4]
            busy += sum(values) - values[3] - values[4]
    return busy, busy + idle


def contention(cores: list[int], window: float = 1.0) -> float:
    """Busy fraction of the pinned cores, sampled before the run that it judges.

    /proc/loadavg is the host's and counts CPUs this cpuset cannot use, so it is
    not commensurable with a two-core slice. Measured here: a host load of 36
    over pinned cores that were 17% idle, of which the benchmark itself held 14%
    and a neighbour 69%. Per-CPU time is commensurable, and sampled before the
    benchmark starts it measures the neighbours rather than the benchmark.
    """
    was = _jiffies(cores)
    time.sleep(window)
    now = _jiffies(cores)
    busy, total = now[0] - was[0], now[1] - was[1]
    return busy / total if total else 0.0


def before(cores: list[int]) -> dict[str, float]:
    """Every machine reading that must be taken BEFORE the run, never after."""
    return {"load15": load15(), "busy_on_pinned_cores": contention(cores)}


def gate(checksums: dict[str, object]) -> None:
    """Raise unless two or more rows folded their work to the same checksum.

    The count is gated as well as the value. One row satisfies any equality test
    while comparing nothing, and a comparison of one row is the quiet failure
    this harness exists to catch.
    """
    if len(checksums) < 2:
        raise RuntimeError(f"a gate over {len(checksums)} row proves nothing: {sorted(checksums)}")
    if len(set(checksums.values())) > 1:
        detail = ", ".join(f"{k}={v}" for k, v in sorted(checksums.items()))
        raise RuntimeError(f"variants did not do identical work: {detail}")


def summarise(values: list[float]) -> dict:
    """Low, median, high and spread. Never a mean alone — the spread is a finding."""
    ordered = sorted(values)
    return {
        "samples": len(ordered),
        "low": ordered[0],
        "median": median(ordered),
        "high": ordered[-1],
        "spread": ordered[-1] - ordered[0],
    }


def fingerprint() -> dict:
    """What the machine was, at the moment of the run."""
    binary = ROOT / "dist" / "fingerprint"
    if not binary.exists():
        raise RuntimeError(f"{binary} missing; run make build first")
    return json.loads(run([str(binary)]))


def record(results: Path, title: str, rows: dict[str, dict], cores: list[int],
           sources: list[str], before: dict[str, float]) -> Path:
    """Write one dated result file and return its path.

    The file is named for the minute the record was written, so a second run on
    the same day stands beside the first instead of replacing it: a superseded
    number has to remain auditable next to the one that replaced it.

    `before` comes from before(), taken ahead of the run: a quiet start that ends
    loud is still a baseline, and a loaded start is structure however quiet the
    finish. QUIET_LOAD_15 is the one limit for the whole repository, so no
    measurement can set itself an easier one. The busy fraction of the pinned
    cores is recorded beside it but does not yet decide the status; BUGS.md
    carries that proposal.
    """
    machine = fingerprint()
    stamp = datetime.now(timezone.utc)
    status = "verified" if before["load15"] <= QUIET_LOAD_15 else "structure"
    results.mkdir(parents=True, exist_ok=True)
    out = results / f"{stamp:%Y%m%d-%H%M}-{title}.md"
    head = {
        "title": title, "date": f"{stamp:%Y-%m-%d}", "status": status,
        "host": machine.get("cpu_model", "unknown"), "cpus": machine.get("cpus"),
        "kernel": machine.get("kernel"), "governor": machine.get("governor") or "unreadable",
        "turbo": machine.get("turbo"), "load_at_start": f"{before['load15']:.2f}",
        "load_limit": QUIET_LOAD_15,
        "load_at_end": " ".join(machine.get("load_avg", "").split()[:3]),
        "busy_on_pinned_cores_at_start": f"{before['busy_on_pinned_cores']:.1%}",
        "pinned_cores": cores,
    }
    lines = ["---", *(f"{k}: {v}" for k, v in head.items()), "sources:",
             *(f"  - {s}" for s in sources), "---", "", f"# {title}", "",
             "| variant | samples | low | median | high | spread |",
             "|---|---:|---:|---:|---:|---:|"]
    for name, s in rows.items():
        lines.append(f"| {name} | {s['samples']} | {s['low']:.3f} | {s['median']:.3f} "
                     f"| {s['high']:.3f} | {s['spread']:.3f} |")
    out.write_text("\n".join(lines) + "\n")
    return out


if __name__ == "__main__":
    if sys.argv[1:2] == ["fingerprint"]:
        print(json.dumps(fingerprint(), indent=2))
    else:
        print(__doc__)
