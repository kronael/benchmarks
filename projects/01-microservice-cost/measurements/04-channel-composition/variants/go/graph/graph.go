// Package graph is the fragment all four compositions share: the calculation
// graph, its node kernel, the checksum fold and the clock. The compositions
// differ in how these nodes are wired and driven and in nothing else, which is
// what makes the pair a measurement rather than two programs.
package graph

import (
	"flag"
	"math"
	"time"
)

const (
	// The node kernel: an integer EMA step in fixed point, mixed with MMIX's
	// LCG (Knuth, TAOCP vol. 2) so the chain is data-dependent and cannot be
	// hoisted. Iteration-bounded, never wall-clock-bounded: a descheduled node
	// sheds no work, and its fold reaches the checksum.
	emaShift = 5
	mmixMul  = 6364136223846793005
	mmixAdd  = 1442695040888963407

	// FNV-1a's prime. The fold is order-sensitive on purpose: a join that
	// arrives out of order changes the checksum instead of passing quietly.
	fnvPrime = 0x100000001b3

	// MaxBatch is the batched message's array, copied whole on every send, so
	// the constant is the batch the medium-effort row is tuned for rather than
	// an upper bound to grow into.
	MaxBatch = 32
)

// Config is the graph's shape and the run's size. Every composition reads the
// same one.
type Config struct {
	Depth       int
	Width       int
	Fanout      int
	Work        int
	Ticks       int
	SampleEvery int
	Buffer      int
	Batch       int
}

// Configure reads the shape from flags. run.py sets them from sweep.toml.
func Configure() Config {
	var c Config
	flag.IntVar(&c.Depth, "depth", 6, "levels of compute nodes")
	flag.IntVar(&c.Width, "width", 4, "nodes per level")
	flag.IntVar(&c.Fanout, "fanout", 2, "parents joined per node")
	flag.IntVar(&c.Work, "work", 64, "kernel iterations per node per tick")
	flag.IntVar(&c.Ticks, "ticks", 16384, "ticks in the measured pass")
	flag.IntVar(&c.SampleEvery, "sample-every", 64, "stamp residence time every Nth tick")
	flag.IntVar(&c.Buffer, "buffer", 8, "channel buffer, batched composition only")
	flag.IntVar(&c.Batch, "batch", 32, "ticks per message, batched composition only")
	flag.Parse()
	if c.Fanout > c.Width {
		panic("fanout exceeds width: a node cannot join more parents than the level has")
	}
	if c.Batch < 1 || c.Batch > MaxBatch {
		panic("batch outside 1..MaxBatch")
	}
	if c.Ticks%c.Batch != 0 {
		panic("ticks must be a multiple of batch, so no partial batch is flushed")
	}
	return c
}

// Nodes counts the source, the compute nodes and the sink.
func (c Config) Nodes() int { return c.Depth*c.Width + 2 }

// Edges is channel messages per tick: every compute level receives width*fanout
// of them and the sink receives width.
func (c Config) Edges() int { return c.Depth*c.Width*c.Fanout + c.Width }

// Msgs and BatchedMsgs are the channel traffic of a whole measured pass, so the
// traffic a row pays for is visible beside its time.
func (c Config) Msgs() int        { return c.Ticks * c.Edges() }
func (c Config) BatchedMsgs() int { return c.Ticks / c.Batch * c.Edges() }
func noMsgs(Config) int           { return 0 }

// Parent is the topology: node n joins a sliding stencil of fanout neighbours
// from the level below.
func (c Config) Parent(n, j int) int { return (n + j) % c.Width }

// States seeds every compute node distinctly, so no two nodes hold the same
// history and a mis-wired parent shows up in the checksum.
func (c Config) States() []uint64 {
	s := make([]uint64, c.Depth*c.Width)
	for id := range s {
		rng := Splitmix64{State: uint64(id) + 1}
		s[id] = rng.Next()
	}
	return s
}

// Source is level 0: one tick index fans out to width seed values. This is the
// generated input, and it is a pure function of the tick, so every composition
// and every repetition sees the same stream.
func (c Config) Source(tick int, out []uint64) {
	rng := Splitmix64{State: uint64(tick) + 1}
	seed := rng.Next()
	for n := range out {
		out[n] = Fold(seed, uint64(n))
	}
}

// eval is one node's tick in the direct compositions: join the parents in fixed
// index order, then advance this node's state with the kernel.
func (c Config) eval(state, in, out []uint64, level, n int) {
	acc := uint64(0)
	for j := 0; j < c.Fanout; j++ {
		acc = Fold(acc, in[c.Parent(n, j)])
	}
	id := level*c.Width + n
	state[id] = Kernel(state[id], acc, c.Work)
	out[n] = state[id]
}

// Kernel is the work. Every composition calls exactly this, the same number of
// times, with the same arguments.
func Kernel(state, in uint64, work int) uint64 {
	s, x := state, in
	for i := 0; i < work; i++ {
		s += (x - s) >> emaShift
		x = x*mmixMul + mmixAdd
		s ^= x >> 33
	}
	return s
}

// Fold accumulates a value into a checksum, order-sensitively.
func Fold(acc, v uint64) uint64 { return (acc ^ v) * fnvPrime }

// Finish folds every node's final state into the sink's running fold, in node
// order, so the checksum covers the whole history and not only what the sink
// saw.
func Finish(sum uint64, state []uint64) uint64 {
	for _, s := range state {
		sum = Fold(sum, s)
	}
	return sum
}

// Splitmix64 is the PRNG, with the constants of the twin in measurement 02's
// benchutil (from github.com/kronael/rsx), so a value generated here means the
// same thing there.
type Splitmix64 struct {
	State uint64
}

func (s *Splitmix64) Next() uint64 {
	s.State += 0x9E3779B97F4A7C15
	z := s.State
	z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9
	z = (z ^ (z >> 27)) * 0x94D049BB133111EB
	return z ^ (z >> 31)
}

// Composition is one way to wire the same graph.
type Composition struct {
	Name string
	Msgs func(Config) int
	Run  func(Config, *Clock) uint64
}

// All is the comparison set, in table order: each structure at its worst case
// and then at its own documented remedy.
var All = []Composition{Direct, DirectParallel, Channel, ChannelBatched}

// Clock samples residence time — source emit to sink fold — every Nth tick.
// Sampling rather than timing every tick keeps the two clock reads under 1% of
// a tick even at work=1, where timing every tick would be the measurement.
type Clock struct {
	every int
	emit  []time.Time
	lat   []uint32
}

func NewClock(c Config) *Clock {
	n := c.Ticks/c.SampleEvery + 1
	return &Clock{every: c.SampleEvery, emit: make([]time.Time, n), lat: make([]uint32, 0, n)}
}

func (k *Clock) Emit(tick int) {
	if tick%k.every == 0 {
		k.emit[tick/k.every] = time.Now()
	}
}

func (k *Clock) Done(tick int) {
	if tick%k.every == 0 {
		ns := time.Since(k.emit[tick/k.every]).Nanoseconds()
		if ns > math.MaxUint32-1 {
			ns = math.MaxUint32 - 1
		}
		k.lat = append(k.lat, uint32(ns))
	}
}
