# Proposal

## Why

Packs are the device truth everything renders from — without the frame schema plus the 3 corrected STM32 packs (spike-001 values, not sibling copies), CLI verbs (req-005) and adapters (req-006) have nothing certified to consume. Second story in dependency order (work-split view story 2).

Evidence: epic children ordering; spike-001/004 findings filed. Verify: `rg "Unblocks|Blocked" tickets/req-004-pack-schema/ticket.md _bmad-output/.../work-split-view.md 2>/dev/null | head -5`.

## What Changes

- Pack schema: shared frame (identity/cores/memory/probe-ref/proof-rung) + STM32 family blocks (openocd config, fpu/linker facets per language), validated by `engine/core` registry from req-003.
- 3 packs authored: `packs/stm32f411re.yaml`, `packs/stm32h755.yaml`, `packs/stm32wl55jc.yaml` with spike-001-corrected OpenOCD targets + proof rungs.
- Config-header path per reconciled spike-004: pack ships library defaults, template generates per-project `config/` dir (template story owns generation; this story defines pack-side fields + resolution order).
- No CLI, no images, no adapters in this change.

## Capabilities

### New Capabilities

- `pack-schema`: frame + family-block schema, 3 STM32 packs, config-header pack fields.

### Modified Capabilities

(none)

## Impact

- New: `packs/` + schema validators in `engine/` (extends req-003 registry).
- Out of scope: template generation, adapters, images, non-STM32 families.
