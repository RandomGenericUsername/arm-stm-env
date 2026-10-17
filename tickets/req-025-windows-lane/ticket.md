---
id: req-025
title: "Windows native lane"
kind: requirement
status: proposed
size: L
lane: bmad-advisory
parent: epic-002
links:
  openspec: none
  bmad: []
worktree: none
branch: none
---

# Windows native lane

## Requirement

Windows host support. Deferred, not designed out (`spec-universal-mcu-env.md:57`); the
container + thin-shim design keeps it possible. A WSL2 path is the likely first step.

## Acceptance

- [ ] A Windows host runs `create` → `build` → `flash` (native, or via a documented
      WSL2 path), **or** a recorded deferral with the reason and the trigger to revisit.

## Context

- `spec` non-goal today (`spec-universal-mcu-env.md:62`); `work-split-view.md:48` parks it.
- The shim is Python; the images are `linux/amd64`-pinned (`images/cpp.Dockerfile:5`).
  Native arm64/Windows needs arch-aware Dockerfiles (not yet supported).
