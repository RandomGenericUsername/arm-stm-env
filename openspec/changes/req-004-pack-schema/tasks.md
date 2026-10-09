# Tasks

## 1. Schema + validators

- [x] 1.1 Implement STM32 family-block validators (`openocd`, `fpu`, `linker`, `config_headers`) registered in `engine/core/registry.py`. Verify: `pytest -k registry` — known blocks validate, unknown still rejects.
- [x] 1.2 Frame-required-fields enforcement (identity, cores, memory, probe ref, proof rung). Verify: `pytest -k frame` — each missing field rejects naming it.

## 2. Packs

- [x] 2.1 Author `packs/stm32f411re.yaml`, `packs/stm32h755.yaml`, `packs/stm32wl55jc.yaml` from spike-001-corrected values (no sibling copies). Verify: `pytest -k packs_accept` — 3 accept; `rg "stm32f4x" packs/stm32h755.yaml packs/stm32wl55jc.yaml` empty.
- [x] 2.2 Config-header defaults blocks in packs + shape tests. Verify: `pytest -k config_headers` — defaults shape asserted; precedence documented for template story.
- [x] 2.3 Proof rungs recorded per pack (readback-first ladder). Verify: every pack has a rung; proof structs cover them.

## 3. Integration checks

- [x] 3.1 Full suite green + `openspec validate req-004-pack-schema` green. Verify: both exit 0.
- [x] 3.2 Update req-004 ticket (evidence, status) + link change. Verify: acceptance boxes checkable.
