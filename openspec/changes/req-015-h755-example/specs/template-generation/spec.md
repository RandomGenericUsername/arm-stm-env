# Spec Delta

## Purpose

The example renders on the primary core with family-correct registers and a
clock-appropriate delay.

## ADDED Requirements

### Requirement: Example renders on the primary core only

When a pack declares `example.led`, `src/main-<core>.c` SHALL render the blink
for the **first** core only; every other core SHALL render the `wfi` stub. The
blink SHALL use the pack's `gpio_base`/`rcc_en_addr`/`rcc_en_bit` and a
`clock_hz`-scaled delay (~10 Hz).

Evidence: dual-core share the LED pin; M7 boots first (design D3/D4). Verify:
`render()` for `stm32h755` → `main-M7.c` blink (H7 regs), `main-M4.c` `wfi`;
`stm32f411re` → `main-M4.c` blink (F4 regs).

#### Scenario: H755 dual core

- **WHEN** `stm32h755` renders
- **THEN** `main-M7.c` drives PE1 via `RCC_EN`/`GPIOE` and `main-M4.c` is the stub

#### Scenario: F411RE single core

- **WHEN** `stm32f411re` renders
- **THEN** `main-M4.c` drives PA5 with the F4 registers
