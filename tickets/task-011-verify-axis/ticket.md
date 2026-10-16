---
id: task-011
title: "R5 — verify matrix keys on (pack, stack) with a shared evidence envelope"
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

# R5 — verify matrix keys on (pack, stack) with a shared evidence envelope

## Parent

`req-021` — lane inherited from parent.

## Work

Change `engine/verify/e2e.py` from `(pack, language)` cells (`:57-59`, per-language builders
`:334-337`) to **`(pack, stack)`** cells; each stack registers its build command and size/fit check
and returns a shared, stack-neutral build-evidence envelope, distinct from the AD-10 flash-proof
keys (`pieces`, `verified`).

## Done-when

`make test` green; 9 existing cells still green with unchanged evidence keys; a third stack can
register a build + fit check. Governed by AD-15, AD-10, AD-16.
