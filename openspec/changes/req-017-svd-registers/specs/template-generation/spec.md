# Spec Delta

## Purpose

`create --vscode` fetches the pack's pinned SVDs and points each core's launch
config at its own file.

## ADDED Requirements

### Requirement: launch.json references a pinned per-core SVD

`create --vscode` SHALL fetch the pack's declared SVDs from a commit-pinned
source into `probe/`, and SHALL set `svdFile` on each core's launch config to its
file. A failed fetch SHALL fail loud naming the URL.

Evidence: ST svd zips HTTP 000; modm mirror pinned `e79021a` (design D1/D2).
Verify: `render(..., vscode=True)` → `svdFile` present; live create →
`probe/STM32F411.svd`.

#### Scenario: F411RE register view

- **WHEN** `stm32f411re` renders with `--vscode`
- **THEN** `probe/STM32F411.svd` is fetched and `svdFile` points at it

#### Scenario: H755 per core

- **WHEN** `stm32h755` renders with `--vscode`
- **THEN** the M7 config's `svdFile` is the CM7 SVD and the M4 config's is the CM4 SVD
