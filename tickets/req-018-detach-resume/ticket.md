---
id: req-018
title: "Keep firmware running after debug: resume-on-detach config"
kind: requirement
status: done
size: S
lane: openspec-single
links:
  openspec:
    - openspec/changes/req-018-detach-resume
  bmad: []
worktree: .worktrees/req-018/
branch: ticket/req-018-detach-resume
parent: epic-001
children: []
---

# Keep firmware running after debug: resume-on-detach config

## User value

Ending a debug session no longer freezes the board (blink stuck on/off): the
generated `probe/resume-on-detach.cfg` resumes the target when the session ends
via detach.

## Acceptance

- [x] `create --vscode` emits `probe/resume-on-detach.cfg` and lists it in `configFiles`. `Verify: pytest -k vscode`
- [x] Live: `curstate` = `running` after detach with the cfg. `Verify: openocd telnet curstate`
- [x] `make test` + `openspec validate req-018-detach-resume` green (257 passed).

## Evidence

cortex-debug #894 (stock OpenOCD leaves Cortex-M halted on detach; no client
fix); live probe 2026-10-14: `stm32f4x.cpu curstate` = `running` after
resume-before-detach / `halted` without. Plain "Stop" (disconnect, no detach)
remains halted — upstream OpenOCD behaviour, documented in the generated cfg.
