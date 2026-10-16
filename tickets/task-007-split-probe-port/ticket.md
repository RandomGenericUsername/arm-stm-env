---
id: task-007
title: "R1 — split the probe port into FlashPort and DebugPort"
kind: task
status: done
lane: inherits
parent: req-021
links:
  openspec: none
  bmad: none
worktree: .worktrees/task-007/
branch: ticket/task-007-split-probe-port
---

# R1 — split the probe port into FlashPort and DebugPort

## Parent

`req-021` — lane inherited from parent; a task is never routed to `bmad-advisory` on its own.

## Work

Split `ProbeAdapter` (currently ABC declares only `flash`/`debug`, `engine/adapters/__init__.py:56-70`,
while callers use `render_argv`/`proof_for`/`last_transcript`, `engine/cli/main.py:315,323`) into
**FlashPort** (programming) and **DebugPort** (sessions). Both backends implement both; declare
per-port proof-rung ownership (AD-12). Re-pin the conformance test
(`engine/adapters/tests/test_conformance.py`). CLI fails a verb whose port is unimplemented rather
than fabricating a handle.

## Done-when

`make test` green; both backends re-conform; rendered trees and tool argv unchanged for every
supported path; the conformance pin reflects the split ports. Governed by AD-12, AD-16.

## Evidence

2026-10-16 — branch `ticket/task-007-split-probe-port`:

- `engine/adapters/__init__.py`: `FlashPort` (`render_argv`/`flash`/`proof_for`),
  `DebugPort` (`debug`), and `ProbeAdapter(FlashPort, DebugPort)` composite; the registry
  now types and returns `FlashPort`.
- `engine/cli/main.py`: `_prepare_flash` returns `FlashPort`; `_run_debug_local` fails with
  exit 2 when the backend is not a `DebugPort` — no fabricated handle (AD-12).
- `make test` → **278 passed** (276 → 277: split-port conformance test; 278: the CLI AD-12 test).
- Blast radius `git diff --stat main`: 6 engine/test files; **`renderer`/`templates` untouched**.
- Tool argv unchanged:
  `mu flash --mcu-config stm32f411re --device /dev/x --files a.elf --mode local --dry-run`
  → `openocd -f interface/stlink.cfg -f board/st_nucleo_f4.cfg -c 'program a.elf verify reset exit'`
- The repo gate `test_cli_carries_no_hardware_knowledge` caught an ESP32 mention in a
  `engine/cli/` comment; removed (gate works).
