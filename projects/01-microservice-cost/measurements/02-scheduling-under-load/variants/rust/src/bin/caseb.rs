//! CASE B — CPU + allocation-bound parallel transform with a live window.
//! 8 worker threads (no cross-worker communication: isolates compute, the
//! allocator and the Go twin's GC behavior). Per message: build a
//! 64..320-element Vec<u64> from splitmix64, xor-fold it, sort it,
//! binary-probe a rolling 512-message window (a live heap the Go twin's GC
//! must repeatedly mark; here every displaced message is an inline free),
//! record per-message latency. Go twin: go/caseb/main.go.

use std::sync::{Arc, Barrier};
use std::time::{Duration, Instant};

use go_vs_rust_bench::{RunInfo, Splitmix64, print_result, read_cpu_ticks};

const WORKERS: usize = 8;
const MSGS_PER_WORKER: usize = 1_000_000;
const WARMUP_MSGS: usize = 50_000;
const N_MIN: u64 = 64;
const N_SPAN: u64 = 257;
const RING_SIZE: usize = 512;
const PROBES: usize = 16;
const SEED_MULTIPLIER: u64 = 0x9E37_79B9_7F4A_7C15;

fn worker(id: usize, start: Arc<Barrier>) -> (Vec<u32>, u64) {
    let mut rng = Splitmix64((id as u64 + 1).wrapping_mul(SEED_MULTIPLIER));
    let mut ring: Vec<Vec<u64>> = vec![Vec::new(); RING_SIZE];
    let mut lags = Vec::with_capacity(MSGS_PER_WORKER - WARMUP_MSGS);
    let mut checksum = 0u64;
    start.wait();
    for m in 0..MSGS_PER_WORKER {
        let t0 = Instant::now();
        let n = (N_MIN + rng.next_u64() % N_SPAN) as usize;
        let mut values = Vec::with_capacity(n);
        let mut fold = 0u64;
        for _ in 0..n {
            let r = rng.next_u64();
            values.push(r);
            fold ^= r;
        }
        values.sort_unstable();
        let median = values[n / 2];
        for _ in 0..PROBES {
            let target = rng.next_u64();
            let slot = (rng.next_u64() % RING_SIZE as u64) as usize;
            let entry = &ring[slot];
            if !entry.is_empty() {
                checksum ^= entry.partition_point(|&v| v < target) as u64;
            }
        }
        checksum ^= fold ^ median;
        ring[m % RING_SIZE] = values;
        if m >= WARMUP_MSGS {
            lags.push(t0.elapsed().as_nanos() as u32);
        }
    }
    (lags, checksum)
}

fn main() {
    let start = Arc::new(Barrier::new(WORKERS + 1));
    let workers: Vec<_> = (0..WORKERS)
        .map(|id| {
            let start = start.clone();
            std::thread::spawn(move || worker(id, start))
        })
        .collect();
    std::thread::sleep(Duration::from_millis(50));

    let cpu0 = read_cpu_ticks();
    let t0 = Instant::now();
    start.wait();
    let finished: Vec<(Vec<u32>, u64)> = workers
        .into_iter()
        .map(|handle| handle.join().expect("worker panicked"))
        .collect();
    let wall_s = t0.elapsed().as_secs_f64();
    let cpu_ticks = read_cpu_ticks() - cpu0;

    let mut samples = Vec::with_capacity(WORKERS * (MSGS_PER_WORKER - WARMUP_MSGS));
    let mut checksum = 0u64;
    for (lags, sum) in finished {
        samples.extend_from_slice(&lags);
        checksum ^= sum;
    }

    let info = RunInfo {
        case: "B",
        tasks: WORKERS,
        ops: (WORKERS * MSGS_PER_WORKER) as u64,
        wall_s,
        cpu_ticks,
        checksum,
    };
    print_result(&info, &mut samples);
}
