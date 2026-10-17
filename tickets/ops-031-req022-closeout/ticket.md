---
id: ops-031
title: "Close req-022 (ESP32 family) and mark spike-007 consumed"
kind: ops-task
status: done
size: XS
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/epic-002/
branch: ticket/epic-002-post-v1-plan
---

# Close req-022 (ESP32 family) and mark spike-007 consumed

> `ops-task`; no `parent:`.

## Work

`req-022` was left `proposed` while all four children (`task-013`…`task-016`) are
`done` and the live proof is recorded (`ops-024`, `ops-026`) — the same drift class
`epic-001` had (closed by `ops-029`).

- Flipped `req-022` `proposed` → `done` (its acceptance checklist was already fully
  ticked, satisfying the requirement done-gate, `LIFECYCLE.md:20`).
- Marked `spike-007` `reported` → `consumed` (its findings live in `req-022` and the
  ESP32 family shipped as E1–E4).
- Updated both INDEX lines.

## Evidence

```
$ grep -m1 '^status:' tickets/req-022-esp32-family/ticket.md     # status: done
$ grep -c '^\- \[x\]' tickets/req-022-esp32-family/ticket.md     # acceptance all ticked
$ grep -m1 '^status:' tickets/spike-007-esp32-cam/ticket.md      # status: consumed
$ # children statuses: task-013..016 all 'done'
```

## Done-when

`req-022` status `done`, `spike-007` status `consumed`, INDEX agrees. ✅
