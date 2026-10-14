# Proposal

## Why

`req-014` shipped a per-MCU blink example, but only for F4: the generated code
hard-coded the F4 register layout (GPIO `0x40020000`, RCC AHB1ENR `0x40023830`)
and a 16 MHz delay. The STM32H755 is dual-core and H7-clocked, so it needs
different facts: GPIO on **AHB4ENR**, base `0x58021000`/`0x580244E0`, and a
**64 MHz** default clock. Enable the H755 example (LD2 = PE1) and make the
example correct per family and per core.

## What Changes

- `example.led` gains the raw-register facts: `gpio_base`, `rcc_en_addr`,
  `rcc_en_bit`, `clock_hz` (typed `ExampleLed` in the model). The renderer no
  longer derives addresses from the port letter.
- The example renders on the **primary (first) core only**; dual-core siblings
  stay a `wfi` stub (they share the LED pin — no fighting).
- `packs/stm32h755.yaml` declares `led: {port: E, pin: 1, active: high,
  gpio_base: 0x58021000, rcc_en_addr: 0x580244E0, rcc_en_bit: 4,
  clock_hz: 64000000}` (LD2 yellow, UM2408). F411RE keeps PA5 with the F4 facts.
- Delay scales with `clock_hz` so both blink ~10 Hz.

## Capabilities

### Modified Capabilities

- `pack-schema`: `example.led` register/clock facts.
- `template-generation`: primary-core-only example; family-correct registers.

## Impact

- Code: `engine/core/{model,loader,registry}.py`,
  `engine/templates/renderer.py`, `packs/stm32h755.yaml`, `packs/stm32f411re.yaml`
  + tests.
- Out of scope: WL55JC example (still stub), M4-core examples, non-LED examples.
