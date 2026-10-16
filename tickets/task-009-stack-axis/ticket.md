---
id: task-009
title: "R3 — pack-declared stacks map + toolchain registry"
kind: task
status: done
lane: inherits
parent: req-021
links:
  openspec: none
  bmad: none
worktree: .worktrees/task-009/
branch: ticket/task-009-stack-axis
---

# R3 — pack-declared stacks map + toolchain registry

## Parent

`req-021` — lane inherited from parent.

## Work

Add the `stacks` map to the shared frame (`language → stack` id: `make-cmsis`, `cargo-cortex`,
`idf-cmake`); replace the hardcoded `DefaultImageLookup.TABLE`
(`engine/adapters/__init__.py:128-137`) with a registry toolchain adapters register into; resolve
image + build command from the **resolved stack**, not the language flag
(`engine/cli/main.py:216-220`); persist the resolved stack in the rendered tree so `build`/`dev`
(which load no pack) resolve identically.

## Done-when

`make test` green; STM32 packs declare `make-cmsis`/`cargo-cortex`; language no longer selects the
toolchain; a missing (pack, language) pair errors loudly. Governed by AD-11, AD-8, AD-16.

## Evidence

2026-10-16 — branch `ticket/task-009-stack-axis`:

- **Frame gains `stacks`** (language → stack id); the three packs and all fixtures declare
  `c/cpp: make-cmsis`, `rust: cargo-cortex`.
- **`engine/core/stacks.py`** — registry *mechanism* (`StackSpec`: template family, build argv,
  image). **`engine/adapters/toolchain/`** registers the shipped stacks (`make-cmsis`,
  `cargo-cortex`) — registration, not a core edit (AD-8/AD-1).
- **`ImageLookup` is now stack → image**; `DefaultImageLookup` delegates to the registry — the
  hardcoded `TABLE` is gone.
- **Renderer selects the template family by the resolved stack**, not the language, and persists
  `.mu/stack`; a (pack, language) pair with no stack errors loudly
  (`test_render_errors_when_pack_declares_no_stack_for_language`).
- **CLI resolves the stack** from the pack (`create`/`flash`/`debug`) or the project's `.mu/stack`
  (`build`/`dev`); the build command and the container image come from the stack.
- `make test` → **295 passed**.

Proof that language no longer selects the toolchain (`mu build --dry-run`, same project):

| project `.mu/stack` | `--lang` | image chosen |
|---|---|---|
| `make-cmsis` | `rust` | `…/lang-cpp:15.3.rel2` |
| `cargo-cortex` | `c` | `…/lang-rust:1.99.0` |

Rendered trees are unchanged apart from the added `.mu/stack` (the `test_cells` file checklist was
updated in this slice); flash argv is unchanged
(`openocd -f interface/stlink.cfg -f board/st_nucleo_f4.cfg -c 'program a.elf verify reset exit'`).

Deliberate, seam-confined behaviour change (AD-16): `build`/`dev` on a directory with no
`.mu/stack` and no `--mcu-config` now error clearly ("no build stack …") instead of guessing the
toolchain from `--lang`. Its tests were updated in the same slice. Note also that auto mode now
loads the pack host-side, because the container *image* depends on the pack-declared stack.
