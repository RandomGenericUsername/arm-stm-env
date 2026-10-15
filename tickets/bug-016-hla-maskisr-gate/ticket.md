---
id: bug-016
title: "HLA targets (stlink.cfg) reject `cortex_m maskisr` -> F411 debug launch fails"
kind: bug
status: done
lane: direct
severity: S1
links:
  openspec: []
  bmad: []
worktree: .worktrees/bug-016/
branch: ticket/bug-016-hla-maskisr-gate
repro: "F5 -> Debug M4 on the F411 (or any HLA pack)"
observed: "Failed to launch GDB: Protocol error with Rcmd: 01 (from interpreter-exec console \"monitor cortex_m maskisr steponly\")"
expected: "the debug session starts"
---

# HLA targets reject `cortex_m maskisr`

## Root cause

bug-011 emits `monitor cortex_m maskisr steponly` as a `postLaunchCommands`
entry for every Cortex-M core (bug-012 gated it by arch). But that workaround
only exists on **DAP-based** targets. An HLA interface (`stlink.cfg`) creates an
`hla_target`, not a `cortex_m` target:

```
> targets
 0* stm32f4x.cpu   hla_target   ...
> cortex_m maskisr steponly
invalid command name "cortex_m"
```

OpenOCD errors the `monitor`, gdb reports `Protocol error with Rcmd: 01`, and
the launch aborts. HLA targets don't need the workaround anyway — F411
single-step already works without it.

## Fix

Emit the workaround only when the pack's OpenOCD interface is a DAP interface
(`_cortex_m_maskisr_available`: `"dap" in interface`). H755 (`stlink-dap.cfg`)
keeps it; F411/WL55 (`stlink.cfg`, HLA) don't.

## Evidence

- `mu-f411`: `targets` → `hla_target`; `cortex_m maskisr steponly` →
  `invalid command name "cortex_m"`.
- Generated configs: H755 → present (3×); F411 → absent; WL55 → absent.
- Tests: `test_vscode_maskisr_gated_to_cortex_m_and_dap`,
  `test_render_vscode_generates_valid_configs` (F411 absent),
  `test_render_vscode_per_core_dual` (H755 present).

## Verify

```sh
make test
```
