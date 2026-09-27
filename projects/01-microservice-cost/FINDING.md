# Finding

Open. No measurement has produced a recorded result yet.

This file answers the main question once the series does. Until then it names
what is still missing, so the gap is visible rather than implied.

## What the four measurements owe the theme

| # | measurement | state |
|---|---|---|
| 01 | in-process coordination | builds, gates, never run |
| 02 | scheduling under load | case C builds and gates; cases A, B, P1, P2 have no Rust twin |
| 03 | transport ladder | ten rows build and agree on one checksum, never run |
| 04 | channel composition | builds, gates, never run |

Measurement 01 is the zero of both groups, so no crossing above it can be
reported as a difference until 01 has a number.

## What is missing before the main question can be answered

- Group A needs rungs 1a, 1b, 2 and 3 plus the same-language control, which is
  measurement 03 in full.
- Group B is measurement 04 in Go only. Python and Rust are unwritten, so the
  question of whether the sign holds across three languages cannot be answered.
- Measurement 02's cross-language rows need the Rust binaries that the rsx lift
  dropped (`BUGS.md`).
