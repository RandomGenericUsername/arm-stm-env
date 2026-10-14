---
id: ops-009
title: "Installable stm CLI (make install / uninstall)"
kind: ops-task
status: in-progress
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/ops-009/
branch: ticket/ops-009-install-cli
---

# Installable stm CLI (make install / uninstall)

> `ops-task` MAY be read as `chore`; the file declares `kind: ops-task`. No `parent:`.

## Work

Add `make install` / `make uninstall` so the `stm` CLI installs globally
without a venv (`uv tool install --editable .`), and document it in the README.
Editable is required (not optional): the CLI resolves `packs/` + `engine/`
relative to the checkout (`engine/cli/shim.py`: `engine_root()` → `repo_root()`
→ `packs_dir()`), so a non-editable install puts `engine` in site-packages and
`packs/` goes missing. Editable also tracks local edits live.

Evidence: `uv tool install --editable .` → `Installed 1 executable: stm`; then
`stm --help` works with no venv and
`stm create --mcu-config stm32f411re --lang c --name probe --out-dir /tmp/opencode --dry-run`
resolves the pack (verified 2026-10-14, uv 0.9.22).

## Done-when

`make install` yields a working `stm` on PATH (no venv, pack resolution OK) and
`make uninstall` removes it; README documents both.
