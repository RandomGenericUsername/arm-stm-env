# Ticket index

> Counting rule: completeness checks cover item files (`tickets/<id>-<slug>/ticket.md`) only.
> `tickets/_template/` (and any `tickets/_fixtures/`) are excluded from INDEX completeness counting.
> Entry format: link — title | `status` | execution links. Epics add `done/total children done`, done-when, and one nested line per child. Bugs add severity. Spikes add timebox state.

## Active epics

- [epic-001-universal-framework](./epic-001-universal-framework/epic.md) — Universal MCU dev framework | `decomposed` | 23/23 children done | done-when: V1 matrix completes create-build-flash-run from clean machines | exec: bmad brief+spec+spine
  - [req-001-product-brief](./req-001-product-brief/ticket.md) — Product brief for universal MCU dev framework | `done`
  - [req-002-distill-spec](./req-002-distill-spec/ticket.md) — Distill spec from finalized brief | `done`
  - [req-008-template-generation](./req-008-template-generation/ticket.md) — Project template generation from packs | `done` | 153/153 tests, 9 cells green
  - [req-009-e2e-build-proof](./req-009-e2e-build-proof/ticket.md) — End-to-end build proof in images | `done` | 9/9 cells, dual-bank fix re-proven
  - [task-001-adopt-split-decompose](./task-001-adopt-split-decompose/ticket.md) — Adopt spine, validate, decompose epic | `done`
  - [req-003-engine-core](./req-003-engine-core/ticket.md) — Engine core + model validation | `done` | 26/26 tests, fixtures spike-001-corrected
  - [req-004-pack-schema](./req-004-pack-schema/ticket.md) — Pack frame schema + 3 STM32 packs | `done` | 54/54 tests, drift-grep clean
  - [req-005-cli-verbs](./req-005-cli-verbs/ticket.md) — Thin CLI verbs + shim | `done` | 91/91 tests, gate clean |
  - [req-006-probe-adapters](./req-006-probe-adapters/ticket.md) — Probe adapters OpenOCD (+ probe-rs second) | `done` | 134/134 tests, no live claims |
  - [req-007-container-images](./req-007-container-images/ticket.md) — Container images per toolchain + caches | `done` | both images built+smoked, pins audited |
  - [spike-001-openocd-targets](./spike-001-openocd-targets/ticket.md) — Per-pack OpenOCD target verification | `done` | boxed 3h — findings filed, 2 verdicts corrected by orchestrator; consumes into req-004
  - [spike-002-cpp-deps](./spike-002-cpp-deps/ticket.md) — C/C++ dependency mechanism | `done` | boxed 4h — findings filed, pick vendoring; consumes into req-007/post-V1
  - [spike-003-toolchain-recon](./spike-003-toolchain-recon/ticket.md) — 2026 toolchain recon | `done` | boxed 3h — findings filed, vanilla-GCC verdict; CubeCLT gated on license proof
  - [spike-004-config-headers](./spike-004-config-headers/ticket.md) — Per-project config-header flow | `done` | boxed 2h — findings filed, pack-defaults + project-config-dir; consumes into req-004
  - [req-012-openocd-probe-wiring](./req-012-openocd-probe-wiring/ticket.md) — OpenOCD config paths + USB probe binding so stm flash programs | `done` | openspec: req-012-openocd-probe-wiring
  - [req-014-mcu-example](./req-014-mcu-example/ticket.md) — Per-MCU example: generated blink (F411RE implemented, others stub) | `done` | openspec: req-014-mcu-example
  - [req-015-h755-example](./req-015-h755-example/ticket.md) — H755 blink example (LD2/PE1, family-correct registers, primary core) | `done` | openspec: req-015-h755-example

## Requirements

(covered under epic-001 above; standalone entries appear here only for items without a parent epic)

## Bugs

- [bug-001-xor-probe-selectors](./bug-001-xor-probe-selectors/ticket.md) — XOR rejects probe selectors combined with --mcu-config | `done` | S1, INDIVIDUAL_FLAGS narrowed
- [bug-002-rust-panic-abort](./bug-002-rust-panic-abort/ticket.md) — Rendered Rust projects fail to compile | `done` | S1, panic=abort, ARM ELFs proven
- [bug-003-openocd-config-path-prefix](./bug-003-openocd-config-path-prefix/ticket.md) — OpenOCD adapter renders unprefixed config paths (Can't find stlink.cfg) | `done` | S1, openspec: req-012
- [bug-004-probe-usb-passthrough](./bug-004-probe-usb-passthrough/ticket.md) — stm flash container receives serial tty, not the ST-Link USB device | `done` | S1, openspec: req-012
- [bug-005-relative-path-vendor](./bug-005-relative-path-vendor/ticket.md) — create fails with a relative project dir (git -C doubles the path) | `done` | S1
- [bug-006-multi-piece-flash](./bug-006-multi-piece-flash/ticket.md) — Multi-piece flash drops pieces / exits non-zero (dual-core) | `done` | S1
- [bug-007-verbose-forward](./bug-007-verbose-forward/ticket.md) — --verbose ignored in auto mode (no log file) | `done` | S2

## Ops tasks

- [ops-007-make-commands](./ops-007-make-commands/ticket.md) — Make commands for fresh-clone rebuild | `done` | exec: direct
- [ops-008-closeouts-fallback-docs](./ops-008-closeouts-fallback-docs/ticket.md) — Spike close-outs, linker fallback removal, user README | `done`
- [ops-009-install-cli](./ops-009-install-cli/ticket.md) — Installable stm CLI (make install / uninstall) | `done`
- [ops-010-rename-cli-mu](./ops-010-rename-cli-mu/ticket.md) — Rename CLI command stm -> mu (device-agnostic) | `done`
- [ops-011-full-rename-mu](./ops-011-full-rename-mu/ticket.md) — Full rename to mu (repo, package, paths, image namespace) | `done`
- [ops-012-create-path-flag](./ops-012-create-path-flag/ticket.md) — create: rename output flag to --path | `done`
- [ops-013-create-git-init](./ops-013-create-git-init/ticket.md) — create: git-init a fresh project dir before vendoring | `done`
- [ops-014-sparse-vendor](./ops-014-sparse-vendor/ticket.md) — Vendoring: partial+sparse clone (create in seconds, not minutes) | `done`
- [ops-015-organized-tree](./ops-015-organized-tree/ticket.md) — Organize generated project tree (probe/ + build/<core>/) | `done`
- [ops-016-project-gitignore](./ops-016-project-gitignore/ticket.md) — Generated projects ship a .gitignore (build/, .mu/) | `done`

## Spikes

(none)

## Tasks

- [task-002-wire-create-renderer](./task-002-wire-create-renderer/ticket.md) — Wire create renderer | `done` | exec: direct | parent epic-001 | 159/159 tests, create renders F411RE c project, flags-only exits 2
- [task-003-container-argv-fix](./task-003-container-argv-fix/ticket.md) — Container argv invokes build tool, not stm | `done` | 184/184 tests, live ELF proof
- [task-004-narrow-mounts](./task-004-narrow-mounts/ticket.md) — Narrow container mounts to engine + packs | `done` | 184/184 tests, live ELF re-proof
- [task-005-probe-default-proof-precheck](./task-005-probe-default-proof-precheck/ticket.md)
- [task-006-backend-settings](./task-006-backend-settings/ticket.md) — Per-backend pack settings | `done` | 195/195 tests, chips verified — Pack-default probe, proof wiring, image pre-check | `done` | 191/191 tests

## Done (links only, newest last)

(none)
