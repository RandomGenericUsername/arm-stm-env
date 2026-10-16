---
id: task-013
title: "E1 — packs/esp32cam.yaml + esp32 family block validators"
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

# E1 — packs/esp32cam.yaml + esp32 family block validators

## Parent

`req-022` — lane inherited from parent.

## Work

Write `packs/esp32cam.yaml`: frame (cores = xtensa-lx6 dual-core, memory = 520 KB SRAM + 4 MB
external PSRAM, `probe` = UART, `probe_backend: esptool`, `proof_rung`), the `stacks` map
(`c → idf-cmake`), and the stock example LED fact (GPIO33, **active-low**). Add the esp32 family
block validators (`esptool` / `partitions` / `sdkconfig`) — shipped alongside `packs/`, not in
`core/` (AD-13), registered by the R2 mechanism.

## Done-when

`mu create --mcu-config esp32cam --lang c --dry-run` resolves; the pack loads and validates;
`make test` green. Governed by AD-4, AD-13. Depends on R2.
