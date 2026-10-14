---
id: ops-016
title: "Generated projects ship a .gitignore (build/, .mu/)"
kind: ops-task
status: done
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/ops-016/
branch: ticket/ops-016-project-gitignore
---

# Generated projects ship a .gitignore (build/, .mu/)

> `ops-task`; no `parent:`.

## Work

`mu create` git-inits the project but wrote no `.gitignore`, so `build/`
artifacts and `.mu/` logs were easy to commit by accident. Render a
`.gitignore` (`build/`, `.mu/`) with every project.

- `engine/templates/renderer.py`: `_GITIGNORE` written by `render()`.
- `engine/templates/tests/test_cells.py`: expected files include `.gitignore`.

Evidence: `mu create` → `cat <proj>/.gitignore` shows `build/` + `.mu/`;
`git check-ignore -v build/x.elf .mu/logs/x.log` matches both rules.

## Done-when

Every generated project has a `.gitignore` ignoring `build/` and `.mu/`;
`make test` green (252 passed).
