---
id: ops-028
title: "Record a flash-run evidence artifact for the V1 packs"
kind: ops-task
status: done
size: S
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/ops-028/
branch: ticket/ops-028-flash-run-evidence
---

# Record a flash-run evidence artifact for the V1 packs

> `ops-task`; no `parent:`.

## Work

`docs/e2e-evidence.md` is **build-only**, and the live flash/run step was
"bench-manual, not automated into the harness" (`tickets/req-022-esp32-family/ticket.md:92`).
Added `docs/flash-run-evidence.md` — the durable flash/run half of the V1 proof.

- Per-pack table (board, probe, openocd target, flash verdict, run proof, date)
  for all three V1 packs, plus the reproduce commands and the probe-readback method.
- Sources: F411RE + H755ZI-Q from `ops-020` / `docs/vscode-debug.md` §9; WL55JC
  from `ops-027`.
- Scope note: Rust is build-parity for V1 (`spike-008`).

## Done-when

A committed evidence artifact shows flash-run proof for every V1 pack in scope,
and `make test` is green. ✅ (`docs/flash-run-evidence.md`; 355 passed.)
