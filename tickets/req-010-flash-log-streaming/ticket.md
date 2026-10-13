---
id: req-010
title: "Streamed flash/debug tool output (+ --verbose)"
kind: requirement
status: triaged
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

- [ ] Tool subprocess streams stdout/stderr live to the terminal during flash/debug. `Verify: <defined at build>`
- [ ] `--verbose` preserves the complete raw log alongside the verdict. `Verify: <defined at build>`
- [ ] Default (non-verbose) output unchanged (verdict line only). `Verify: <defined at build>`

## Evidence

User requirement (2026-10-13 session): "want this to be streamed ... definitely a behavior that must be written somewhere as requirement". Proof wiring (task-005) covers result data only, not live output.
