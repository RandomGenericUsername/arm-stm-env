---
id: req-012
title: "OpenOCD config paths + USB probe binding so stm flash programs"
kind: requirement
status: in-progress
size: M
lane: openspec-single
links:
  openspec:
    - openspec/changes/req-012-openocd-probe-wiring
  bmad: []
worktree: .worktrees/req-012/
branch: ticket/req-012-openocd-probe-wiring
parent: epic-001
children: []
---

# OpenOCD config paths + USB probe binding so stm flash programs

## Requirement

`stm flash` SHALL program a board over the container path. The OpenOCD adapter
SHALL render config-file paths from a single model-owned source, and the shim
SHALL resolve a probe binding that gives the container access to the probe's
USB device node. Details in
`openspec/changes/req-012-openocd-probe-wiring/`.

## Acceptance

- [x] `OpenOCDAdapter.render_argv` emits `-f interface/…` and `-f board/…|target/…` (no bare filenames); test `engine/adapters/tests/test_openocd.py` updated. `Verify: pytest -k openocd`
- [x] Model exposes resolved OpenOCD config paths; renderer and adapter consume it (no duplicated prefix logic). `Verify: pytest -k "renderer or core"`
- [x] Shim resolves USB probes to a host binding carrying `/dev/bus/usb/<bus>/<dev>`. `Verify: pytest -k shim`
- [ ] Live: `uv run stm flash --mcu-config stm32f411re --project-dir <demo> --vid 0483 --pid 3752 --files stm32f411re-M4.elf` reaches `** Verified OK **`. `Verify: exit 0 + streamed log` (PENDING board)
- [x] `openspec validate req-012-openocd-probe-wiring` and full `make test` green (235 passed). `Verify: exit 0`

## Evidence

Live session 2026-10-13 (NUCLEO-F411RE, ST-LINK/V2.1 `0483:3752`): `stm flash`
failed `Can't find stlink.cfg`; a tty-only container run failed
`LIBUSB_ERROR_NO_DEVICE`; the corrected direct OpenOCD run programmed and
verified. Root causes and layer mapping in the linked change's proposal/design.
