---
id: task-010
title: "R4 — gate artifact emission on model facts; functional pack probe block"
kind: task
status: proposed
lane: inherits
parent: req-021
links:
  openspec: none
  bmad: none
worktree: none
branch: none
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
