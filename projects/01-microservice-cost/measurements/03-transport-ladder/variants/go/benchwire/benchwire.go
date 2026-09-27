// Package benchwire mirrors ../../python/benchwire.py 1:1 — any change here
// must land there too, or the cross-language checksum gate stops proving
// identical work and starts hiding a divergence.
//
// Every rung of the ladder carries the same two application messages:
//
//	request:  8 bytes big-endian id, then payloadBytes of payload
//	reply:    8 bytes big-endian id, then 4 bytes big-endian CRC-32 of the payload
//
// A transport is free to frame those bytes however it likes, because that
// framing is part of what the transport costs. What may not differ is the
// payload, so every row generates it from the same splitmix64 stream, and the
// timed loop, so every row runs it from Drive below.
package benchwire

import (
	"encoding/binary"
	"fmt"
	"hash/crc32"
	"math"
	"os"
	"slices"
	"strconv"
	"strings"
	"time"
)

// ReplyLen is the fixed application reply size: id and CRC, nothing else.
const ReplyLen = 12

// PoolSize is how many distinct payloads a client cycles through. Distinct
// payloads give distinct CRCs, so the fold proves the bytes as well as the
// count; a pool rather than per-request generation keeps payload generation
// out of the timed region on every row.
const PoolSize = 64

// Splitmix64 PRNG — identical constants in the Python twin so both sides
// generate byte-identical payloads from the same seed.
type Splitmix64 struct {
	State uint64
}

func (s *Splitmix64) Next() uint64 {
	s.State += 0x9E3779B97F4A7C15
	z := s.State
	z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9
	z = (z ^ (z >> 27)) * 0x94D049BB133111EB
	return z ^ (z >> 31)
}

// Pool builds the PoolSize payloads of payloadBytes each. Seeded from the slot
// and the size, so two rows at one size provably share a payload set and two
// sizes provably do not.
func Pool(payloadBytes int) [][]byte {
	if payloadBytes%8 != 0 {
		panic("payload_bytes must be a multiple of 8: " + strconv.Itoa(payloadBytes))
	}
	pool := make([][]byte, PoolSize)
	for slot := range pool {
		rng := Splitmix64{State: uint64(slot)*0x9E3779B97F4A7C15 ^ uint64(payloadBytes)}
		buf := make([]byte, payloadBytes)
		for off := 0; off < payloadBytes; off += 8 {
			binary.LittleEndian.PutUint64(buf[off:], rng.Next())
		}
		pool[slot] = buf
	}
	return pool
}

// CRC is the work the service does: IEEE CRC-32 over the payload. zlib.crc32
// in the Python twin computes the same polynomial over the same bytes, which
// is what lets one checksum gate span both languages.
func CRC(payload []byte) uint32 {
	return crc32.ChecksumIEEE(payload)
}

// Fold accumulates one reply into the running checksum. Order-dependent, so a
// dropped, duplicated or reordered reply changes it. The trailing xor-shift is
// what makes every output bit depend on the CRC as well as the id; without it
// the multiply only carries information leftwards and the low half of the
// checksum would not discriminate the payload at all.
func Fold(acc uint64, id uint64, crc uint32) uint64 {
	mixed := (acc ^ (uint64(crc)<<32 | id&0xFFFFFFFF)) * 0x100000001B3
	return mixed ^ (mixed >> 29)
}

// EncodeRequest writes id and payload into buf, which must hold 8+len(payload).
func EncodeRequest(buf []byte, id uint64, payload []byte) []byte {
	binary.BigEndian.PutUint64(buf, id)
	copy(buf[8:], payload)
	return buf[:8+len(payload)]
}

// ServeRequest is the service fragment, identical on every rung: read the id,
// CRC the payload, answer with both.
func ServeRequest(request []byte, reply []byte) []byte {
	id := binary.BigEndian.Uint64(request)
	binary.BigEndian.PutUint64(reply, id)
	binary.BigEndian.PutUint32(reply[8:], CRC(request[8:]))
	return reply[:ReplyLen]
}

// DecodeReply reads back the id and CRC the server computed.
func DecodeReply(reply []byte) (uint64, uint32) {
	return binary.BigEndian.Uint64(reply), binary.BigEndian.Uint32(reply[8:])
}

// Exchange is one crossing: hand the transport an id and a payload, get back
// the id and CRC the server answered with. Everything a row does differently
// lives in here and nowhere else.
type Exchange func(id uint64, payload []byte) (uint64, uint32, error)

