---
id: task-015
title: "E3 — idf-cmake template family"
kind: task
status: done
lane: inherits
parent: req-022
links:
  openspec: none
  bmad: none
worktree: .worktrees/task-015/
branch: ticket/task-015-idf-template
---

# E3 — idf-cmake template family

## Parent

`req-022` — lane inherited from parent.

## Work

Add the `idf-cmake` template family to `engine/templates/renderer.py`: a rendered tree of
`CMakeLists.txt` + `main/CMakeLists.txt` + `main/main.c` + `sdkconfig.defaults` (optional
`partitions.csv`), targeting ESP-IDF (`idf.py build`). The OpenOCD/CMSIS artifacts must **not** be
emitted for this stack (R4 gating). Register the template family only — the `espressif/idf:v6.1` stack registration moved to **E2** (auto mode
needed the image to resolve); extend the built-in example to the ESP32 LED fact.

## Done-when

`mu create --mcu-config esp32cam --lang c` renders a CMake tree; `idf.py build` in
`espressif/idf:v6.1` produces the ESP32 triple; no OpenOCD/CMSIS files in the tree. Governed by
AD-11, AD-14. Depends on R3, R4. (Image/stack registration done in E2; this slice adds the
`idf-cmake` template family to the renderer.)

## Evidence

2026-10-16 — branch `ticket/task-015-idf-template`:

- **`renderer.py` gains the `idf-cmake` template family**: `CMakeLists.txt`,
  `main/CMakeLists.txt`, `main/main.c`, `sdkconfig.defaults`, plus an ESP-IDF `README.md`
  dispatched by template family. Everything is read from the pack's blocks — the LED pin/active
  level from `example_led`, the chip target and flash size from `sdkconfig`.
- `make test` → **335 passed** (6 new render tests: CMake shape, GPIO/active-low levels, the
  sdkconfig lines, the UART README, and the **absence** of OpenOCD/CMSIS/vendor/make/cargo).
- `mu create --name esp32demo --mcu-config esp32cam --lang c` renders exactly: `CMakeLists.txt`,
  `main/CMakeLists.txt`, `main/main.c`, `sdkconfig.defaults`, `README.md`, `.gitignore`,
  `.mu/stack`.
- **Built for real** in the pinned image:
  `docker run --rm -v /tmp/opencode/esp32demo:/project -w /project espressif/idf:v6.1 bash -lc "idf.py build"`
  → `Project build complete`, producing `build/bootloader/bootloader.bin` (26176 B),
  `build/partition_table/partition-table.bin` (3072 B), `build/esp32cam.bin` (149120 B).
- **Independent corroboration**: ESP-IDF's own `build/flash_args` emits
  `--flash-mode dio --flash-freq 40m --flash-size 4MB`, `0x1000 bootloader/bootloader.bin`,
  `0x8000 partition_table/partition-table.bin` — exactly what E2's esptool argv derives from the
  pack's `esptool` + `partitions` blocks. The pack's facts and IDF's output agree.
