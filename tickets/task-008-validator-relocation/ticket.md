---
id: task-008
title: "R2 — relocate family block validators to packs/ with (family, block) keys"
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
