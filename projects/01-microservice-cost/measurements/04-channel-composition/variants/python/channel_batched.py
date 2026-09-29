"""The graph composed of queues, buffered and batched: composition 2, medium
effort.

Mirrors ../go/graph/batched.go and ../go/channel-batched/main.go. The same
graph, the same threads, the same join order, with the channel structure's two
documented remedies for per-item cost — a buffer, and a batch of ticks per
message. It pays for them in residence time, because a tick waits for its batch
to close before it moves.

The Go twin sends a fixed array by value, so a copied batch costs it no
allocation. A list here is sent by reference, which is cheaper still; no node
ever writes into a batch it received, so the values are the same values in the
same order.
"""

from __future__ import annotations

import queue

import graph
import report
import wiring


def node_batched(cfg: graph.Config, state: list[int], node_id: int,
                 into: list[queue.Queue], out: list[queue.Queue]) -> None:
    """One graph node with the batch unrolled inside it. The kernel still runs
    once per tick per node, on the same accumulator, in the same order."""
    s = state[node_id]
    for _ in range(cfg.ticks // cfg.batch):
        got = [parent.get() for parent in into]
        send = [0] * cfg.batch
        for k in range(cfg.batch):
            acc = 0
            for batch in got:
                acc = graph.fold(acc, batch[k])
            s = graph.kernel(s, acc, cfg.work)
            send[k] = s
        for consumer in out:
            consumer.put(send)
    state[node_id] = s


def sink_batched(cfg: graph.Config, clock: graph.Clock, into: list[queue.Queue],
                 done: queue.SimpleQueue) -> None:
    total = 0
    for b in range(cfg.ticks // cfg.batch):
        got = [parent.get() for parent in into]
        for k in range(cfg.batch):
            for batch in got:
                total = graph.fold(total, batch[k])
            clock.done(b * cfg.batch + k)
    done.put(total)


def channel_batched(cfg: graph.Config, clock: graph.Clock) -> int:
    """Drive the tick stream into the graph a batch at a time and return the
    checksum."""
    state = cfg.states()
    edge = wiring.wire(cfg, cfg.buffer)
    threads = []
    for level in range(1, cfg.depth + 1):
        for n in range(cfg.width):
            threads.append(graph.THREADS.start(
                node_batched, cfg, state, (level - 1) * cfg.width + n,
                edge[level][n], wiring.outs(cfg, edge, level, n)))
    done: queue.SimpleQueue = queue.SimpleQueue()
    threads.append(graph.THREADS.start(
        sink_batched, cfg, clock, edge[cfg.depth + 1][0], done))

    vals = [0] * cfg.width
    for b in range(cfg.ticks // cfg.batch):
        batch = [[0] * cfg.batch for _ in range(cfg.width)]
        for k in range(cfg.batch):
            clock.emit(b * cfg.batch + k)
            cfg.source(b * cfg.batch + k, vals)
            for p in range(cfg.width):
                batch[p][k] = vals[p]
        for j in range(cfg.fanout):
            for n in range(cfg.width):
                edge[1][n][j].put(batch[cfg.parent(n, j)])
    total = done.get()
    for thread in threads:
        thread.join()
    return graph.finish(total, state)


def main() -> None:
    report.run("py-channel-batched", graph.batched_msgs, channel_batched)


if __name__ == "__main__":
    main()
