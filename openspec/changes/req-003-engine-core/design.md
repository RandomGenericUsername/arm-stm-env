# Design

## Context

See proposal.md (Why). Spine AD-1/AD-2/AD-4/AD-9/AD-10 bind this story; work-split view story 1. No brownfield: greenfield package. Python + uv per spec (verified uv 0.12.23 on this machine).

## Goals / Non-Goals

**Goals:** importable `engine.core` with model, loader, validators, structs, tested against STM32-shaped fixtures.

**Non-Goals:** CLI, containers, adapters, YAML pack authoring UX, registry population.

## Decisions

- **Python dataclasses (frozen) for the model, PyYAML for loading.** Over pydantic: stdlib-plus-one-dep keeps the core dependency-free-ish and audit-small; validation logic is explicit functions per frame section (reviewable rules, not schema magic). Revisit if family blocks demand recursive schemas.
- **Registry as explicit mapping in `core/registry.py`** (`block_name -> validator fn`, `family -> blocks`), populated by pack families at import. Unknown block = hard error (fail-closed per AD-4).
- **Fixtures, not sibling copies:** 3 STM32-shaped YAML fixtures authored from spike-001-corrected values (F411RE stlink/f4, H755 dapdirect/dual-bank, WL55JC stlink/wlx+DUAL_CORE). Sibling files are evidence for values, never imported.
- **Provenance on the model** (pack id + version + source hash) so proof payloads trace to inputs.

## Risks / Trade-offs

- [Risk] Hand-rolled validation drifts toward an ad-hoc schema language → Mitigation: validators are total functions over typed blocks; family-block additions require registry + tests in the same change.
- [Risk] Frozen dataclasses complicate adapter ergonomics → Mitigation: adapters get reader views, not the model internals (enforced by module boundary + import test).

## Verification plan

- `python -m pytest engine/core/tests/` green: 3 pack fixtures accept, unknown-block rejects, frozen-model mutation raises, endpoint/proof structs cover all rungs, cache-key flips on digest change.
- `uv run --frozen` reproducibility: lockfile committed, `uv sync --frozen` in CI.

## Open Questions

None — validation library (dataclasses+PyYAML) chosen above; revisit trigger recorded.
