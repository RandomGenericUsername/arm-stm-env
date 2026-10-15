---
id: bug-021
title: "WL55JC dual-core: HLA hides the CM0+, both cores share flash, M0+ arch wrong, CPU2 never released"
kind: bug
status: done
lane: direct
severity: S2
links:
  openspec: []
  bmad: []
worktree: .worktrees/bug-021/
branch: ticket/bug-021-wl55-dual-core
repro: "mu create --mcu-config stm32wl55jc --vscode, then make flash"
observed: "flash-M4 fails (Error 1); both images link at 0x08000000; no cpu1 in OpenOCD; the CM0+ never runs"
expected: "both images flash to their own regions, the M4 runs, the CM0+ is exposed and released"
---

# WL55JC dual-core

## Root causes (all reproduced)

1. **HLA hides the CM0+**: the pack used `interface/stlink.cfg`; the stm32wlx
   script warns *"hla does not support multicore debugging"* and forces
   `DUAL_CORE 0` → no `cpu1`. The probe is an STLINK-V3 (dapdirect) → use
   `stlink-dap.cfg`.
2. **`set DUAL_CORE 1` was emitted *after* the target cfg** (and the target cfg
   reads `DUAL_CORE` while creating the second core) → `cpu1` never existed.
3. **Both cores linked flash at `0x08000000`** → the images overwrite each other.
   CPU2 boots from its reset vector (`FLASH_SRRVR.SBRV`), normally `0x08020000`.
4. **M0+ arch was `thumbv7em`** (it is ARMv6-M).
5. **CPU2 stays in reset until CPU1 releases it** (RM0453 §2.3) → the pack must
   declare the release sequence.

## Fix

- Pack: `stlink-dap.cfg`; `flash_m4` 0x08000000/128K + `flash_m0plus`
  0x08020000/128K (per-core tags); M0+ arch `thumbv6m-none-eabi`; a
  `example.cpu2_boot` fact (masked register writes).
- Renderer: a generated `probe/dual-core.cfg` (`set DUAL_CORE 1`) sourced
  **before** the target; `_cpu2_boot_sections` emits the release writes into the
  primary core's `main()`; **flash** omits the dual-core cfg when the pack must
  release its sibling (the asleep core fails the final reset — *"AP write error,
  reset will not halt"*), while the debug helper keeps it.

## Evidence

- `openocd -f interface/stlink-dap.cfg -c 'set DUAL_CORE 1' -f target/stm32wlx.cfg`
  → `cpu0` **and** `cpu1` created.
- Direct `mww 0x5800040C 0x8000` (PWR_CR4.C2BOOT) → `stm32wlx.cpu1 arp_examine`
  → **Cortex-M0+ r0p1 detected, Examination succeed**.
- Live (NUCLEO-WL55JC, 2026-10-15): `make flash` → `Verified OK` ×2 (both
  regions); GPIOB ODR toggles `0/0x8000` → **M4 LED (PB15) blinks**.
- `uv run pytest engine -q` → 266 passed.

## Open

**The CM0+ still does not run.** The M4's `main` contains the release writes
(confirmed in the disassembly) but `PWR_CR4.C2BOOT` reads 0 afterwards and the
CM0+ double-faults when examined → the WL55 security/RAM-allocation model
(GTZC) — see `spike-006`.
