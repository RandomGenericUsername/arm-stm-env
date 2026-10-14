# Spec Delta

## Purpose

Packs may declare per-core SVD files so the generated debug config shows the
peripheral register view.

## ADDED Requirements

### Requirement: Optional svd block

A pack MAY declare `blocks.svd` as a mapping of core name -> SVD source path
(non-empty strings). Any other shape SHALL be rejected naming the field.

Evidence: req-017; sibling `download_svd_files.sh`. Verify: registry test;
`packs/stm32f411re.yaml` validates.

#### Scenario: Valid svd fact

- **WHEN** a pack declares `svd: {M4: stm32f4/STM32F411.svd}`
- **THEN** the block validates and the loader stores it on the model

#### Scenario: Empty path rejected

- **WHEN** an `svd` entry path is empty
- **THEN** validation fails naming `path`
