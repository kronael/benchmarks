"""The graph composed of queues: composition 2, worst case.

Mirrors ../go/graph/channel.go and ../go/channel/main.go. One thread per node,
the shallowest queue the stdlib offers, one tick per message. This is the
obvious way to write a channel-composed graph — the pipeline shape from Go's own
concurrency patterns, one stage per derived value — and it is what a team gets
by reaching for the structure without tuning it.
"""

from __future__ import annotations

import queue

import graph
import report
import wiring


def node(cfg: graph.Config, state: list[int], node_id: int,
         into: list[queue.Queue], out: list[queue.Queue]) -> None:
    """One graph node: receive every parent in fixed index order, advance the
    state with the same kernel the direct walk calls, publish the value to every
    consumer."""
    s = state[node_id]
    for _ in range(cfg.ticks):
        acc = 0
        for parent in into:
            acc = graph.fold(acc, parent.get())
        s = graph.kernel(s, acc, cfg.work)
        for consumer in out:
            consumer.put(s)
    state[node_id] = s


def sink(cfg: graph.Config, clock: graph.Clock, into: list[queue.Queue],
         done: queue.SimpleQueue) -> None:
    """Join the whole last level in index order and fold the tick.

    This is the only place a tick is observed complete, so residence time is
    stamped here.
    """
    total = 0
    for t in range(cfg.ticks):
        for parent in into:
            total = graph.fold(total, parent.get())
        clock.done(t)
    done.put(total)


def channel(cfg: graph.Config, clock: graph.Clock) -> int:
    """Drive the tick stream into the graph and return the checksum."""
    state = cfg.states()
    edge = wiring.wire(cfg, 1)
    threads = []
    for level in range(1, cfg.depth + 1):
        for n in range(cfg.width):
            threads.append(graph.THREADS.start(
                node, cfg, state, (level - 1) * cfg.width + n,
                edge[level][n], wiring.outs(cfg, edge, level, n)))
    done: queue.SimpleQueue = queue.SimpleQueue()
    threads.append(graph.THREADS.start(sink, cfg, clock, edge[cfg.depth + 1][0], done))

    vals = [0] * cfg.width
    for t in range(cfg.ticks):
        clock.emit(t)
        cfg.source(t, vals)
        for j in range(cfg.fanout):
            for n in range(cfg.width):
                edge[1][n][j].put(vals[cfg.parent(n, j)])
    total = done.get()
    for thread in threads:
        thread.join()
    return graph.finish(total, state)


def main() -> None:
    report.run("py-channel", graph.msgs, channel)


if __name__ == "__main__":
    main()
