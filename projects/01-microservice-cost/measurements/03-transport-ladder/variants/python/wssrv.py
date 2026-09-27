"""WebSocket server — rung 1b, on the websockets library's sync API.

The handler body is byte-identical across both effort rows. Only compression
differs: "deflate" is the library's own default and the medium row turns it off,
which is the remedy the library documents.

The sync (thread-per-connection) API is used rather than the asyncio one so the
concurrency model matches the HTTP rows of the same rung. That keeps the
HTTP-versus-WebSocket comparison inside rung 1 about the transport instead of
about threads versus an event loop.
"""

from __future__ import annotations

from websockets.sync.server import ServerConnection, serve

import benchwire


def handle(connection: ServerConnection) -> None:
    benchwire.pin_nodelay(connection.socket)
    for request in connection:
        connection.send(benchwire.serve_request(request))


def main() -> None:
    cfg = benchwire.env()
    host, port = cfg.host_port
    server = serve(handle, host, port, compression=None if cfg.tuned else "deflate")
    bound_host, bound_port = server.socket.getsockname()[:2]
    benchwire.ready(f"{bound_host}:{bound_port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
