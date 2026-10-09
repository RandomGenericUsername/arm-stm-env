# Design

## Context

See proposal.md. Spine AD-2/AD-3/AD-9/AD-10; port ABCs from req-005; spike-001 corrected targets as vectors.

## Goals / Non-Goals

**Goals:** OpenOCD adapter proven against faked transcripts; probe-rs skeleton with mapped results; port conformance green.

**Non-Goals:** live probe runs, images, other backends.

## Decisions

- **Subprocess boundary**: adapters shell `openocd`/`probe-rs` binaries via a runner seam (injectable fake in tests, real `subprocess` in prod). No binary required at test time.
- **Transcript fixtures**: captured-style OpenOCD outputs (verify OK, dual-core session lines) authored from documented formats, marked as fixtures — never presented as live runs.
- **probe-rs via `--chip` + JSON-ish output parsing**; live proof deferred (OPEN), mapping code reviewed against probe-rs docs.

## Risks / Trade-offs

- [Risk] Faked transcripts drift from real tool output → Mitigation: fixtures cite doc sources; HW smoke (later, with probe) replays them against live runs.
- [Risk] probe-rs output format changes → Mitigation: version pinned per spike-003 (v0.32.0); parser isolated in one module.

## Verification plan

- `pytest` adapter suite green; no-board-names grep empty; cross-adapter comparability green; suite contains zero live-probe claims.
- `openspec validate req-006-probe-adapters` green.

## Open Questions

None.
