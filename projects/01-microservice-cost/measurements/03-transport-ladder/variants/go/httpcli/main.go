// Go stdlib HTTP client — the control's client side, mirrored 1:1 by
// ../../python/httpcli.py.
//
// Worst row: DisableKeepAlives, so every crossing pays a fresh TCP handshake
// and the server closes afterwards. Medium row: the same code with keep-alives
// left on and one idle connection held, which is the documented remedy on both
// sides of the mirror.
package main

import (
	"bytes"
	"io"
	"net/http"

	"benchtransport/benchwire"
)

func main() {
	cfg := benchwire.Env()
	request := make([]byte, 8+cfg.PayloadBytes)
	reply := make([]byte, benchwire.ReplyLen)
	url := "http://" + cfg.Addr + "/w"

	transport := &http.Transport{
		DisableKeepAlives:   !cfg.Tuned,
		MaxIdleConnsPerHost: 1,
		ForceAttemptHTTP2:   false,
	}
	client := &http.Client{Transport: transport}

	benchwire.Drive("go-http", cfg, func(id uint64, payload []byte) (uint64, uint32, error) {
		body := benchwire.EncodeRequest(request, id, payload)
		response, err := client.Post(url, "application/octet-stream", bytes.NewReader(body))
		if err != nil {
			return 0, 0, err
		}
		if _, err := io.ReadFull(response.Body, reply); err != nil {
			return 0, 0, err
		}
		if err := response.Body.Close(); err != nil {
			return 0, 0, err
		}
		gotID, crc := benchwire.DecodeReply(reply)
		return gotID, crc, nil
	})
}
