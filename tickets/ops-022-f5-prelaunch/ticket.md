---
id: ops-022
title: "F5 = build + flash + debug (preLaunchTask in the generated launch configs)"
kind: ops-task
status: done
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/ops-022/
branch: ticket/ops-022-f5-prelaunch
---

# F5 does the work

> `ops-task`; no `parent:`.

## Work

`bug-024` made the WL55's configs attach-only (no reset), so F5 stopped
programming the target — the user had to Flash first. Wire the existing tasks
into the launch configs with cortex-debug's `preLaunchTask`:

- **primary core**: `Flash` for attach-only packs (its reset also releases the
  sibling), `Build` for launch packs (they already flash via gdb `load`);
- **siblings**: `Build` only — they are also the compound's chained children, and
  a chained child runs its own `preLaunchTask`, so a `Flash` there would
  re-program the target and disturb the parent session.

## Done-when

`F5` on the primary config builds, flashes, and starts the session; the compound
builds/flashes once (via the primary) and attaches both cores.

## Evidence

- Generated: WL55 → M4 `Flash`, M0+ `Build`, compound `Flash`; H755/F411 → `Build`.
- The underlying commands are verified live (`bug-024`): `make flash` →
  `Verified OK` ×2, then the M4 and M0+ attach flows both step.
- `uv run pytest engine -q` → 276 passed.
