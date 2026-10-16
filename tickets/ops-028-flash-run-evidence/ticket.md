---
id: ops-028
title: "Record a flash-run evidence artifact for the V1 packs"
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

# Record a flash-run evidence artifact for the V1 packs

> `ops-task`; no `parent:`.

## Work

`docs/e2e-evidence.md` is **build-only** ("E2E build evidence (req-009) — 10/10
cells green"), and the live flash/run step is "bench-manual, not automated into
the harness" (`tickets/req-022-esp32-family/ticket.md:92`). V1's done-when names
**flash-run**, so the proof needs a durable artifact (the way `ops-023` did for
build).

- Add `docs/flash-run-evidence.md` (or a clearly-marked section of
  `docs/e2e-evidence.md`) with, per V1 pack: board, probe id, openocd target,
  `flash` verdict, and the run proof (LED / RTT / UART per the pack ritual).
- Source F411RE + H755ZI-Q from `tickets/ops-020-clean-test-doc/ticket.md` /
  `docs/vscode-debug.md:156-161`; WL55JC from `ops-027`; Rust, if gated in, from
  `spike-008`.

## Done-when

A committed evidence artifact shows flash-run proof for every V1 pack in scope,
and `make test` is green.
