# Ticket index

> Counting rule: completeness checks cover item files (`tickets/<id>-<slug>/ticket.md`) only.
> `tickets/_template/` (and any `tickets/_fixtures/`) are excluded from INDEX completeness counting.
> Entry format: link — title | `status` | execution links. Epics add `done/total children done`, done-when, and one nested line per child. Bugs add severity. Spikes add timebox state.

## Active epics

- [epic-001-universal-framework](./epic-001-universal-framework/epic.md) — Universal MCU dev framework | `decomposed` | 8/12 children done | done-when: V1 matrix completes create-build-flash-run from clean machines | exec: bmad brief+spec+spine
  - [req-001-product-brief](./req-001-product-brief/ticket.md) — Product brief for universal MCU dev framework | `done`
  - [req-002-distill-spec](./req-002-distill-spec/ticket.md) — Distill spec from finalized brief | `done`
  - [task-001-adopt-split-decompose](./task-001-adopt-split-decompose/ticket.md) — Adopt spine, validate, decompose epic | `done`
  - [req-003-engine-core](./req-003-engine-core/ticket.md) — Engine core + model validation | `done` | 26/26 tests, fixtures spike-001-corrected
  - [req-004-pack-schema](./req-004-pack-schema/ticket.md) — Pack frame schema + 3 STM32 packs | `triaged`
  - [req-005-cli-verbs](./req-005-cli-verbs/ticket.md) — Thin CLI verbs + shim | `done` | 91/91 tests, gate clean |
  - [req-006-probe-adapters](./req-006-probe-adapters/ticket.md) — Probe adapters OpenOCD (+ probe-rs second) | `done` | 134/134 tests, no live claims |
  - [req-007-container-images](./req-007-container-images/ticket.md) — Container images per toolchain + caches | `done` | both images built+smoked, pins audited |
  - [spike-001-openocd-targets](./spike-001-openocd-targets/ticket.md) — Per-pack OpenOCD target verification | `reporting` | boxed 3h — findings filed, 2 verdicts corrected by orchestrator; consumes into req-004
  - [spike-002-cpp-deps](./spike-002-cpp-deps/ticket.md) — C/C++ dependency mechanism | `reporting` | boxed 4h — findings filed, pick vendoring; consumes into req-007/post-V1
  - [spike-003-toolchain-recon](./spike-003-toolchain-recon/ticket.md) — 2026 toolchain recon | `reporting` | boxed 3h — findings filed, vanilla-GCC verdict; CubeCLT gated on license proof
  - [spike-004-config-headers](./spike-004-config-headers/ticket.md) — Per-project config-header flow | `reporting` | boxed 2h — findings filed, pack-defaults + project-config-dir; consumes into req-004

## Requirements

(covered under epic-001 above; standalone entries appear here only for items without a parent epic)

## Bugs

(none)

## Ops tasks

(none)

## Spikes

(none)

## Tasks

(none)

## Done (links only, newest last)

(none)
