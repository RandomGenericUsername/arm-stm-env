---
id: ops-007
title: "Make commands for fresh-clone rebuild"
kind: ops-task
status: done
trivial: false
blast-radius: "Root Makefile/shop commands; wrong defaults waste hours of image builds. No engine behavior changes."
links:
  openspec: []
  bmad: []
worktree: .worktrees/ops-007/
branch: ticket/ops-007-make-commands
---

## What

Root `Makefile` so a fresh clone rebuilds everything with documented commands: engine tests/sync, image builds (platform-aware), smoke tests, digest recording, registry push (parameterized, GHCR default).

## Done-check

- [x] `make help` lists targets. `Verify: make help`
- [x] `make test` green. `Verify: make test`
- [x] `make -n image-cpp image-rust` prints correct build commands without building. `Verify: make -n ...`
- [x] Fresh-clone path documented (README section or Makefile header). `Verify: read it`
