// Raw UDP server — rung 3, the floor. A service must answer whichever peer
// wrote to it, so the loop shape is the same in both effort rows; the medium
// row only enlarges SO_RCVBUF and SO_SNDBUF, which is the documented knob.
package main

import (
	"net"

	"benchtransport/benchwire"
)

// socketBuffer is what the medium row asks the kernel for on each direction.
// The kernel doubles the request for bookkeeping and clamps it at
// net.core.rmem_max / wmem_max, so the effective size is whatever survives
// that; the row is "asked for a megabyte", not "got a megabyte".
const socketBuffer = 1 << 20

func main() {
	cfg := benchwire.Env()
	addr, err := net.ResolveUDPAddr("udp", cfg.Addr)
	if err != nil {
		panic("resolve: " + err.Error())
	}
	conn, err := net.ListenUDP("udp", addr)
	if err != nil {
		panic("listen: " + err.Error())
	}
	if cfg.Tuned {
		if err := conn.SetReadBuffer(socketBuffer); err != nil {
			panic("set read buffer: " + err.Error())
		}
		if err := conn.SetWriteBuffer(socketBuffer); err != nil {
			panic("set write buffer: " + err.Error())
		}
	}

	request := make([]byte, 8+cfg.PayloadBytes)
	reply := make([]byte, benchwire.ReplyLen)
	benchwire.Ready(conn.LocalAddr().String())
	for {
		n, peer, err := conn.ReadFromUDP(request)
		if err != nil {
			panic("read: " + err.Error())
		}
		if _, err := conn.WriteToUDP(benchwire.ServeRequest(request[:n], reply), peer); err != nil {
			panic("write: " + err.Error())
		}
	}
}
