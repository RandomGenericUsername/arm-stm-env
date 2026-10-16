---
id: req-022
title: "ESP32 family support (first non-STM32 device)"
kind: requirement
status: proposed
size: L
lane: bmad-advisory
links:
  openspec: none
  bmad:
    - _bmad-output/initiative-universal-mcu-env/architecture-universal-mcu-env/architecture-universal-mcu-env.md
    - _bmad-output/initiative-universal-mcu-env/spec-universal-mcu-env/spec-universal-mcu-env.md
worktree: none
branch: none
children:
  - task-013
  - task-014
  - task-015
  - task-016
---

# ESP32 family support (first non-STM32 device)

## Requirement

Add ESP32 (ESP32-CAM / ESP32-D0WD) as the first non-STM32 family: ESP-IDF build via `idf-cmake`,
`esptool` UART flashing at the pack-declared offsets, and an AD-10 proof with no DebugPort.

**Timing: post-V1.** V1 is the three-STM32-board × three-language matrix (spec Constraint); ESP32 is
the proof the engine is general, not a V1 gate.

This is **not** a drop-in — the needs it surfaced (build-stack axis, programming-only devices,
non-CMSIS templates, a third verify stack) require the **engine to be generalised first**
(`req-021`, slices R1–R6, AD-16). Only then does the family land as a pure addition, which is
CAP-7's success criterion and the AD-1 acceptance test.

## Acceptance

- [ ] All four child tasks done.
- [ ] CAP-7 holds: the ESP32 family lands with **zero `engine/core` diffs**.
      `Verify: git diff --stat <R6-merge>..<E4-merge> -- engine/core` → empty
- [ ] `esptool` flashes an ESP32-D0WD over UART and reports an AD-10 proof with no DebugPort (CAP-8).
- [ ] `mu create --mcu-config esp32cam --lang c` → `idf.py build` green via the pinned
      `espressif/idf:v6.1` image; `make test` green.

## Evidence

Live reference already exists: `tickets/spike-007-esp32-cam` — ESP32-D0WD rev1.0, 4 MB flash,
MAC `30:83:98:57:5f:c4`; IDF v6.1 built the triple, all three flashed `Hash of data verified.`,
app printed `mu/esp32cam: blink N` over UART0 @115200.

## Non-goals

Bare-metal xtensa, OpenOCD/JTAG debugging, and the Rust `esp-hal` path for ESP32.
