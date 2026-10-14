---
id: ops-010
title: "Rename the CLI command stm -> mu (device-agnostic)"
kind: ops-task
status: in-progress
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/ops-010/
branch: ticket/ops-010-rename-cli-mu
---

# Rename the CLI command stm -> mu (device-agnostic)

> `ops-task`; the file declares `kind: ops-task`. No `parent:`.

## Work

The tool is device-agnostic, so the `stm` command name is a misnomer. Rename the
console script and every **live** reference to `mu`:

- `pyproject.toml` console script → `mu`.
- `engine/cli/main.py`: argparse `prog`, `stm: error:` prefixes, next-step hints,
  docstrings, and the project log dir `.stm/` → `.mu/`.
- `engine/cli/shim.py` docstring; `README.md`, `Makefile`, `docs/*`,
  `HANDOFF.md`; CLI tests asserting the command token.

Unchanged on purpose: `stm32*` device names and the `arm-stm-env` repo name.
Historical tickets and OpenSpec changes keep the old token — they are records.

Evidence: `rg -nP "(?<![\w-])stm(?![\w-])"` enumerates the live spots (excludes
`stm32*` and `arm-stm-env`). Verify after: `uv run mu --help` works, `uv run stm`
does not, `make install` installs `mu`.

## Done-when

`make install` yields a working `mu` (and no `stm`); `mu --help` and
`mu create --mcu-config stm32f411re --dry-run` work; full suite green.
