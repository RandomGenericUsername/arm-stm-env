# Spec Delta

## Purpose

Template generation turns certified pack models into complete, buildable project trees — per language, with library config wiring — without copying sibling generators.

## ADDED Requirements

### Requirement: Every pack-times-lang cell renders

For each of 3 packs × (c, cpp, rust), rendering SHALL produce the expected file set with zero unrendered placeholders (`$`, `{{`, `@@` leftovers fail the check).

Evidence: CAP-1 (spec). Verify: render harness asserts file list + placeholder grep empty per cell.

#### Scenario: Placeholder leak fails

- **WHEN** a rendered tree contains an unsubstituted placeholder
- **THEN** the cell check fails naming the file

### Requirement: C/C++ output carries pack-derived flags

Generated Makefiles SHALL carry arch/FPU flags from the pack (not hardcoded per board), CMSIS include paths pointing at vendored submodule locations, and linker script references from pack linker facets.

Evidence: AD-2 (facts from model only). Verify: rendered flags diffed against pack values in test.

#### Scenario: New pack without template edits

- **WHEN** a fourth STM32 pack is added
- **THEN** C/C++ rendering works with zero template-code changes (data-driven)

### Requirement: Rust output pins and maps memory

Generated `Cargo.toml` SHALL pin deps to spike-003 versions; `memory.x` SHALL encode the pack's flash/ram origins and lengths; `build.rs` SHALL wire link args.

Evidence: spike-003 table; sibling Cargo shape (evidence, not source). Verify: pin grep on rendered Cargo.toml; memory.x origins match pack.

#### Scenario: Memory mismatch fails

- **WHEN** rendered memory.x disagrees with the pack map
- **THEN** the cell check fails naming the region

### Requirement: config/ dir wiring per spike-004

Every rendered project SHALL contain `config/` with pack library defaults; documented override order is project-file-wins; build flags reference it (`-I`, `-D`).

Evidence: spike-004 recommendation (consumes into req-004 + here). Verify: `config/` present per cell with defaults + override doc.

#### Scenario: Missing defaults fail

- **WHEN** a rendered project lacks `config/` defaults for a library the pack declares
- **THEN** the cell check fails naming the library
