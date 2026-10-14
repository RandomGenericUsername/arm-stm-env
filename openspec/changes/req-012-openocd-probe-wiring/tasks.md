# Tasks

## 1. Model: OpenOCD config paths (single source of truth)

- [x] 1.1 Add resolved config-file paths to the model/reader view (D1): `interface/<interface>` + `board/<board>`|`target/<target>`. Verify: unit test returns `("interface/stlink.cfg","board/st_nucleo_f4.cfg")` for the F411RE pack and `target/stm32wlx.cfg` for WL55.
- [x] 1.2 Point `engine/templates/renderer.py` at the model fact and delete its duplicate prefix logic. Verify: `pytest -k renderer` green; `engine/templates/tests/test_cells.py` unchanged output.

## 2. Adapter: consume resolved paths + real selector

- [x] 2.1 `engine/adapters/openocd.py` renders the resolved paths and drops the inert `set PROBE_ADDRESS` line (D2). Verify: `pytest -k openocd` green; `rg "set PROBE_ADDRESS" engine/` empty.
- [x] 2.2 Update `engine/adapters/tests/test_openocd.py` expectations to prefixed paths. Verify: the test that previously asserted bare names now asserts `interface/…`/`board/…`.

## 3. Shim: ProbeBinding (USB-aware host access)

- [x] 3.1 Add `ProbeBinding {selector, host_devices}` + sysfs enumeration (D3); `build_container_argv` emits the host device nodes. Verify: `pytest -k shim` green; a fixture-sysfs test resolves `--vid/--pid` to a `/dev/bus/usb/...` node.
- [x] 3.2 `Endpoint` carries a selector, not a path (D4); update macOS/limit tests (D5). Verify: `pytest -k shim` green; `rg "by-id/usb-" engine/cli/shim.py` empty.

## 4. Second backend + integration

- [x] 4.1 `probe-rs` receives the selector via `--probe`. Verify: `pytest -k probe_rs` green.
- [x] 4.2 Full suite + `openspec validate`. Verify: `make test` exit 0; `uv run openspec validate req-012-openocd-probe-wiring` green.

## 5. Live acceptance + close-out

- [ ] 5.1 Live flash: `uv run stm flash --mcu-config stm32f411re --project-dir <demo> --vid 0483 --pid 3752 --files stm32f411re-M4.elf`. Verify: exit 0 and `** Verified OK **` in the streamed log (save log as evidence). **PENDING: board not attached at implementation time.**
- [x] 5.2 Correct `docs/flash-stm32-linux.md` (USB node / selector, not tty). Verify: doc no longer instructs `/dev/ttyUSB0` as the probe node.
- [x] 5.3 Update `tickets/req-012…` + INDEX + bug-003/bug-004 statuses. Verify: INDEX line matches ticket status.
