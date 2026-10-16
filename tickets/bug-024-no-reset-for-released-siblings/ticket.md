---
id: bug-024
title: "cortex-debug launch fails on a released-sibling pack: 'monitor reset halt' errors (Protocol error with Rcmd)"
kind: bug
status: done
lane: direct
severity: S1
links:
  openspec: []
  bmad: []
worktree: .worktrees/bug-024/
branch: ticket/bug-024-no-reset-for-released-siblings
repro: "WL55JC: F5 -> Debug M4 (any config)"
observed: "Failed to launch GDB: Protocol error with Rcmd: FC. (from interpreter-exec console \"monitor reset halt\")"
expected: "the debug session starts"
---

# cortex-debug launch fails on a released-sibling pack

## Root cause

cortex-debug's **launch** runs `monitor reset halt`. On a pack whose sibling is
released by the primary (`cpu2_boot`), the system reset cannot halt the asleep
sibling:

```
[stm32wlx.cpu1] AP write error, reset will not halt
[stm32wlx.cpu1] Examination failed
```

OpenOCD errors the whole `reset halt`, and cortex-debug aborts the launch with
`Protocol error with Rcmd`. (Batch gdb tests hid this — gdb continues after an
`-ex` error; cortex-debug does not.)

## Fix

For `cpu2_boot` packs, emit **`request: attach`** for **every** config — no
reset at all. `monitor halt` touches neither core's reset state, so the released
sibling stays accessible and the chained compound works.

## Evidence

- Live (NUCLEO-WL55JC): `cpu1` → `Cortex-M0+ r0p1 processor detected`,
  `Examination succeed` (no warnings).
- M4 attach flow: `halted 0x8000142 → stepi 0x8000144 → next 0x800014a` ✓
- M0+ attach flow: `halted 0x80200d0 → stepi 0x80200d2` ✓
- `make flash` → `Verified OK` ×2.
- H755/F411 configs unchanged (`launch`); `uv run pytest engine -q` → 276 passed.
