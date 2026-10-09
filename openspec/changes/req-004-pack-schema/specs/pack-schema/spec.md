# Spec Delta

## Purpose

The pack schema fixes the shape of device truth: a shared frame every pack carries plus typed family blocks, with the 3 STM32 packs as the reference population and config-header defaults as pack-side data.

## ADDED Requirements

### Requirement: Frame validates three packs

The frame validator SHALL accept the 3 authored packs and reject packs missing required frame fields (identity, cores, memory, probe ref, proof rung).

Evidence: AD-4 (spine). Verify: `pytest -k pack_schema` — 3 accept + missing-field rejects.

#### Scenario: Missing proof rung rejected

- **WHEN** a pack omits `proof_rung`
- **THEN** loading fails naming the field

### Requirement: STM32 family blocks carry corrected values

STM32 blocks SHALL carry spike-001-corrected OpenOCD targets (F411RE stlink/f4; H755 stlink-dap/h745zi DUAL_CORE; WL55JC stlink/wlx DUAL_CORE) — never sibling-copied values.

Evidence: spike-001 findings (corrected). Verify: `rg "stm32f4x" packs/stm32h755.yaml packs/stm32wl55jc.yaml` empty; `rg "st_nucleo_h745zi|stm32wlx" packs/` hits present.

#### Scenario: Sibling drift cannot recur

- **WHEN** a pack is authored from sibling memory instead of spike values
- **THEN** review against spike-001 ticket rejects it

### Requirement: Config-header defaults live in packs

Packs SHALL declare library config-header defaults (header name, default values source); user overrides resolve project-file-wins per spike-004, wired via `-I` order + `-D` selectors at template level.

Evidence: spike-004 recommendation. Verify: pack schema test asserts defaults block shape; template wiring deferred to template story with this field contract.

#### Scenario: Override precedence

- **WHEN** user project file and pack defaults define the same key
- **THEN** project file wins; pack default fills the rest
