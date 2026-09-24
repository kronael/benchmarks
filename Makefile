GO ?= go
M ?=

.PHONY: all build lint test fingerprint bench clean

all: build lint test

build:
	$(GO) build -o dist/fingerprint ./fingerprint

lint:
	$(GO) vet ./...

test:
	$(GO) test ./...

fingerprint: build
	./dist/fingerprint

bench: build
	@test -n "$(M)" || { echo "usage: make bench M=<project>/<measurement>"; exit 2; }
	@test -d projects/$(firstword $(subst /, ,$(M)))/measurements/$(lastword $(subst /, ,$(M))) \
		|| { echo "no such measurement: $(M)"; exit 2; }
	./dist/fingerprint > projects/$(firstword $(subst /, ,$(M)))/measurements/$(lastword $(subst /, ,$(M)))/results/fingerprint.json
	@echo "fingerprint written for $(M)"

clean:
	rm -f dist/fingerprint
