---
id: ops-013
title: "create: git-init a fresh project dir before vendoring"
kind: ops-task
status: done
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/ops-013/
branch: ticket/ops-013-create-git-init
---

# create: git-init a fresh project dir before vendoring

> `ops-task`; no `parent:`.

## Work

`mu create` failed when the target dir was not already a git repo:
`vendoring: out-dir … is not inside a git work tree; git init the project dir
first`. Now `vendor()` runs `git init` in the project dir when it is not already
inside a work tree (idempotent — a monorepo is left alone), then adds the pinned
submodules. A failed `git init` raises a loud `VendorError`.

- `engine/templates/vendoring.py`: add `_ensure_repo()`, call it in `vendor()`.
- `engine/templates/tests/test_vendoring.py`: `FakeGit` gains an `inside` flag;
  non-repo case now asserts `git init`; add init-failure test.

Evidence: 2026-10-14 live —
`mu create --mcu-config stm32f411re --lang c --name demo --path /tmp/opencode/fresh`
succeeded into a fresh non-repo path: auto `.git`, `git rev-parse
--is-inside-work-tree` → `true`, submodules pinned (`vendor/CMSIS (5.9.0)`,
`vendor/cmsis-device-stm32f411re (v2.6.9)`).

## Done-when

`mu create` succeeds in a new/empty directory with no manual `git init`;
`make test` green (237 passed).
