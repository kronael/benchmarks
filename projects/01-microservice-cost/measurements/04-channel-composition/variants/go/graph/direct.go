package graph

// Direct is composition 1 at its worst case: the graph as an ordinary call
// graph, walked in topological order by one goroutine. No channels, no
// goroutines, no scheduler. This row is also the pure-work reference every
// other row is read against, because its per-tick time is the kernel and
// nothing else.
var Direct = Composition{Name: "direct", Msgs: noMsgs, Run: direct}

func direct(cfg Config, clk *Clock) uint64 {
	state := cfg.States()
	cur := make([]uint64, cfg.Width)
	next := make([]uint64, cfg.Width)
	sum := uint64(0)
	for t := 0; t < cfg.Ticks; t++ {
		clk.Emit(t)
		cfg.Source(t, cur)
		for l := 0; l < cfg.Depth; l++ {
			for n := 0; n < cfg.Width; n++ {
				cfg.eval(state, cur, next, l, n)
			}
			cur, next = next, cur
		}
		for n := 0; n < cfg.Width; n++ {
			sum = Fold(sum, cur[n])
		}
		clk.Done(t)
	}
	return Finish(sum, state)
}
