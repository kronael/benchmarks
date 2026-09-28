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

### The load gate reads a number that is not about the pinned cores (2026-09-27)

`bench.QUIET_LOAD_15` gates on `/proc/loadavg`, which is the host's and is not
namespaced. It counts runnable tasks across every CPU the host has, while a
measurement runs inside this container's two-CPU cpuset. The two numbers are not
commensurable, and measurement disproves the assumption that they track:

| moment | host load 15m | pinned cores 0-1 |
|---|---:|---|
| during measurement 02 | 36.2 | 17% idle, zero steal, 14% of capacity mine |
| during measurement 02, later | 10.6 | 76% busy |

A host load of 36 said nothing about cores 0-1, and the 69% of those two cores
that a neighbour held is invisible in the load average. The gate also counts this
repository's own finished runs, so four measurements in a row downgrade each
other.

`bench.contention()` now samples the busy fraction of the pinned cores before the
run and every result file carries it as `busy_on_pinned_cores_at_start`. It does
NOT yet decide the status.

**Proposal, needs sign-off.** Gate on `busy_on_pinned_cores_at_start` instead of
the host load average, at roughly 10%, and keep the load average as fingerprint
only. This changes the method statement in `CLAUDE.md`, which is why it is a
proposal: every result recorded so far is labelled by the old gate, and the two
labels do not agree.

## Measurement 02 — scheduling under load

### The rsx lift left the Rust variant without its binaries (2026-09-27)

`variants/rust` holds only `src/lib.rs`. The four binary sources never came
across, so cases A, B, P1 and P2 cannot run and the measurement has no
cross-language row. Case C, which is the axis this measurement predicts, is
Go-only and unaffected.

The checksum gate now refuses these cases rather than passing them: a workload
that reaches the gate with one row raises. Before that, every case A and case B
workload reported green while comparing nothing.

### Half of measurement 02's sweep exceeds the latency field (2026-09-28)

`casec/main.go` stores a request's latency in `uint32` nanoseconds and clamps at
4,294,967,295 ns. At 16 and 20 bursts/s the scalar rows clamp 228,886 and
268,836 of 600,000 requests, so their p99 and p99.9 are the ceiling and their
recorded spread of 0.0 is saturation rather than precision.

The row reports its own `clamped=` count, so no result is silently wrong and the
finding excludes those points. But three of the six swept values cannot be
measured with the field as it stands, which makes half the sweep dead weight.

Fix is either a `uint64` latency field or a sweep that stops at the knee. Both
change what the measurement claims to cover, so this waits for sign-off.

## Toolchain

### staticcheck cannot read go1.27 export data (2026-09-27)

The copy of staticcheck on this host fails with "export data version 4 is
greater than maximum supported version 2" against the pinned go1.27.1
toolchain, so `lint.py` runs `gofmt` and `go vet` only.

Either upgrade staticcheck or say in the method that `go vet` is the analyser.
