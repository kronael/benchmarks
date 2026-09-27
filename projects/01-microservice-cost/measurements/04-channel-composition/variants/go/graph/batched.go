package graph

import "sync"

// Batch is a batched message. It is sent by value, so a copied array costs no
// allocation and the medium-effort row's buffering does not quietly buy GC
// pressure it would then have to explain.
type Batch [MaxBatch]uint64

// ChannelBatched is composition 2 at medium effort: the same graph, the same
// goroutines, the same join order, with the channel structure's two documented
// remedies for per-item cost — a buffer, and a batch of ticks per message. It
// pays for them in residence time, because a tick waits for its batch to close
// before it moves.
var ChannelBatched = Composition{Name: "channel-batched", Msgs: Config.BatchedMsgs, Run: channelBatched}

func channelBatched(cfg Config, clk *Clock) uint64 {
	state := cfg.States()
	edge := wire[Batch](cfg, cfg.Buffer)
	var wg sync.WaitGroup
	for l := 1; l <= cfg.Depth; l++ {
		for n := 0; n < cfg.Width; n++ {
			wg.Add(1)
			go nodeBatched(cfg, &state[(l-1)*cfg.Width+n], edge[l][n], outs(cfg, edge, l, n), &wg)
		}
	}
	sum := uint64(0)
	wg.Add(1)
	go func() {
		defer wg.Done()
		sum = sinkBatched(cfg, clk, edge[cfg.Depth+1][0])
	}()

	vals := make([]uint64, cfg.Width)
	batch := make([]Batch, cfg.Width)
	for b := 0; b < cfg.Ticks/cfg.Batch; b++ {
		for k := 0; k < cfg.Batch; k++ {
			clk.Emit(b*cfg.Batch + k)
			cfg.Source(b*cfg.Batch+k, vals)
			for p := 0; p < cfg.Width; p++ {
				batch[p][k] = vals[p]
			}
		}
		for j := 0; j < cfg.Fanout; j++ {
			for n := 0; n < cfg.Width; n++ {
				edge[1][n][j] <- batch[cfg.Parent(n, j)]
			}
		}
	}
	wg.Wait()
	return Finish(sum, state)
}

// nodeBatched is node with the batch unrolled inside it. The kernel still runs
// once per tick per node, on the same accumulator, in the same order.
func nodeBatched(cfg Config, state *uint64, in, out []chan Batch, wg *sync.WaitGroup) {
	defer wg.Done()
	s := *state
	got := make([]Batch, len(in))
	var send Batch
	for b := 0; b < cfg.Ticks/cfg.Batch; b++ {
		for j := range in {
			got[j] = <-in[j]
		}
		for k := 0; k < cfg.Batch; k++ {
			acc := uint64(0)
			for j := range got {
				acc = Fold(acc, got[j][k])
			}
			s = Kernel(s, acc, cfg.Work)
			send[k] = s
		}
		for _, c := range out {
			c <- send
		}
	}
	*state = s
}

func sinkBatched(cfg Config, clk *Clock, in []chan Batch) uint64 {
	sum := uint64(0)
	got := make([]Batch, len(in))
	for b := 0; b < cfg.Ticks/cfg.Batch; b++ {
		for n := range in {
			got[n] = <-in[n]
		}
		for k := 0; k < cfg.Batch; k++ {
			for n := range got {
				sum = Fold(sum, got[n][k])
			}
			clk.Done(b*cfg.Batch + k)
		}
	}
	return sum
}
