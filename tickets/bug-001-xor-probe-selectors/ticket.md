---
id: bug-001
title: "XOR rejects probe selectors combined with --mcu-config"
kind: bug
status: done
severity: S1
parent: epic-001
lane: openspec-single
links:
  openspec: []
  bmad: []
worktree: .worktrees/bug-001/
branch: ticket/bug-001-xor-probe-selectors
---

## Repro (REQUIRED)

- command: `stm flash --mcu-config stm32f411re --project-dir <proj> --device /dev/ttyUSB0 --files a.elf --dry-run`
- observed: `exit 2` + `stm: error: --mcu-config cannot be mixed with individual flag(s): --device (one source per invocation)`
- expected: `exit 0` + docker argv carrying both `--mcu-config` and `--device` (probe selectors are run config, must compose with pack ref)

## Regression check

- check: `pytest engine/cli/tests/ -k "xor or flash or probe"` green + live dry-run above exits 0
