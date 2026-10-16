---
id: ops-029
title: "epic-001 closeout: reconcile children, add the rollup checklist, flip to done"
kind: ops-task
status: proposed
size: S
lane: direct
links:
  openspec: none
  bmad: none
worktree: none
branch: none
---

# epic-001 closeout: reconcile children, add the rollup checklist, flip to done

> `ops-task`; no `parent:`.

## Work

The V1 epic is still open and its rollup does not hold. Concretely:

1. **Reconcile the children list (drift).** `tickets/epic-001-universal-framework/epic.md`
   declares **23** children, but **29** tickets declare `parent: epic-001`. The
   list is missing `req-012`, `req-014`–`req-020` (8 items) and wrongly lists
   `req-001`/`req-002`, which declare no parent.
   Evidence: `grep -rl '^parent: epic-001' tickets/*/ticket.md` →
   29 dirs; `sed -n '/^children:/,/^done-when:/p' tickets/epic-001-universal-framework/epic.md` → 23 ids.
2. **Add the rollup checklist** — one `- [x] <id> — <title>` per child — so the
   `in-progress → done` gate passes (`tickets/LIFECYCLE.md:12`: checklist count
   must equal `children:` count). The epic currently has **0** such lines.
3. **Normalise the status.** The epic is `decomposed`, which is not a lifecycle
   state (`tickets/LIFECYCLE.md:9`: `proposed → in-progress → done`).
4. **Flip to `done` only after** `ops-027`, `ops-028`, `ops-030` close and the
   done-when (clean-machine create-build-flash-run per pack) actually holds —
   not before. (`spike-008` is resolved: Rust is build-parity for V1.)
5. **Update the INDEX rollup line in the same commit** (`tickets/LIFECYCLE.md:3`).

## Done-when

`tickets/epic-001-universal-framework/epic.md` children list == the actual
children, checklist count == children count, status `done`, and INDEX agrees.
