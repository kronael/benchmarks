package divto

// Scalar is gonum's portable DivTo loop, unchanged:
//
//	for i, v := range s {
//		dst[i] = v / t[i]
//	}
//
// from internal/asm/f64/stubs_noasm.go. On amd64 gonum replaces it with
// hand-written assembly; here it is the unvectorised half of the pair.
//
//go:noinline
func Scalar(dst, x, y []float64) {
	for i, v := range x {
		dst[i] = v / y[i]
	}
}
