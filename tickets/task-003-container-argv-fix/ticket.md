---
id: task-003
title: "Container argv invokes build tool, not stm"
kind: task
status: done
parent: epic-001
lane: direct
links:
  openspec: []
  bmad: []
worktree: .worktrees/task-003/
branch: ticket/task-003-container-argv-fix
---

## What

`stm build` fails in-container: shim renders `docker run … stm build …` but images contain toolchains only, no `stm`. Fix: container side invokes the build tool (`make`/`cargo`) with the right args; host-side `stm` stays the entry point.

## Done-check

- [x] Container argv for build renders `make`/`cargo`, never bare `stm`. `Verify: stm build --dry-run`
- [x] `--mode local` path unchanged (bare `stm`). `Verify: existing tests`
- [x] Full suite green. `Verify: pytest engine/`
- [x] Local dispatch implemented (no re-exec); backend registry keeps CLI backend-free. `Verify: suite + gate`
- [x] Live proof: fresh images run engine; rendered demo compiles to ELF via fixed path. `Verify: commands in merge message`

## Follow-ups (out of scope, recorded)

- Wire CMSIS-submodule vendoring into `create` (stub interim documented in images/README).
- `--probe` backend selection flag (registry ready: `get_adapter(name)`).
- Flash proof-rung wiring (transcript → proof struct; verdict currently pieces-only).
