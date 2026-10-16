---
id: task-018
title: "ESP32 VS Code flow: build / flash / monitor (no fake debug)"
kind: task
status: done
lane: inherits
parent: req-022
links:
  openspec: none
  bmad: none
worktree: .worktrees/task-018/
branch: ticket/task-018-esp32-vscode
---

# ESP32 VS Code flow: build / flash / monitor (no fake debug)

## Parent

`req-022` — lane inherited from parent.

## Work

`--vscode` generated nothing for the ESP-IDF stack (the generator was gated on the OpenOCD fact),
so an ESP32 project had no VS Code flow at all. Add one that is honest about the device: `idf.py`
tasks for **build / flash / monitor** and explicitly **no** `launch.json`, since a classic ESP32 has
no attach without external JTAG wired to the SD pins (`req-022` non-goals).

## Done-when

`mu create --mcu-config esp32cam --lang c --vscode` renders a usable ESP32 VS Code flow, and the
Cortex flows are unchanged. `make test` green.

## Evidence

2026-10-16 — branch `ticket/task-018-esp32-vscode`:

- `renderer.py`: `_vscode_files_idf()` emits `.vscode/tasks.json`
  (labels `Build`, `Flash`, `Monitor`, `Build + Flash + Monitor` → `idf.py build` /
  `idf.py flash` / `idf.py monitor` / combined) and `.vscode/extensions.json`
  (`ms-vscode.cpptools`). The render dispatch now sends the ESP-IDF stack to it and keeps
  OpenOCD stacks on the cortex-debug path.
- `mu create --name esp32vscode --mcu-config esp32cam --lang c --vscode` renders
  `CMakeLists.txt`, `main/{CMakeLists.txt,main.c}`, `sdkconfig.defaults`, `README.md`, `.mu/stack`
  and `.vscode/{tasks.json,extensions.json}`.
- **No fake debug**: no `.vscode/launch.json`, and nothing in `.vscode/` mentions
  `cortex-debug` or OpenOCD; no `probe/` directory is emitted.
- `make test` → **347 passed** (2 new tests: the task set, and the absence of launch/cortex-debug).
- The dev container it attaches to is the pinned IDF image:
  `mu dev --project-dir … --dry-run` → `espressif/idf:v6.1@sha256:81893c71…`, project at
  `/project`, engine+packs read-only at `/opt/mu`.

Steps to use it: `mu dev --project-dir <proj> [--device /dev/ttyUSB0]`, then VS Code →
*Dev Containers: Attach to Running Container* → open `/project` → **Terminal: Run Task** →
Build / Flash / Monitor.

**Note:** `Flash` uses `idf.py flash`, which writes the same offsets our pack declares (verified:
IDF's own `flash_args` matches `partition_table=0x8000`, `app=0x10000`, `dio/40m/4MB`). It does not
go through `mu`'s proof rung — that stays the `mu flash` path.
