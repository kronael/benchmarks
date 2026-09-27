MEASUREMENT := 01-microservice-cost/01-in-process-coordination
include ../../../../mk/measurement.mk

build:
	./run.py --build

lint:
	cd variants/go && gofmt -l . && go vet ./...

test:
	cd variants/go && go test ./...

bench: build record
	./run.py

clean:
	./run.py --clean
