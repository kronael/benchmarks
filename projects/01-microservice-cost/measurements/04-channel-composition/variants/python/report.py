"""Mirrors ../go/graph/report.go 1:1: the warmup, the counters, the RESULT line.

A discarded warmup pass, then the measured pass with the machine's own counters
differenced across it, then the single RESULT line run.py parses. The measured
pass builds fresh state, so the warmup cannot reach the checksum.

The line carries the Go twin's keys in the Go twin's order, and four of its
columns have no CPython equivalent. They are emitted as NO_EQUIVALENT rather
than as a number that would read as measured:

- `sched_p50_ns` and `sched_p99_ns` are the Go runtime's own
  runnable-to-running histogram, /sched/latencies:seconds. CPython keeps no
  such histogram, and the OS scheduler will not hand one back per process.
- `mutex_wait_ms` is /sync/mutex/wait/total:seconds. CPython exposes no
  contention time for the GIL or for a lock.
- `alloc_mb` is /gc/heap/allocs:bytes. The only stdlib answer is tracemalloc,
  which changes the allocation cost it is there to report.
- `gc_pause_total_ms` has no counterpart: the cyclic collector reports
  collections, not the time it spent in them.

Zero is not the sentinel, because zero is what a Go `direct` row legitimately
reads on the scheduler columns.

Three columns are real here and mean something adjacent rather than identical,
and a table that mixes the rungs has to say so:

- `spawned` counts OS threads this pass started, where the Go twin counts
  goroutines. The counts are comparable; a thread and a goroutine are not.
- `gomaxprocs` is the size of the process's CPU affinity mask, which is what
  GOMAXPROCS is derived from under the same taskset.
- `numgc` is the cyclic collector's collections summed over its generations.
  CPython frees by reference count, so this counts cycle collections only and
  is not a count of the heap being swept.
"""

from __future__ import annotations

import gc
import math
import os
import resource
import time
from collections.abc import Callable
from dataclasses import dataclass, replace

import graph

NO_EQUIVALENT = -1

Composition = Callable[[graph.Config, graph.Clock], int]


def run(name: str, msgs: Callable[[graph.Config], int], composition: Composition) -> None:
    """Drive one composition and print its RESULT line."""
    cfg = graph.configure()
    warm = replace(cfg, ticks=warmup_ticks(cfg))
    composition(warm, graph.Clock(warm))

    before = take()
    clock = graph.Clock(cfg)
    checksum = composition(cfg, clock)
    after = take()
    report(name, msgs(cfg), cfg, warm.ticks, checksum, clock.lat, before, after)


def warmup_ticks(cfg: graph.Config) -> int:
    """An eighth of the measured pass: enough to build and tear down the same
    threads and queues and make the kernel hot."""
    n = cfg.ticks // 8 // cfg.batch * cfg.batch
    return cfg.batch if n < cfg.batch else n


@dataclass(frozen=True, slots=True)
class Counters:
    """The machine's own view of the pass, read twice and differenced, so
    process startup and the warmup are excluded."""

    wall: float
    cpu: float
    rss: int
    spawned: int
    numgc: int


def take() -> Counters:
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return Counters(
        wall=time.perf_counter(),
        cpu=usage.ru_utime + usage.ru_stime,
        rss=usage.ru_maxrss,
        spawned=graph.THREADS.started,
        numgc=sum(stat["collections"] for stat in gc.get_stats()),
    )


def percentile(ordered: list[int], q: float) -> int:
    """Nearest-rank percentile over an ascending-sorted list, mirroring the Go
    twin so a percentile means the same thing in both rungs."""
    if not ordered:
        return 0
    idx = math.ceil(q * len(ordered)) - 1
    return ordered[min(max(idx, 0), len(ordered) - 1)]


def report(name: str, sent: int, cfg: graph.Config, warmup: int, checksum: int,
           lat: list[int], a: Counters, b: Counters) -> None:
    lat.sort()
    wall = b.wall - a.wall
    print(
        f"RESULT comp={name} depth={cfg.depth} width={cfg.width} fanout={cfg.fanout} "
        f"work={cfg.work} ticks={cfg.ticks} warmup={warmup} nodes={cfg.nodes()} "
        f"msgs={sent} batch={cfg.batch} buffer={cfg.buffer} wall_s={wall:.4f} "
        f"ns_per_tick={wall * 1e9 / cfg.ticks:.1f} thr_ticks_s={cfg.ticks / wall:.0f} "
        f"p50_ns={percentile(lat, 0.50)} p99_ns={percentile(lat, 0.99)} "
        f"p999_ns={percentile(lat, 0.999)} max_ns={lat[-1] if lat else 0} "
        f"samples={len(lat)} cpu_cores={(b.cpu - a.cpu) / wall:.2f} "
        f"gomaxprocs={len(os.sched_getaffinity(0))} spawned={b.spawned - a.spawned} "
        f"sched_p50_ns={NO_EQUIVALENT} sched_p99_ns={NO_EQUIVALENT} "
        f"mutex_wait_ms={NO_EQUIVALENT} alloc_mb={NO_EQUIVALENT} "
        f"numgc={b.numgc - a.numgc} gc_pause_total_ms={NO_EQUIVALENT} "
        f"rss_peak_mb={b.rss / 1024.0:.1f} checksum={checksum:x}",
        flush=True,
    )
