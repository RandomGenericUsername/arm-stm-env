---
id: bug-013
title: "Generated M4 launch config attaches to the M7 core (no per-core targeting, no dual-core session)"
kind: bug
status: done
lane: direct
severity: S2
links:
  openspec: []
  bmad: []
worktree: .worktrees/bug-013/
branch: ticket/bug-013-dual-core-debug
repro: "F5 -> Debug M4 on a dual-core device (H755)"
observed: "the session attaches to cpu0 (M7): M4 ELF against M7 code"
expected: "Debug M4 attaches to cpu1/M4; a compound config can debug both cores at once"
---

# Generated M4 launch config attaches to the M7 core

## Root cause

Both generated configs were identical apart from the ELF/SVD — neither set
`targetProcessor`. cortex-debug chooses the gdb port from `targetProcessor`
(default 0) and OpenOCD assigns `gdb_port` + N per core, so **every** session
landed on cpu0 (M7). "Debug M4" was therefore M7 code with M4 symbols.

Doc evidence: cortex-debug `src/gdb.ts:1147` (`calculatePortsNeeded`),
`src/gdb.ts:697` (port pick), `src/openocd.ts:79` (`target-select
extended-remote localhost:${gdbport}`); wiki *Multi core debugging*.

## Fix

- Per-core `"numberOfProcessors"` + `"targetProcessor"`, taken from the pack's
  `openocd.targets` name (`…cpuN`) when declared, else the core's index.
- A compound config `Debug <primary>+<other>` using `chainedConfigurations`
  (`detached: false`, `waitOnEvent: "postInit"`) so one session starts OpenOCD
  and the other cores share it.

## Evidence

Generated configs (worktree engine):

```
stm32h755   Debug M7 (OpenOCD) proc 0/2 | Debug M4 (OpenOCD) proc 1/2 | Debug M7+M4 chained[Debug M4]
stm32wl55jc Debug M4 (OpenOCD) proc 0/2 | Debug M0+ (OpenOCD) proc 1/2 | Debug M4+M0+ chained[Debug M0+]
```

Port↔core mapping on the board (`openocd -c "gdb_port 50000"`):

```
cpu0 -> :50000 ; gdb :50000 pc=0x80002fc  (M7 flash)
cpu1 -> :50001 ; gdb :50001 pc=0x81002a0  (M4 flash)
```

Tests: `test_render_vscode_per_core_dual` (proc indices + compound),
`test_render_vscode_generates_valid_configs` (single-core: no proc fields).

## Open

- WL55: the M0+ is woken by the M4 and, per the cortex-debug wiki, must be
  debugged in **attach** mode — the compound child may need `request: attach`
  for that pack. Needs a live WL55 test.
- The chained/compound behaviour was not exercised in the VS Code UI here (no
  UI in this environment). The per-core targeting and port mapping are
  verified above; the compound is the documented mechanism.

## Verify

```sh
make test
```
