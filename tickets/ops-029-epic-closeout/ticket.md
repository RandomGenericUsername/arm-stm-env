---
id: ops-029
title: "epic-001 closeout: reconcile children, add the rollup checklist, flip to done"
kind: ops-task
status: done
size: S
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/ops-029/
branch: ticket/ops-029-epic-closeout
---

# epic-001 closeout: reconcile children, add the rollup checklist, flip to done

> `ops-task`; no `parent:`.

## Work

1. Reconciled the children list. `epic.md` declared **23** but **29** tickets
   declared `parent: epic-001`; it also listed `req-001`/`req-002`, which carried
   `parent: ""`. The list is now the full **31** children (the 29 + req-001 +
   req-002, the latter two given `parent: epic-001`).
2. Added the `## Children` checklist (one `- [x] <id> — <title>` per child), so
   the `in-progress → done` gate passes (`tickets/LIFECYCLE.md:12`: checklist
   count == `children:` count).
3. Normalised the status: `decomposed` (not a lifecycle state, `LIFECYCLE.md:9`)
   → `done`.
4. Updated the INDEX rollup line and the nested children list (31) in the same
   commit (`LIFECYCLE.md:3`); the section header `## Active epics` → `## Epics`.

## Evidence

```
# children reconcile: 23 -> 31, all done
$ grep -c '^  - ' tickets/epic-001-universal-framework/epic.md        # frontmatter children
31
$ grep -c '^- \[x\] ' tickets/epic-001-universal-framework/epic.md    # checklist (gate)
31
$ rg -l '^parent: epic-001' tickets/*/ticket.md | wc -l               # declaring parent
31

# done-when holds
- create->build: ops-023 (docs/e2e-evidence.md, 10/10)
- flash->run per pack (clean machine): docs/flash-run-evidence.md
  (F411RE + H755ZI-Q = ops-020; WL55JC = ops-027)
- Rust = build-parity (spike-008 decision)
```

## Done-when

`tickets/epic-001-universal-framework/epic.md` children list == the actual
children, checklist count == children count, status `done`, and INDEX agrees. ✅
