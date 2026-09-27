"""CPython stdlib HTTP client — rung 1a, mirrored 1:1 by ../go/httpcli/main.go.

Worst row: a fresh HTTPConnection per crossing, which is what the obvious code
does and what every requests.post call without a Session does. Medium row: one
connection held open for the whole run, against an HTTP/1.1 server.

http.client sets TCP_NODELAY on connect itself, so Nagle is already pinned off
on this side of the socket.
"""

from __future__ import annotations

import http.client

import benchwire

HEADERS = {"Content-Type": "application/octet-stream"}


def main() -> None:
    cfg = benchwire.env()
    host, port = cfg.host_port

    if cfg.tuned:
        conn = http.client.HTTPConnection(host, port)

        def exchange(msg_id: int, payload: bytes) -> tuple[int, int]:
            conn.request("POST", "/w", benchwire.encode_request(msg_id, payload), HEADERS)
            response = conn.getresponse()
            return benchwire.decode_reply(response.read())
    else:

        def exchange(msg_id: int, payload: bytes) -> tuple[int, int]:
            fresh = http.client.HTTPConnection(host, port)
            fresh.request("POST", "/w", benchwire.encode_request(msg_id, payload), HEADERS)
            response = fresh.getresponse()
            reply = response.read()
            fresh.close()
            return benchwire.decode_reply(reply)

    benchwire.drive("py-http", cfg, exchange)


if __name__ == "__main__":
    main()
