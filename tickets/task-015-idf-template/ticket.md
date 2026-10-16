---
id: task-015
title: "E3 — idf-cmake template family"
kind: task
status: proposed
lane: inherits
parent: req-022
links:
  openspec: none
  bmad: none
worktree: none
branch: none
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
