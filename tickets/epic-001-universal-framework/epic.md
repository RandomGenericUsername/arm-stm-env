---
id: epic-001
title: "Universal MCU dev framework"
kind: epic
status: decomposed
children:
  - req-001
  - req-002
  - req-003
  - req-004
  - req-005
  - req-006
  - req-007
  - spike-001
  - spike-002
  - spike-003
  - task-001
done-when: "V1 matrix (3 packs x 3 langs, OpenOCD) completes create-build-flash-run from clean machines per pack proof rituals"
links:
  openspec: []
  bmad:
    - _bmad-output/initiative-universal-mcu-env/brief-universal-mcu-env/brief-universal-mcu-env.md
    - _bmad-output/initiative-universal-mcu-env/spec-universal-mcu-env/spec-universal-mcu-env.md
worktree: ""
branch: ""
---

## Goal

One CLI from zero to running program on any supported MCU: config-driven scaffolding plus zero-host-deps dual-mode execution, vendor-neutral by design, STM32 reference packs day one.

## Non-goals

Non-STM32 vendors, Windows native, pack validator, cloud/team features, IDE plugins (per brief).

## Decomposition notes

Triage lane 4 (bmad-advisory); user selected BMAD architecture over plain split. Children grow here as architecture lands (engine, packs, CLI/shim, containers, probe adapters, spikes).

## Rollup

Done iff every child is done AND done-when holds.
