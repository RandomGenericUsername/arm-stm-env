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