---
id: req-020
title: "Auto-detect a single attached probe (no --vid/--pid needed)"
kind: requirement
status: done
size: S
lane: openspec-single
links:
  openspec:
    - openspec/changes/req-020-probe-autodetect
  bmad: []
worktree: .worktrees/req-020/
branch: ticket/req-020-probe-autodetect
parent: epic-001
children: []
---

# Auto-detect a single attached probe (no --vid/--pid needed)

## User value

With one board plugged in, `mu dev` / `mu flash` just work — no `--vid/--pid`.
A selector is needed only when several probes are attached.

## Acceptance

- [x] No selector + one probe → auto-detected. `Verify: pytest -k binding`
- [x] None → "no debug probe found"; several → error naming them. `Verify: pytest -q`
- [x] Live: `mu dev` (no selector) resolved the H755 node. `Verify: mu dev … --dry-run`
- [x] `make test` + `openspec validate req-020-probe-autodetect` green (260 passed).

## Evidence

2026-10-14: `mu dev --project-dir ~/Desktop/h755-clean --dry-run` (no selector,
one probe) → `--device /dev/bus/usb/003/045:/dev/bus/usb/003/045`. Probe VID list
in the shim (host layer, AD-9); pack-declared VIDs are a follow-up.
