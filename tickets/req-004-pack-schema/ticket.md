---
id: req-004
title: "Pack frame schema + 3 STM32 packs"
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

Frame validator, STM32 family blocks, F411RE/H755/WL55JC packs with re-verified OpenOCD targets and proof rungs.

## Acceptance

- [ ] All 3 packs validate against the frame + family schema. `Verify: <defined at build>`
- [ ] OpenOCD targets re-verified (depends on spike-001). `Verify: <defined at build>`

## Evidence

Work-split view story 2; governed by AD-4, AD-5, AD-10. Blocked on spike-001 output.
