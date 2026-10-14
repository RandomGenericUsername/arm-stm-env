---
id: bug-014
title: "Dual-core packs link both cores into one RAM region (same _estack) -> M7 hard-faults"
kind: bug
status: done
lane: direct
severity: S1
links:
  openspec: []
  bmad: []
worktree: .worktrees/bug-014/
branch: ticket/bug-014-dual-core-ram
repro: "make flash on the H755 (dual core), then look at the LED"
observed: "the LED never starts blinking; M7 sits in the default handler (HardFault), GPIOE ODR stays 0xffffffff"
expected: "the M7 runs and blinks right after flashing"
---

# Dual-core packs link both cores into one RAM region

## Root cause

`memory:` was a single shared map, so both cores' linker scripts got the same
RAM region **and the same stack top**:

```
RAM (rwx) : ORIGIN = 0x10000000, LENGTH = 294912   _estack = 0x10048000   (both cores)
```

Two cores sharing one stack clobber each other's frames at boot: the M7's return
address got corrupted, it `blx`ed to a bad address, and the resulting UsageFault
escalated to HardFault:

```
current mode: Handler HardFault
CFSR = 0x00010000 (UFSR.UNDEFINSTR)   HFSR = 0x40000000 (FORCED)
GPIOE ODR = 0xffffffff  -> peripheral never clocked -> main() never ran
```

Debugging appeared to "fix" it because a debug session halts the M4 (the H755's
CTI couples the cores; cortex-debug resumes only its own target), leaving the M7
to run alone — no collision.

## Fix

`MemoryRegion` gains optional `cores:` tagging (+ `applies_to`); the renderer
emits only the regions a core can see, and `pick_region` (e2e) honours it. Packs:

- **H755**: `ram_m7` = AXI SRAM (D1) `0x24000000`/512K, `ram_m4` = D2 SRAM1+2+3
  `0x30000000`/288K; flash banks tagged M7/M4.
- **WL55**: the 64K split `ram_m4` `0x20000000`/48K, `ram_m0plus`
  `0x2000C000`/16K — **UNVERIFIED** (no WL55 attached).

## Evidence

- Aliasing probe: `0xdeadbeef` written at `0x10000000` reads back at `0x30000000`
  (alias of D2 SRAM); `0x24000000` and `0x38000000` are independent.
- Generated linkers: M7 -> `FLASH_M7`/`RAM_M7` (0x24000000); M4 ->
  `FLASH_M4`/`RAM_M4` (0x30000000); `_estack` differs.
- Live (NUCLEO-H755ZI-Q, 2026-10-14): `make flash` -> `Verified OK`; GPIOE ODR
  toggles `0/2`; M7 pc `0x80002aa` (delay_half_period), M4 pc `0x81002a8`.
- Tests: `test_renderer_dual_core_ram_does_not_overlap`,
  `test_renderer_dual_bank_cores_link_own_flash`, `test_pick_region_prefers_core_bank`,
  pack-schema + `memory.x` tests updated.

## Open

- WL55 dual-core flash placement: both cores link `.isr_vector` at `0x08000000`,
  so the two images overlap — separate bug, unverified (no board).
- The WL55 per-core RAM split is unverified on hardware.

## Verify

```sh
make test
```
