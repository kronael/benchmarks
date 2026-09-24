# mk

`measurement.mk` is the standard Makefile every measurement includes. Targets
mean the same thing in every measurement, and a new one inherits the rules
rather than restating them.

A measurement's own `Makefile` sets `MEASUREMENT`, includes this, and overrides
only `prepare`, `build`, `lint`, `test` and `clean` where it has real work.
`bench` always records the fingerprint; that part is not overridable by design.
