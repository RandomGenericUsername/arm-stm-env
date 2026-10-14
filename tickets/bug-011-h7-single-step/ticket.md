---
id: bug-011
title: "OpenOCD never single-steps the H755 (PC frozen) — mask interrupts during step"
kind: bug
status: done
lane: direct
severity: S1
links:
  openspec: []
  bmad: []
worktree: .worktrees/bug-011/
branch: ticket/bug-011-h7-single-step
repro: "F5 -> Debug M7 on the H755; press Step Over (F10) / Step Into (F11)"
observed: "the highlighted line never advances (PC frozen at the same address)"
expected: "each step advances one line/instruction"
---

# OpenOCD never single-steps the H755 (PC frozen)

## Repro

VS Code F5 -> *Debug M7* on the NUCLEO-H755ZI-Q, then F10/F11. Reproduced
without VS Code (container gdb), so it is not a cortex-debug/UI issue:

```sh
openocd -f interface/stlink-dap.cfg -f board/st_nucleo_h745zi.cfg -c init &
arm-none-eabi-gdb build/M7/stm32h755-M7.elf \
  -ex "target extended-remote :3333" -ex "monitor reset halt" \
  -ex "info registers pc" -ex stepi -ex "info registers pc"
```

## Observed

`monitor reset halt` -> `pc 0x80002f8` (`Reset_Handler`); every `stepi`/`next`
returns the **same** PC. gdb sends a proper hardware step (`vCont;s:0;c`);
OpenOCD replies but the core does not advance. `run`/`halt`/flash/verify and
the LED (GPIOE ODR bit 1 toggles) all work — only single-step is dead.

## Root cause

OpenOCD single-steps Cortex-M by setting `C_STEP` in DHCSR. If an interrupt
lands during the step, the step is lost and the core re-halts at the same PC.
J-Link and ST-Link GDB servers **mask interrupts during a step by default**;
OpenOCD does not. `cortex_m maskisr` is OpenOCD's knob for this.

## Fix

Generated `.vscode/launch.json` now sets, on every per-core config:

```json
"postLaunchCommands": ["monitor cortex_m maskisr steponly"]
```

`postLaunchCommands` run after OpenOCD's `reset halt` (target halted) and
before `runToEntryPoint`, so the setting is applied before the user steps.
`steponly` masks interrupts only for the duration of a step — normal run stays
interrupt-enabled.

## Evidence

- H755 M7 (stlink-dap), `reset halt; maskisr steponly; stepi`:
  `pc 0x80002fc -> 0x800034c -> 0x800034e` (advances).
- H755 M7 exact cortex-debug flow (`reset halt; maskisr steponly; break main;
  continue; next x3`): `0x80002b8 -> 0x80002d0 -> 0x80002d8 -> 0x80002e0`.
- H755 M4 (cpu1) also fixed (`0x810029c -> 0x81002a0 -> 0x81002f0`).
- F411RE (HLA `stlink`) unaffected: `break main; continue; next` ->
  `0x80001b8 -> 0x80001ca -> 0x80001d2`.
- Both cores and both OpenOCD builds (ST fork `0.12.0+dev-00664-gc8d973bda`,
  upstream Debian `0.12.0`) fail without the fix; both work with it.
- Regression tests: `test_render_vscode_generates_valid_configs`,
  `test_render_vscode_per_core_dual`.

## Verify

```sh
make test            # includes the two launch.json assertions
# live (probe attached):
openocd -f interface/stlink-dap.cfg -f board/st_nucleo_h745zi.cfg -c init &
arm-none-eabi-gdb build/M7/stm32h755-M7.elf \
  -ex "target extended-remote :3333" -ex "monitor reset halt" \
  -ex "monitor cortex_m maskisr steponly" -ex stepi -ex stepi \
  -ex "info registers pc"
```

Consumes `spike-005` (same symptom; cause now known).
