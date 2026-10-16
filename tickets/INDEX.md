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
  - [req-016-vscode-integration](./req-016-vscode-integration/ticket.md) — Generated .vscode/ for the container-attached debug flow (C/C++ first) | `done` | openspec: req-016-vscode-integration
  - [req-017-svd-registers](./req-017-svd-registers/ticket.md) — Per-core SVD fetch -> Cortex-Debug peripheral register view | `done` | openspec: req-017-svd-registers
  - [req-018-detach-resume](./req-018-detach-resume/ticket.md) — Keep firmware running after debug: resume-on-detach config | `done` | openspec: req-018-detach-resume
  - [req-019-dev-probe](./req-019-dev-probe/ticket.md) — mu dev accepts probe selectors (dev container gets the probe) | `done` | openspec: req-019-dev-probe
  - [req-020-probe-autodetect](./req-020-probe-autodetect/ticket.md) — Auto-detect a single attached probe (no --vid/--pid needed) | `done` | openspec: req-020-probe-autodetect

## Requirements

(covered under epic-001 above; standalone entries appear here only for items without a parent epic)

- [req-021-arch-separation](./req-021-arch-separation/ticket.md) — Architecture separation: pack-declared build stack + split probe ports | `done` | bmad-advisory, spine AD-8 amended + AD-11…AD-17; pre-ESP32 refactor gate; follow-ups ticketed
- [req-022-esp32-family](./req-022-esp32-family/ticket.md) — ESP32 family support (first non-STM32 device) | `proposed` | bmad-advisory | 0/4 children done | parents req-021's refactor

## Bugs

