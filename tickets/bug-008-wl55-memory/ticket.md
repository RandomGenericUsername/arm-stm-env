---
id: bug-008
title: "WL55JC pack memory map wrong (RAM 128K vs real 64K) -> HardFault"
kind: bug
status: done
lane: direct
severity: S1
links:
  openspec: []
  bmad: []
worktree: .worktrees/bug-008/
branch: ticket/bug-008-wl55-memory
repro: "mu create --mcu-config stm32wl55jc … && mu build && mu flash … --files build/M4/stm32wl55jc-M4.elf"
observed: "M4 hardfaults immediately: PC stuck in the default handler; stack at 0x20020000 is past the real 64K SRAM (top 0x20010000) so the first push/bl faults"
expected: "blink runs (GPIOB ODR bit 15 toggles)"
---

# WL55JC pack memory map wrong (RAM 128K vs real 64K) -> HardFault

## Repro

```sh
mu create --mcu-config stm32wl55jc --lang c --name wl55-blink --path ~/Desktop
mu build  --project-dir ~/Desktop/wl55-blink
mu flash  --mcu-config stm32wl55jc --project-dir ~/Desktop/wl55-blink \
  --vid 0483 --pid 374e --files build/M4/stm32wl55jc-M4.elf
```

## Observed

Flash verifies OK, but the M4 immediately HardFaults (PC stuck at the default
handler `0x080001ec`; `xPSR` IPSR = HardFault). The generated linker set
`_estack = ORIGIN(RAM)+LENGTH(RAM) = 0x20020000`, but the STM32WL55JC SRAM ends
at `0x20010000` — the first `push`/`bl` writes past RAM.

## Expected

The generated blink runs; `GPIOB_ODR` bit 15 toggles.

## Fix notes

`packs/stm32wl55jc.yaml` declared **flash 1024K / RAM 128K**; the real part is
**256K flash / 64K SRAM**. Corrected to `flash 262144`, `ram 65536`.

Evidence: vendored `cmsis-device-stm32wl55jc` header — `FLASH_BASE 0x08000000`
"FLASH(up to 256 KB)"; `SRAM1_SIZE`/`SRAM2_SIZE` = 0x8000 each (32K+32K=64K);
OpenOCD flash probe "flash size = 256 KiB". Tests updated
(`test_packs.py`, `test_pack_schema_packs.py`, fixture). Live 2026-10-14:
rebuilt + reflashed → `GPIOB_ODR` toggles `0x00008000`↔`0x00000000`.

Note: the WL55 also required the **JP3 (BOOT0) pull-down** to be connected
(JP3 OFF) so `nSWBOOT0=1` pin-boot selects flash, not the ROM bootloader.
