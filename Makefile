GO ?= go

.PHONY: all build lint test fingerprint clean

all: build lint test

build:
	$(GO) build -o dist/fingerprint ./fingerprint

lint:
	$(GO) vet ./...

test:
	$(GO) test ./...

fingerprint: build
	./dist/fingerprint

# A measurement is run from its own directory, so its sweep.toml, variants and
# results stay together:
#
#   make -C projects/<project>/measurements/<measurement> bench

clean:
	rm -f dist/fingerprint
