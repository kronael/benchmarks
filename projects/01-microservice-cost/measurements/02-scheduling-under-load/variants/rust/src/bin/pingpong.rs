//! PROBE P1 — massive-concurrency message passing.
//! 50k actor pairs (100k tokio tasks). Each pair plays ROUNDS ping-pongs over
//! two mpsc(1) channels — the tokio-native idiom, and equivalent to the Go
//! twin's unbuffered rendezvous channels because the exchange strictly
//! alternates. Go twin: go/pingpong/main.go.

use std::time::Duration;

use go_vs_rust_bench::{RunInfo, print_result, read_cpu_ticks};
use tokio::sync::mpsc::{Receiver, Sender};
use tokio::sync::watch;
use tokio::time::Instant;

const PAIRS: usize = 50_000;
const ROUNDS: usize = 200;
const WARMUP_ROUNDS: usize = 16;
const SAMPLE_EVERY: usize = 4;
const PER_PAIR: usize = (ROUNDS - WARMUP_ROUNDS) / SAMPLE_EVERY + 1;

async fn pinger(
    mut start: watch::Receiver<bool>,
    ping: Sender<u64>,
    mut pong: Receiver<u64>,
) -> (Vec<u32>, u64) {
    let mut lags = Vec::with_capacity(PER_PAIR);
    start.changed().await.expect("start gate dropped");
    let mut v = 0u64;
    for round in 0..ROUNDS {
        let sampled =
            round >= WARMUP_ROUNDS && (round - WARMUP_ROUNDS).is_multiple_of(SAMPLE_EVERY);
        if sampled {
            let t0 = Instant::now();
            ping.send(v).await.expect("ponger gone");
            v = pong.recv().await.expect("ponger gone");
            lags.push(t0.elapsed().as_nanos() as u32);
        } else {
            ping.send(v).await.expect("ponger gone");
            v = pong.recv().await.expect("ponger gone");
        }
    }
    drop(ping);
    (lags, v)
}

async fn ponger(mut ping: Receiver<u64>, pong: Sender<u64>) {
    while let Some(v) = ping.recv().await {
        pong.send(v + 1).await.expect("pinger gone");
    }
}

#[tokio::main]
async fn main() {
    let (gate, start) = watch::channel(false);
    let mut pingers = Vec::with_capacity(PAIRS);
    let mut pongers = Vec::with_capacity(PAIRS);
    for _ in 0..PAIRS {
        let (ping_tx, ping_rx) = tokio::sync::mpsc::channel(1);
        let (pong_tx, pong_rx) = tokio::sync::mpsc::channel(1);
        pingers.push(tokio::spawn(pinger(start.clone(), ping_tx, pong_rx)));
        pongers.push(tokio::spawn(ponger(ping_rx, pong_tx)));
    }
    drop(start);
    tokio::time::sleep(Duration::from_millis(300)).await;

    let cpu0 = read_cpu_ticks();
    let t0 = Instant::now();
    gate.send(true).expect("no pinger waiting on the gate");
    let mut finished = Vec::with_capacity(PAIRS);
    for handle in pingers {
        finished.push(handle.await.expect("pinger panicked"));
    }
    for handle in pongers {
        handle.await.expect("ponger panicked");
    }
    let wall_s = t0.elapsed().as_secs_f64();
    let cpu_ticks = read_cpu_ticks() - cpu0;

    let mut samples = Vec::with_capacity(PAIRS * PER_PAIR);
    let mut checksum = 0u64;
    for (lags, last) in finished {
        samples.extend_from_slice(&lags);
        checksum = checksum.wrapping_add(last);
    }

    let info = RunInfo {
        case: "P1",
        tasks: PAIRS * 2,
        ops: (PAIRS * ROUNDS) as u64,
        wall_s,
        cpu_ticks,
        checksum,
    };
    print_result(&info, &mut samples);
}
