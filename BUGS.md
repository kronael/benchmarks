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

**Fixed 2026-10-01.** The status now decides on `busy_on_pinned_cores_at_start`
against `bench.QUIET_CORES`, set at the 10% the proposal named. The host load
average stays in every result as `host_load_at_start`, because it describes the
machine the slice lives on, but it decides nothing.

Every result recorded before that commit is labelled by the old gate, so a
`verified` stamp dated earlier means only that the host load average was low. It
is not comparable with a `verified` stamp from the new gate, and the superseded
files are kept rather than relabelled.

## Measurement 02 — scheduling under load

### Case A's operating points exceed this box (2026-09-29)

The four Rust twins now exist and every case gates cross-language, so cases A,
B, P1 and P2 can run. Case A's inherited operating points ask for 3.0 and 6.0
cores of burst work against this box's 2.0, so both saturate the `uint32`
latency field and report the ceiling rather than a latency.

`make bench` therefore still runs `--cases C` only. Running A and B by default
needs either retuned `BENCH_HEAVY_EVERY` values for a two-core box or a wider
latency field, and either changes what the inherited comparison means, so it
waits for sign-off.

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
