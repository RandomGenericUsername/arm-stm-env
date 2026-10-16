---
id: req-023
title: "Reconcile AD-15 with the R5 verify implementation"
kind: requirement
status: done
size: XS
lane: bmad-advisory
links:
  openspec: none
  bmad:
    - _bmad-output/initiative-universal-mcu-env/architecture-universal-mcu-env/architecture-universal-mcu-env.md
worktree: .worktrees/req-023/
branch: ticket/req-023-ad15-refinement
children: []
---

# Reconcile AD-15 with the R5 verify implementation

## Requirement

`task-011` (R5) deliberately kept the verify cell key at `(pack, language)` and moved *dispatch* to
the resolved build stack, because one stack (`make-cmsis`) serves both `c` and `cpp` whose rendered
trees differ. AD-15 as written ("the cell id is the deduped `(pack, stack)` pair") contradicted
that. Amend the AD in place so the spine matches the shipped code.

## Acceptance

- [x] AD-15 amended in place (ID stable): dispatch is by the stack's template family; the cell key
      stays `(pack, language)`; each cell reports its resolved stack.
- [x] `work-split-view.md` R5 row reworded to match.
- [x] Spine lint clean.
      `Verify: uv run .agents/skills/bmad-architecture/scripts/lint_spine.py --workspace _bmad-output/initiative-universal-mcu-env/architecture-universal-mcu-env`

## Evidence

2026-10-16: documentation-only amendment; no invariant semantics changed (the load-bearing half —
"each stack registers its build + fit check" — is unchanged and is what R5 implements). The
reviewer gate was scaled to the deterministic lint with the subagent lenses skipped for a wording
fix; recorded in the spine memlog.

Source: `tickets/task-011-verify-axis/ticket.md` §Evidence ("Refinement to AD-15").
