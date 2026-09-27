// CASE C — receiver work width under contention.
// Case A's driver verbatim — 50 requests released every 1ms (50k req/s), one
// goroutine per request, 1 in BENCH_HEAVY_EVERY running the same 80M-iteration
// splitmix64 burst, latency measured against the INTENDED arrival tick — with
// one thing changed: the light request reduces a payload window instead of
// running a PRNG chain, because a PRNG chain is a dependent sequence and
// cannot be vectorised without changing the work. BENCH_WIDTH selects how that
// reduction executes, scalar or vector, and nothing else moves. Case A stays
// untouched: it is the cross-language row against the Rust twin.
// No Rust twin here. The gate is across widths, not across languages.
package main

import (
	"math"
	"os"
	"runtime/debug"
	"simd"
	"strconv"
	"sync"
	"time"

	"benchgovsrust/benchutil"
)

const (
	batch             = 50 // requests released per 1ms tick = 50k req/s
	tick              = time.Millisecond
	defaultTotal      = 600_000    // 12s of traffic
	warmupFraction    = 12         // first 1/12 of traffic (1s at the default) excluded
	defaultHeavyIters = 80_000_000 // ~100ms, identical to case A's burst
	defaultHeavyEvery = 2_500      // ~20 heavy/s => 2.0 cores of burst on this box
	heavySentinel     = math.MaxUint32

	// The payload pool is built once, before the measured window, and is read
	// only: a per-request allocation would turn this into an allocator
	// measurement. 512 KiB of float64 holds eight 64 KiB windows, so a window
	// is L2-resident and the reduce stays bound by its own dependent adds
	// rather than by memory bandwidth on either side of the axis.
	poolLen    = 65_536
	window     = 8_192
	windows    = poolLen / window
	poolSeed   = 0x5EED_CA5E_0000_0C03
	valueBits  = 20
	valueMask  = (1 << valueBits) - 1
	threshold  = 1 << (valueBits - 1)
	overWeight = 3
)

// The scalar and vector reductions are the pair, and they are the whole axis:
// for each element, add it once below the threshold and three times at or
// above it. They agree bit for bit because every value is an exact integer —
// elements below 2^20, weights 1 and 3, 8192 of them, so every partial sum is
// an integer below 2^35 and float64 arithmetic over them does not round. That
// exactness is what lets one checksum gate three widths; without it the
// lane-partitioned sum and the sequential sum would differ in the low bits and
// there would be no gate at all.

func reduceScalar(payload []float64) float64 {
	acc := 0.0
	for _, x := range payload {
		weight := 1.0
		if x >= threshold {
			weight = overWeight
		}
		acc += x * weight
	}
	return acc
}

func reduceSIMD(payload []float64) float64 {
	limit := simd.BroadcastFloat64s(threshold)
	over := simd.BroadcastFloat64s(overWeight)
	under := simd.BroadcastFloat64s(1)
	var acc simd.Float64s
	for i := 0; i < len(payload); {
		// LoadFloat64sPart zero-fills a short tail, and a zero element is
		// below the threshold and contributes zero, so any vector length
		// works without a tail case.
		values, loaded := simd.LoadFloat64sPart(payload[i:])
		weights := over.IfElse(values.GreaterEqual(limit), under)
		acc = values.MulAdd(weights, acc)
		i += loaded
	}
	var lanes [8]float64
	acc.Store(lanes[:acc.Len()])
	total := 0.0
	for _, lane := range lanes[:acc.Len()] {
		total += lane
	}
	return total
}

// spinWork is case A's burst, copied rather than shared: benchutil mirrors the
// Rust twin 1:1 and case C has no Rust twin. The burst is the contention
// source and is scalar in every row, so it cannot move with the axis.
func spinWork(seed uint64, iters int) uint64 {
	rng := benchutil.Splitmix64{State: seed}
	fold := uint64(0)
	for i := 0; i < iters; i++ {
		fold ^= rng.Next()
	}
	return fold
}

func isHeavy(id, every uint64) bool {
	rng := benchutil.Splitmix64{State: id}
	return rng.Next()%every == 0
}

func envUint(name string, fallback uint64) uint64 {
	v := os.Getenv(name)
	if v == "" {
		return fallback
	}
	n, err := strconv.ParseUint(v, 10, 64)
	if err != nil {
		panic("parse " + name + ": " + err.Error())
	}
	return n
}

