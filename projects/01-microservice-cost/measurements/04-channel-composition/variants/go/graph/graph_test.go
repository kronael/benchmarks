package graph

import "testing"

// shapes covers a plain stencil, a full join where every node reads the whole
// level below, and a fanout of one. The send order the channel compositions
// rely on has to hold in all three.
var shapes = []Config{
	{Depth: 4, Width: 3, Fanout: 2, Work: 4, Ticks: 256, SampleEvery: 8, Buffer: 4, Batch: 8},
	{Depth: 3, Width: 4, Fanout: 4, Work: 2, Ticks: 128, SampleEvery: 8, Buffer: 2, Batch: 8},
	{Depth: 2, Width: 2, Fanout: 1, Work: 1, Ticks: 64, SampleEvery: 8, Buffer: 1, Batch: 8},
}

// The gate the measurement rests on: the compositions do identical work, and
// they prove it rather than assert it.
func TestCompositionsAgree(t *testing.T) {
	for _, cfg := range shapes {
		want := uint64(0)
		for i, c := range All {
			got := c.Run(cfg, NewClock(cfg))
			if i == 0 {
				want = got
				continue
			}
			if got != want {
				t.Errorf("shape %+v: %s checksum %x, %s %x", cfg, c.Name, got, All[0].Name, want)
			}
		}
	}
}

// A checksum that does not move with the work would pass the gate while proving
// nothing.
func TestChecksumFollowsWork(t *testing.T) {
	cfg := shapes[0]
	more := cfg
	more.Work = cfg.Work + 1
	for _, c := range All {
		if c.Run(cfg, NewClock(cfg)) == c.Run(more, NewClock(more)) {
			t.Errorf("%s: checksum unchanged by an extra kernel iteration", c.Name)
		}
	}
}

// The fold is order-sensitive so that a join arriving out of order fails the
// gate instead of passing quietly.
func TestFoldIsOrderSensitive(t *testing.T) {
	if Fold(Fold(0, 1), 2) == Fold(Fold(0, 2), 1) {
		t.Error("fold is commutative: a mis-ordered join would not be caught")
	}
}

// Residence time is sampled, so a row's sample count has to be the count the
// sweep asked for.
func TestClockSamplesEveryNthTick(t *testing.T) {
	cfg := shapes[0]
	for _, c := range All {
		clk := NewClock(cfg)
		c.Run(cfg, clk)
		if len(clk.lat) != cfg.Ticks/cfg.SampleEvery {
			t.Errorf("%s: %d residence samples, want %d", c.Name, len(clk.lat), cfg.Ticks/cfg.SampleEvery)
		}
	}
}
