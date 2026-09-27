package graph

import (
	"fmt"
	"math"
	"runtime"
	"runtime/metrics"
	"slices"
	"syscall"
	"time"
)

// Run drives one composition: a discarded warmup pass, then the measured pass
// with the machine's own counters differenced across it, then the single RESULT
// line run.py parses. The measured pass builds fresh state, so the warmup cannot
// reach the checksum.
func Run(c Composition) {
	cfg := Configure()
	warm := cfg
	warm.Ticks = warmupTicks(cfg)
	c.Run(warm, NewClock(warm))

	before := take()
	clk := NewClock(cfg)
	checksum := c.Run(cfg, clk)
	after := take()
	report(c, cfg, warm.Ticks, checksum, clk.lat, before, after)
}

// warmupTicks is an eighth of the measured pass: enough to build and tear down
// the same goroutines and channels, grow the heap and make the kernel hot.
func warmupTicks(c Config) int {
	n := c.Ticks / 8 / c.Batch * c.Batch
	if n < c.Batch {
		return c.Batch
	}
	return n
}

// counters is the machine's own view of the pass. Everything here is read twice
// and differenced, so process startup and the warmup are excluded.
type counters struct {
	wall    time.Time
	cpu     float64
	rss     int64
	sched   []uint64
	buckets []float64
	spawned uint64
	alloc   uint64
	mutex   float64
	numgc   uint32
	pause   uint64
}

func take() counters {
	sample := []metrics.Sample{
		{Name: "/sched/latencies:seconds"},
		{Name: "/sched/goroutines-created:goroutines"},
		{Name: "/gc/heap/allocs:bytes"},
		{Name: "/sync/mutex/wait/total:seconds"},
	}
	metrics.Read(sample)
	hist := sample[0].Value.Float64Histogram()
	var stats runtime.MemStats
	runtime.ReadMemStats(&stats)
	cpu, rss := usage()
	return counters{
		wall:    time.Now(),
		cpu:     cpu,
		rss:     rss,
		sched:   slices.Clone(hist.Counts),
		buckets: hist.Buckets,
		spawned: sample[1].Value.Uint64(),
		alloc:   sample[2].Value.Uint64(),
		mutex:   sample[3].Value.Float64(),
		numgc:   stats.NumGC,
		pause:   stats.PauseTotalNs,
	}
}

func report(c Composition, cfg Config, warmup int, checksum uint64, lat []uint32, a, b counters) {
	slices.Sort(lat)
	wall := b.wall.Sub(a.wall).Seconds()
	fmt.Printf(
		"RESULT comp=%s depth=%d width=%d fanout=%d work=%d ticks=%d warmup=%d nodes=%d "+
			"msgs=%d batch=%d buffer=%d wall_s=%.4f ns_per_tick=%.1f thr_ticks_s=%.0f "+
			"p50_ns=%d p99_ns=%d p999_ns=%d max_ns=%d samples=%d cpu_cores=%.2f "+
			"gomaxprocs=%d spawned=%d sched_p50_ns=%d sched_p99_ns=%d mutex_wait_ms=%.2f "+
			"alloc_mb=%.1f numgc=%d gc_pause_total_ms=%.2f rss_peak_mb=%.1f checksum=%x\n",
		c.Name, cfg.Depth, cfg.Width, cfg.Fanout, cfg.Work, cfg.Ticks, warmup, cfg.Nodes(),
		c.Msgs(cfg), cfg.Batch, cfg.Buffer, wall,
		wall*1e9/float64(cfg.Ticks), float64(cfg.Ticks)/wall,
		Percentile(lat, 0.50), Percentile(lat, 0.99), Percentile(lat, 0.999), maxOf(lat),
		len(lat), (b.cpu-a.cpu)/wall,
		runtime.GOMAXPROCS(0), b.spawned-a.spawned,
		schedPercentile(a, b, 0.50), schedPercentile(a, b, 0.99),
		(b.mutex-a.mutex)*1e3,
		float64(b.alloc-a.alloc)/(1<<20), b.numgc-a.numgc,
		float64(b.pause-a.pause)/1e6, float64(b.rss)/1024.0, checksum,
	)
}

// Percentile is the nearest-rank percentile over an ascending-sorted slice,
// mirroring measurement 02's benchutil so a percentile means the same thing in
// both measurements.
func Percentile(sorted []uint32, q float64) uint32 {
	if len(sorted) == 0 {
		return 0
	}
	idx := int(math.Ceil(q*float64(len(sorted)))) - 1
	if idx < 0 {
		idx = 0
	}
	if idx >= len(sorted) {
		idx = len(sorted) - 1
	}
	return sorted[idx]
}

func maxOf(sorted []uint32) uint32 {
	if len(sorted) == 0 {
		return 0
	}
	return sorted[len(sorted)-1]
}

// schedPercentile reads the quantile, in ns, of the runtime's own
// runnable-to-running histogram over the measured pass. This is queueing
// measured by something other than my clock: work never appears in it.
func schedPercentile(a, b counters, q float64) uint64 {
	total := uint64(0)
	for i := range b.sched {
		total += b.sched[i] - a.sched[i]
	}
	if total == 0 {
		return 0
	}
	target := uint64(float64(total)*q + 0.5)
	seen := uint64(0)
	for i := range b.sched {
		seen += b.sched[i] - a.sched[i]
		if seen >= target {
			hi := b.buckets[i+1]
			if math.IsInf(hi, 1) {
				hi = b.buckets[i]
			}
			return uint64(hi * 1e9)
		}
	}
	return 0
}

// usage is the process's CPU seconds and its peak RSS in kB. Measurement 02's
// benchutil reads both out of /proc for cross-language comparability; there is
// no twin in another language here, and /proc's 10 ms USER_HZ tick quantises a
// 13 ms repetition to zero, so this reads getrusage's microseconds instead.
// cpu_cores is one of the five readings that separate queueing from work and it
// has to survive the fastest row.
func usage() (float64, int64) {
	var ru syscall.Rusage
	if err := syscall.Getrusage(syscall.RUSAGE_SELF, &ru); err != nil {
		panic("getrusage: " + err.Error())
	}
	seconds := func(t syscall.Timeval) float64 {
		return float64(t.Sec) + float64(t.Usec)/1e6
	}
	return seconds(ru.Utime) + seconds(ru.Stime), ru.Maxrss
}
