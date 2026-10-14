# Design

## Context

See proposal.md. `req-014` assumed F4 register addresses; H7 differs. The LED
pin and the family register facts are all board/MCU data → they belong in the
pack, keeping the renderer device-agnostic.

## Goals / Non-Goals

**Goals:** the H755 blink (LD2/PE1) works; the example is family-correct and
doesn't double-drive a shared pin on dual-core.

**Non-Goals:** WL55 example, M4 examples, timers/other peripherals.

## Decisions

- **D1 — Register facts in the pack.** `example.led` carries `gpio_base`,
  `rcc_en_addr`, `rcc_en_bit`, `clock_hz`. Rationale: address math (GPIO base,
  RCC enable register) is family truth; hard-coding F4 broke H7. The renderer
  emits `RCC_EN`, `GPIO_MODER`, `GPIO_BSRR` from these. Evidence: H7 facts from
  the vendored `cmsis-device-stm32h755` header — `GPIOE_BASE` (= D3_AHB1PERIPH +
  0x1000 = 0x58021000), `RCC_BASE` (= +0x4400 = 0x58024400), `RCC_AHB4ENR`
  offset 0xE0, `RCC_AHB4ENR_GPIOEEN` bit 4.
- **D2 — LED choice.** Use **LD2 = PE1** (UM2408: "User LD2: A yellow user LED is
  connected to PE1"). LD1 (green) is PB0 *or* PA5 via solder bridge SB54/SB65 —
  ambiguous — so PE1 is the safe, bridge-independent choice.
- **D3 — Primary core only.** The blink renders for `cores[0]` only; others get
  the stub. Rationale: dual-core share the pin; M7 is the boot core. Evidence:
  H755 boots M7 first.
- **D4 — Clock-aware delay.** `DELAY_ITERS = round(0.05 s × clock_hz / 16)`
  (~10 Hz): F4 16 MHz → 50,000; H7 64 MHz → 200,000. Evidence: vendored H755
  `SystemCoreClock = 64000000`.

## Risks / Trade-offs

- [Risk] `clock_hz` wrong → wrong blink rate → Mitigation: default-clock value
  recorded per pack from the vendored system file; tunable in the pack.
- [Risk] PE1 driven by M4 too → Mitigation: primary-core-only (D3).

## Verification plan

- Unit: F411RE `main-M4.c` blink with F4 regs; H755 `main-M7.c` blink with H7
  regs (0x580244E0/0x58021000), `main-M4.c` stub; registry validates the new
  fields; loader attaches `ExampleLed`.
- Live: `mu create … stm32h755` → build → flash (probe 0483:3754) → LD2 blinks.
- `make test` green; `openspec validate req-015-h755-example` green.

## Open Questions

- WL55JC LED fact — deferred (still a stub).
