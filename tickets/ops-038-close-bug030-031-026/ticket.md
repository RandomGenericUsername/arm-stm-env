---
id: ops-038
title: "Close bug-030/bug-031/req-026 (fixes merged + verified); recount epic-002"
kind: ops-task
status: done
size: XS
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/ops-038/
branch: ticket/ops-038-close-bug030-031-026
---

# Close bug-030/bug-031/req-026 (fixes merged + verified); recount epic-002

> `ops-task`; no `parent:`.

## Work

Verified and merged the `bug-030` + `bug-031` worker run, then closed the tickets.

- **bug-030** (S2): released-sibling packs now emit a `make debug-m0plus` target and
  a README section — attach-only, `probe/dual-core.cfg` sourced **before** the
  target, no reset (preserving `bug-024`'s rule). Verified on the board: `pc` inside
  the M0+ `main` loop (3/8 runs; the other 5 were `bug-027`).
- **bug-031** (S3): `probe/cpu2-boot.cfg` is **no longer emitted** (removed from the
  render path and from `launch.json` configFiles). The measurement is truthful again:
  C2BOOT was set in exactly the 6/10 runs where the CM0+ counter advanced.
- **req-026** acceptance met → `done` (CM0+ boots+runs; generated attach path exists).
- `epic-002` rollup recounted from files: **2/4** (`req-026`, `req-027` done).
- `bug-028` remains `done` but its artifact is superseded — the file it fixed is gone.

## Evidence

`uv run python -m pytest engine/ -q` → **360 passed** (was 357). Bench: `make flash`
2/2 `Verified OK`, then `make debug-m0plus` → `pc (/32): 0x0802017c`; 10 ×
(`reset run`, C2BOOT, counter) → C2BOOT set in exactly the runs where the counter moved.

## Done-when

`bug-030`, `bug-031`, `req-026` `done`; `epic-002` recount correct; INDEX agrees. ✅