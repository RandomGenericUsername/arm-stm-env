---
id: ops-008
title: "Spike close-outs, linker fallback removal, user README"
kind: ops-task
status: done
trivial: false
blast-radius: "README rewrite (docs only); linker_for fail-loud (covered by suite); status flips."
links:
  openspec: []
  bmad: []
worktree: .worktrees/ops-008/
branch: ticket/ops-008-closeouts-fallback-docs
---

## What

Close 4 reporting spikes (findings consumed), remove linker_for invented-name fallback, replace scaffold README with verified user docs.

## Done-check

- [x] Spikes 001-004 `done`; rollup recounted from files. `Verify: counter script`
- [x] Undeclared linker core raises naming it. `Verify: pytest`
- [x] README commands all previously executed live. `Verify: history in session`
- [x] Suite green. `Verify: pytest engine/`
