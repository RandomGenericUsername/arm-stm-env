---
id: req-014
title: "Per-MCU example: generated blink (F411RE implemented, others stub)"
kind: requirement
status: done
size: M
lane: openspec-single
links:
  openspec:
    - openspec/changes/req-014-mcu-example
  bmad: []
worktree: .worktrees/req-014/
branch: ticket/req-014-mcu-example
parent: epic-001
children: []
---

# Per-MCU example: generated blink (F411RE implemented, others stub)

## User value

A freshly flashed board visibly does something: the generated `main` blinks the
on-board LED instead of idling in `wfi`. Implemented for the packs that declare
an LED; the rest keep the stub.

## Acceptance

- [x] Pack `example` block validates; `stm32f411re` declares `led: {port: A, pin: 5, active: high}`. `Verify: pytest -k registry`
- [x] `stm32f411re` renders a blink `main-M4.c`; `stm32h755`/`stm32wl55jc` stay `wfi`. `Verify: pytest -k cells`
- [x] Live: `mu create … stm32f411re` → build → flash blinks. `Verify: ** Verified OK **`
- [x] `make test` + `openspec validate req-014-mcu-example` green (245 passed).

## Evidence

Live 2026-10-14 (NUCLEO-F411RE, PA5, 10 Hz) — the blink was flashed and verified;
this change makes it the generated example. Design in
`openspec/changes/req-014-mcu-example/`.
