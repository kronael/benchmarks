#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Lint the paths given, and fail when a formatter has something to say.

    ./lint.py variants/go [variants/rust] [run.py variants/python]

`gofmt -l` and `cargo fmt --check` are the reason this file exists. gofmt lists
unformatted files on stdout and exits 0, so a Make recipe that calls it reports
green over an unformatted tree. Here the listing is the failure.

Each path is linted by what it holds: a go.mod gets gofmt and go vet, a
Cargo.toml gets cargo fmt and clippy, anything else goes to ruff.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def sh(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    print(f"+ {' '.join(command)}", file=sys.stderr)
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)


def fail(what: str, done: subprocess.CompletedProcess) -> str:
    return f"{what}\n{done.stdout.strip()}\n{done.stderr.strip()}".strip()


def go(path: Path) -> list[str]:
    """gofmt's listing is a failure, and go vet's exit code is its own."""
    bad = []
    listed = sh(["gofmt", "-l", "."], cwd=path)
    if listed.returncode != 0:
        bad.append(fail(f"gofmt failed in {path}", listed))
    elif listed.stdout.strip():
        bad.append(f"unformatted Go files in {path}:\n{listed.stdout.strip()}")
    vet = sh(["go", "vet", "./..."], cwd=path)
    if vet.returncode != 0:
        bad.append(fail(f"go vet failed in {path}", vet))
    return bad


def rust(path: Path) -> list[str]:
    bad = []
    for command in (["cargo", "fmt", "--check"], ["cargo", "clippy", "--", "-D", "warnings"]):
        done = sh(command, cwd=path)
        if done.returncode != 0:
            bad.append(fail(f"{command[1]} failed in {path}", done))
    return bad


def python(path: Path) -> list[str]:
    done = sh(["uvx", "ruff@0.14.3", "check", str(path)])
    return [fail(f"ruff failed on {path}", done)] if done.returncode != 0 else []


def main() -> None:
    if not sys.argv[1:]:
        raise SystemExit(__doc__)
    bad = []
    for name in sys.argv[1:]:
        path = Path(name).resolve()
        if not path.exists():
            raise SystemExit(f"no such path: {name}")
        if (path / "go.mod").exists():
            bad += go(path)
        elif (path / "Cargo.toml").exists():
            bad += rust(path)
        else:
            bad += python(path)
    if bad:
        raise SystemExit("\n\n".join(bad))
    print("lint clean")


if __name__ == "__main__":
    main()