- [bug-001-xor-probe-selectors](./bug-001-xor-probe-selectors/ticket.md) — XOR rejects probe selectors combined with --mcu-config | `done` | S1, INDIVIDUAL_FLAGS narrowed
- [bug-002-rust-panic-abort](./bug-002-rust-panic-abort/ticket.md) — Rendered Rust projects fail to compile | `done` | S1, panic=abort, ARM ELFs proven
- [bug-003-openocd-config-path-prefix](./bug-003-openocd-config-path-prefix/ticket.md) — OpenOCD adapter renders unprefixed config paths (Can't find stlink.cfg) | `done` | S1, openspec: req-012
- [bug-004-probe-usb-passthrough](./bug-004-probe-usb-passthrough/ticket.md) — stm flash container receives serial tty, not the ST-Link USB device | `done` | S1, openspec: req-012
- [bug-005-relative-path-vendor](./bug-005-relative-path-vendor/ticket.md) — create fails with a relative project dir (git -C doubles the path) | `done` | S1
- [bug-006-multi-piece-flash](./bug-006-multi-piece-flash/ticket.md) — Multi-piece flash drops pieces / exits non-zero (dual-core) | `done` | S1
- [bug-007-verbose-forward](./bug-007-verbose-forward/ticket.md) — --verbose ignored in auto mode (no log file) | `done` | S2
- [bug-008-wl55-memory](./bug-008-wl55-memory/ticket.md) — WL55JC pack memory map wrong (RAM 128K vs real 64K) -> HardFault | `done` | S1
- [bug-009-detach-targets](./bug-009-detach-targets/ticket.md) — resume-on-detach cfg breaks the H7 server (undefined _TARGETNAME) | `done` | S1
- [bug-010-build-probe-gate](./bug-010-build-probe-gate/ticket.md) — mu build broken: probe auto-detect forwards --device to build | `done` | S1
- [bug-011-h7-single-step](./bug-011-h7-single-step/ticket.md) — OpenOCD never single-steps the H755 (PC frozen): mask interrupts during step | `done` | S1, consumes spike-005
- [bug-012-vscode-maskisr-gate](./bug-012-vscode-maskisr-gate/ticket.md) — Generated launch.json emits cortex_m maskisr for non-Cortex-M packs | `done` | S3, gates bug-011
- [bug-013-dual-core-debug](./bug-013-dual-core-debug/ticket.md) — Generated M4 launch config attaches to the M7 core (no per-core targeting) | `done` | S2, per-core targetProcessor + chained dual-core config
- [bug-014-dual-core-ram](./bug-014-dual-core-ram/ticket.md) — Dual-core packs link both cores into one RAM region (same _estack) -> M7 hard-faults | `done` | S1, per-core memory regions
- [bug-015-blink-rate](./bug-015-blink-rate/ticket.md) — Generated blink runs ~29 Hz (delay formula 3x off) — LED looks steady, not blinking | `done` | S2
- [bug-016-hla-maskisr-gate](./bug-016-hla-maskisr-gate/ticket.md) — HLA targets (stlink.cfg) reject `cortex_m maskisr` -> F411 debug launch fails | `done` | S1
- [bug-017-login-shell-path](./bug-017-login-shell-path/ticket.md) — Image /etc/profile resets PATH -> login shells (VS Code tasks) lose the toolchain (Error 127) | `done` | S2, needs image rebuild
- [bug-018-usb-bus-binding](./bug-018-usb-bus-binding/ticket.md) — Containers bind a USB node number -> a replug breaks them (GDB Server Quit Unexpectedly) | `done` | S2, whole-bus mount + serial selection
- [bug-019-cli-test-isolation](./bug-019-cli-test-isolation/ticket.md) — CLI tests depend on the host USB bus (fail when more than one probe is attached) | `done` | S3
- [bug-020-dockerfile-layer-order](./bug-020-dockerfile-layer-order/ticket.md) — bug-017's profile.d RUN sits before the toolchain layers -> every image rebuild is a full rebuild | `done` | S3
- [bug-021-wl55-dual-core](./bug-021-wl55-dual-core/ticket.md) — WL55JC dual-core: HLA hides the CM0+, both cores share flash, M0+ arch wrong, CPU2 never released | `done` | S2, M4 verified; CM0+ -> spike-006
- [bug-022-mount-preflight](./bug-022-mount-preflight/ticket.md) — Unshared Docker mount paths fail with raw daemon error (no preflight, no hint) | `done` | S3, probe + tee fallback, 276/276 tests, live repro proven
- [bug-023-sibling-attach](./bug-023-sibling-attach/ticket.md) — WL55JC: released sibling can't be launched, primary's reset hides it, flash order boots it into an unflashed image | `done` | S2, M4+CM0+ run; compound sequence fragile
- [bug-024-no-reset-for-released-siblings](./bug-024-no-reset-for-released-siblings/ticket.md) — cortex-debug launch fails on a released-sibling pack: 'monitor reset halt' errors (Protocol error with Rcmd) | `done` | S1, attach-only for cpu2_boot packs

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
- [ops-017-wl55-example](./ops-017-wl55-example/ticket.md) — WL55JC blink example (LD1/PB15) | `done`
- [ops-018-sibling-core-example](./ops-018-sibling-core-example/ticket.md) — Sibling-core example: debuggable counter loop instead of a wfi stub | `done`
- [ops-019-vscode-debug-docs](./ops-019-vscode-debug-docs/ticket.md) — Document the VS Code debug flow (docs/vscode-debug.md) | `done`
- [ops-020-clean-test-doc](./ops-020-clean-test-doc/ticket.md) — Document the clean from-zero test (docs/vscode-debug.md §9) | `done`
- [ops-021-project-readme](./ops-021-project-readme/ticket.md) — Generated project README.md (each project documents its own flow) | `done`
- [ops-022-f5-prelaunch](./ops-022-f5-prelaunch/ticket.md) — F5 = build + flash + debug (preLaunchTask in the generated launch configs) | `done`

## Spikes

- [spike-005-h755-single-step](./spike-005-h755-single-step/ticket.md) — H755 single-step doesn't advance (stlink-dap) | `consumed` | boxed 3h — cause found (interrupts during step); fixed in bug-011
- [spike-006-wl55-cm0p-bringup](./spike-006-wl55-cm0p-bringup/ticket.md) — WL55JC CM0+ bring-up: C2BOOT doesn't persist and the CM0+ double-faults | `reported` | boxed 4h — M4 works; CM0+ needs security/RAM investigation

## Tasks

- [task-002-wire-create-renderer](./task-002-wire-create-renderer/ticket.md) — Wire create renderer | `done` | exec: direct | parent epic-001 | 159/159 tests, create renders F411RE c project, flags-only exits 2
- [task-003-container-argv-fix](./task-003-container-argv-fix/ticket.md) — Container argv invokes build tool, not stm | `done` | 184/184 tests, live ELF proof
- [task-004-narrow-mounts](./task-004-narrow-mounts/ticket.md) — Narrow container mounts to engine + packs | `done` | 184/184 tests, live ELF re-proof
- [task-005-probe-default-proof-precheck](./task-005-probe-default-proof-precheck/ticket.md)
- [task-006-backend-settings](./task-006-backend-settings/ticket.md) — Per-backend pack settings | `done` | 195/195 tests, chips verified — Pack-default probe, proof wiring, image pre-check | `done` | 191/191 tests
- [task-007-split-probe-port](./task-007-split-probe-port/ticket.md) — R1: split the probe port into FlashPort + DebugPort | `done` | parent req-021 | 278/278 tests, argv unchanged, renderer untouched
- [task-008-validator-relocation](./task-008-validator-relocation/ticket.md) — R2: family block validators → packs/, (family, block) keys | `proposed` | parent req-021
- [task-009-stack-axis](./task-009-stack-axis/ticket.md) — R3: pack-declared stacks map + toolchain registry | `proposed` | parent req-021
- [task-010-artifact-gating](./task-010-artifact-gating/ticket.md) — R4: gate artifact emission on model facts; functional pack probe block | `proposed` | parent req-021
- [task-011-verify-axis](./task-011-verify-axis/ticket.md) — R5: verify matrix (pack, stack) + shared evidence envelope | `proposed` | parent req-021
- [task-012-operational-envelope](./task-012-operational-envelope/ticket.md) — R6: name the operational envelope as one owned contract | `proposed` | parent req-021
- [task-013-esp32-pack](./task-013-esp32-pack/ticket.md) — E1: packs/esp32cam.yaml + esp32 family validators | `proposed` | parent req-022
- [task-014-esptool-backend](./task-014-esptool-backend/ticket.md) — E2: esptool probe backend (FlashPort) + UART binding | `proposed` | parent req-022
- [task-015-idf-template](./task-015-idf-template/ticket.md) — E3: idf-cmake template family | `proposed` | parent req-022
- [task-016-idf-verify-cell](./task-016-idf-verify-cell/ticket.md) — E4: build_idf_cell in the verify harness | `proposed` | parent req-022

## Done (links only, newest last)

(none)
