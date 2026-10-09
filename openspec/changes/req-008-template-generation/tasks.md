# Tasks

## 1. Renderer

- [x] 1.1 `engine/templates/` renderer (pack model in → tree out, `string.Template`, per-core contexts, dual-core via iteration). Verify: `pytest -k renderer` green.
- [x] 1.2 Structural harness (9 cells: file lists + placeholder grep + memory/pin greps). Verify: `pytest -k cells` 9/9.

## 2. Templates

- [x] 2.1 C/C++ templates (Makefile flags from pack, CMSIS vendored paths, linker refs) + `config/` generation. Verify: cells green for c/cpp.
- [x] 2.2 Rust templates (pinned Cargo.toml, memory.x from map, build.rs, openocd.cfg corrected) + `config/` generation. Verify: cells green for rust.

## 3. Integration checks

- [x] 3.1 Full suite green + `openspec validate` green. Verify: exits 0.
- [x] 3.2 Update req-008 ticket + link change. Verify: acceptance boxes checkable.
