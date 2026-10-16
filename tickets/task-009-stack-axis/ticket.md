---
id: task-009
title: "R3 — pack-declared stacks map + toolchain registry"
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

# R3 — pack-declared stacks map + toolchain registry

## Parent

`req-021` — lane inherited from parent.

## Work

Add the `stacks` map to the shared frame (`language → stack` id: `make-cmsis`, `cargo-cortex`,
`idf-cmake`); replace the hardcoded `DefaultImageLookup.TABLE`
(`engine/adapters/__init__.py:128-137`) with a registry toolchain adapters register into; resolve
image + build command from the **resolved stack**, not the language flag
(`engine/cli/main.py:216-220`); persist the resolved stack in the rendered tree so `build`/`dev`
(which load no pack) resolve identically.

## Done-when

`make test` green; STM32 packs declare `make-cmsis`/`cargo-cortex`; language no longer selects the
toolchain; a missing (pack, language) pair errors loudly. Governed by AD-11, AD-8, AD-16.
