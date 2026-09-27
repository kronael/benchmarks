MEASUREMENT := 01-microservice-cost/01-in-process-coordination
include ../../../../mk/measurement.mk

build:
	./run.py --build

lint:
	$(LINT) variants/go

test:
	cd variants/go && go test ./...

bench: build
	./run.py

clean:
	./run.py --clean
