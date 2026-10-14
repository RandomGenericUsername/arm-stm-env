---
id: req-015
title: "H755 blink example (LD2/PE1, family-correct registers, primary core)"
kind: requirement
status: done
size: M
lane: openspec-single
links:
  openspec:
    - openspec/changes/req-015-h755-example
  bmad: []
worktree: .worktrees/req-015/
branch: ticket/req-015-h755-example
parent: epic-001
children: []
---

# H755 blink example (LD2/PE1, family-correct registers, primary core)

## User value

The dual-core NUCLEO-H755ZI-Q ships a working blink too. The example now carries
the family register/clock facts (F4 AHB1ENR/16 MHz vs H7 AHB4ENR/64 MHz) and
renders on the boot core only, so it's correct across families.

## Acceptance

- [x] `example.led` carries gpio_base/rcc_en_addr/rcc_en_bit/clock_hz; validated. `Verify: pytest -k registry`
- [x] `stm32h755` renders `main-M7.c` blink (H7 regs) + `main-M4.c` stub; `stm32f411re` unchanged. `Verify: pytest -k cells`
- [x] Live: `mu create … stm32h755` → build → flash (probe 0483:3754) → `** Verified OK **`.
- [x] `make test` + `openspec validate req-015-h755-example` green (250 passed).

## Evidence

Board/probe 2026-10-14: H755 STLINK-V3 `0483:3754` (distinct from F411RE
`0483:3752`). LED facts from UM2408 (LD2 = PE1) + vendored cmsis-device-stm32h755
header (GPIOE 0x58021000, RCC_AHB4ENR 0x580244E0 bit 4) + SystemCoreClock 64 MHz.
