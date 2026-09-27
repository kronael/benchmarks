package divto

import (
	"math"
	"simd"
	"testing"
)

// TestPairDoesIdenticalWork is the checksum gate at unit scale. Every length up
// to a few vectors, so every tail position is covered: one differing bit at any
// size means the table would be comparing two computations, not two
// configurations of one.
func TestPairDoesIdenticalWork(t *testing.T) {
	for n := 0; n <= 259; n++ {
		x, y := fill(1, n), fill(2, n)
		got, want := make([]float64, n), make([]float64, n)
		Scalar(want, x, y)
		Vector(got, x, y)
		if fold(got) == fold(want) {
			continue
		}
		for i := range want {
			if got[i] != want[i] {
				t.Fatalf("n=%d: element %d scalar=%x vector=%x", n, i,
					math.Float64bits(want[i]), math.Float64bits(got[i]))
			}
		}
		t.Fatalf("n=%d: folds differ but every element matches", n)
	}
}

// TestFoldSeesOneBit keeps the gate from being vacuous: a fold that cannot
// notice a single flipped bit would pass any two implementations.
func TestFoldSeesOneBit(t *testing.T) {
	v := fill(1, 64)
	before := fold(v)
	v[63] = math.Float64frombits(math.Float64bits(v[63]) ^ 1)
	if fold(v) == before {
		t.Fatal("fold is blind to a one-bit change")
	}
}

// TestInputStaysNormal holds the operand range the design depends on: both
// operands in [1, 2) and every quotient normal, so no size in the sweep can
// hand the divider a subnormal and time something else.
func TestInputStaysNormal(t *testing.T) {
	x, y := fill(1, 4096), fill(2, 4096)
	for i := range x {
		q := x[i] / y[i]
		if x[i] < 1 || x[i] >= 2 || y[i] < 1 || y[i] >= 2 || q < 0.5 || q >= 2 {
			t.Fatalf("element %d out of range: x=%v y=%v q=%v", i, x[i], y[i], q)
		}
	}
}

// TestRegime fails when this box would measure something other than hardware
// SIMD. An emulated or one-lane vector makes the axis meaningless, and finding
// that out from the numbers afterwards is too late.
func TestRegime(t *testing.T) {
	if simd.Emulated() {
		t.Fatal("simd is emulated here; the vector row would measure the emulation")
	}
	lanes := (simd.Float64s{}).Len()
	if lanes < 2 {
		t.Fatalf("float64 lanes=%d: nothing to vectorise", lanes)
	}
	t.Logf("vector_bits=%d float64_lanes=%d goamd64=%s", simd.VectorBitSize(), lanes, goamd64())
}
