---
id: bug-012
title: "Generated launch.json emits cortex_m maskisr for non-Cortex-M packs"
kind: bug
status: done
lane: direct
severity: S3
links:
  openspec: []
  bmad: []
worktree: .worktrees/bug-012/
branch: ticket/bug-012-vscode-maskisr-gate
repro: "mu create --vscode for a (hypothetical) non-Cortex-M pack, e.g. RISC-V"
observed: "postLaunchCommands runs `monitor cortex_m maskisr steponly`; OpenOCD has no cortex_m group -> command errors, launch aborts"
expected: "the Cortex-M single-step workaround is only emitted for Cortex-M cores"
---

# Generated launch.json emits cortex_m maskisr for non-Cortex-M packs

## Context

`bug-011` added `postLaunchCommands: ["monitor cortex_m maskisr steponly"]` to
every generated launch config to fix Cortex-M single-step. The `cortex_m`
command group only exists for Cortex-M targets; on any other architecture the
command errors and aborts the launch. Preventive hardening — no non-Cortex-M
pack exists yet, so this is latent, not observed in the field.

## Fix

`_vscode_files` now gates the workaround on the core arch via `_is_cortex_m`
(`thumbv6m` / `thumbv7m` / `thumbv7em` / `thumbv8m` Rust target triples).

## Evidence

- `test_vscode_maskisr_gated_to_cortex_m`: `thumbv7em-none-eabihf` -> command
  present; `riscv32imac-unknown-none-elf` -> absent.
- Cortex-M packs unaffected: `test_render_vscode_generates_valid_configs` and
  `test_render_vscode_per_core_dual` still assert the command is present.

## Verify

```sh
make test
```
