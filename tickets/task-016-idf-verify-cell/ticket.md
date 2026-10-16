---
id: task-016
title: "E4 — build_idf_cell in the verify harness"
kind: task
status: done
lane: inherits
parent: req-022
links:
  openspec: none
  bmad: none
worktree: .worktrees/task-016/
branch: ticket/task-016-idf-verify-cell
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

## Evidence

2026-10-16 — branch `ticket/task-016-idf-verify-cell`:

- **`build_idf_cell`** registered for the `idf-cmake` template family: runs `idf.py build` in the
  pinned image, asserts the triple (`bootloader.bin`, `partition-table.bin`, `<pack>.bin`), and
  fit-checks the app against the factory partition size **IDF itself reports**
  (`Smallest app partition is 0x… bytes`) — offsets/sizes, never `arm-none-eabi-size`.
- **Cells are derived from the packs' `stacks` maps**, so a pack that ships one language
  contributes one cell: `CELLS` is now 10 (the 9 STM32 cells unchanged and first, plus
  `(esp32cam, c)`).
- `make test` → **338 passed**.
- **The cell is green in the harness**:
  `uv run python -m engine.verify.e2e --only esp32cam --workdir … --evidence …` →
  `[PASS] esp32cam/c exits=[0] elfs=[build/bootloader/bootloader.bin, build/partition_table/partition-table.bin, build/esp32cam.bin] warnings=5`
  → **1/1 green**, and the evidence records the shared envelope:
  `… artifacts=build/bootloader/bootloader.bin=26176,build/partition_table/partition-table.bin=3072,build/esp32cam.bin=149120; fits=factory=149120/1048576`
- Warnings are recorded and never fail the cell (warn-only policy, unchanged).

**Open (recorded, not claimed done):** the *flash + boot-log* proof of the done-when is not
produced by this harness run — it needs the owner's board plus E2's open containerized-UART-tty
gap. Live host-side flash + boot log already exist from **spike-007**; what remains is proving the
same through the container path.
