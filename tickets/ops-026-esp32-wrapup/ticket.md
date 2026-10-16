---
id: ops-026
title: "ESP32-CAM wrap-up: record the final state and prune merged branches"
kind: ops-task
status: done
size: XS
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/ops-026/
branch: ticket/ops-026-esp32-wrapup
---

# ESP32-CAM wrap-up

## Work

Record where the ESP32-CAM support deliberately stops (`req-022` §Final state), so the next person
sees the supported path and the out-of-scope items in one place, and prune the merged
`ticket/*` branches that this session left on `origin`.

## Done-when

`req-022` states the final state; `main` is clean, committed and pushed; merged branches are gone;
`make test` green.

## Evidence

2026-10-16: `req-022` §Final state records the supported chain (create → build → flash → run →
monitor, plus the VS Code tasks) and the deliberate stop at JTAG debugging (classic ESP32 has no
USB-serial-JTAG; its JTAG pins are the microSD lines here). Remote branches merged into `main` are
deleted; `git branch -r --merged origin/main` lists only `main`.
