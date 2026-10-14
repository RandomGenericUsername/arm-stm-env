# Proposal

## Why

Generated C/C++ projects ship a do-nothing `wfi` `main`. A freshly flashed board
shows no sign of life, so the first thing every user does is hand-write a blink
— exactly what happened on 2026-10-14 (NUCLEO-F411RE, PA5, 10 Hz). Ship a
working on-board-LED example **per MCU** so `create → build → flash` visibly
does something, implemented for the packs that declare it and a stub elsewhere.

## What Changes

- New optional pack block **`example`** carrying the board's on-board LED:
  `example: {led: {port: A, pin: 5, active: high}}` (board fact, so it lives in
  the pack — the core stays device-agnostic).
- Registry validator for `example` (pack-schema), loader → `DeviceFacets`,
  reader view → `DeviceView`.
- Template generation: `src/main-<core>.c` renders a **blink example** when the
  pack declares `example.led` (raw registers, NOP delay, ~10 Hz); otherwise the
  existing `wfi` stub.
- **`stm32f411re`** declares `led: {port: A, pin: 5, active: high}` →
  implemented. `stm32h755`, `stm32wl55jc` declare no `example` → stub.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `pack-schema`: optional `example` block (on-board LED fact).
- `template-generation`: generated `main` renders the example or the stub.

## Impact

- Code: `engine/core/registry.py`, `engine/core/model.py`,
  `engine/core/loader.py`, `engine/templates/renderer.py`,
  `packs/stm32f411re.yaml` + tests.
- Out of scope: examples for H755/WL55 (stubs for now), Rust examples, and any
  peripheral beyond a single GPIO LED.
