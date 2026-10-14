# Spec Delta

## Purpose

The certified model is the single source of truth for OpenOCD config-file
paths, so renderers and adapters cannot drift.

## ADDED Requirements

### Requirement: OpenOCD config-file paths are a resolved model fact

The model SHALL expose its OpenOCD config-file paths as ordered, prefixed facts.
Renderers and adapters SHALL consume this fact and SHALL NOT re-derive the
`board/`|`target/` decision.

Evidence: engine/adapters/openocd.py:191-197 vs engine/templates/renderer.py:65-87 (drift, 2026-10-13). Verify: unit test on packs/stm32f411re.yaml returns the prefixed pair.

#### Scenario: Board-backed pack

- **WHEN** the pack declares `interface: stlink.cfg` and `board: st_nucleo_f4.cfg`
- **THEN** the model fact is `("interface/stlink.cfg", "board/st_nucleo_f4.cfg")`

#### Scenario: Target-only pack

- **WHEN** the pack declares `interface: stlink.cfg` and `target: stm32wlx.cfg` (no board)
- **THEN** the model fact is `("interface/stlink.cfg", "target/stm32wlx.cfg")`
