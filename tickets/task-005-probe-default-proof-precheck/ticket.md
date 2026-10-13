---
id: task-005
title: "Pack-default probe, proof wiring, image pre-check"
kind: task
status: done
parent: epic-001
lane: direct
links:
  openspec: []
  bmad: []
worktree: .worktrees/task-005/
branch: ticket/task-005-probe-default-proof-precheck
---

## What

Pack-declared probe default with `--probe` override (config primary, flag override); flash verdicts carry proof via retained transcripts (no ABC change); friendly missing-image error naming `make images`.

## Done-check

- [x] `--probe nope` → exit 2 with registry message. `Verify: live run`
- [x] Pack default used with no flag; proof rung in verdict. `Verify: unit + live dry-run`
- [x] Missing image → exit 1 naming `make images`. `Verify: unit test`
- [x] Full suite green. `Verify: pytest engine/ (191)`
