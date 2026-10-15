---
id: ops-021
title: "Generated project README.md (each project documents its own flow)"
kind: ops-task
status: done
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/ops-021/
branch: ticket/ops-021-project-readme
---

# Generated project README.md

> `ops-task`; no `parent:`.

## Work

Generated projects carried no README (ops-019 noted this as the remaining doc
gap). `render()` now writes a self-contained `README.md`, built from the pack
model (not a static file): device + cores, the LED example and which core drives
it, the sibling `counter` note, the make targets (per core), the VS Code tasks +
launch configs + keys, expected behaviour (blink rate, step over the delay),
probe-by-serial, and a troubleshooting table.

Rust projects get the cargo-oriented variant (no make targets, and the note that
the VS Code integration is C/C++-first).

## Done-when

`mu create` writes `README.md` for c/cpp/rust, reflecting the pack (cores, LED
pin, dual-core or not).

## Evidence

- `_readme(stm32h755, "c")` → device, `M7`/`M4`, `PE1`, `make flash-M4`,
  `Debug M7+M4 (OpenOCD)`, `MU_PROBE_SERIAL`.
- `_readme(stm32f411re, "rust")` → `mu build --project-dir .`, no `make flash`.
- Tests: `test_renderer_writes_project_readme`,
  `test_renderer_readme_rust_has_no_make_targets`, `test_cells` file list.
- `uv run pytest engine -q` → 266 passed.
