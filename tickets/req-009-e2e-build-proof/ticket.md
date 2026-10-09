---
id: req-009
title: "End-to-end build proof in images"
kind: requirement
status: done
size: M
lane: openspec-single
links:
  openspec:
    - req-009-e2e-build-proof
  bmad:
    - _bmad-output/initiative-universal-mcu-env/architecture-universal-mcu-env/architecture-universal-mcu-env.md
worktree: .worktrees/req-009/
branch: ticket/req-009-e2e-build-proof
parent: epic-001
children: []
---

## User value

Proof that rendered projects actually compile under pinned toolchains: all 9 cells rendered + built/checked in images, sizes fit pack maps. Biggest V1 risk reduction short of hardware.

## Acceptance

- [ ] 9/9 cells: render + image build/check green with evidence log. `Verify: <defined at build>`
- [ ] C sizes fit pack flash/RAM; Rust memory.x consistent. `Verify: <defined at build>`
- [ ] Warnings recorded, not failed on (initial policy). `Verify: <defined at build>`

## Evidence

User "go" on e2e proposal (2026-10-09 session); V1 success criteria minus flash-run.
