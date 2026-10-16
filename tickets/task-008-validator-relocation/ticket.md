---
id: task-008
title: "R2 — relocate family block validators to packs/ with (family, block) keys"
kind: task
status: done
lane: inherits
parent: req-021
links:
  openspec: none
  bmad: none
worktree: .worktrees/task-008/
branch: ticket/task-008-validator-relocation
---

# R2 — relocate family block validators to packs/ with (family, block) keys

## Parent

`req-021` — lane inherited from parent.

## Work

Move the family block validators out of `engine/core/registry.py:88-273` and into `packs/`
(AD-13); qualify registry keys by `(family, block)` so two families cannot silently collide;
make `FAMILY_BLOCKS` the dispatch source; make the loader attach validated blocks **generically**
(no hardcoded family block names or STM32-flavoured defaults in `core/`, cf.
`engine/core/loader.py:89-140`, `engine/core/model.py:221-223`).

## Done-when

`make test` green; a pure move (STM32 packs validate identically); adding a family no longer
requires a `core/` diff. Governed by AD-13, AD-1, AD-16.

## Evidence

2026-10-16 — branch `ticket/task-008-validator-relocation`:

- **New `engine/packs/`** — `__init__.py` (`ensure_registered()`) + `stm32.py` holding the ten
  STM32 block validators, registered per family. `engine/core/registry.py` is now **mechanism
  only** (`rg -c "def _validate_" engine/core/registry.py` → 0).
- **Family-qualified registry**: keys are `(family, block)`; `FAMILY_BLOCKS` is the dispatch
  source; `FamilyCollisionError` when two validators claim one key; `register` is idempotent
  (so `clear()` + `ensure_registered()` works).
- **Frame gains `family`** (`FRAME_KEYS`); the loader validates every block against the pack's
  family (a foreign family's block is a `UnknownBlockError`) and attaches **all** validated
  blocks generically — `DeviceFacets.blocks` + `block_for(name)`.
- `make test` → **285 passed**; `mu create … --dry-run` and flash argv unchanged.
- **AD-13 acceptance proven**: `test_new_family_needs_no_core_change` registers family `acme`
  and its `widgets` block *outside* `core/`, loads a pack through the mechanism, and confirms
  the block is rejected for another family — with no `engine/core` edit.

Deferred: `DeviceFacets` still carries typed STM32 accessors (`fpu`/`linker`/`config_headers`/
…), derived from the pack. They are unused by any other family and do not block a new one
(that family's blocks arrive via `.blocks`), so the full de-STSTM32-ing of `DeviceFacets` is
left to a later slice rather than expanding this one.
