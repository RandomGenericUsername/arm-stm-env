---
id: req-010
title: "Streamed flash/debug tool output (+ --verbose)"
kind: requirement
status: done
size: S
lane: openspec-single
links:
  openspec: []
  bmad: []
worktree: ""
branch: ""
parent: epic-001
children: []
---

## User value

During `flash`/`debug`, the user watches the probe tool's output as it moves — not just the final verdict line. Opt-in `--verbose` dumps the full raw log; default stays verdict-only.

## Acceptance

- [ ] Tool subprocess streams output live during flash/debug; verdict line closes each run. `Verify: <defined at build>`
- [ ] `--verbose` preserves the complete raw log (also written to a per-run log file). `Verify: <defined at build>`
- [ ] Non-verbose output is progress + verdict only (no firehose). `Verify: <defined at build>`

## Evidence

User requirement (2026-10-13 session): "want this to be streamed ... definitely a behavior that must be written somewhere as requirement". Proof wiring (task-005) covers result data only, not live output.
