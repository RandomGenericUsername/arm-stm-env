# Design

## Context

See proposal.md. Board facts belong in the pack (device-agnostic core, packs own
device/board truth). The example is board-specific (which pin drives LD2), so it
is a **pack block**, not core logic.

## Goals / Non-Goals

**Goals:** one working on-board-LED example per shipped MCU that declares it;
loud validation; the stub remains for the rest.

**Non-Goals:** H755/WL55 examples, Rust examples, timers/other peripherals.

## Decisions

- **D1 — `example` block.** `blocks.example.led = {port, pin, active}` where
  `port` is a single letter A–Z, `pin` int 0–15, `active` in {high, low}
  (default high). Validator fails closed. Rationale: the LED pin is a board
  fact; declaring it in the pack keeps the renderer device-agnostic and makes
  "implemented vs stub" a data difference, not a code fork.
- **D2 — Facets + view.** Loader stores `example_led: (port, pin, active)` in
  `DeviceFacets`; `DeviceView` exposes it (adapters/renderer read the view only).
- **D3 — Blink generation.** When `example_led` is present, the renderer emits a
  self-contained blink: raw registers (RCC AHB1ENR clock-enable, GPIO MODER
  output, BSRR set/reset) + a NOP busy-loop half-period (~10 Hz at 16 MHz).
  `GPIOx` base = `0x40020000 + (port-A)*0x400`; clock bit = `port-A` (AHB1).
  No HAL/CMSIS dependency beyond `<stdint.h>`. Otherwise the existing `wfi` stub.
  Evidence: the same code was flashed live on F411RE 2026-10-14 (`Verified OK`).
- **D4 — Delay is approximate.** `DELAY_ITERS` is a tunable constant
  (~50,000 ≈ 0.05 s at ~16 cycles/iteration); documented as approximate.

## Risks / Trade-offs

- [Risk] Port letters outside A–K (AHB1) or pins >15 → Mitigation: validator
  bounds pin 0–15 and port A–Z; only A–E are AHB1 today (documented; packs ship
  A for now).
- [Risk] NOP delay varies with `-O`/clock → Mitigation: comment it as
  approximate + tunable.

## Verification plan

- Unit: `render()` for `stm32f411re` (c/cpp) → `src/main-M4.c` contains
  `GPIO_BSRR` + `delay_half_period` + `LED_PIN`; `stm32h755`/`stm32wl55jc` →
  `wfi` stub. Registry test rejects a bad `example` payload.
- Live: `mu create … stm32f411re` → `mu build` → flash → LED blinks.
- `make test` green; `openspec validate req-014-mcu-example` green.

## Open Questions

- Should the example also cover Rust (cortex-m) later? Deferred.
