---
id: req-005
title: "Thin CLI verbs + shim"
kind: requirement
status: triaged
size: M
lane: bmad-advisory
links:
  openspec: none
  bmad:
    - _bmad-output/initiative-universal-mcu-env/architecture-universal-mcu-env/architecture-universal-mcu-env.md
worktree: ""
branch: ""
parent: epic-001
children: []
---

## User value

create/dev/build/flash/debug orchestration with zero hardware knowledge in commands; per-OS probe mapping in the shim; Python+uv packaging.

## Acceptance

- [ ] All verbs run orchestration-only (no device conditionals in `cli/`). `Verify: <defined at build>`
- [ ] Shim maps probe endpoints on Linux and macOS. `Verify: <defined at build>`

## Evidence

Work-split view story 3; governed by AD-5, AD-6, AD-9.
