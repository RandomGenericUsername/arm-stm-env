---
id: spike-008
title: "Rust live flash/run: is it a V1 gate, and does probe-rs flash F411RE/H755?"
kind: spike
status: boxed
lane: direct
timebox: 3h
questions:
  - "Does the V1 success signal ('each matrix cell ... flash and the board runs', spec:65-67) require a live Rust flash/run proof, or does build-to-ELF parity (ops-023) suffice?"
  - "Does probe-rs (pinned 0.32.0) flash + run the generated Rust images on NUCLEO-F411RE and NUCLEO-H755ZI-Q?"
  - "If required, what is the concrete per-board proof command, and does the pack already declare the probe-rs chip?"
answered: []
open: []
links:
  openspec: none
  bmad: none
worktree: none
branch: none
---

# Rust live flash/run: is it a V1 gate, and does probe-rs flash F411RE/H755?

## Questions

- Does the V1 success signal require a live Rust flash/run proof, or does
  build-to-ELF parity (`tickets/ops-023-e2e-matrix/ticket.md`) suffice?
  (signal: `spec-universal-mcu-env.md:65-67` — "each V1 matrix cell ... completes
  create → build → flash and the board runs".)
- Does `probe-rs` (pinned `0.32.0`, `HANDOFF.md:53`) flash + run the generated
  Rust images on NUCLEO-F411RE and NUCLEO-H755ZI-Q?
- If required, what is the concrete per-board proof command, and is the chip
  already pack-declared (`packs/stm32f411re.yaml:60-62` →
  `probe_settings.probe-rs.chip: STM32F411RE`)?

## Findings

### Answered

- <pending>

### Open

- Live flash/run evidence for Rust is absent: the recorded `make flash` proofs are
  C/C++ only; Rust is proven to ARM ELF32 at build time (`HANDOFF.md:40`, and
  `tickets/ops-021-project-readme/ticket.md:39` shows the Rust README deliberately
  omits `make flash`).

> Spike stops at the box and reports `answered:` / `open:`. Implementation output
> from a spike is a failure. No second box without an explicit user call.
