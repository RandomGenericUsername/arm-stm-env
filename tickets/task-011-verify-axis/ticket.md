---
id: task-011
title: "R5 — verify matrix keys on (pack, stack) with a shared evidence envelope"
kind: task
status: done
lane: inherits
parent: req-021
links:
  openspec: none
  bmad: none
worktree: .worktrees/task-011/
branch: ticket/task-011-verify-axis
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

## Evidence

2026-10-16 — branch `ticket/task-011-verify-axis`:

- **`engine/core/build_cells.py`** — registry *mechanism* plus the shared, stack-neutral
  **`BuildEvidence`** envelope (`stack`, `template_family`, `commands`, `exits`, `artifacts`,
  `fits`). It carries **no** `pieces`/`verified`, so build evidence can never be confused with the
  AD-10 flash-proof keys.
- **`engine/verify/e2e.py`** no longer dispatches on language: it resolves the pack-declared stack
  and calls `build_cell_for(stack.template_family)`. The two shipped builders register against
  `c-cmsis` / `rust-cortex`; every built cell gets its envelope assembled in `run_all`.
- `make test` → **305 passed**.
- Cells unchanged at **9** (`(pack, language)`), and all 9 resolve a builder through the registry:
  `uv run python -c "…"` → `existing cells: 9`, `registered builders: ['c-cmsis','rust-cortex']`,
  `all 9 cells resolve a builder via the registry`.
- **A third build system registers** (`test_a_third_stack_registers_its_builder`) — no harness edit.

**Refinement to AD-15 (to fold back into the spine):** "the cell id is the deduped `(pack, stack)`
pair" would collapse `c` and `cpp` into one cell (both map to `make-cmsis`) and lose their
distinct trees/flags. This slice therefore keeps the cell key at `(pack, language)` and moves the
*dispatch* to the stack — each stack still registers its build + fit check, which is the
load-bearing half of the AD. Worth an `AD-15` wording amendment rather than silently diverging.
