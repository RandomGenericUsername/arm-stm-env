---
id: epic-002
title: "Post-V1 roadmap"
kind: epic
status: proposed
lane: bmad-advisory
children:
  - req-024
  - req-025
  - req-026
  - req-027
done-when: "Every post-V1 track is shipped or explicitly declined with a recorded reason."
links:
  openspec: none
  bmad:
    - _bmad-output/initiative-universal-mcu-env/brief-universal-mcu-env/brief-universal-mcu-env.md
    - _bmad-output/initiative-universal-mcu-env/spec-universal-mcu-env/spec-universal-mcu-env.md
worktree: ""
branch: ""
---

# Post-V1 roadmap

## Goal

Track the work explicitly out of V1 scope (epic-001 was closed 2026-10-16): the C/C++
dependency story, a Windows lane, the WL55 CM0+ bring-up, and the CubeCLT decision.
One home so nothing is a floating "known open thread".

## Children

- [ ] `req-024` — C/C++ dependency integration (Conan 2 / CPM) (proposed)
- [ ] `req-025` — Windows native lane (proposed)
- [ ] `req-026` — WL55JC CM0+ dual-core bring-up (proposed)
- [x] `req-027` — STM32CubeCLT verdict (done 2026-10-16 — exclude from images, optional host tool)

## Rollup

Done iff every child is done AND the done-when holds. Scope is broad → BMAD advisory
before execution (lane `bmad-advisory`); only `bmad`/`bmad-build` are installed.

## Not children (parked non-goals)

Pack validator/generator tooling, cloud builds, team/enterprise, IDE plugins
(`spec-universal-mcu-env.md:62`, `work-split-view.md:46-48`). Small housekeeping items
are standalone `ops` tasks (`ops-032`…`ops-034`), not epic children.
