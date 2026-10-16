---
id: req-021
title: "Architecture separation: pack-declared build stack + split probe ports"
kind: requirement
status: in-progress
size: M
lane: bmad-advisory
links:
  openspec: none
  bmad:
    - _bmad-output/initiative-universal-mcu-env/architecture-universal-mcu-env/architecture-universal-mcu-env.md
worktree: none
branch: ticket/req-021-arch-separation
children: []
---

# Architecture separation: pack-declared build stack + split probe ports

## Requirement

The framework must separate concerns it currently conflates, so a non-STM32 board (ESP32 first)
integrates as pure addition — no `core/` diff (AD-1). Specifically: the build stack is
pack-declared and language-keyed (not the `--lang` flag selecting the toolchain/image/build
command); the probe port splits into FlashPort (programming) and DebugPort (sessions) so a
programming-only device (ESP32 over UART, no JTAG) needs no fabricated debug semantics; family
block validators ship with device truth rather than inside `core/`; artifact emission is gated on
model facts; and the verify matrix keys on `(pack, stack)`.

## Acceptance

- [x] Spine updated: AD-8 amended in place; AD-11…AD-17 added (build stack axis, FlashPort/DebugPort,
      validator relocation, artifact gating, verify axis, refactor-first, operational envelope).
      `Verify: uv run .agents/skills/bmad-architecture/scripts/lint_spine.py --workspace _bmad-output/initiative-universal-mcu-env/architecture-universal-mcu-env` → 0 findings
- [x] Reviewer gate run (rubric + web-verify + adversary, parallel); findings applied (AD-8/AD-11
      contradiction, validator-key collision, `stacks`-location question resolved, per-port rung
      ownership, AD-16 rewording, AD-17 added). Reviews under `reviews/`.
- [ ] Spec refreshed and adopts the spine as a companion (bmad-spec), AD ids stable.
- [ ] Follow-up: the refactor slices R1–R6 and the ESP32 slices E1–E4 are ticketed
      (`work-split-view.md`).

## Evidence

2026-10-16: spine `updated: 2026-10-16`, `status: final`, AD-1…AD-17 present, IDs stable.
Live ESP32 bring-up that motivated this is recorded in `tickets/spike-007-esp32-cam` (ESP32-D0WD
rev1.0, 4 MB, IDF v6.1 triple flashed, blink over UART0 @115200) — a "cell green" reference for
the future `build_idf_cell`.

Drift this fixes (verified against the code during the review): `engine/cli/shim.py:64`
(`_PROBE_VIDS = ("0483",)`), `engine/adapters/__init__.py:128-137` (hardcoded image table),
`engine/adapters/__init__.py:56-70` (ABC declares only `flash`/`debug`), `engine/core/registry.py:88-273`
(validators in `core/`, not `packs/`), `engine/templates/renderer.py:32-36,71,807` and
`engine/templates/vendoring.py:41-45,59-67` (STM32-only assumptions).

## Out of scope

The implementation of R1–R6 / E1–E4 (separate tickets); ESP32 is a non-goal of epic-001
(`epic-001-universal-framework/epic.md:44-46`), so this is a standalone requirement.
