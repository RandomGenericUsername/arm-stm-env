# Proposal

## Why

`create` currently has verbs with no content: the engine, packs, CLI, adapters, and images exist, but nothing renders a project from a pack. Both siblings' entire value lived in generation (C++ bash/Python scaffolder, Rust cargo-generate templates) — this story reclaims it on the new architecture.

Evidence: work-split gap found post-req-007 (no story owns generation); spec CAP-1 assumes rendered trees. Verify: `rg -i "template" _bmad-output/initiative-universal-mcu-env/architecture-universal-mcu-env/work-split-view.md` — generation appears only as unowned future work.

## What Changes

- `engine/templates/` renderer: pack model in → project tree out, per language (c/cpp, rust), driven by Jinja-style stdlib templates (`string.Template` — stdlib, no new deps).
- C/C++ output: Makefile (gcc flags per arch/FPU from pack), linker script reference, CMSIS include wiring (vendored submodule paths per spike-002), `config/` dir with library defaults + documented override order.
- Rust output: `Cargo.toml` (pinned deps per spike-003 versions), `memory.x` from pack memory map, `build.rs` link glue, `config/` dir similarly.
- Structural-check harness: every pack × lang cell asserts expected files + no unrendered placeholders.

## Capabilities

### New Capabilities

- `template-generation`: pack-driven project rendering per language + config-dir wiring.

### Modified Capabilities

(none)

## Impact

- New code: `engine/templates/` + template sources. Tested by render-all-cells harness (no hardware).
- Out of scope: building rendered projects in images (next story), IDE files (later), non-STM32 templates.
