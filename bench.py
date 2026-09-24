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
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import median

ROOT = Path(__file__).parent


def run(command: list[str], cwd: Path | None = None, cores: list[int] | None = None) -> str:
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
    done = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)
    if done.returncode != 0:
        raise RuntimeError(f"{' '.join(command)} exited {done.returncode}\n{done.stderr.strip()}")
    return done.stdout


def gate(checksums: dict[str, object]) -> None:
    """Raise unless every variant folded its work to the same checksum."""
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
           sources: list[str], status: str = "verified") -> Path:
    """Write one dated result file and return its path.

    Status is "structure" when the host was contended; such a run is shape,
    never a baseline, and the file has to say so itself.
    """
    machine = fingerprint()
    stamp = datetime.now(timezone.utc)
    results.mkdir(parents=True, exist_ok=True)
    out = results / f"{stamp:%Y%m%d}-{title}.md"
    head = {
        "title": title, "date": f"{stamp:%Y-%m-%d}", "status": status,
        "host": machine.get("cpu_model", "unknown"), "cpus": machine.get("cpus"),
        "kernel": machine.get("kernel"), "governor": machine.get("governor") or "unreadable",
        "turbo": machine.get("turbo"), "load_at_start": machine.get("load_avg"),
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
