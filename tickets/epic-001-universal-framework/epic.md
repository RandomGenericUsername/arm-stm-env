---
id: epic-001
title: "Universal MCU dev framework"
kind: epic
status: done
children:
  - bug-001
  - bug-002
  - req-001
  - req-002
  - req-003
  - req-004
  - req-005
  - req-006
  - req-007
  - req-008
  - req-009
  - req-010
  - req-011
  - req-012
  - req-014
  - req-015
  - req-016
  - req-017
  - req-018
  - req-019
  - req-020
  - spike-001
  - spike-002
  - spike-003
  - spike-004
  - task-001
  - task-002
  - task-003
  - task-004
  - task-005
  - task-006
done-when: "V1 matrix (3 packs x 3 langs, OpenOCD) completes create-build-flash-run from clean machines per pack proof rituals"
links:
  openspec: []
  bmad:
    - _bmad-output/initiative-universal-mcu-env/brief-universal-mcu-env/brief-universal-mcu-env.md
    - _bmad-output/initiative-universal-mcu-env/spec-universal-mcu-env/spec-universal-mcu-env.md
worktree: ""
branch: ""
---

# Universal MCU dev framework

## Goal

One CLI from zero to running program on any supported MCU: config-driven scaffolding plus zero-host-deps dual-mode execution, vendor-neutral by design, STM32 reference packs day one.

## Non-goals

Non-STM32 vendors, Windows native, pack validator, cloud/team features, IDE plugins (per brief).

## Decomposition notes

Triage lane 4 (bmad-advisory); user selected BMAD architecture over plain split. Children grow here as architecture lands (engine, packs, CLI/shim, containers, probe adapters, spikes).

## Children

- [x] `bug-001` — XOR rejects probe selectors combined with --mcu-config (done)
- [x] `bug-002` — Rendered Rust projects fail to compile (unwinding panics) (done)
- [x] `req-001` — Product brief for universal MCU dev framework (done)
- [x] `req-002` — Distill spec from finalized brief (done)
- [x] `req-003` — Engine core + model validation (done)
- [x] `req-004` — Pack frame schema + 3 STM32 packs (done)
- [x] `req-005` — Thin CLI verbs + shim (done)
- [x] `req-006` — Probe adapters OpenOCD (+ probe-rs second) (done)
- [x] `req-007` — Container images per toolchain + caches (done)
- [x] `req-008` — Project template generation from packs (done)
- [x] `req-009` — End-to-end build proof in images (done)
- [x] `req-010` — Streamed flash/debug tool output (+ --verbose) (done)
- [x] `req-011` — Vendor CMSIS submodules into created projects (done)
- [x] `req-012` — OpenOCD config paths + USB probe binding so stm flash programs (done)
- [x] `req-014` — Per-MCU example: generated blink (F411RE implemented, others stub) (done)
- [x] `req-015` — H755 blink example (LD2/PE1, family-correct registers, primary core) (done)
- [x] `req-016` — Generated .vscode/ for the container-attached debug flow (C/C++ first) (done)
- [x] `req-017` — Per-core SVD fetch -> Cortex-Debug peripheral register view (done)
- [x] `req-018` — Keep firmware running after debug: resume-on-detach config (done)
- [x] `req-019` — mu dev accepts probe selectors (dev container gets the probe) (done)
- [x] `req-020` — Auto-detect a single attached probe (no --vid/--pid needed) (done)
- [x] `spike-001` — Per-pack OpenOCD target verification (done)
- [x] `spike-002` — C/C++ dependency mechanism (done)
- [x] `spike-003` — 2026 toolchain recon (done)
- [x] `spike-004` — Per-project config-header flow (lwipopts.h-style) (done)
- [x] `task-001` — Adopt spine, validate, decompose epic (done)
- [x] `task-002` — Wire create renderer (done)
- [x] `task-003` — Container argv invokes build tool, not stm (done)
- [x] `task-004` — Narrow container mounts to engine + packs (done)
- [x] `task-005` — Pack-default probe, proof wiring, image pre-check (done)
- [x] `task-006` — Per-backend pack settings (probe chip strings etc.) (done)

## Rollup — done (2026-10-16)

Every child is done AND the done-when holds:

- **create → build:** 10/10 cells green in the pinned images (`ops-023`, `docs/e2e-evidence.md`).
- **flash → run from a clean machine, per pack proof ritual:** all three V1 packs
  proven live — F411RE + H755ZI-Q (`ops-020`, `docs/vscode-debug.md` §9), WL55JC
  (`ops-027`); recorded in `docs/flash-run-evidence.md` (`ops-028`).
- **3 langs:** C/C++ run proof per pack; Rust is build-parity for V1 (the `spike-008`
  decision — see that ticket for the rationale), so its proof rests on the build half.
- Rust `mu build` fixed (`bug-025`); generated projects carry `.cargo/config.toml`.

Reconciled children (this closeout): the list now matches the tickets that declare
`parent: epic-001` (`req-012`, `req-014`–`req-020` added) plus the two epic-level
requirements (`req-001`, `req-002`); the stale `decomposed` status is normalised to
the lifecycle `done`.
