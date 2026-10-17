---
id: req-022
title: "ESP32 family support (first non-STM32 device)"
kind: requirement
status: done
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

- [x] All four child tasks done.
- [x] CAP-7 holds in substance: the ESP32 family needed **no brand-specific core change**. The one
      core edit across E1–E4 is generic — `DeviceView` exposing family blocks (`blocks`/`block_for`),
      the R2 leftover, landed as a framework generalisation per AD-1's corollary (E2). ESP32 itself
      lives entirely in `engine/packs/esp32.py` + `packs/esp32cam.yaml` + `engine/adapters/esptool.py`
      + the renderer's `idf-cmake` family.
      `Verify: git diff --stat aa950e9 -- engine/core` → `model.py` (+15) + a test file, nothing
      brand-specific
- [x] `esptool` flashes over UART and reports an AD-10 proof with no DebugPort (CAP-8) — proven
      **live** in `spike-007` (host-side: triple flashed, `Hash of data verified`, blink @115200).
      `mu debug` is refused for the backend (AD-12).
- [x] `mu create --mcu-config esp32cam --lang c` → `idf.py build` green via the pinned
      `espressif/idf:v6.1` image; `make test` green (338).

## Evidence

Live reference: `tickets/spike-007-esp32-cam` — ESP32-D0WD rev1.0, 4 MB flash,
MAC `30:83:98:57:5f:c4`; IDF v6.1 built the triple, all three flashed `Hash of data verified.`,
app printed `mu/esp32cam: blink N` over UART0 @115200.

## Open (recorded, not papered over)

- ~~Containerized UART tty passthrough~~ — **CLOSED**: `task-017` forwards `/dev/ttyUSB*`, and
  `ops-024` proves the live containerized flash + boot log on the bench
  (`flash verdict: 3/3 OK`; `esp32cam: blink on GPIO33`).
- ~~The harness's flash + boot-log step~~ — the *build* cell is green (`task-016`); the live
  flash/run proof is captured in `ops-024` (run manually on the bench, not yet automated into the
  harness).

## Final state — 2026-10-16 (this is as far as the ESP32-CAM goes for now)

Working end to end on the bench, through the container: **create → build → flash → run →
monitor**, plus a VS Code flow (build / flash / monitor tasks) on an attachable dev container.

| Stage | How |
|---|---|
| create | `mu create --mcu-config esp32cam --lang c [--vscode]` |
| build | `idf.py build` in `espressif/idf:v6.1` (digest-pinned) — harness cell green |
| flash | `mu flash …` (container, `esptool` over the forwarded tty) or the task |
| run / monitor | UART0 @115200; `idf.py -p /dev/ttyUSB0 monitor --no-reset` |

**Deliberately stops here:**

- **JTAG debugging** — the classic ESP32 has no USB-serial-JTAG, and its JTAG pins
  (GPIO12–15) are the microSD lines on this board; it needs an ESP-Prog-class adapter wired
  there. Out of scope (`req-022` non-goals), so there is no F5/breakpoint flow — debugging is
  log-based (`Monitor`, and IDF prints a full backtrace on panic).
- **Bare-metal xtensa / Rust `esp-hal`** — non-goals.

**Carried follow-ups (not ESP32-specific):**

- `core/` still builds its typed STM32 LED facet from the `example` block, so families cannot
  share that block name (hence ESP32's `example_led`) — recorded on `task-008`.
- The live flash/boot-log step is bench-manual (`ops-024`), not automated into the harness.

**Bench-driven fixes this session** (each found by actually using the flow, not by unit tests):
`task-020` per-blink logs, `task-021` `--no-reset` + named port, `task-022` monitor as its own
task, `ops-025` the port-ownership note.

## Non-goals

Bare-metal xtensa, OpenOCD/JTAG debugging, and the Rust `esp-hal` path for ESP32.
