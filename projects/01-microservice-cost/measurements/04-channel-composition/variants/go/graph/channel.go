package graph

import "sync"

// Channel is composition 2 at its worst case: one goroutine per node,
// unbuffered channels, one tick per message. This is the obvious way to write a
// channel-composed graph — the pipeline shape from Go's own concurrency
// patterns, one stage per derived value — and it is what a team gets by reaching
// for the structure without tuning it.
var Channel = Composition{Name: "channel", Msgs: Config.Msgs, Run: channel}

func channel(cfg Config, clk *Clock) uint64 {
	state := cfg.States()
	edge := wire[uint64](cfg, 0)
	var wg sync.WaitGroup
	for l := 1; l <= cfg.Depth; l++ {
		for n := 0; n < cfg.Width; n++ {
			wg.Add(1)
			go node(cfg, &state[(l-1)*cfg.Width+n], edge[l][n], outs(cfg, edge, l, n), &wg)
		}
	}
	sum := uint64(0)
	wg.Add(1)
	go func() {
		defer wg.Done()
		sum = sink(cfg, clk, edge[cfg.Depth+1][0])
	}()

	vals := make([]uint64, cfg.Width)
	for t := 0; t < cfg.Ticks; t++ {
		clk.Emit(t)
		cfg.Source(t, vals)
		for j := 0; j < cfg.Fanout; j++ {
			for n := 0; n < cfg.Width; n++ {
				edge[1][n][j] <- vals[cfg.Parent(n, j)]
			}
		}
	}
	wg.Wait()
	return Finish(sum, state)
}

// node is one graph node: receive every parent in fixed index order, advance
// the state with the same kernel the direct walk calls, publish the value to
// every consumer.
func node(cfg Config, state *uint64, in, out []chan uint64, wg *sync.WaitGroup) {
	defer wg.Done()
	s := *state
	for t := 0; t < cfg.Ticks; t++ {
		acc := uint64(0)
		for j := range in {
			acc = Fold(acc, <-in[j])
		}
		s = Kernel(s, acc, cfg.Work)
		for _, c := range out {
			c <- s
		}
	}
	*state = s
}

// sink joins the whole last level in index order and folds the tick. It is the
// only place a tick is observed complete, so residence time is stamped here.
func sink(cfg Config, clk *Clock, in []chan uint64) uint64 {
	sum := uint64(0)
	for t := 0; t < cfg.Ticks; t++ {
		for n := range in {
			sum = Fold(sum, <-in[n])
		}
		clk.Done(t)
	}
	return sum
}
