# The standard measurement Makefile. Every measurement includes this and sets
# MEASUREMENT plus the variant recipes it needs. One file, so a target means
# the same thing everywhere and a new measurement inherits the rules.
#
#   MEASUREMENT := 01-microservice-cost/01-in-process-coordination
#   include ../../../../mk/measurement.mk

ifndef MEASUREMENT
$(error set MEASUREMENT before including measurement.mk)
endif

ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)
RESULTS := results
STAMP := $(shell date -u +%Y%m%d)

.PHONY: all prepare build lint test bench record clean help

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

# bench always records the machine beside the numbers. A result without its
# fingerprint cannot be compared to anything later, so this is not optional.
bench: build record

# One command, no shell logic. Everything real lives in bench.py.
record:
	uv run --project $(ROOT) $(ROOT)/bench.py fingerprint

clean:
	@:
