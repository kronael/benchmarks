// Raw UDP client — rung 3, the floor.
//
// Worst row: an unconnected socket from ListenUDP, with the destination named
// on every send. That is the symmetric code a first draft writes, and it makes
// the kernel resolve the route and copy a sockaddr per datagram.
//
// Medium row: DialUDP, which connect(2)s the socket so the destination is
// resolved once, plus the enlarged socket buffers the server also gets. Both
// are the documented remedies rather than tricks.
//
// The payload is capped so that 8+payload stays inside one datagram; see
// sweep.toml. A fragmented or rejected datagram would measure a different
// thing, not a slower one.
package main

import (
	"net"

	"benchtransport/benchwire"
)

const socketBuffer = 1 << 20

func main() {
	cfg := benchwire.Env()
	serverAddr, err := net.ResolveUDPAddr("udp", cfg.Addr)
	if err != nil {
		panic("resolve: " + err.Error())
	}
	request := make([]byte, 8+cfg.PayloadBytes)
	reply := make([]byte, benchwire.ReplyLen)

	var exchange benchwire.Exchange
	if cfg.Tuned {
		conn, err := net.DialUDP("udp", nil, serverAddr)
		if err != nil {
			panic("dial: " + err.Error())
		}
		if err := conn.SetReadBuffer(socketBuffer); err != nil {
			panic("set read buffer: " + err.Error())
		}
		if err := conn.SetWriteBuffer(socketBuffer); err != nil {
			panic("set write buffer: " + err.Error())
		}
		exchange = func(id uint64, payload []byte) (uint64, uint32, error) {
			if _, err := conn.Write(benchwire.EncodeRequest(request, id, payload)); err != nil {
				return 0, 0, err
			}
			if _, err := conn.Read(reply); err != nil {
				return 0, 0, err
			}
			gotID, crc := benchwire.DecodeReply(reply)
			return gotID, crc, nil
		}
	} else {
		conn, err := net.ListenUDP("udp", &net.UDPAddr{IP: net.IPv4(127, 0, 0, 1)})
		if err != nil {
			panic("listen: " + err.Error())
		}
		exchange = func(id uint64, payload []byte) (uint64, uint32, error) {
			if _, err := conn.WriteToUDP(benchwire.EncodeRequest(request, id, payload), serverAddr); err != nil {
				return 0, 0, err
			}
			if _, _, err := conn.ReadFromUDP(reply); err != nil {
				return 0, 0, err
			}
			gotID, crc := benchwire.DecodeReply(reply)
			return gotID, crc, nil
		}
	}
	benchwire.Drive("go-udp", cfg, exchange)
}
