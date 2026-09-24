MEASUREMENT := 01-microservice-cost/02-scheduling-under-load
include ../../../../mk/measurement.mk

prepare:
	cd variants/go && go mod download
	cd variants/rust && cargo fetch

build:
	cd variants/go && go build ./...
	cd variants/rust && cargo build --release

lint:
	cd variants/go && gofmt -l . && go vet ./...
	cd variants/rust && cargo fmt --check && cargo clippy -- -D warnings

test:
	./run.py --quick

bench: build record
	./run.py

clean:
	cd variants/rust && cargo clean
