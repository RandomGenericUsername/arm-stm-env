# Tasks

## 1. Model + schema

- [x] 1.1 `ExampleLed` dataclass (port/pin/active + gpio_base/rcc_en_addr/rcc_en_bit/clock_hz) in `engine/core/model.py`. Verify: `pytest -k model`.
- [x] 1.2 `registry.py` validates the new fields; `loader.py` builds `ExampleLed`. Verify: `pytest -k registry`.

## 2. Template generation

- [x] 2.1 `renderer.py`: `_main_sections(facets, primary)` uses the register facts + clock-scaled delay; primary core only. Verify: `pytest -k cells`.
- [x] 2.2 Packs: F411RE F4 facts; `stm32h755` adds LD2/PE1 H7 facts. Verify: packs validate.

## 3. Tests + live proof

- [x] 3.1 F411RE blink; H755 M7 blink + M4 stub; registry/loader tests. Verify: `pytest -q` (250 passed).
- [x] 3.2 Live: `mu create … stm32h755` → build → flash (probe 0483:3754) → LD2 blinks. Verify: `** Verified OK **`.
- [x] 3.3 `make test` + `openspec validate req-015-h755-example` green; ticket/INDEX updated.
