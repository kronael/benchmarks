// gRPC server — rung 2, the common professional answer. Both methods run the
// same service fragment, a CRC-32 over the payload, so the unary and the
// streaming row do identical work and differ only in how gRPC carries it.
//
// The medium row adds the flow-control and buffer sizes grpc-go documents as
// its performance knobs; the recipe and citations are in
// ../../../notes/design.md.
package main

import (
	"context"
	"io"
	"net"

	"google.golang.org/grpc"

	"benchtransport/benchwire"
	"benchtransport/ladderpb"
)

const (
	windowSize = 1 << 20
	bufferSize = 64 << 10
)

type service struct {
	ladderpb.UnimplementedLadderServer
}

func (s *service) Unary(_ context.Context, work *ladderpb.Work) (*ladderpb.Ack, error) {
	return &ladderpb.Ack{Id: work.GetId(), Crc: benchwire.CRC(work.GetPayload())}, nil
}

func (s *service) Stream(stream ladderpb.Ladder_StreamServer) error {
	for {
		work, err := stream.Recv()
		if err == io.EOF {
			return nil
		}
		if err != nil {
			return err
		}
		ack := &ladderpb.Ack{Id: work.GetId(), Crc: benchwire.CRC(work.GetPayload())}
		if err := stream.Send(ack); err != nil {
			return err
		}
	}
}

func main() {
	cfg := benchwire.Env()
	listener, err := net.Listen("tcp", cfg.Addr)
	if err != nil {
		panic("listen: " + err.Error())
	}

	var options []grpc.ServerOption
	if cfg.Tuned {
		options = append(options,
			grpc.InitialWindowSize(windowSize),
			grpc.InitialConnWindowSize(windowSize),
			grpc.ReadBufferSize(bufferSize),
			grpc.WriteBufferSize(bufferSize))
	}
	server := grpc.NewServer(options...)
	ladderpb.RegisterLadderServer(server, &service{})

	benchwire.Ready(listener.Addr().String())
	if err := server.Serve(listener); err != nil {
		panic("serve: " + err.Error())
	}
}
