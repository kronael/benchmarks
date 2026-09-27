// Go stdlib HTTP server — the control's server side, mirrored 1:1 by
// ../../python/httpsrv.py. The handler is byte-identical across both effort
// rows; only SetKeepAlivesEnabled differs, so the row measures connection
// reuse and nothing else.
//
// TCP_NODELAY is pinned on for every row of this measurement. Go's net package
// already sets it on accepted connections and the Python twin sets it
// explicitly, so neither language's default leaks into the comparison.
package main

import (
	"io"
	"net"
	"net/http"

	"benchtransport/benchwire"
)

func main() {
	cfg := benchwire.Env()
	requestLen := 8 + cfg.PayloadBytes

	mux := http.NewServeMux()
	mux.HandleFunc("POST /w", func(w http.ResponseWriter, r *http.Request) {
		request := make([]byte, requestLen)
		if _, err := io.ReadFull(r.Body, request); err != nil {
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}
		reply := make([]byte, benchwire.ReplyLen)
		w.Header().Set("Content-Type", "application/octet-stream")
		// client disconnect; the response is already committed
		_, _ = w.Write(benchwire.ServeRequest(request, reply))
	})

	listener, err := net.Listen("tcp", cfg.Addr)
	if err != nil {
		panic("listen: " + err.Error())
	}
	server := &http.Server{Handler: mux}
	server.SetKeepAlivesEnabled(cfg.Tuned)

	benchwire.Ready(listener.Addr().String())
	if err := server.Serve(listener); err != nil {
		panic("serve: " + err.Error())
	}
}
