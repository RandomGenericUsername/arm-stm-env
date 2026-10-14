# Tasks

## 1. Pack schema

- [x] 1.1 `engine/core/registry.py`: `example` block validator (led.port/pin/active). Verify: `pytest -k registry`.
- [x] 1.2 `engine/core/loader.py` + `engine/core/model.py`: `example_led` on facets + `DeviceView`. Verify: loader test reads `(A,5,high)`.

## 2. Template generation

- [x] 2.1 `engine/templates/renderer.py`: `_MAIN_C` renders blink when `example_led` present, else `wfi`. Verify: `pytest -k cells`.
- [x] 2.2 `packs/stm32f411re.yaml`: declare `example.led = {port: A, pin: 5, active: high}`. Verify: pack validates.

## 3. Tests + live proof

- [x] 3.1 `test_cells`: F411RE main has blink markers; H755/WL55 stay `wfi`. Verify: `pytest -q` (245 passed).
- [x] 3.2 Live: `mu create … stm32f411re` → `build` → `flash` → LED blinks. Verify: `** Verified OK **` (964 B).
- [x] 3.3 `make test` + `openspec validate req-014-mcu-example` green; ticket/INDEX updated.
