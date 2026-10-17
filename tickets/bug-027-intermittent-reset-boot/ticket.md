---
id: bug-027
title: "M4 app starts only ~2/6 times after an OpenOCD reset (sits in ROM at 0x1fff2cc0)"
kind: bug
status: triage
lane: direct
severity: S2
links:
  openspec: none
  bmad: []
worktree: none
branch: none
repro: "flash a generated WL55JC project, then run openocd 'reset run' six times in a row, reading RCC_AHB2ENR (0x5800004c) and PWR_CR4 each time"
observed: "iterations 0 and 3 run main (AHB2ENR=0x00000002, PWR_CR4=0x00008000); iterations 1,2,4,5 do not (AHB2ENR=0x00000003, PWR_CR4=0x00000000). In the failed state DHCSR=0x01010001 (core running) but PC=0x1fff2cc0 (system ROM) — it never jumps to flash. Same ratio with and without the bug-026 fix."
expected: "after a reset the generated app always starts from its vector table (AHB2ENR shows the GPIO enable, PWR_CR4 gets written by the ctor)"
---

# M4 app starts only ~2/6 times after an OpenOCD reset

## Repro

```sh
# with the generated project flashed, in the container:
openocd -f interface/stlink-dap.cfg -f probe/probe-serial.cfg -f target/stm32wlx.cfg \
  -c 'init' -c 'targets stm32wlx.cpu0' \
  -c 'reset run' -c 'mdw 0x5800004c 1' -c 'mdw 0x5800040c 1' -c 'exit'   # repeat ~6x
```

## Observed

```
iter 0: PWR_CR4=0x00008000  AHB2ENR=0x00000002   # booted (main ran)
iter 1: PWR_CR4=0x00000000  AHB2ENR=0x00000003   # NOT booted
iter 2: PWR_CR4=0x00000000  AHB2ENR=0x00000003   # NOT booted
iter 3: PWR_CR4=0x00008000  AHB2ENR=0x00000002   # booted
iter 4: PWR_CR4=0x00000000  …                    # NOT booted
iter 5: PWR_CR4=0x00000000  …                    # NOT booted
```

In the failed state `DHCSR=0x01010001` (core is running) yet the PC sits at
`0x1fff2cc0` (system/ROM memory) — the core never jumps to the flash reset vector.
Forcing the PC (`reg pc 0x0800019c` + `resume`) always starts the app. Tried:
`reset run`, `reset halt`+`resume`, `reset halt`+gdb `continue`. **Independent of
bug-026** — the same ratio occurs with the unfixed image.

## Expected

After a reset the app always starts from its vector table.

## Fix notes

Needs a physical NRST / power-on reset (not reachable from this bench) to decide
whether this is an STLINK-V3/dapdirect reset artefact or a genuine boot-mode /
reset-vector problem. Note `bug-026` makes the M4's release ctor fire only when the
app runs, so this is the likely reason the earlier WL55 observations (bug-021/023/024,
spike-006) were non-reproducible. Also test whether halting inside the ROM window
(e.g. landing at the flash vector) is what makes the one working case work.
## Investigation update (2026-10-16)

Characterised: **pooled boot rate ≈ 53% (18/34)** — not the 2/6 first estimated.
It is a **real device-level boot-selection problem**, not an OpenOCD/STLINK artefact:

- Measured **at the reset vector, before anything runs**: `pc = 0x1fff2cc0` (system
  memory) vs `pc = 0x0800025c` (= `Reset_Handler`) — the boot-mode decision itself is
  non-deterministic. Flash contents are intact at that moment.
- **Not the reset method / driver**: forcing an nSRST pulse
  (`reset_config srst_only srst_open_drain`) gives the same rate (4/6 vs 4/6), and
  **probe-rs 0.32.0 reproduces it** (a completely different stack): pc flips between
  `0x080001e8` (booted, `PWR_CR4=0x8000`) and `0x1fff2ba2` (ROM).
- Failure forensics: `RCC_CSR = 0` (no reset-cause flags); `OPTR (0x58004020) = 0x3ffff0aa`
  (`nBOOT0=1`, `BOOT_LOCK=0`, `C2BOOT_LOCK=0`) — so `nBOOT0=1` yet it boots from
  system memory, which is inconsistent and needs RM0453's boot-mode chapter.
- Failure state persists until the next reset; the core spins forever at `0x1fff2b9e`
  (semihosting trap + RCC-touching ROM helper in the region).
- **`probe/cpu2-boot.cfg` masks this bug** (it sets C2BOOT on every attach, so a stuck
  board looks healthy) — see `bug-031`.

**Blocked on:** identifying which ROM subsystem this is requires a reset the debugger
cannot synthesise. A ≈2-minute physical-reset procedure (NRST button ×10, power-cycle
×10, option-byte read, with a BOOTED/STUCK decision rule) is recorded in the
investigation report; run it at the bench to discriminate.
