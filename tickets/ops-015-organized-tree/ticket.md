---
id: ops-015
title: "Organize generated project tree (probe/ + build/<core>/)"
kind: ops-task
status: done
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/ops-015/
branch: ticket/ops-015-organized-tree
---

# Organize generated project tree (probe/ + build/<core>/)

> `ops-task`; no `parent:`.

## Work

Generated projects were flat — `openocd.cfg` and the `.elf/.hex/.bin` sat at the
root next to sources. Group generated + tool files into homes (nothing at root):

```
<project>/
  src/  config/  linker/  vendor/   # unchanged
  probe/openocd.cfg                 # moved from root
  build/<core>/                     # .o .map .elf .hex .bin (all outputs)
```

- `engine/templates/renderer.py`: `openocd.cfg` → `probe/openocd.cfg`; Makefile
  per-core targets emit `build/<core>/<TARGET>.{elf,hex,bin,map}`; `clean` wipes
  `build/<core>/`.
- `engine/verify/e2e.py`: sizes `build/<core>/<id>-<core>.elf`.
- Tests (`test_cells`, `test_renderer`) + README + `docs/flash-stm32-linux.md`
  updated to `build/<core>/…` and `probe/openocd.cfg`.

Not migrated: pre-existing projects keep the old layout (re-`create` for the new).

## Evidence

Live 2026-10-14 (F411RE/C), `mu create` → `mu build`:

```
<project>/{Makefile, config/, linker/, src/, Startup/, vendor/, probe/openocd.cfg, build/M4/}
root *.elf/*.hex/*.bin → none
build/M4/ → main-M4.o startup-M4.o system-M4.o stm32f411re-M4.{elf,hex,bin,map}
```

Verify: `mu build` → artifact at `build/M4/stm32f411re-M4.elf`; root has none.
`mu flash … --files build/M4/stm32f411re-M4.elf` → `** Verified OK **`. `make test` → 238 passed.

## Done-when

A fresh project has no generated artifacts at the root; outputs live in
`build/<core>/` and probe config in `probe/`; build + flash still green.
