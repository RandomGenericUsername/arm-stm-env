---
id: task-020
title: "ESP32 example logs every blink (the monitor showed one line then went quiet)"
kind: task
status: done
lane: inherits
parent: req-022
links:
  openspec: none
  bmad: none
worktree: .worktrees/task-020/
branch: ticket/task-020-esp32-blink-log
---

# ESP32 example logs every blink

## Parent

`req-022` — lane inherited from parent.

## Work

The generated ESP-IDF app printed once at boot and then blinked silently, so the
`Monitor` task looked broken: after the boot banner there was no further output
unless the board was reset. Log the counter each loop, so the monitor shows live
output (and a reset is not needed to see activity).

## Done-when

`mu create … --mcu-config esp32cam` renders an app that logs per blink; the
render tests cover it; `make test` green.

## Evidence

2026-10-16 — branch `ticket/task-020-esp32-blink-log`:

- `_IDF_MAIN_C` now emits `int n = 0;` and, inside the loop,
  `printf("<project>: blink %d\n", ++n);`.
- `make test` → **355 passed** (new `test_idf_example_logs_every_blink`).
- Bench: rebuilt + reflashed the ESP32-CAM project; `idf.py monitor` then showed a
  continuous `esp32cam: blink N` counter instead of a single line.

Note: the Cortex examples are unchanged (they are debugger-first, and their README
already states the expected ~2 Hz blink).