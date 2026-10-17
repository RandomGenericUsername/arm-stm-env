---
id: spike-006
title: "WL55JC CM0+ bring-up: C2BOOT doesn't persist and the CM0+ double-faults"
kind: spike
status: reported
lane: direct
timebox: 4h
questions:
  - "Why does PWR_CR4.C2BOOT read 0 after the M4's runtime write, when a direct debug write persists?"
  - "Why does the CM0+ double-fault on boot (its RAM/security allocation? GTZC?)"
  - "What does the WL55 security model require for the CM0+ to run from 0x08020000?"
links:
  openspec: none
  bmad: none
worktree: none
branch: none
---

# WL55JC CM0+ bring-up

## Findings (2026-10-15)

The M4 side works (`bug-021`). The CM0+ does not:

- `PWR_CR4.C2BOOT` (0x5800040C, bit 15): a **direct** debug write
  (`mww 0x5800040C 0x8000`) **persists**, and `stm32wlx.cpu1 arp_examine` then
  succeeds — `Cortex-M0+ r0p1 processor detected`.
- The M4's generated `main()` contains the same write (disassembly confirmed:
  `ldr/orr #0x8000/str [r3,#0x40c]`, r3 = 0x58000000), and the M4 runs (the LED
  blinks) — yet after boot `PWR_CR4` reads **0**.
- `FLASH_SRRVR` (0x58004084) reads `0xFEFF8000` → SBRV = 0x8000 → CPU2 reset
  vector 0x08020000, which matches the M0+ image region (flashed, Verified OK).
- Examining cpu1 after a debug-set C2BOOT logs
  `[stm32wlx.cpu1] clearing lockup after double fault` then succeeds → the CM0+
  starts but faults.

## Open / next

- Who clears `C2BOOT` (CPU2 entering CStop? the CM0+ itself?) and whether the
  M4 must set it *before* the sibling image is valid.
- The WL55 **security/RAM allocation** (GTZC / option bytes): the CM0+ may not
  own `0x2000C000` (its `ram_m0plus`) or may need `SRAM2` security configured —
  the community reports needing option bytes (`C2BOOT_LOCK`, `SRRVR`, `SFSA`)
  for dual-core boot.
- Whether the CM0+ needs `RCC`/`PWR` CPU2-side clocking (`HCLK2`).
- Debug flow: the CM0+ must be **attached** after the M4 boots it (cortex-debug
  `request: attach`); the launch configs still assume a launchable sibling.

Implementation output is a failure for a spike; file a `bug` once the cause is
known.

## Correction (2026-10-16) — this spike's premise was wrong

Two of this spike's conclusions are **disproved by measurement**:

1. **"C2BOOT doesn't persist"** — it does persist, and the CM0+ does not double-fault.
   The CM0+ boots and runs from `0x08020000` as soon as the M4's release constructor
   writes C2BOOT (`PWR_CR4 = 0x00008000`, counter at **`0x2000C01C`** advancing).
   *This spike also sampled `0x2000C000`, which is GCC's `completed.1` (always 0) —
   the real `counter` is at `0x2000C01C`; that false signal is what made the sibling
   look dead.*
2. **"The release write is missing"** — it was missing, but for a different reason than
   suspected: the generated **linker script had no `.init_array`**, so *every*
   constructor in *every* generated C/C++ project was dropped by `--gc-sections`.
   Fixed in `bug-026` (verified end-to-end).
3. **C2BOOT is a boot-request bit, not a live gate** — clearing it does not stop a
   running CM0+.

Still open: `bug-027` (the M4 boots from system memory ~47% of the time — real,
device-level) and `bug-030`/`bug-031`. The CM0+ bring-up requirement itself
(`req-026`) is satisfied.
