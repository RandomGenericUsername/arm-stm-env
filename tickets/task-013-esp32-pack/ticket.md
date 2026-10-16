---
id: task-013
title: "E1 — packs/esp32cam.yaml + esp32 family block validators"
kind: task
status: done
lane: inherits
parent: req-022
links:
  openspec: none
  bmad: none
worktree: .worktrees/task-013/
branch: ticket/task-013-esp32-pack
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

## Evidence

2026-10-16 — branch `ticket/task-013-esp32-pack`:

- **`engine/packs/esp32.py`** — the ESP32 family module (device truth, outside `core/`): validators
  for `esptool`, `partitions`, `sdkconfig`, `example_led`, plus the family's UART-bridge probe ids
  (`10c4` CP210x, `1a86` CH340). Registered via `engine/packs/__init__.py`.
- **`packs/esp32cam.yaml`** — `family: esp32`, `stacks: {c: idf-cmake}`, xtensa-lx6 dual-core,
  SRAM + 4 MB PSRAM, `probe: uart-serial`, `probe_backend: esptool`, `proof_rung: uart-boot-log`,
  and the four family blocks (offsets `0x1000`/`0x8000`/`0x10000` from the live spike-007 run).
- **`engine/templates/renderer.py`** — `SUPPORTED_TEMPLATE_FAMILIES`, so "stack recognised, its
  template slice not shipped yet" is explicit rather than a mystery failure.
- **`engine/cli/tests/packs.py`** — tests now select a shipped pack **by capability** (the ESP32
  pack sorts first alphabetically), which keeps them hardware-name-free.
- `make test` → **319 passed**.
- Done-when: `mu create --name demo --mcu-config esp32cam --lang c --dry-run` →
  `would render esp32cam (c) to demo/`.
- **AD-1 acceptance holds**: `git diff --stat main -- engine/core` → **EMPTY** — the first
  non-STM32 family landed with no core change (only a new core *test* file).
- Family qualification is enforced: an `sdkconfig` block in an `stm32f4` pack raises
  `UnknownBlockError`.

Notes: auto-mode `flash` for this pack correctly fails loudly with
`unknown build stack: 'idf-cmake'` until **E3** registers the toolchain — a real error, not a
silent guess. The ESP32 example block is named `example_led` rather than reusing `example`,
because `core/` still builds its typed STM32 LED facet from that shape (the R2 leftover); a
follow-up should generalise that extraction so a family can reuse the block name.
