# The standard measurement Makefile. Every measurement includes this and sets
# MEASUREMENT plus the variant recipes it needs. One file, so a target means
# the same thing everywhere and a new measurement inherits the rules.
#
#   MEASUREMENT := 01-microservice-cost/01-in-process-coordination
#   include ../../../../mk/measurement.mk

ifndef MEASUREMENT
$(error set MEASUREMENT before including measurement.mk)
endif

# Pinned so every measurement builds with one toolchain. simd is still an
# experiment in go1.27, so a variant that imports it needs GOEXPERIMENT set at
# build time, not at run time.
export GOTOOLCHAIN := go1.27.1
export GOEXPERIMENT := simd

ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)
LINT := $(ROOT)/lint.py
RESULTS := results

.PHONY: all prepare build lint test bench clean help

all: build lint test

help:
	@echo "$(MEASUREMENT)"
	@echo "  make prepare   fetch or build whatever the variants need"
	@echo "  make build     build every variant"
	@echo "  make lint      format check and static analysis"
	@echo "  make test      fast correctness check, under five seconds"
	@echo "  make bench     build, take the pinned cores, measure, record"
	@echo "  make clean     remove build output, keep results"

# Variants that need no preparation override nothing.
prepare:
	@:

build:
	@echo "no build step defined for $(MEASUREMENT)" >&2; exit 2

lint:
	@:

test:
	@echo "no test defined for $(MEASUREMENT)" >&2; exit 2

# bench does NOT depend on build, and that is deliberate. run.py builds first
# and then re-executes itself under `sudo chrt -f 80 taskset`, so `make bench`
# on its own is the whole measured run. Everything compiles before that
# escalation, because under root's HOME GOTOOLCHAIN cannot resolve the pinned
# toolchain and `go` silently becomes the system one. A make recipe that built
# here would compile as root whenever the old `sudo ... make bench` form is
# used, which is why the dependency stays out.
#
# The record is written by bench.record inside the measurement's run.py, which is
# the only place a result file comes from: it writes the machine fingerprint and
# the starting load into the same file as the numbers.
bench:
	@echo "no bench step defined for $(MEASUREMENT)" >&2; exit 2

clean:
	@:
