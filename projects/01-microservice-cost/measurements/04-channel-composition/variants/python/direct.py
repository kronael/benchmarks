"""The direct call graph: composition 1, worst case.

Mirrors ../go/graph/direct.go and ../go/direct/main.go. The graph as an ordinary
call graph, walked in topological order by one thread: no queues, no threads, no
scheduler. This row is also the pure-work reference every other row is read
against, because its per-tick time is the kernel and nothing else.
"""

from __future__ import annotations

import graph
import report


def direct(cfg: graph.Config, clock: graph.Clock) -> int:
    """Walk the graph once per tick and return the checksum."""
    state = cfg.states()
    cur = [0] * cfg.width
    nxt = [0] * cfg.width
    total = 0
    for t in range(cfg.ticks):
        clock.emit(t)
        cfg.source(t, cur)
        for level in range(cfg.depth):
            for n in range(cfg.width):
                cfg.eval_node(state, cur, nxt, level, n)
            cur, nxt = nxt, cur
        for value in cur:
            total = graph.fold(total, value)
        clock.done(t)
    return graph.finish(total, state)


def main() -> None:
    report.run("py-direct", graph.no_msgs, direct)


if __name__ == "__main__":
    main()
