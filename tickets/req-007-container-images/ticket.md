---
id: req-007
title: "Container images per toolchain + caches"
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

cpp/rust images with pinned toolchains, core-owned cache keys, language→image registry lookup.

## Acceptance

- [ ] cpp and rust images build pinned; cache invalidates on image bump. `Verify: <defined at build>`
- [ ] CubeCLT-vs-GCC decision recorded; ST OpenOCD fork pinned. `Verify: <defined at build>`

## Evidence

Work-split view story 5; governed by AD-7, AD-8. Needs spike-003 output.
