---
id: task-006
title: "Per-backend pack settings (probe chip strings etc.)"
kind: task
status: done
parent: epic-001
lane: direct
links:
  openspec: []
  bmad: []
worktree: .worktrees/task-006/
branch: ticket/task-006-backend-settings
---

## What

Packs gain an optional per-backend settings section (e.g. `probe_rs: {chip: STM32F411RETx}`); the selected adapter reads its settings from the certified model instead of deriving names. `--probe` + pack default + settings compose; unknown backend still exits 2.

## Done-check

- [ ] Pack section validated by family validators; model carries it; no CLI literals. `Verify: pytest + gate`
- [ ] probe-rs renders exact registry chip from pack (not device id). `Verify: unit test`
- [ ] Full suite green. `Verify: pytest engine/`
