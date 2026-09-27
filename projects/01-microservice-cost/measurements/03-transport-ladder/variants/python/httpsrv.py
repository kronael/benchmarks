"""CPython stdlib HTTP server — rung 1a, mirrored 1:1 by ../go/httpsrv/main.go.

The handler body is byte-identical across both effort rows. Only
protocol_version differs: HTTP/1.0 is what CPython ships and it closes the
connection after every response, HTTP/1.1 is the documented remedy and permits
persistent connections. Setting it is the whole medium-effort change, and the
docs are explicit that HTTP/1.1 then obliges the server to send an accurate
Content-Length, which the handler does in both rows.

disable_nagle_algorithm is pinned True. socketserver leaves it False, so an
accepted socket would otherwise keep Nagle on here and have it off in the Go
twin, which would put a kernel setting inside the language comparison.
"""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import benchwire


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"
    disable_nagle_algorithm = True

    def do_POST(self) -> None:
        request = self.rfile.read(int(self.headers["Content-Length"]))
        reply = benchwire.serve_request(request)
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(len(reply)))
        self.end_headers()
        self.wfile.write(reply)

    def log_message(self, format: str, *args: object) -> None:
        """Silence the per-request access log; the runner parses this stream."""


def main() -> None:
    cfg = benchwire.env()
    Handler.protocol_version = "HTTP/1.1" if cfg.tuned else "HTTP/1.0"
    host, port = cfg.host_port
    server = ThreadingHTTPServer((host, port), Handler)
    server.daemon_threads = True
    bound_host, bound_port = server.server_address[:2]
    benchwire.ready(f"{bound_host}:{bound_port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
