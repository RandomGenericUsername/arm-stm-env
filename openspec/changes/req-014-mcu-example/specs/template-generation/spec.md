# Spec Delta

## Purpose

The generated `main` shows the board doing something when the pack declares an
example, and stays a stub otherwise.

## ADDED Requirements

### Requirement: Generated main renders the example or the stub

When a pack declares `example.led`, `src/main-<core>.c` SHALL render a
self-contained blink of that LED (raw registers + NOP delay, no HAL); otherwise
it SHALL render the `wfi` stub.

Evidence: 2026-10-14 F411RE blink flashed live (`Verified OK`). Verify:
`render()` for `stm32f411re` → `GPIO_BSRR`/`delay_half_period` in `main-M4.c`;
`stm32h755`/`stm32wl55jc` → `wfi`.

#### Scenario: F411RE ships the blink

- **WHEN** `stm32f411re` (declares `led: {port: A, pin: 5, active: high}`) is rendered
- **THEN** `src/main-M4.c` drives PA5 via `GPIOA` BSRR with a NOP half-period delay

#### Scenario: Others stay a stub

- **WHEN** `stm32h755` / `stm32wl55jc` (no `example` block) are rendered
- **THEN** `src/main-<core>.c` is the `wfi` stub
