//! PROBE P2 — 50k concurrent periodic tasks (timer + fan-in).
//! Each task ticks on an absolute-deadline schedule, records wakeup lag and
//! sends an 8-byte event into one shared fan-in channel.
//! Go twin: go/sleepers/main.go.

use std::time::Duration;

use go_vs_rust_bench::{RunInfo, print_result, read_cpu_ticks};
use tokio::sync::mpsc::{Receiver, Sender};
use tokio::sync::watch;
use tokio::time::Instant;

const TASKS: usize = 50_000;
const TICKS: usize = 30;
const WARMUP_TICKS: usize = 5;
const INTERVAL_MS: u64 = 100;
const FAN_IN_CAP: usize = 4096;

async fn ticker(id: usize, mut start: watch::Receiver<bool>, events: Sender<u64>) -> Vec<u32> {
    let mut lags = Vec::with_capacity(TICKS - WARMUP_TICKS);
    start.changed().await.expect("start gate dropped");
    let interval = Duration::from_millis(INTERVAL_MS);
    let offset = Duration::from_nanos(INTERVAL_MS * 1_000_000 * id as u64 / TASKS as u64);
    let mut deadline = Instant::now() + offset;
    for tick in 0..TICKS {
        deadline += interval;
        tokio::time::sleep_until(deadline).await;
        if tick >= WARMUP_TICKS {
            let lag = Instant::now()
                .saturating_duration_since(deadline)
                .as_nanos();
            lags.push(lag as u32);
        }
        let event = ((id as u64) << 32) | tick as u64;
        events.send(event).await.expect("collector gone");
    }
    lags
}

async fn collect(mut events: Receiver<u64>) -> u64 {
    let mut checksum = 0u64;
    while let Some(event) = events.recv().await {
        checksum = checksum.wrapping_add(event);
    }
    checksum
}

#[tokio::main]
async fn main() {
    let (gate, start) = watch::channel(false);
    let (events, sink) = tokio::sync::mpsc::channel(FAN_IN_CAP);
    let collected = tokio::spawn(collect(sink));
    let mut tickers = Vec::with_capacity(TASKS);
    for id in 0..TASKS {
        tickers.push(tokio::spawn(ticker(id, start.clone(), events.clone())));
    }
    drop(start);
    drop(events);
    tokio::time::sleep(Duration::from_millis(300)).await;

    let cpu0 = read_cpu_ticks();
    let t0 = Instant::now();
    gate.send(true).expect("no ticker waiting on the gate");
    let mut finished = Vec::with_capacity(TASKS);
    for handle in tickers {
        finished.push(handle.await.expect("ticker panicked"));
    }
    let checksum = collected.await.expect("collector panicked");
    let wall_s = t0.elapsed().as_secs_f64();
    let cpu_ticks = read_cpu_ticks() - cpu0;

    let mut samples = Vec::with_capacity(TASKS * (TICKS - WARMUP_TICKS));
    for lags in finished {
        samples.extend_from_slice(&lags);
    }

    let info = RunInfo {
        case: "P2",
        tasks: TASKS,
        ops: (TASKS * TICKS) as u64,
        wall_s,
        cpu_ticks,
        checksum,
    };
    print_result(&info, &mut samples);
}
