---
id: ops-012
title: "create: rename output flag to --path"
kind: ops-task
status: done
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/ops-012/
branch: ticket/ops-012-create-path-flag
---

# create: rename output flag to --path

> `ops-task`; no `parent:`.

## Work

Rename `mu create`'s `--out-dir` flag to `--path`. Semantics are unchanged
(and already correct): the project renders to `<path>/<name>`, defaulting to the
current directory when `--path` is omitted.

- `engine/cli/main.py`: `--out-dir` → `--path`, `args.out_dir` → `args.path`.
- CLI tests + README + `docs/flash-stm32-linux.md` command examples.

Internal function params (`render(..., out_dir)`) are not the CLI flag and stay.

Evidence: behavior verified 2026-10-14 — no flag → `demo/` in cwd;
`--out-dir <x>` → `<x>/demo/` (`engine/cli/main.py:106,179`).

## Done-when

`mu create --name demo --mcu-config stm32f411re` → `./demo`; with
`--path <dir>` → `<dir>/demo`; `--out-dir` now errors as unrecognized; suite green.
