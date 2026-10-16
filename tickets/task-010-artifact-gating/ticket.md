---
id: task-010
title: "R4 — gate artifact emission on model facts; functional pack probe block"
kind: task
status: done
lane: inherits
parent: req-021
links:
  openspec: none
  bmad: none
worktree: .worktrees/task-010/
branch: ticket/task-010-artifact-gating
---

# R4 — gate artifact emission on model facts; functional pack probe block

## Parent

`req-021` — lane inherited from parent.

## Work

Gate artifact emission on model facts (AD-14): emit `probe/openocd.cfg`, the config header, and the
vendor tree only when the model carries the corresponding fact — `engine/templates/renderer.py:1209,1224-1225`
currently writes them unconditionally, and vendoring keys on the pack-id prefix
(`engine/templates/vendoring.py:59-67`). Make the pack `probe:` block functional (AD-9): the shim
merges it with CLI selectors (CLI **replaces** it wholesale, AD-5), and autodetect IDs are
registered per family instead of the hardcoded `_PROBE_VIDS = ("0483",)` (`engine/cli/shim.py:64`).

## Done-when

`make test` green; rendered STM32 trees byte-identical; a non-STM32 pack emits no OpenOCD/CMSIS
artifacts. Governed by AD-14, AD-9, AD-16.

## Evidence

2026-10-16 — branch `ticket/task-010-artifact-gating`:

- **Artifact emission is fact-gated** (`engine/templates/renderer.py`): `probe/openocd.cfg`,
  `probe/probe-serial.cfg` (and the dual-core cfg) only when the model carries an `openocd` block;
  the VS Code block too (cortex-debug is OpenOCD); `config/OVERRIDES.md` + `config/<header>` only
  when the pack declares the `config_headers` block.
- **Vendor tree** is emitted only when the pack declares vendored vendor files, and keyed by the
  **declared family** — `vendoring._family_of` (the pack-id-prefix parse) is deleted;
  `family_repo(pack_id, family)` + `FAMILY_REPOS` keyed `stm32f4`/`stm32h7`/`stm32wl` (AD-14).
- **`Device.family`** added (frame-declared), so family-owned facts key off the declaration.
- **Probe autodetect ids** moved out of `engine/cli/`: `engine/core/probe_ids.py` (mechanism) +
  the STM32 family module registers `0483` (AD-14). The hardcoded `_PROBE_VIDS` tuple is gone;
  `rg "_PROBE_VIDS = "` finds no literal list.
- `make test` → **300 passed**.
- STM32 tree byte-identical vs `main`: `diff -r` of a rendered `stm32h755` C tree → **IDENTICAL**.
- A model without the STM32 facts renders **no** `probe/` or `config/` artifacts
  (`test_render_emits_no_openocd_or_cmsis_artifacts_without_the_facts`,
  `test_render_emits_no_config_artifacts_without_the_config_block`).

Deferred (recorded): making the **pack `probe:` block** supply per-device connection requirements
(VID/PID/serial the shim consumes when no CLI selector is given) lands with **E2** (ESP32 UART
binding) — it is where per-device requirements actually differ; for STM32 the family-level id is
sufficient and now comes from device truth.
