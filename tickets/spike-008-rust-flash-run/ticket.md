---
id: spike-008
title: "Rust live flash/run: is it a V1 gate, and does probe-rs flash F411RE/H755?"
kind: spike
status: reported
lane: direct
timebox: 3h
questions:
  - "Does the V1 success signal ('each matrix cell ... flash and the board runs', spec:65-67) require a live Rust flash/run proof, or does build-to-ELF parity (ops-023) suffice?"
  - "Does probe-rs (pinned 0.32.0) flash + run the generated Rust images on NUCLEO-F411RE and NUCLEO-H755ZI-Q?"
  - "If required, what is the concrete per-board proof command, and does the pack already declare the probe-rs chip?"
answered:
  - "Q2: YES — probe-rs 0.32.0 flashes, verifies and runs the generated Rust ELFs on both boards."
  - "Q3: proof command is `probe-rs run --chip <CHIP> --probe <VID:PID:SERIAL> <elf>`; both chips are pack-declared."
  - "Blocker: `mu build` (Rust) omits `--target`, so the documented build command fails; filed as bug-025."
open:
  - "Q1 (gate): the generated Rust example has no observable run proof (bare `wfi` loop — no LED/RTT/UART), and `mu build` needs a workaround, so Rust cannot satisfy the pack proof ritual today. Needs a product call."
links:
  openspec: none
  bmad: none
worktree: .worktrees/spike-008/
branch: ticket/spike-008-rust-flash-run
---

# Rust live flash/run: is it a V1 gate, and does probe-rs flash F411RE/H755?

## Questions

- Does the V1 success signal require a live Rust flash/run proof, or does
  build-to-ELF parity (`tickets/ops-023-e2e-matrix/ticket.md`) suffice?
- Does `probe-rs` (pinned `0.32.0`) flash + run the generated Rust images on
  NUCLEO-F411RE and NUCLEO-H755ZI-Q?
- If required, what is the concrete per-board proof command, and is the chip
  pack-declared?

## Findings

### Answered

**Q2 — probe-rs flashes + runs both boards: YES.** (2026-10-16, both probes attached.)

- `probe-rs list` → `STLink V2-1 -- 0483:3752:0672FF515250898367070638` (F411RE),
  `STLink V3 -- 0483:3754:0023004B3132511438363431` (H755ZI);
  `probe-rs chip list` carries `STM32F411RE` and `STM32H755ZI`.
- **F411RE**: `probe-rs download --chip STM32F411RE --probe 0483:3752:<serial> <elf>`
  → `Finished in 0.68s`; `probe-rs verify …` → `Verification successful`;
  `probe-rs run …` → `Finished in 0.67s` then attached until SIGTERM (no fault/halt).
- **H755ZI**: `download --verify` → `Finished in 2.06s`; `verify` →
  `Verification successful`; `run` → attached until SIGTERM.
- ELFs: `target/thumbv7em-none-eabihf/debug/stm32f411re` (825612 B),
  `…/stm32h755` (825596 B).

**Q3 — proof command + pack facts.** `probe-rs run --chip <CHIP> --probe
<VID:PID:SERIAL> <elf>`; chips pack-declared (`packs/stm32f411re.yaml:62`
`STM32F411RE`, `packs/stm32h755.yaml:93` `STM32H755ZI`).

**Blocker found (not a spike artifact): `mu build` does not set the target.**
`cargo-cortex`'s `build_argv` is `("cargo","build")` (`engine/adapters/toolchain/__init__.py:27`)
with no `--target`, and no `.cargo/config.toml` is rendered — so `mu build`
compiles for the x86_64 host and fails (`rust-lld: error: undefined symbol:
Reset` … `libcore-…x86_64-unknown-linux-gnu`). The verify harness works only
because it passes `--target` itself (`engine/verify/e2e.py:340`). Filed as
`bug-025`; ELFs here were produced with the harness command
`cargo build --target thumbv7em-none-eabihf`.

### Open

- **Q1 (the gate question) — Rust has no observable run proof.** The generated
  `src/main.rs` is `#[entry] fn main() -> ! { loop { cortex_m::asm::wfi() } }`
  (`engine/templates/renderer.py:670-…`): no LED, no RTT, no UART. The pack proof
  ritual accepts LED/RTT/UART (`device-matrix.md:14`, `spec:69`), so "the board
  runs" is not observable from the Rust image as generated — and `mu build`
  needs the bug-025 workaround first. Options for the user:
  (a) port the LED example to Rust (like C/C++ req-014/req-015) **and** fix
  bug-025, making Rust flash a first-class ritual; (b) accept a weaker Rust proof
  rung (debug-attach / `probe-rs` run staying attached, as recorded here);
  (c) scope Rust to build-parity only (as `ops-023` recorded) and gate V1 on the
  C/C++ LED proof per board.
  Related: the generated Rust `README.md` claims "on-board LED PA5 … blinking on
  M4", which does not match the `wfi` code.
- **Nuance:** after a *detached* run (`probe-rs reset`, session torn down), a
  reconnect on F411RE failed with `JtagNoDeviceConnected` — consistent with the
  bare `wfi` sleep stopping the core clock with default DBGMCU. `probe-rs run`
  (which stays attached) works; a first-class flow should keep the session or
  configure DBGMCU.

> Spike stops at the box. No implementation here beyond the workaround builds;
> the `mu build` fix is `bug-025` (separate ticket).
