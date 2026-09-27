# Bugs

Open defects, recorded on discovery and not fixed in the same breath. A fix
needs its own pass, so the record stays honest about what is still wrong.

## Open

### The documented pin names cores that do not exist (2026-09-27)

`CLAUDE.md:117` gives the run command as
`sudo chrt -f 80 taskset -c 2,3 <command>`. This host publishes `0-1` in both
`/sys/devices/system/cpu/possible` and `/sys/devices/system/cpu/online`, and
`nproc` reports 2. CPUs 2 and 3 do not exist, so that command fails.

Every measurement inherits the wrong command from the method document. The
substitution is `-c 0,1`, which pins the same way against the cores that are
here. Two agents reached this independently.

Only the core list is wrong. `sudo -n chrt -f 80 taskset -c 0,1 true` returns 0
once the Bash sandbox is off, so real-time priority stays available. Both
agents reported `sudo` as blocked; that was their own sandbox, and taking the
fallback would have left the tail unprotected.

Fixing `CLAUDE.md` changes the method statement, so it waits for sign-off.

### make record writes the fingerprint to stdout and not into results (2026-09-27)

`mk/measurement.mk` defines `record` as
`uv run --project $(ROOT) $(ROOT)/bench.py fingerprint`, which prints to
stdout. Nothing lands in `results/`. A result file therefore carries its
machine only when the caller redirects the whole of `make bench`.

`CLAUDE.md` says the runner writes the fingerprint into every result file and
never a human. Today the runner does not.

### The rsx lift left the Rust variant without its binaries (2026-09-27)

`projects/01-microservice-cost/measurements/02-scheduling-under-load/variants/rust`
holds only `src/lib.rs`. The four binary sources never came across, so cases
A, B, P1 and P2 cannot run and the measurement has no cross-language row.

### The checksum gate passes when a workload holds one row (2026-09-27)

`run.py` in measurement 02 gates on `len(sums) > 1`, so a workload with a
single row is reported green while it compares nothing. With the Rust binaries
missing, every case A and case B workload passes without proving identical
work. This is the failure mode `CLAUDE.md` warns about: a benchmark fails
quietly where ordinary code fails loudly.

### The project FINDING names five steps and four exist (2026-09-27)

`projects/01-microservice-cost/FINDING.md` says "Missing: all five steps".
`measurements/` holds four directories. Either a measurement is unwritten or
the count is wrong.
