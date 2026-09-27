"""WebSocket client — rung 1b, on the websockets library's sync API.

Worst row: compression left at the library default, which is permessage-deflate.
The payload is an incompressible splitmix64 stream, so deflate buys no bytes and
costs CPU on every crossing in both directions — that is the realistic case for
binary payloads and the reason the library documents compression=None.

Medium row: compression=None. The connection is persistent in both rows, because
a WebSocket has no other mode; that is rung 1b's whole difference from rung 1a.
"""

from __future__ import annotations

from websockets.sync.client import connect

import benchwire


def main() -> None:
    cfg = benchwire.env()
    url = f"ws://{cfg.addr}"
    with connect(url, compression=None if cfg.tuned else "deflate") as connection:
        benchwire.pin_nodelay(connection.socket)

        def exchange(msg_id: int, payload: bytes) -> tuple[int, int]:
            connection.send(benchwire.encode_request(msg_id, payload))
            return benchwire.decode_reply(connection.recv())

        benchwire.drive("py-ws", cfg, exchange)


if __name__ == "__main__":
    main()
