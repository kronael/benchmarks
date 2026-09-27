package divto

import "simd"

// Vector is the same loop, one vector of lanes at a time. The lane count is a
// property of the machine and not of this source: simd is vector-length
// agnostic and dispatches on the hardware, so Len() is 4 on this box and the
// tail is whatever LoadFloat64sPart could not fill.
//
// The tail's padded lanes divide zero by zero and produce NaN. StorePart never
// writes them, so the result is bit-identical to Scalar; what they cost is part
// of what the sizes that are not a multiple of the lane count measure.
//
//go:noinline
func Vector(dst, x, y []float64) {
	lanes := (simd.Float64s{}).Len()
	i := 0
	for ; i+lanes <= len(x); i += lanes {
		simd.LoadFloat64s(x[i:]).Div(simd.LoadFloat64s(y[i:])).Store(dst[i:])
	}
	if i < len(x) {
		a, _ := simd.LoadFloat64sPart(x[i:])
		b, _ := simd.LoadFloat64sPart(y[i:])
		a.Div(b).StorePart(dst[i:])
	}
}
