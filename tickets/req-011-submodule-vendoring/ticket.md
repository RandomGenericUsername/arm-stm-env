---
id: req-011
title: "Vendor CMSIS submodules into created projects"
kind: requirement
status: done
size: M
lane: openspec-single
links:
  openspec:
    - req-011-submodule-vendoring
  bmad:
    - _bmad-output/initiative-universal-mcu-env/architecture-universal-mcu-env/architecture-universal-mcu-env.md
worktree: .worktrees/req-011/
branch: ticket/req-011-submodule-vendoring
parent: epic-001
children: []
---

## User value

Fresh `create`d C projects build out of the box: `create` initializes pinned CMSIS submodules (core + device family) so vendor startup/headers exist — no hand-placed stubs, no per-project network fetch.

## Acceptance

- [ ] `create` on all 3 packs yields projects whose vendor paths resolve (submodule present + pinned). `Verify: <defined at build>`
- [ ] Upstream remotes + pins evidenced (reachable URLs, recorded SHAs). `Verify: <defined at build>`
- [ ] Offline second `create` (submodule cache) or clear online requirement documented. `Verify: <defined at build>`

## Evidence

Spike-002 vendoring pick; sibling fetch paths (svn CMSIS + curl cmsis_device_*) as source evidence for WHAT to vendor; user-approved order (2026-10-13 session).
