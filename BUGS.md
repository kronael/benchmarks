# Bugs

Open defects, recorded on discovery and not fixed in the same breath. A fix
needs its own pass, so the record stays honest about what is still wrong.

## Method document

### The documented pin names cores that do not exist (2026-09-27)

`CLAUDE.md:117` gives the run command as
`sudo chrt -f 80 taskset -c 2,3 <command>`. This host publishes `0-1` in both
`/sys/devices/system/cpu/possible` and `/sys/devices/system/cpu/online`, and
`nproc` reports 2. CPUs 2 and 3 do not exist, so that command fails.

Every measurement inherits the wrong command from the method document. The
substitution is `-c 0,1`, which pins the same way against the cores that are
here. Two agents reached this independently.

Only the core list is wrong. `sudo -n chrt -f 80 taskset -c 0,1 true` returns 0
once the Bash sandbox is off, so real-time priority stays available.

Fixing `CLAUDE.md` changes the method statement, so it waits for sign-off.

### The load gate cannot tell my own run from someone else's (2026-09-27)

`bench.QUIET_LOAD_15` compares the 15-minute average against 1.6, and that
average includes the benchmark runs this repository just finished. Four
measurements run back to back therefore file the later ones as `structure` on
the strength of their own predecessors, which is not the contention the rule was
written about.

A run is still never upgraded by this defect, only downgraded, so no number is
overstated. The fix is either a longer gap between runs or a gate that reads
only the load outside the pinned cores, and both change the method.

## Measurement 02 — scheduling under load

### The rsx lift left the Rust variant without its binaries (2026-09-27)

`variants/rust` holds only `src/lib.rs`. The four binary sources never came
across, so cases A, B, P1 and P2 cannot run and the measurement has no
cross-language row. Case C, which is the axis this measurement predicts, is
Go-only and unaffected.

The checksum gate now refuses these cases rather than passing them: a workload
that reaches the gate with one row raises. Before that, every case A and case B
workload reported green while comparing nothing.

## Toolchain

### staticcheck cannot read go1.27 export data (2026-09-27)

The copy of staticcheck on this host fails with "export data version 4 is
greater than maximum supported version 2" against the pinned go1.27.1
toolchain, so `lint.py` runs `gofmt` and `go vet` only.

Either upgrade staticcheck or say in the method that `go vet` is the analyser.
