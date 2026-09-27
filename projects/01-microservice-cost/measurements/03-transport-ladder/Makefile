MEASUREMENT := 01-microservice-cost/03-transport-ladder
include ../../../../mk/measurement.mk

prepare:
	cd variants/go && go mod download
	uv venv --python 3.11 variants/python/.venv
	uv pip install --python variants/python/.venv/bin/python websockets==17.1

build:
	cd variants/go && go build -o ../../dist/ ./...

# gofmt, go vet and ruff, matching measurement 02's formatter-plus-analyser pair
# per language. staticcheck is left out on purpose: the copy on this host cannot
# read go1.27 export data ("export data version 4 is greater than maximum
# supported version 2"), so adding it would make lint fail on every run.
lint:
	cd variants/go && gofmt -l .
	cd variants/go && go vet ./...
	uvx ruff@0.14.3 check run.py variants/python

test:
	./run.py sweep.toml --quick

bench: build record
	./run.py sweep.toml

clean:
	rm -f dist/grpccli dist/grpcsrv dist/httpcli dist/httpsrv dist/udpcli dist/udpsrv