// Drive is the timed loop. Every Go row calls it, so the sampling, the fold
// and the warmup cut are provably one implementation and a difference between
// two rows can only come from their Exchange.
func Drive(row string, cfg Config, exchange Exchange) {
	pool := Pool(cfg.PayloadBytes)
	samples := make([]uint32, 0, cfg.Ops-cfg.Warmup)
	checksum := uint64(0)
	wall := time.Now()
	for op := 0; op < cfg.Ops; op++ {
		id := uint64(op)
		start := time.Now()
		gotID, crc, err := exchange(id, pool[op%PoolSize])
		elapsed := time.Since(start).Nanoseconds()
		if err != nil {
			panic("exchange: " + err.Error())
		}
		if gotID != id {
			panic("reply id mismatch: want " + strconv.FormatUint(id, 10) +
				" got " + strconv.FormatUint(gotID, 10))
		}
		checksum = Fold(checksum, gotID, crc)
		if op >= cfg.Warmup {
			if elapsed > math.MaxUint32 {
				elapsed = math.MaxUint32
			}
			samples = append(samples, uint32(elapsed))
		}
	}
	PrintResult(row, cfg, time.Since(wall).Seconds(), samples, checksum)
}

// Config is what the runner passes down. Environment variables rather than a
// config file: the runner owns the TOML, the variant owns the measuring.
type Config struct {
	Addr         string
	PayloadBytes int
	Ops          int
	Warmup       int
	Tuned        bool
}

func Env() Config {
	return Config{
		Addr:         envStr("BENCH_ADDR", "127.0.0.1:0"),
		PayloadBytes: envInt("BENCH_PAYLOAD_BYTES", 128),
		Ops:          envInt("BENCH_OPS", 5000),
		Warmup:       envInt("BENCH_WARMUP", 500),
		Tuned:        envStr("BENCH_TUNED", "0") == "1",
	}
}

func envStr(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

func envInt(key string, fallback int) int {
	v := os.Getenv(key)
	if v == "" {
		return fallback
	}
	n, err := strconv.Atoi(strings.TrimSpace(v))
	if err != nil {
		panic("parse " + key + ": " + err.Error())
	}
	return n
}

// Ready tells the runner the listener is bound and on which address. The
// runner waits for this line rather than sleeping, so a slow start cannot be
// misread as a slow first crossing. os.Stdout is unbuffered in Go, so the line
// leaves the process on the Printf.
func Ready(addr string) {
	fmt.Printf("READY %s\n", addr)
}

// Percentile is the nearest-rank percentile over an ascending-sorted slice.
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

// ReadPeakRSSKB returns VmHWM in kB from /proc/self/status.
func ReadPeakRSSKB() uint64 {
	status, err := os.ReadFile("/proc/self/status")
	if err != nil {
		panic("read /proc/self/status: " + err.Error())
	}
	for _, line := range strings.Split(string(status), "\n") {
		if rest, ok := strings.CutPrefix(line, "VmHWM:"); ok {
			kb := strings.TrimSpace(strings.TrimSuffix(strings.TrimSpace(rest), " kB"))
			n, err := strconv.ParseUint(kb, 10, 64)
			if err != nil {
				panic("parse VmHWM: " + err.Error())
			}
			return n
		}
	}
	return 0
}

// PrintResult sorts the samples and prints the single RESULT line the runner
// parses. A row that cannot print this line cannot be reported.
func PrintResult(row string, cfg Config, wallS float64, samples []uint32, checksum uint64) {
	slices.Sort(samples)
	maxNs := uint32(0)
	if len(samples) > 0 {
		maxNs = samples[len(samples)-1]
	}
	fmt.Printf(
		"RESULT row=%s payload_bytes=%d ops=%d wall_s=%.6f thr_ops_s=%.0f "+
			"min_ns=%d p50_ns=%d p99_ns=%d p999_ns=%d max_ns=%d "+
			"rss_peak_mb=%.1f samples=%d checksum=%016x\n",
		row, cfg.PayloadBytes, cfg.Ops, wallS, float64(cfg.Ops)/wallS,
		Percentile(samples, 0), Percentile(samples, 0.50), Percentile(samples, 0.99),
		Percentile(samples, 0.999), maxNs,
		float64(ReadPeakRSSKB())/1024.0, len(samples), checksum)
}
