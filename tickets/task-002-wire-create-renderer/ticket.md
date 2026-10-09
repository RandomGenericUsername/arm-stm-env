---
id: task-002
title: "Wire create renderer"
kind: task
status: done
parent: epic-001
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/task-002/
branch: ticket/task-002-wire-create-renderer
---

# Wire create renderer

## Parent

`epic-001` — lane inherited from parent (direct execution).

## Work

Wire `stm create --mcu-config <pack-id-or-file> [--lang c|cpp|rust, default c]
--name <project> [--out-dir]` to loader + `render()` into `<out-dir>/<name>`,
printing the created file list + next steps (build command).

- `--mcu-config` accepts a file path or a shipped pack id (`packs/<id>.yaml`).
- Individual-flags path (`--mcu`/`--device`/`--vid`/`--pid`/`--serial` without
  `--mcu-config`) exits 2 with a clear "not wired yet (follow-up)" message;
  no flags schema invented. Follow-up: design the individual-flags surface
  (e.g. `--flash-origin` et al.) in a later ticket.
- Invalid pack id exits non-zero and names the known pack candidates.
- `create --dry-run` prints the render plan and writes nothing.

## Done-when

`stm create` renders an F411RE C project to a tmp dir (non-empty file list, no
placeholders); flags-only exits 2; invalid pack id exits non-zero naming
candidates. `Verify: uv run pytest -q` (159 passed) + `uv run stm create
--mcu-config stm32f411re --name demo --out-dir /tmp/x`.
