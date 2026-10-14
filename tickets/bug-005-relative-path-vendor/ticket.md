---
id: bug-005
title: "create fails with a relative project dir (git -C doubles the path)"
kind: bug
status: done
lane: direct
severity: S1
links:
  openspec: []
  bmad: []
worktree: .worktrees/bug-005/
branch: ticket/bug-005-relative-path-vendor
repro: "mkdir /tmp/x && cd /tmp/x && mu create --mcu-config stm32f411re --lang c --name project"
observed: "mu: error: vendoring: `git -C project config -f project/.gitmodules submodule.vendor/CMSIS.path vendor/CMSIS` failed in project (cannot record the pin): fatal: cannot change to 'project': No such file or directory"
expected: "project/ is created with the pinned submodules vendored"
---

# create fails with a relative project dir (git -C doubles the path)

## Repro

```sh
mkdir -p /tmp/x && cd /tmp/x
mu create --mcu-config stm32f411re --lang c --name project   # default --path . → relative "project"
```

## Observed

```
mu: error: vendoring: `git -C project config -f project/.gitmodules submodule.vendor/CMSIS.path vendor/CMSIS` failed in project (cannot record the pin): fatal: cannot change to 'project': No such file or directory
```

## Expected

`project/` renders with `vendor/CMSIS` + `vendor/cmsis-device-…` pinned; exit 0.

## Fix notes

`vendor()` passed the project dir through unresolved. ops-014 introduced
`git -C <project_dir> …` while `_run_git` also runs with `cwd=<project_dir>`; for
a **relative** dir the `-C` looked up `<dir>/<dir>`. Tests only used absolute
`tmp_path`, so they missed it. Fix: resolve the project dir to absolute at the
top of `vendor()` (`engine/templates/vendoring.py`). Regression:
`test_vendor_relative_project_dir_uses_absolute_paths`. Live 2026-10-14:
relative `mu create --name project` → `project/` with both submodules pinned;
`make test` → 238 passed.
