---
id: req-017
title: "Per-core SVD fetch -> Cortex-Debug peripheral register view"
kind: requirement
status: done
size: M
lane: openspec-single
links:
  openspec:
    - openspec/changes/req-017-svd-registers
  bmad: []
worktree: .worktrees/req-017/
branch: ticket/req-017-svd-registers
parent: epic-001
children: []
---

# Per-core SVD fetch -> Cortex-Debug peripheral register view

## User value

With `.vscode/` generated, F5 now also shows the **Peripheral Registers** view
(peripherals/registers/bitfields, live values, editable) — the SVD-driven panel
from the sibling repos.

## Acceptance

- [x] `svd` pack block validates; packs declare per-core SVD paths. `Verify: pytest -k registry`
- [x] `create --vscode` fetches pinned SVDs into `probe/` and sets `svdFile` per core. `Verify: grep svdFile .vscode/launch.json`
- [x] `make test` + `openspec validate req-017-svd-registers` green (257 passed).

## Evidence

Sibling prior art `ArmDevelopmentEnvironment@main:setup/create_project/download_svd_files.sh`;
ST svd zips unreachable (HTTP 000); source `modm-io/cmsis-svd-stm32` pinned
`e79021accd49bf19bd0b16065f5471fb073ff3ac` (Apache-2.0). Live 2026-10-14:
`probe/STM32F411.svd` (856480 bytes) + `svdFile` in launch.
