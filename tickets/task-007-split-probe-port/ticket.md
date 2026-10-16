---
id: task-007
title: "R1 — split the probe port into FlashPort and DebugPort"
kind: task
status: proposed
lane: inherits
parent: req-021
links:
  openspec: none
  bmad: none
worktree: none
branch: none
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
