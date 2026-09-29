"""Mirrors ../go/graph/graph.go 1:1: the fragment all four compositions share.

The calculation graph, its node kernel, the checksum fold and the clock. The
compositions differ in how these nodes are wired and driven and in nothing
else, which is what makes the pair a measurement rather than two programs.

Any change here must land in the Go twin too, or the cross-language checksum
gate stops proving identical work and starts hiding a divergence. Go wraps a
uint64 where Python grows the integer, so every result Go would wrap is masked
to 64 bits here, including the difference inside the kernel's shift, which is a
logical shift of a wrapped subtraction and not an arithmetic one.

The kernel is an integer EMA step in fixed point mixed with MMIX's LCG (Knuth,
TAOCP vol. 2). It is iteration-bounded, never wall-clock-bounded, so a
descheduled node sheds no work, and its result feeds the checksum so it cannot
be optimised away. The fold is FNV-1a's prime and is order-sensitive on
purpose: a join that arrives out of order changes the checksum instead of
passing quietly.

MAX_BATCH is the Go twin's batched message array, which is copied whole on
every send there, so a batch outside 1..32 is rejected here as it is there.
"""

from __future__ import annotations

import argparse
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass

MASK64 = 0xFFFFFFFFFFFFFFFF

EMA_SHIFT = 5
MMIX_MUL = 6364136223846793005
MMIX_ADD = 1442695040888963407

FNV_PRIME = 0x100000001B3

MAX_BATCH = 32

MAX_RESIDENCE_NS = 0xFFFFFFFF - 1


def kernel(state: int, value: int, work: int) -> int:
    """The work. Every composition calls exactly this, the same number of times."""
    s, x = state, value
    for _ in range(work):
        s = (s + (((x - s) & MASK64) >> EMA_SHIFT)) & MASK64
        x = (x * MMIX_MUL + MMIX_ADD) & MASK64
        s ^= x >> 33
    return s


def fold(acc: int, value: int) -> int:
    """Accumulate a value into a checksum, order-sensitively."""
    return ((acc ^ value) * FNV_PRIME) & MASK64


def finish(total: int, state: list[int]) -> int:
    """Fold every node's final state into the sink's running fold, in node order.

    The checksum then covers the whole history and not only what the sink saw.
    """
    for s in state:
        total = fold(total, s)
    return total


class Splitmix64:
    """The PRNG, with the constants of the Go twin and of measurement 02's benchutil."""

    def __init__(self, state: int) -> None:
        self.state = state & MASK64

    def next(self) -> int:
        self.state = (self.state + 0x9E3779B97F4A7C15) & MASK64
        z = self.state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK64
        return z ^ (z >> 31)


@dataclass(frozen=True, slots=True)
class Config:
    """The graph's shape and the run's size. Every composition reads the same one."""

    depth: int
    width: int
    fanout: int
    work: int
    ticks: int
    sample_every: int
    buffer: int
    batch: int

    def nodes(self) -> int:
        """The source, the compute nodes and the sink."""
        return self.depth * self.width + 2

    def edges(self) -> int:
        """Channel messages per tick: every compute level receives width*fanout
        of them and the sink receives width."""
        return self.depth * self.width * self.fanout + self.width

    def parent(self, n: int, j: int) -> int:
        """The topology: node n joins a sliding stencil of fanout neighbours
        from the level below."""
        return (n + j) % self.width

    def states(self) -> list[int]:
        """Seed every compute node distinctly, so no two nodes hold the same
        history and a mis-wired parent shows up in the checksum."""
        return [Splitmix64(node + 1).next() for node in range(self.depth * self.width)]

    def source(self, tick: int, out: list[int]) -> None:
        """Level 0: one tick index fans out to width seed values.

        This is the generated input and it is a pure function of the tick, so
        every composition and every repetition sees the same stream.
        """
        seed = Splitmix64(tick + 1).next()
        for n in range(len(out)):
            out[n] = fold(seed, n)

    def eval_node(self, state: list[int], into: list[int], out: list[int],
                  level: int, n: int) -> None:
        """One node's tick in the direct compositions: join the parents in fixed
        index order, then advance this node's state with the kernel."""
        acc = 0
        for j in range(self.fanout):
            acc = fold(acc, into[self.parent(n, j)])
        node = level * self.width + n
        state[node] = kernel(state[node], acc, self.work)
        out[n] = state[node]


def msgs(cfg: Config) -> int:
    """Channel traffic of a whole measured pass, so the traffic a row pays for
    is visible beside its time."""
    return cfg.ticks * cfg.edges()


def batched_msgs(cfg: Config) -> int:
    return cfg.ticks // cfg.batch * cfg.edges()


def no_msgs(cfg: Config) -> int:
    return 0


def configure() -> Config:
    """Read the shape from flags, spelled as the Go twin's flag package spells them.

    run.py sets them from sweep.toml and passes the same argv to either
    language, so a runner drives both rungs with one list of flags.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-depth", type=int, default=6, help="levels of compute nodes")
    parser.add_argument("-width", type=int, default=4, help="nodes per level")
    parser.add_argument("-fanout", type=int, default=2, help="parents joined per node")
    parser.add_argument("-work", type=int, default=64,
                        help="kernel iterations per node per tick")
    parser.add_argument("-ticks", type=int, default=16384, help="ticks in the measured pass")
    parser.add_argument("-sample-every", type=int, default=64,
                        help="stamp residence time every Nth tick")
    parser.add_argument("-buffer", type=int, default=8,
                        help="queue depth, batched composition only")
    parser.add_argument("-batch", type=int, default=32,
                        help="ticks per message, batched composition only")
    args = parser.parse_args()
    cfg = Config(depth=args.depth, width=args.width, fanout=args.fanout, work=args.work,
                 ticks=args.ticks, sample_every=args.sample_every, buffer=args.buffer,
                 batch=args.batch)
    if cfg.fanout > cfg.width:
        raise ValueError("fanout exceeds width: a node cannot join more parents "
                         "than the level has")
    if cfg.batch < 1 or cfg.batch > MAX_BATCH:
        raise ValueError("batch outside 1..MAX_BATCH")
    if cfg.ticks % cfg.batch != 0:
        raise ValueError("ticks must be a multiple of batch, so no partial batch "
                         "is flushed")
    return cfg


class Clock:
    """Residence time — source emit to sink fold — sampled every Nth tick.

    Sampling rather than timing every tick keeps the two clock reads under 1% of
    a tick even at work=1, where timing every tick would be the measurement.
    """

    def __init__(self, cfg: Config) -> None:
        self.every = cfg.sample_every
        self.stamp = [0] * (cfg.ticks // cfg.sample_every + 1)
        self.lat: list[int] = []

    def emit(self, tick: int) -> None:
        if tick % self.every == 0:
            self.stamp[tick // self.every] = time.perf_counter_ns()

    def done(self, tick: int) -> None:
        if tick % self.every == 0:
            ns = time.perf_counter_ns() - self.stamp[tick // self.every]
            self.lat.append(min(ns, MAX_RESIDENCE_NS))


class Threads:
    """Starts the threads a composition needs, and counts them.

    CPython keeps no cumulative count of threads created, and the Go twin reads
    /sched/goroutines-created for its `spawned` column, so the count is kept
    here and report.py differences it across the measured pass the same way.
    """

    def __init__(self) -> None:
        self.started = 0

    def start(self, target: Callable[..., None], *args: object) -> threading.Thread:
        thread = threading.Thread(target=target, args=args)
        self.started += 1
        thread.start()
        return thread


THREADS = Threads()
