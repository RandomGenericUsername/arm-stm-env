# Proposal

## Why

Every adapter, verb, and pack builds on the certified device model — without `core/` (model, validation, family-block registry, endpoint/proof structs), stories 2–5 have nothing to build against. It is the dependency-order first story (work-split view story 1).

Evidence: work-split view (architecture run) lists this story first with "Unblocks 2–5". Verify: `rg "Unblocks 2" _bmad-output/initiative-universal-mcu-env/architecture-universal-mcu-env/work-split-view.md`.

## What Changes

- New Python package `engine/core/`: canonical device model (dataclasses), pack loader, frame validator, family-block registry (core-owned), endpoint/proof structs.
- Validation rejects unknown family blocks and parentless tasks per specs; errors carry verb + adapter + proof-attempt context.
- No CLI, no containers, no adapters in this change — model + validation only, proven by fixtures (3 STM32 packs as test vectors, corrected OpenOCD targets from spike-001).

## Capabilities

### New Capabilities

- `engine-core`: canonical device model, pack loading/validation, family-block registry, endpoint/proof structs.

### Modified Capabilities

(none)

## Impact

- New code: `engine/core/` (+ `pyproject.toml`, uv-managed). Test vectors from `mcu-configs` shapes (sibling evidence, not copied code).
- Out of scope: CLI verbs, images, adapters, pack authoring, registry map population (story 5), family validators beyond STM32 frame.
