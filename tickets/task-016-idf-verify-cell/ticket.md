---
id: task-016
title: "E4 — build_idf_cell in the verify harness"
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

# E4 — build_idf_cell in the verify harness

## Parent

`req-022` — lane inherited from parent.

## Work

Register a `build_idf_cell` for the `idf-cmake` stack (AD-15): render the ESP32 tree, run
`idf.py build` in `espressif/idf:v6.1`, and assert the triple exists (`bootloader.bin`,
`partition-table.bin`, app `.bin`) with a partition-fit check (offsets/sizes — not
`arm-none-eabi-size`). Evidence uses the shared build-evidence envelope.

## Done-when

The `(esp32cam, idf-cmake)` cell is green in the harness; the flash + boot-log proof is captured;
9 existing cells unchanged. Governed by AD-15, AD-10. Depends on E3, R5.
