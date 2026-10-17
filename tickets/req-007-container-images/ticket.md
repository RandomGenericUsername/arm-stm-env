---
id: req-007
title: "Container images per toolchain + caches"
kind: requirement
status: done
size: M
lane: bmad-advisory
links:
  openspec: none
  bmad:
    - _bmad-output/initiative-universal-mcu-env/architecture-universal-mcu-env/architecture-universal-mcu-env.md
worktree: ""
branch: ""
parent: epic-001
children: []
---

## User value

cpp/rust images with pinned toolchains, core-owned cache keys, language→image registry lookup.

## Acceptance

- [ ] cpp and rust images build pinned; cache invalidates on image bump. `Verify: <defined at build>`
- [x] CubeCLT-vs-GCC decision recorded; ST OpenOCD fork pinned. `Verify: rg -n "CubeCLT|ARM_GCC_VERSION|OPENOCD_SHA" images/cpp.Dockerfile` → vanilla 15.3.rel2 + OpenOCD fork `c8d973b`, no CubeCLT. Decision: `tickets/req-027-cubeclt-verdict/ticket.md` (excluded — practical, SLA0048 permits redistribution with conditions), recorded in `images/README.md`.

## Evidence

Work-split view story 5; governed by AD-7, AD-8. Needs spike-003 output.
