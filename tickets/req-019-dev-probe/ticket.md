---
id: req-019
title: "mu dev accepts probe selectors (dev container gets the probe)"
kind: requirement
status: done
size: S
lane: openspec-single
links:
  openspec:
    - openspec/changes/req-019-dev-probe
  bmad: []
worktree: .worktrees/req-019/
branch: ticket/req-019-dev-probe
parent: epic-001
children: []
---

# mu dev accepts probe selectors (dev container gets the probe)

## User value

`mu dev --vid/--pid/--serial` hands the probe's USB node to the dev container —
the same automatic resolution `mu flash` uses. No more hand-rolled `docker run
--device …`, manual node lookups, or stale-node surprises.

## Acceptance

- [x] `dev` accepts the probe selectors; container argv gets `--device <node>:<node>`. `Verify: pytest -k dev`
- [x] Live dry-run resolves the H755 node. `Verify: mu dev --vid 0483 --pid 3754 --dry-run`
- [x] `make test` + `openspec validate req-019-dev-probe` green (258 passed).

## Evidence

`mu flash` already resolves the probe (req-012); `dev` lacked the flags. Live
2026-10-14: `mu dev --vid 0483 --pid 3754 --dry-run` →
`--device /dev/bus/usb/003/045:/dev/bus/usb/003/045`. Mid-session replug remains
a follow-up.
