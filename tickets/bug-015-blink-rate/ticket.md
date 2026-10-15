---
id: bug-015
title: "Generated blink runs ~29 Hz (delay formula 3x off) — the LED looks steady, not blinking"
kind: bug
status: done
lane: direct
severity: S2
links:
  openspec: []
  bmad: []
worktree: .worktrees/bug-015/
branch: ticket/bug-015-blink-rate
repro: "make flash on the H755, then look at LD2 (PE1) — it does not appear to blink"
observed: "the M7 runs and drives PE1, but the toggle rate is ~29 Hz, which reads as steady/dim rather than a blink"
expected: "a clearly visible blink"
---

# Generated blink runs ~29 Hz

## Root cause

The example delay was sized as `iters = round(0.05 * clock_hz / 16)` — i.e. it
assumed **16 cycles/iteration** for the NOP loop. Measured on the H755 M7 at
`-Os` it is ~5.3, so the intended "~10 Hz" blink actually ran ~3x faster:

```
3000 OpenOCD GPIOE-ODR reads in 1380 ms (460 us/read)
runs of ~37 identical samples  ->  17 ms half-period  ->  ~29 Hz
```

29 Hz is below the flicker-fusion rate, so the LED reads as steady (and dim) —
indistinguishable from "not blinking" even though the pin toggles correctly.
(It also explains why a debug session looked different: intermittent halts slow
the apparent rate.)

## Fix

Calibrate the loop and target a visibly slow blink: `_DELAY_CYCLES_PER_ITER = 5`,
`_DELAY_HALF_PERIOD_S = 0.25` (~2 Hz). H755 → `DELAY_ITERS = 3200000`; F411 →
`800000`. Applies to the blink and the sibling counter delay.

## Evidence

- before: 400 reads / 186 ms, run ~37 → **17 ms** half-period (~29 Hz)
- after:  3000 reads / 1380 ms, run ~600 → **~276 ms** half-period (~1.8 Hz)
- live: M7 pc in `delay_half_period`, GPIOE ODR toggling `0/2`.

## Verify

```sh
make test
```
