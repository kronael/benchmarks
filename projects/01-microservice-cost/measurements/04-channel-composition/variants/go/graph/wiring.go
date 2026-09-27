package graph

// The edge wiring both channel compositions use. They differ in what a message
// carries and in whether the channel has a buffer, not in the graph.

// wire builds one channel per graph edge: edge[l][n][j] carries level l-1's
// node parent(n,j) into node n at level l, and edge[depth+1][0][n] carries the
// last level's node n into the sink.
func wire[T any](cfg Config, buf int) [][][]chan T {
	edge := make([][][]chan T, cfg.Depth+2)
	for l := 1; l <= cfg.Depth; l++ {
		edge[l] = make([][]chan T, cfg.Width)
		for n := range edge[l] {
			edge[l][n] = make([]chan T, cfg.Fanout)
			for j := range edge[l][n] {
				edge[l][n][j] = make(chan T, buf)
			}
		}
	}
	sink := make([]chan T, cfg.Width)
	for n := range sink {
		sink[n] = make(chan T, buf)
	}
	edge[cfg.Depth+1] = [][]chan T{sink}
	return edge
}

// outs lists the edges node p at level l writes, in ascending consumer input
// index. That order is not cosmetic: consumers receive their parents in the
// same ascending order, so at step j every producer p meets the one consumer
// waiting for it, and any other send order deadlocks a level against itself on
// an unbuffered channel.
func outs[T any](cfg Config, edge [][][]chan T, l, p int) []chan T {
	if l == cfg.Depth {
		return []chan T{edge[cfg.Depth+1][0][p]}
	}
	o := make([]chan T, 0, cfg.Fanout)
	for j := 0; j < cfg.Fanout; j++ {
		for n := 0; n < cfg.Width; n++ {
			if cfg.Parent(n, j) == p {
				o = append(o, edge[l+1][n][j])
			}
		}
	}
	return o
}
