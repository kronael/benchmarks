"""Mirrors ../go/graph/wiring.go 1:1: the edge wiring both channel compositions use.

They differ in what a message carries and in how deep the queue is, not in the
graph.

Go's unbuffered channel is a rendezvous, and CPython's stdlib has no queue that
hands a value over without accepting it first, so the worst-case row asks for a
depth of one where its twin asks for zero: one slot of slack against Go's none.
That is the one place this rung cannot mirror the Go one, and it flatters the
Python row rather than the other way round. The batched row's depth is
sweep.toml's `buffer` on both sides.
"""

from __future__ import annotations

import queue

import graph


def wire(cfg: graph.Config, maxsize: int) -> list[list[list[queue.Queue]]]:
    """One queue per graph edge: edge[l][n][j] carries level l-1's node
    parent(n,j) into node n at level l, and edge[depth+1][0][n] carries the last
    level's node n into the sink."""
    edge: list[list[list[queue.Queue]]] = [[] for _ in range(cfg.depth + 2)]
    for level in range(1, cfg.depth + 1):
        edge[level] = [[queue.Queue(maxsize) for _ in range(cfg.fanout)]
                       for _ in range(cfg.width)]
    edge[cfg.depth + 1] = [[queue.Queue(maxsize) for _ in range(cfg.width)]]
    return edge


def outs(cfg: graph.Config, edge: list[list[list[queue.Queue]]],
         level: int, p: int) -> list[queue.Queue]:
    """The edges node p at level l writes, in ascending consumer input index.

    That order is not cosmetic: consumers receive their parents in the same
    ascending order, so at step j every producer p meets the one consumer
    waiting for it, and any other send order deadlocks a level against itself
    on a queue this shallow.
    """
    if level == cfg.depth:
        return [edge[cfg.depth + 1][0][p]]
    out = []
    for j in range(cfg.fanout):
        for n in range(cfg.width):
            if cfg.parent(n, j) == p:
                out.append(edge[level + 1][n][j])
    return out