// reduceFor refuses an unknown or absent width rather than defaulting to one,
// because a row mislabelled in the table is worse than a run that does not
// start. It also refuses an emulated vector: a pure-Go fallback would report
// itself as the SIMD row while measuring something else entirely.
func reduceFor(width string) func([]float64) float64 {
	switch width {
	case "scalar":
		return reduceScalar
	case "simd":
		if simd.Emulated() {
			panic("BENCH_WIDTH=simd but simd is emulated: this would not measure a vector unit")
		}
		return reduceSIMD
	}
	panic("set BENCH_WIDTH to scalar or simd, got " + strconv.Quote(width))
}

// buildSetting reports what the binary was actually compiled with, so the
// stock row and the GOAMD64=v3 row name their own build instead of being told
// apart by their position in the table.
func buildSetting(key string) string {
	info, ok := debug.ReadBuildInfo()
	if !ok {
		panic("no build info: cannot prove which build this row is")
	}
	for _, setting := range info.Settings {
		if setting.Key == key {
			return setting.Value
		}
	}
	return "unset"
}

func buildPool() []float64 {
	rng := benchutil.Splitmix64{State: poolSeed}
	pool := make([]float64, poolLen)
	for i := range pool {
		pool[i] = float64(rng.Next() & valueMask)
	}
	return pool
}

func handle(id int, intended time.Time, lat []uint32, work []uint64, pool []float64,
	reduce func([]float64) float64, every uint64, heavyIters int, wg *sync.WaitGroup) {
	defer wg.Done()
	if isHeavy(uint64(id), every) {
		work[id] = spinWork(uint64(id), heavyIters)
		lat[id] = heavySentinel
		return
	}
	off := (id % windows) * window
	work[id] = uint64(reduce(pool[off : off+window]))
	ns := time.Since(intended).Nanoseconds()
	if ns > math.MaxUint32-1 {
		ns = math.MaxUint32 - 1
	}
	lat[id] = uint32(ns)
}

func main() {
	width := os.Getenv("BENCH_WIDTH")
	reduce := reduceFor(width)
	every := envUint("BENCH_HEAVY_EVERY", defaultHeavyEvery)
	total := int(envUint("BENCH_TOTAL", defaultTotal))
	heavyIters := int(envUint("BENCH_HEAVY_ITERS", defaultHeavyIters))
	warmup := total / warmupFraction

	pool := buildPool()
	lat := make([]uint32, total)
	work := make([]uint64, total)
	var wg sync.WaitGroup

	cpu0 := benchutil.ReadCPUTicks()
	t0 := time.Now()
	start := time.Now()
	for t := 0; t < total/batch; t++ {
		intended := start.Add(time.Duration(t) * tick)
		if wait := time.Until(intended); wait > 0 {
			time.Sleep(wait)
		}
		for k := 0; k < batch; k++ {
			id := t*batch + k
			wg.Add(1)
			go handle(id, intended, lat, work, pool, reduce, every, heavyIters, &wg)
		}
	}
	wg.Wait()
	wallS := time.Since(t0).Seconds()
	cpuTicks := benchutil.ReadCPUTicks() - cpu0

	// Addition, not xor. The reduction runs over a pool of `windows` shared
	// payloads, so its result repeats every `windows` requests, and xor cancels
	// any value that appears an even number of times — the gate would pass on
	// zero. Case A can xor because its fold is seeded by the request id.
	checksum := uint64(0)
	clamped := 0
	samples := make([]uint32, 0, total-warmup)
	for id := 0; id < total; id++ {
		checksum += work[id]
		if lat[id] == heavySentinel {
			checksum += uint64(id)
			continue
		}
		if lat[id] == math.MaxUint32-1 {
			clamped++
		}
		if id >= warmup {
			samples = append(samples, lat[id])
		}
	}
	checksum += uint64(len(samples))

	// The regime this row claims to have run in, beside the numbers that claim
	// it. An emulated or narrower vector, or a saturated latency field, makes
	// the row mean something other than the table says.
	benchutil.PrintResult("C", "go", total, uint64(total), wallS, cpuTicks, samples, checksum)
	os.Stdout.WriteString("REGIME width=" + width +
		" goamd64=" + buildSetting("GOAMD64") +
		" goexperiment=" + buildSetting("GOEXPERIMENT") +
		" vector_bits=" + strconv.Itoa(simd.VectorBitSize()) +
		" lanes=" + strconv.Itoa(simd.BroadcastFloat64s(0).Len()) +
		" emulated=" + strconv.FormatBool(simd.Emulated()) +
		" heavy_every=" + strconv.FormatUint(every, 10) +
		" clamped=" + strconv.Itoa(clamped) + "\n")
}
