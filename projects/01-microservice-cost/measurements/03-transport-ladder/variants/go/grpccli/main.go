// gRPC client — rung 2.
//
// Worst row: a unary RPC per crossing on a stock client, which is how gRPC
// gets wired the quick way. Every crossing pays HTTP/2 header framing and a
// fresh stream.
//
// Medium row: one bidirectional stream opened once and reused, plus the
// flow-control window and buffer sizes grpc-go documents. Streaming for a
// long-lived flow of small messages is gRPC's own advice, so the loser's fix
// is in the table rather than left out.
package main

import (
	"context"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"

	"benchtransport/benchwire"
	"benchtransport/ladderpb"
)

const (
	windowSize = 1 << 20
	bufferSize = 64 << 10
)

func main() {
	cfg := benchwire.Env()
	options := []grpc.DialOption{grpc.WithTransportCredentials(insecure.NewCredentials())}
	if cfg.Tuned {
		options = append(options,
			grpc.WithInitialWindowSize(windowSize),
			grpc.WithInitialConnWindowSize(windowSize),
			grpc.WithReadBufferSize(bufferSize),
			grpc.WithWriteBufferSize(bufferSize))
	}
	conn, err := grpc.NewClient(cfg.Addr, options...)
	if err != nil {
		panic("dial: " + err.Error())
	}
	client := ladderpb.NewLadderClient(conn)
	ctx := context.Background()

	var exchange benchwire.Exchange
	if cfg.Tuned {
		stream, err := client.Stream(ctx)
		if err != nil {
			panic("open stream: " + err.Error())
		}
		exchange = func(id uint64, payload []byte) (uint64, uint32, error) {
			if err := stream.Send(&ladderpb.Work{Id: id, Payload: payload}); err != nil {
				return 0, 0, err
			}
			ack, err := stream.Recv()
			if err != nil {
				return 0, 0, err
			}
			return ack.GetId(), ack.GetCrc(), nil
		}
	} else {
		exchange = func(id uint64, payload []byte) (uint64, uint32, error) {
			ack, err := client.Unary(ctx, &ladderpb.Work{Id: id, Payload: payload})
			if err != nil {
				return 0, 0, err
			}
			return ack.GetId(), ack.GetCrc(), nil
		}
	}
	benchwire.Drive("go-grpc", cfg, exchange)
}
