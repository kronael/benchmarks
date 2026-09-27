MEASUREMENT := 01-microservice-cost/02-scheduling-under-load
include ../../../../mk/measurement.mk

prepare:
	cd variants/go && go mod download
	cd variants/rust && cargo fetch

# One command that calls Python. run.py owns the build because the case C rows
# need a second Go build at GOAMD64=v3, and because a measured run started
# under sudo must be able to skip compiling entirely (--no-build).
build:
	./run.py --cases A,B,C --build-only

lint:
	$(LINT) variants/go variants/rust

test:
	./run.py --quick --cases C

# Cases A and B need the Rust binaries restored first: variants/rust holds only
# src/lib.rs, so `--cases A,B` cannot run here yet.
bench: build
	./run.py --cases C

clean:
	cd variants/rust && cargo clean
