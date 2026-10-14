---
id: ops-018
title: "Sibling-core example: debuggable counter loop instead of a wfi stub"
kind: ops-task
status: done
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/ops-018/
branch: ticket/ops-018-sibling-core-example
---

# Sibling-core example: debuggable counter loop instead of a wfi stub

> `ops-task`; no `parent:`.

## Work

Non-primary cores rendered a bare `wfi` stub, so a sibling debug session had
nothing to step or watch (it made the bug-013 sibling-debug path unverifiable).
`_main_sections` now falls back to `_sibling_sections`: a
`volatile uint32_t counter` incremented in a NOP-delay loop. No pin is touched,
so a sibling core can't fight the primary core's LED example.

## Done-when

`mu create --mcu-config stm32h755` → `src/main-M4.c` runs the counter loop while
`src/main-M7.c` still blinks PE1; the project builds; `make test` green.

## Evidence

- Generated `src/main-M4.c` (H755) contains `counter++` / `delay_loop`; the
  blink markers (`GPIO_BSRR`, `LED_PIN`) stay on `main-M7.c`.
- WL55: `src/main-M0+.c` likewise; `src/main-M4.c` still blinks PB15.
- Live (hand-applied first, then shipped here): flashed M4 image runs it —
  `counter` @`0x10000000`: `0x14 → 0x24` over 1 s; halted PC `0x81002b6`
  (inside the M4 loop).
- `engine/templates/tests/test_cells.py` asserts the sibling markers.

## Open

Rust: `_MAIN_RS` is a `wfi` stub for **every** core (Rust doesn't consume
`example.led` at all) — a separate Rust-example ticket, out of scope here.
