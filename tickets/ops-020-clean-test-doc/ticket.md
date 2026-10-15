---
id: ops-020
title: "Document the clean from-zero test (docs/vscode-debug.md §9)"
kind: ops-task
status: done
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/ops-020/
branch: ticket/ops-020-clean-test-doc
---

# Document the clean from-zero test

> `ops-task`; no `parent:`.

## Work

Added §9 to `docs/vscode-debug.md`: the repeatable clean test — fresh project →
fresh container (whole USB bus + resolved serial) → build/flash in a **login**
shell (what the VS Code tasks use) → verify the firmware *runs*, with the
expected result per board.

## Done-when

The section runs as written against a fresh project and container, and the
expected table matches reality.

## Evidence

Ran it for both boards (2026-10-14, both probes attached so each container sees
two):

- F411RE → openocd picks `0483:3752`, `Verified OK`, LD2 toggles, PC in
  `delay_half_period`.
- H755ZI-Q → openocd picks `0483:3754`, `Verified OK` ×2 (both banks), M7 LD2
  toggles, M4 `counter` increments.
