# Spec Delta

## Purpose

Packs may declare a board's on-board LED as an example fact, validated
fail-closed.

## ADDED Requirements

### Requirement: Optional example block

A pack MAY declare `blocks.example.led = {port, pin, active}`. `port` SHALL be a
single letter A–Z, `pin` an int 0–15, and `active` `high` (default) or `low`.
Any other shape SHALL be rejected naming the field.

Evidence: example is a board fact; core stays device-agnostic (proposal D1).
Verify: registry test rejects bad payloads; `packs/stm32f411re.yaml` validates.

#### Scenario: Valid LED fact

- **WHEN** a pack declares `example: {led: {port: A, pin: 5, active: high}}`
- **THEN** the block validates and the loader stores `(A, 5, high)` on the model

#### Scenario: Bad pin rejected

- **WHEN** `example.led.pin` is 20 (out of 0–15)
- **THEN** validation fails naming `pin`
