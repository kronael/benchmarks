"""The direct call graph with each level evaluated in parallel: composition 1,
medium effort.

Mirrors ../go/graph/pool.go and ../go/direct-parallel/main.go. The same
topological walk, with each level's nodes evaluated by one thread per node and
joined before the next level reads them. This is the whole of the documented
remedy available to the direct structure — ticks are serially dependent through
node state, so a level is the only thing there is to parallelise, and the walk
has to re-synchronise at every level boundary of every tick.

The Go twin spawns a goroutine per node per level per tick and joins it on a
WaitGroup; the thread here is the same structure through CPython's own
primitive. It is also the row where the runtimes are least alike: the GIL lets
one thread at a time run the kernel, so this row buys concurrency and no cores.
Processes would buy the cores, and would put the node state behind IPC on every
level boundary, which changes the composition rather than the effort — the
other two threaded rows would then be measuring a different machine.
"""

from __future__ import annotations

import graph
import report


def direct_parallel(cfg: graph.Config, clock: graph.Clock) -> int:
    """Walk the graph once per tick, a thread per node within a level."""
    state = cfg.states()
    cur = [0] * cfg.width
    nxt = [0] * cfg.width
    total = 0
    for t in range(cfg.ticks):
        clock.emit(t)
        cfg.source(t, cur)
        for level in range(cfg.depth):
            threads = [graph.THREADS.start(cfg.eval_node, state, cur, nxt, level, n)
                       for n in range(cfg.width)]
            for thread in threads:
                thread.join()
            cur, nxt = nxt, cur
        for value in cur:
            total = graph.fold(total, value)
        clock.done(t)
    return graph.finish(total, state)


def main() -> None:
    report.run("py-direct-parallel", graph.no_msgs, direct_parallel)


if __name__ == "__main__":
    main()
