"""Mirrors ../go/benchwire/benchwire.go 1:1.

Any change here must land there too, or the cross-language checksum gate stops
proving identical work and starts hiding a divergence.

Every rung of the ladder carries the same two application messages:

    request:  8 bytes big-endian id, then payload_bytes of payload
    reply:    8 bytes big-endian id, then 4 bytes big-endian CRC-32 of the payload

A transport is free to frame those bytes however it likes, because that framing
is part of what the transport costs. What may not differ is the payload, so
every row generates it from the same splitmix64 stream, and the timed loop, so
every row runs it from drive() below.
"""

from __future__ import annotations

import math
import os
import socket
import sys
import time
import zlib
from collections.abc import Callable
from dataclasses import dataclass

MASK64 = 0xFFFFFFFFFFFFFFFF

# The fixed application reply size: id and CRC, nothing else.
REPLY_LEN = 12

# How many distinct payloads a client cycles through. Distinct payloads give
# distinct CRCs, so the fold proves the bytes as well as the count; a pool
# rather than per-request generation keeps payload generation out of the timed
# region on every row.
POOL_SIZE = 64


class Splitmix64:
    """Identical constants to the Go twin, so both sides generate the same bytes."""

    def __init__(self, state: int) -> None:
        self.state = state & MASK64

    def next(self) -> int:
        self.state = (self.state + 0x9E3779B97F4A7C15) & MASK64
        z = self.state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK64
        return z ^ (z >> 31)


def pool(payload_bytes: int) -> list[bytes]:
    """The POOL_SIZE payloads of payload_bytes each, seeded from slot and size."""
    if payload_bytes % 8 != 0:
        raise ValueError(f"payload_bytes must be a multiple of 8: {payload_bytes}")
    payloads = []
    for slot in range(POOL_SIZE):
        rng = Splitmix64((slot * 0x9E3779B97F4A7C15) ^ payload_bytes)
        buf = bytearray(payload_bytes)
        for off in range(0, payload_bytes, 8):
            buf[off : off + 8] = rng.next().to_bytes(8, "little")
        payloads.append(bytes(buf))
    return payloads


def crc(payload: bytes) -> int:
    """The work the service does: IEEE CRC-32, the same polynomial Go's crc32 uses."""
    return zlib.crc32(payload)


def fold(acc: int, msg_id: int, msg_crc: int) -> int:
    """Accumulate one reply. Order-dependent, so a lost or reordered reply shows.

    The trailing xor-shift is what makes every output bit depend on the CRC as
    well as the id; without it the multiply only carries information leftwards
    and the low half of the checksum would not discriminate the payload at all.
    """
    mixed = ((acc ^ (msg_crc << 32 | msg_id & 0xFFFFFFFF)) * 0x100000001B3) & MASK64
    return mixed ^ (mixed >> 29)


def encode_request(msg_id: int, payload: bytes) -> bytes:
    return msg_id.to_bytes(8, "big") + payload


def serve_request(request: bytes) -> bytes:
    """The service fragment, identical on every rung: read the id, CRC the payload."""
    return request[:8] + crc(request[8:]).to_bytes(4, "big")


def decode_reply(reply: bytes) -> tuple[int, int]:
    return int.from_bytes(reply[:8], "big"), int.from_bytes(reply[8:12], "big")


def pin_nodelay(sock: socket.socket) -> None:
    """Disable Nagle.

    Pinned on for every row of this measurement. http.client sets TCP_NODELAY
    itself (CPython Lib/http/client.py), but socketserver leaves
    disable_nagle_algorithm False, so the accepted server socket keeps Nagle on
    unless somebody says otherwise. Go's net package disables it on both ends by
    default. Setting it explicitly everywhere keeps that asymmetry out of the
    language comparison.
    """
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)


@dataclass(frozen=True)
class Config:
    """What the runner passes down. The runner owns the TOML, the variant measures."""

    addr: str
    payload_bytes: int
    ops: int
    warmup: int
    tuned: bool

    @property
    def host_port(self) -> tuple[str, int]:
        host, _, port = self.addr.rpartition(":")
        return host, int(port)


def env() -> Config:
    return Config(
        addr=os.environ.get("BENCH_ADDR", "127.0.0.1:0"),
        payload_bytes=int(os.environ.get("BENCH_PAYLOAD_BYTES", "128")),
        ops=int(os.environ.get("BENCH_OPS", "5000")),
        warmup=int(os.environ.get("BENCH_WARMUP", "500")),
        tuned=os.environ.get("BENCH_TUNED", "0") == "1",
    )


def ready(addr: str) -> None:
    """Tell the runner the listener is bound and on which address.

    The runner waits for this line rather than sleeping, so a slow interpreter
    start cannot be misread as a slow first crossing.
    """
    print(f"READY {addr}", flush=True)


# One crossing: hand the transport an id and a payload, get back the id and CRC
# the server answered with. Everything a row does differently lives in here.
Exchange = Callable[[int, bytes], tuple[int, int]]


def drive(row: str, cfg: Config, exchange: Exchange) -> None:
    """The timed loop, shared by every Python row exactly as Drive is by every Go row."""
    payloads = pool(cfg.payload_bytes)
    samples: list[int] = []
    checksum = 0
    clock = time.perf_counter_ns
    wall = clock()
    for op in range(cfg.ops):
        start = clock()
        got_id, msg_crc = exchange(op, payloads[op % POOL_SIZE])
        elapsed = clock() - start
        if got_id != op:
            raise RuntimeError(f"reply id mismatch: want {op} got {got_id}")
        checksum = fold(checksum, got_id, msg_crc)
        if op >= cfg.warmup:
            samples.append(min(elapsed, 0xFFFFFFFF))
    print_result(row, cfg, (clock() - wall) / 1e9, samples, checksum)


def percentile(ordered: list[int], q: float) -> int:
    """Nearest-rank percentile over an ascending-sorted list."""
    if not ordered:
        return 0
    idx = math.ceil(q * len(ordered)) - 1
    return ordered[min(max(idx, 0), len(ordered) - 1)]


def read_peak_rss_kb() -> int:
    """VmHWM in kB from /proc/self/status."""
    with open("/proc/self/status", encoding="ascii") as status:
        for line in status:
            if line.startswith("VmHWM:"):
                return int(line.split()[1])
    return 0


def print_result(
    row: str, cfg: Config, wall_s: float, samples: list[int], checksum: int
) -> None:
    """Print the single RESULT line the runner parses, in the Go twin's field order."""
    samples.sort()
    print(
        f"RESULT row={row} payload_bytes={cfg.payload_bytes} ops={cfg.ops} "
        f"wall_s={wall_s:.6f} thr_ops_s={cfg.ops / wall_s:.0f} "
        f"min_ns={percentile(samples, 0)} p50_ns={percentile(samples, 0.50)} "
        f"p99_ns={percentile(samples, 0.99)} p999_ns={percentile(samples, 0.999)} "
        f"max_ns={samples[-1] if samples else 0} "
        f"rss_peak_mb={read_peak_rss_kb() / 1024.0:.1f} samples={len(samples)} "
        f"checksum={checksum:016x}",
        file=sys.stdout,
        flush=True,
    )
