# mk

`measurement.mk` is the standard Makefile every measurement includes. Targets
mean the same thing in every measurement, and a new one inherits the rules
rather than restating them.

A measurement's own `Makefile` sets `MEASUREMENT`, includes this, and defines
its own `build`, `test` and `bench`, plus `prepare`, `lint` and `clean` where it
has real work. Those last three are optional and do nothing when left out. The
first three are not: a measurement that omits one fails with `defines no
'<target>' target` rather than reporting nothing to be done.

Every target a measurement defines is defined only there, so including this file
prints no overriding-recipe warnings.

The fingerprint comes from `bench.record`, which the measurement's `run.py`
calls. It is not a make-level guarantee, and `bench` is an ordinary target.
