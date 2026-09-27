MEASUREMENT := 01-microservice-cost/04-channel-composition
include ../../../../mk/measurement.mk

build:
	cd variants/go && go build -o ../../bin/ ./...

lint:
	$(LINT) variants/go

test:
	cd variants/go && go test ./...
	./run.py sweep.toml --quick

bench:
	./run.py sweep.toml

clean:
	rm -f bin/direct bin/direct-parallel bin/channel bin/channel-batched
