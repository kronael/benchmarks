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
	@echo "  make bench     run the measurement and record it"
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

# The record is written by bench.record inside the measurement's run.py, which
# is the only place a result file is allowed to come from: it writes the machine
# fingerprint and the starting load into the same file as the numbers. There is
# deliberately no separate record target, because one that printed a fingerprint
# to stdout would look like the guarantee without being it.
bench: build

clean:
	@:
