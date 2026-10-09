# Design

## Context

See proposal.md. Spine AD-4/AD-5/AD-10; req-003 registry (explicit `block_name -> validator` map in `engine/core/registry.py`, family validators in `packs/`). Spikes 001 (corrected targets) and 004 (config-header flow) are inputs.

## Goals / Non-Goals

**Goals:** schema + validators + 3 correct packs + config-header pack fields, all proven by tests.

**Non-Goals:** template generation, adapters, images, other vendors.

## Decisions

- **Packs as YAML files under `packs/`**, loaded by req-003 loader; STM32 family validator registered for `openocd`, `fpu`, `linker`, `config_headers` blocks. Unknown blocks keep failing closed.
- **Per-core entries** carry arch triple + memory + probe config (cores differ in flash origin/size per spike-001 fixtures, re-verified at build: H755 M7/M4, WL55JC M4/M0+).
- **Config-header defaults block**: `{library, header, defaults_source}`; resolution order project-file > pack-defaults recorded as contract for the template story.
- **Proof rungs assigned**: F411RE readback-capable path first (ST-Link + OpenOCD verify), H755 per-core readback, WL55JC readback where DUAL_CORE session allows else LED fallback — rung recorded per pack, verdict comparable via proof struct.

## Risks / Trade-offs

- [Risk] WL55JC M0+ map details thin (no board file in fork) → Mitigation: pack records M0+ conservatively from `stm32wlx.cfg` cpu1 evidence; HW smoke test flagged OPEN for later.
- [Risk] FPU/linker facet shape guesses C/C++ needs → Mitigation: facets carry arch triple + FPU flags + linker names exactly as C++ sibling tables do (evidence), extended only with proof.

## Verification plan

- `pytest` pack suite: 3 packs accept, missing-field rejects, sibling-drift grep empty, config-header defaults shape asserted.
- `openspec validate req-004-pack-schema` green.

## Open Questions

None.
