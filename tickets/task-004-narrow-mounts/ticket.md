---
id: task-004
title: "Narrow container mounts to engine + packs"
kind: task
status: done
parent: epic-001
lane: direct
links:
  openspec: []
  bmad: []
worktree: .worktrees/task-004/
branch: ticket/task-004-narrow-mounts
---

## What

Replace the whole-repo read-only mount with exactly two mounts (`engine/`, `packs/`); container paths unchanged so `__file__`-derived resolution keeps working.

## Done-check

- [x] Docker argv mounts only engine + packs (+ project rw); no repo-root mount. `Verify: stm build --dry-run`
- [x] PACKS_DIR single-sourced (shim owns it, main imports). `Verify: rg PACKS_DIR`
- [x] Full suite green + live build re-proof. `Verify: pytest + container build`
