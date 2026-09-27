package graph

import "sync"

// DirectParallel is composition 1 at medium effort: the same topological walk,
// with each level's nodes evaluated in parallel by goroutines joined on a
// WaitGroup. This is the whole of the documented remedy available to the direct
// structure — ticks are serially dependent through node state, so a level is
// the only thing there is to parallelise, and the walk has to re-synchronise at
// every level boundary of every tick.
var DirectParallel = Composition{Name: "direct-parallel", Msgs: noMsgs, Run: directParallel}

func directParallel(cfg Config, clk *Clock) uint64 {
	state := cfg.States()
	cur := make([]uint64, cfg.Width)
	next := make([]uint64, cfg.Width)
	var wg sync.WaitGroup
	sum := uint64(0)
	for t := 0; t < cfg.Ticks; t++ {
		clk.Emit(t)
		cfg.Source(t, cur)
		for l := 0; l < cfg.Depth; l++ {
			wg.Add(cfg.Width)
			for n := 0; n < cfg.Width; n++ {
				go evalNode(cfg, state, cur, next, l, n, &wg)
			}
			wg.Wait()
			cur, next = next, cur
		}
		for n := 0; n < cfg.Width; n++ {
			sum = Fold(sum, cur[n])
		}
		clk.Done(t)
	}
	return Finish(sum, state)
}

// evalNode is Direct's node body, reached through a goroutine. Each n writes
// only state[level*width+n] and out[n], and the level's writes are all joined
// before the next level reads them.
func evalNode(cfg Config, state, in, out []uint64, level, n int, wg *sync.WaitGroup) {
	defer wg.Done()
	cfg.eval(state, in, out, level, n)
}
