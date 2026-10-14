# Spec Delta

## Purpose

The example LED fact carries the family register/clock facts, so it works on
non-F4 families.

## ADDED Requirements

### Requirement: Example LED carries register and clock facts

`example.led` SHALL declare `gpio_base`, `rcc_en_addr`, `rcc_en_bit`, and
`clock_hz` alongside `port`/`pin`/`active`. Addresses SHALL be positive ints (or
`0x` strings), `rcc_en_bit` 0–31, `clock_hz` a positive int. Bad shapes SHALL be
rejected naming the field.

Evidence: F4 and H7 differ (AHB1ENR vs AHB4ENR; 16 vs 64 MHz) — see design D1.
Verify: registry test; `packs/stm32f411re.yaml` + `stm32h755.yaml` validate.

#### Scenario: H7 facts

- **WHEN** `stm32h755` declares `gpio_base 0x58021000`, `rcc_en_addr 0x580244E0`, `rcc_en_bit 4`, `clock_hz 64000000`
- **THEN** the model stores them on `ExampleLed`

#### Scenario: Missing clock rejected

- **WHEN** `example.led` omits `clock_hz`
- **THEN** validation fails naming `clock_hz`
