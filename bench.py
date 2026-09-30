# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Everything a measurement needs from the harness, and nothing else.

The benchmark programs do the measuring. This only runs them on the cores you
chose, refuses to report when they did different work, and writes the result
down with the machine beside it. Why each rule is here at all is in
notes/harness.md. If this file grows past one screen, something that belongs in
a variant has leaked into it.

    uv run bench.py fingerprint
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from collections.abc import Callable, Mapping
from datetime import datetime, timezone
from pathlib import Path
from statistics import median

ROOT = Path(__file__).parent
TOOLCHAINS = ROOT / "dist" / "toolchains.json"

QUIET_LOAD_15 = 1.6


def run(command: list[str], cwd: Path | None = None, cores: list[int] | None = None,
        env: dict[str, str] | None = None) -> str:
    """Run a command, pinned when cores are given, and return its stdout."""
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


def claim(cores: list[int], build: Callable[[], object] | None = None) -> None:
    """Build, then take the cores by re-executing this script pinned and privileged.

    Returns straight away in the measured pass, which is how `build` runs under
    the caller's toolchain and never under root's. In the pass that starts the
    measured one this does not return: it builds, escalates, and exits with the
    child's status.
    """
    if os.geteuid() == 0:
        return
    run(["make", "-C", str(ROOT), "build"])
    if build is not None:
        build()
    machine = fingerprint()
    TOOLCHAINS.write_text(json.dumps({"toolchains": machine["toolchains"],
                                      "go_env": machine["go_env"]}))
    print(f"# cores {','.join(str(c) for c in cores)} are "
          f"{1 - contention(cores):.1%} idle", file=sys.stderr)
    pinned = ["sudo", "-n", "chrt", "-f", "80", "taskset", "-c",
              ",".join(str(c) for c in cores), sys.executable, *sys.argv]
    print(f"# measured pass: chrt -f 80, cores {pinned[7]}", file=sys.stderr)
    raise SystemExit(subprocess.run(pinned, check=False).returncode)


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
    """Busy fraction of the pinned cores, sampled before the run that it judges."""
    was = _jiffies(cores)
    time.sleep(window)
    now = _jiffies(cores)
    busy, total = now[0] - was[0], now[1] - was[1]
    return busy / total if total else 0.0


def before(cores: list[int]) -> dict[str, float]:
    """Every machine reading that must be taken BEFORE the run, never after."""
    return {"load15": os.getloadavg()[2], "busy_on_pinned_cores": contention(cores)}


def gate(checksums: Mapping[str, str]) -> str:
    """Return the one checksum two or more rows agreed on, or raise."""
    if len(checksums) < 2:
        raise RuntimeError(f"a gate over {len(checksums)} row proves nothing: {sorted(checksums)}")
    agreed = set(checksums.values())
    if len(agreed) > 1:
        detail = ", ".join(f"{k}={v}" for k, v in sorted(checksums.items()))
        raise RuntimeError(f"variants did not do identical work: {detail}")
    return agreed.pop()


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
           sources: list[str], before: dict[str, float], *,
           checksums: Mapping[str, str], detail: str = "") -> Path:
    """Write one dated result file, named for the minute, and return its path.

    `checksums` carries the value each gated point agreed on. The gate already
    refused a mismatch; writing the value down is what makes the claim auditable
    from the file instead of from a console nobody kept.
    """
    machine = fingerprint()
    built = json.loads(TOOLCHAINS.read_text())
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
    lines = ["---", *(f"{k}: {v}" for k, v in head.items()),
             "toolchains:", *(f"  {k}: {v}" for k, v in built["toolchains"].items()),
             "go_env:", *(f"  {k}: {v}" for k, v in built["go_env"].items()),
             "checksums:", *(f"  {k}: {v}" for k, v in checksums.items()),
             "sources:", *(f"  - {s}" for s in sources), "---", "", f"# {title}", "",
             "| variant | samples | low | median | high | spread |",
             "|---|---:|---:|---:|---:|---:|"]
    for name, s in rows.items():
        lines.append(f"| {name} | {s['samples']} | {s['low']:.3f} | {s['median']:.3f} "
                     f"| {s['high']:.3f} | {s['spread']:.3f} |")
    out.write_text("\n".join(lines) + "\n" + detail)
    print(f"wrote {out}, 15-minute load {before['load15']:.2f} at the start against a "
          f"limit of {QUIET_LOAD_15}, pinned cores "
          f"{before['busy_on_pinned_cores']:.1%} busy")
    return out


if __name__ == "__main__":
    if sys.argv[1:2] == ["fingerprint"]:
        print(json.dumps(fingerprint(), indent=2))
    else:
        print(__doc__)
