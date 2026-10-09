---
id: req-003
title: "Engine core + model validation"
kind: requirement
status: done
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

`core/` model, validation, family-block registry, endpoint/proof structs — the certified-facts foundation every adapter builds on.

## Acceptance

- [x] Canonical model validates the 3 STM32 packs with zero drift. `Verify: <defined at build>`
- [x] No adapter parses device semantics (adversary re-run clean). `Verify: <defined at build>`

## Evidence

Work-split view story 1 (architecture run); governed by AD-1, AD-2.
