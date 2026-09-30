MEASUREMENT := 01-microservice-cost/02-scheduling-under-load
include ../../../../mk/measurement.mk

prepare:
	cd variants/go && go mod download
	cd variants/rust && cargo fetch

# One command that calls Python. run.py owns the build because the case C rows
# need a second Go build at GOAMD64=v3.
build:
	./run.py --cases A,B,C --build-only

lint:
	$(LINT) variants/go variants/rust

test:
	./run.py --quick --cases C

# Case C only. The Rust twins for A and B exist, but BUGS.md records that case
# A's operating points exceed this box, so `--cases A,B` is not a measurement
# here yet. --no-build is gone on purpose: run.py builds before it takes the
# cores, so editing a variant and running this no longer measures the old
# binary in silence.
bench:
	./run.py --cases C

clean:
	cd variants/rust && cargo clean
