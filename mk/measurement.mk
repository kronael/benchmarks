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

# prepare, lint and clean are optional, so a measurement that needs none of
# them gets a silent no-op here.
.PHONY: all prepare lint clean

all: build lint test

# build, test and bench are not optional. Without this rule a measurement that
# forgets one gets "Nothing to be done" and exit 0, which is the quiet failure
# this repository is built to avoid. Defining the three as recipes here instead
# would make every measurement's own copy print an overriding-recipe warning.
.DEFAULT:
	$(error $(MEASUREMENT) defines no '$@' target)

# bench does NOT depend on build. run.py builds before it re-executes itself
# under `sudo chrt -f 80 taskset`, so a make-side dependency would build twice.
