//! CASE A — tail latency under unpredictable CPU bursts (open-loop).
//! A generator task releases 50 requests every 1ms (50k req/s) and spawns one
//! tokio task per request. 1 in BENCH_HEAVY_EVERY requests (PRNG hash of the
//! id, identical in Go) runs an 80M-iteration PRNG chain (~75ms here, ~100ms
//! in Go) — an unpredictable expensive path inside an ordinary handler; the
//! rest run 8k iterations (~7.5us). Spins are ITERATION-bounded, not
//! wall-clock-bounded, and their fold feeds the checksum: both sides provably
//! execute identical CPU work at their native speed, and the loop cannot be
//! optimized away. Latency is measured against the request's INTENDED arrival
//! tick (open-loop: immune to coordinated omission). tokio reschedules only at
//! await points and a compute loop has none, so a burst holds its worker for
//! its whole duration. BENCH_MITIGATE=1 wraps the burst in
//! tokio::task::block_in_place — tokio's own documented remedy, and the tuned
//! row the table keeps. Go twin: go/casea/main.go.

use std::sync::Arc;
use std::sync::atomic::{AtomicU32, AtomicU64, Ordering};
use std::time::Duration;

use go_vs_rust_bench::{RunInfo, Splitmix64, print_result, read_cpu_ticks};
use tokio::sync::mpsc::Sender;
use tokio::time::Instant;

const BATCH: usize = 50;
const TICK: Duration = Duration::from_millis(1);
const TOTAL: usize = 600_000;
const WARMUP: usize = 50_000;
const LIGHT_ITERS: usize = 8_000;
const HEAVY_ITERS: usize = 80_000_000;
const DEFAULT_HEAVY_EVERY: u64 = 1_666;
const HEAVY_SENTINEL: u32 = u32::MAX;

struct Requests {
    lat: Vec<AtomicU32>,
    work: Vec<AtomicU64>,
    every: u64,
    mitigate: bool,
}

fn heavy_every() -> u64 {
    let set = std::env::var("BENCH_HEAVY_EVERY").unwrap_or_default();
    if set.is_empty() {
        return DEFAULT_HEAVY_EVERY;
    }
    set.parse().expect("parse BENCH_HEAVY_EVERY")
}

fn mitigate() -> bool {
    match std::env::var("BENCH_MITIGATE").unwrap_or_default().as_str() {
        "" | "0" => false,
        "1" => true,
        other => panic!("set BENCH_MITIGATE to 0 or 1, got {other:?}"),
    }
}

fn spin_work(seed: u64, iters: usize) -> u64 {
    let mut rng = Splitmix64(seed);
    let mut fold = 0;
    for _ in 0..iters {
        fold ^= rng.next_u64();
    }
    fold
}

fn is_heavy(id: u64, every: u64) -> bool {
    let mut rng = Splitmix64(id);
    rng.next_u64().is_multiple_of(every)
}

async fn handle(id: usize, intended: Instant, requests: Arc<Requests>, done: Sender<()>) {
    if is_heavy(id as u64, requests.every) {
        let fold = if requests.mitigate {
            tokio::task::block_in_place(|| spin_work(id as u64, HEAVY_ITERS))
        } else {
            spin_work(id as u64, HEAVY_ITERS)
        };
        requests.work[id].store(fold, Ordering::Relaxed);
        requests.lat[id].store(HEAVY_SENTINEL, Ordering::Relaxed);
    } else {
        requests.work[id].store(spin_work(id as u64, LIGHT_ITERS), Ordering::Relaxed);
        let ns = Instant::now()
            .saturating_duration_since(intended)
            .as_nanos();
        let capped = ns.min(u128::from(HEAVY_SENTINEL) - 1) as u32;
        requests.lat[id].store(capped, Ordering::Relaxed);
    }
    drop(done);
}

#[tokio::main]
async fn main() {
    let every = heavy_every();
    let mitigate = mitigate();
    let requests = Arc::new(Requests {
        lat: (0..TOTAL).map(|_| AtomicU32::new(0)).collect(),
        work: (0..TOTAL).map(|_| AtomicU64::new(0)).collect(),
        every,
        mitigate,
    });
    let (done, mut drained) = tokio::sync::mpsc::channel::<()>(1);

    let cpu0 = read_cpu_ticks();
    let t0 = Instant::now();
    let start = Instant::now();
    for t in 0..TOTAL / BATCH {
        let intended = start + TICK * t as u32;
        if intended > Instant::now() {
            tokio::time::sleep_until(intended).await;
        }
        for k in 0..BATCH {
            let id = t * BATCH + k;
            tokio::spawn(handle(id, intended, requests.clone(), done.clone()));
        }
    }
    drop(done);
    while drained.recv().await.is_some() {}
    let wall_s = t0.elapsed().as_secs_f64();
    let cpu_ticks = read_cpu_ticks() - cpu0;

    let mut checksum = 0u64;
    let mut samples = Vec::with_capacity(TOTAL - WARMUP);
    for id in 0..TOTAL {
        checksum ^= requests.work[id].load(Ordering::Relaxed);
        let lat = requests.lat[id].load(Ordering::Relaxed);
        if lat == HEAVY_SENTINEL {
            checksum ^= id as u64;
        } else if id >= WARMUP {
            samples.push(lat);
        }
    }
    checksum ^= samples.len() as u64;

    let info = RunInfo {
        case: "A",
        tasks: TOTAL,
        ops: TOTAL as u64,
        wall_s,
        cpu_ticks,
        checksum,
    };
    print_result(&info, &mut samples);
    let workers = tokio::runtime::Handle::current().metrics().num_workers();
    println!("REGIME workers={workers} heavy_every={every} mitigate={mitigate}");
}
