// Package divto runs one work unit — gonum's element-wise float64 divide —
// once scalar and once vectorised, and proves the two did the same work.
//
// Provenance: the kernel is floats.DivTo in gonum. Scalar is gonum's own
// portable loop (internal/asm/f64/stubs_noasm.go), unchanged. Vector is that
// loop with the Go 1.27 simd package. gonum ships hand-written amd64 assembly
// for the same function (internal/asm/f64/divto_amd64.s), which is why this
// loop is worth measuring rather than invented to be measured.
//
// Everything except the kernel lives in this file and is shared by both
// binaries: the input, the timing, the checksum and the output format cannot
// differ between the two configurations, because there is only one copy.
package divto

import (
	"flag"
	"fmt"
	"math"
	"runtime/debug"
	"simd"
	"strconv"
	"strings"
	"time"
)

// Kernel is the work unit under test. Scalar and Vector are its two
// configurations and nothing else in this package knows which one it has.
type Kernel func(dst, x, y []float64)

// fill draws n operands from [1, 2). Splitmix64 with the constants used by
// measurement 02, so input generation is the same across this project. The
// range matters: both operands normal and every quotient in (0.5, 2) keeps the
// divider off any data-dependent path, so a size difference in the table is a
// size difference and not a change of operand.
func fill(seed uint64, n int) []float64 {
	state := seed
	out := make([]float64, n)
	for i := range out {
		state += 0x9E3779B97F4A7C15
		z := state
		z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9
		z = (z ^ (z >> 27)) * 0x94D049BB133111EB
		z ^= z >> 31
		out[i] = 1 + float64(z>>11)*0x1p-53
	}
	return out
}

// fold is FNV-1a over the bits of every element. Identical work is proved with
// it, never assumed: the runner refuses to report when two variants fold
// different values at the same size.
func fold(v []float64) uint64 {
	h := uint64(14695981039346656037)
	for _, f := range v {
		h = (h ^ math.Float64bits(f)) * 1099511628211
	}
	return h
}

// sample times one batch of repeat calls and returns nanoseconds. Both kernels
// are noinline, as the assembly stub they stand in for also is, so the batch
// cannot collapse into one call and the small sizes pay a real call each.
func sample(k Kernel, dst, x, y []float64, repeat int) float64 {
	start := time.Now()
	for i := 0; i < repeat; i++ {
		k(dst, x, y)
	}
	return float64(time.Since(start).Nanoseconds())
}

// goamd64 is what this binary was built for, read out of its own build info
// rather than taken on trust from whoever labelled the row.
func goamd64() string {
	info, ok := debug.ReadBuildInfo()
	if !ok {
		return "unknown"
	}
	for _, s := range info.Settings {
		if s.Key == "GOAMD64" {
			return s.Value
		}
	}
	return "unset"
}

// Main sweeps the sizes given on the command line and prints one RESULT line
// per size: every sample, not a summary. The summary belongs to the runner.
func Main(name string, k Kernel) {
	sizes := flag.String("sizes", "1024", "comma-separated element counts")
	visits := flag.Int("visits", 16_000_000, "element visits per sample")
	samples := flag.Int("samples", 11, "measured samples per size")
	warmup := flag.Int("warmup", 3, "discarded samples per size")
	flag.Parse()

	for _, field := range strings.Split(*sizes, ",") {
		n, err := strconv.Atoi(field)
		if err != nil || n < 1 {
			panic("bad size: " + field)
		}
		repeat := max(*visits/n, 1)
		x, y, dst := fill(1, n), fill(2, n), make([]float64, n)
		for i := 0; i < *warmup; i++ {
			sample(k, dst, x, y, repeat)
		}
		ns := make([]string, *samples)
		for i := range ns {
			elapsed := sample(k, dst, x, y, repeat)
			ns[i] = strconv.FormatFloat(elapsed/float64(repeat*n), 'f', 4, 64)
		}
		fmt.Printf("RESULT kernel=%s goamd64=%s vector_bits=%d lanes=%d emulated=%v "+
			"elements=%d repeat=%d samples=%d checksum=%016x ns_per_elem=%s\n",
			name, goamd64(), simd.VectorBitSize(), (simd.Float64s{}).Len(), simd.Emulated(),
			n, repeat, *samples, fold(dst), strings.Join(ns, ","))
	}
}
