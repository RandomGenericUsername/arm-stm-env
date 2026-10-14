---
id: ops-017
title: "WL55JC blink example (LD1/PB15)"
kind: ops-task
status: done
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/ops-017/
branch: ticket/ops-017-wl55-example
---

# WL55JC blink example (LD1/PB15)

> `ops-task`; no `parent:`.

## Work

Add the WL55JC on-board LED fact so `mu create --mcu-config stm32wl55jc`
generates a blink (mechanism from req-014/req-015; this is data only).

- `packs/stm32wl55jc.yaml`: `example.led = {port: B, pin: 15, active: high,
  gpio_base: 0x48000400, rcc_en_addr: 0x5800004C, rcc_en_bit: 1,
  clock_hz: 4000000}`.

Facts (vendored `cmsis-device-stm32wl55jc`): `GPIOB_BASE` = IOPORT_BASE+0x400
= **0x48000400**; `RCC_BASE` = 0x58000000; `RCC_AHB2ENR` offset 0x4C →
**0x5800004C**; `RCC_AHB2ENR_GPIOBEN` bit **1**; default `SystemCoreClock` =
**4000000** (MSI). LED from UM2592 (MB1389): "LED1 blue LED (USER) ... connected
to STM32WL I/O PB15 ... HIGH logic state". Blink runs on the primary core (M4).

## Done-when

`mu create --mcu-config stm32wl55jc` → `main-M4.c` blinks PB15 (WL regs),
`main-M0+.c` is a stub; project builds; `make test` green (252 passed).
