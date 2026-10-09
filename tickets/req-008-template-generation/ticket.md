---
id: req-008
title: "Project template generation from packs"
kind: requirement
status: done
size: M
lane: openspec-single
links:
  openspec:
    - req-008-template-generation
  bmad:
    - _bmad-output/initiative-universal-mcu-env/architecture-universal-mcu-env/architecture-universal-mcu-env.md
worktree: .worktrees/req-008/
branch: ticket/req-008-template-generation
parent: epic-001
children: []
---

## User value

`create` renders a complete buildable project from any pack: C/C++ (Makefile/CMake? + linker + CMSIS refs) and Rust (Cargo + memory.x + build.rs), plus per-project `config/` dir for library config headers.

## Acceptance

- [ ] All 3 packs × C/C++/Rust render projects that pass a structural check (expected files present, no empty placeholders). `Verify: <defined at build>`
- [ ] `config/` dir wiring per spike-004 (pack defaults + project overrides). `Verify: <defined at build>`
- [ ] No sibling code copied (shapes evidenced, content authored). `Verify: <defined at build>`

## Evidence

Triage lane 2 (single bounded feature, spine-covered); gap found post-req-007 (generation unowned).
