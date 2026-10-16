---
id: task-021
title: "ESP32 Monitor task failed: it reset the chip through the ROM, which this board can't do"
kind: task
status: done
lane: inherits
parent: req-022
links:
  openspec: none
  bmad: none
worktree: .worktrees/task-021/
branch: ticket/task-021-monitor-no-reset
---

# ESP32 Monitor task failed against a running app

## Parent

`req-022` — lane inherited from parent.

## Work

The generated `Monitor` task ran `idf.py monitor`, which **resets the chip
through the ROM** (via DTR/RTS) before reading. On a board with no auto-reset
circuit — the ESP32-CAM, reached through a 4-lead UART bridge — that reset does
nothing, so the ROM sync gets no answer while the app is running and monitor
aborts:

```
Serial port /dev/ttyUSB0:
Connecting.......................
/dev/ttyUSB0 failed to connect: Failed to connect to Espressif device: No serial data received.
```

Fix: read the port as-is. `idf.py monitor --no-reset` requires an explicit port,
so the generated tasks name it (the pack now declares the serial port as its
connection requirement) and the README says to press **RST** to catch the boot
banner.

## Done-when

`mu create … --vscode` generates a Monitor task that works against a running app
on this board; the render tests cover it; `make test` green.

## Evidence

2026-10-16 — branch `ticket/task-021-monitor-no-reset`:

- Reproduced in the container: `idf.py monitor` → the failure above;
  `idf.py -p /dev/ttyUSB0 monitor --no-reset` → past the connect step, launching
  `idf_monitor.py -p /dev/ttyUSB0 … --no-reset` (it then only refused because the
  exec had no TTY — VS Code's terminal has one).
- The board was meanwhile streaming `esp32cam: blink 186…191`, so app + port were
  healthy; only the reset attempt was wrong.
- Generated tasks now:
  `Build` → `idf.py build`;
  `Flash` → `idf.py -p /dev/ttyUSB0 flash`;
  `Monitor` → `idf.py -p /dev/ttyUSB0 monitor --no-reset`;
  `Build + Flash + Monitor` → `idf.py build && idf.py -p /dev/ttyUSB0 monitor --no-reset`.
- `packs/esp32cam.yaml` declares `probe.address: /dev/ttyUSB0` (the conventional
  Linux bridge node; macOS overrides it in the tasks).
- `make test` → **355 passed**.