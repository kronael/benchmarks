GO ?= go
EXP ?=

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
	@test -n "$(EXP)" || { echo "usage: make bench EXP=01-channel-vs-serial"; exit 2; }
	@test -d experiments/$(EXP) || { echo "no such experiment: $(EXP)"; exit 2; }
	./dist/fingerprint > experiments/$(EXP)/results/fingerprint.json
	@echo "fingerprint written; run the variant under experiments/$(EXP)"

clean:
	rm -f dist/fingerprint
