---
id: req-027
title: "STM32CubeCLT verdict"
kind: requirement
status: proposed
size: S
lane: bmad-advisory
parent: epic-002
links:
  openspec: none
  bmad: []
worktree: none
branch: none
---

# STM32CubeCLT verdict

## Requirement

Settle whether STM32CubeCLT belongs in the `cpp` image: its use/redistribution rights,
and whether it adds anything over the pinned vanilla ARM GNU GCC + ST OpenOCD fork.
Verdict include / optional / exclude, with evidence.

## Context

- `spike-003`: vanilla-GCC verdict; CubeCLT gated on a license proof.
- `HANDOFF.md:42-45` lists "CubeCLT verdict (st.com unreachable)" as an open thread.
- The repo depends on nothing from CubeCLT today (`images/cpp.Dockerfile`).

## Acceptance

- [ ] A verdict recorded with evidence (license clause + what each component adds), and
      the open thread in `HANDOFF.md` closed.
