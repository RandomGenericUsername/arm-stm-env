# Design

## Context

See proposal.md. Two live-reproduced defects break the `flash` path. This is a
bounded slice: fix both at the correct layer and give them one source of truth,
without reworking unrelated concerns. Governed by the repo contract
(`AGENTS.md`) and the existing ports: `engine-core` (model), `cli-verbs`
(shim/host layer, AD-9), `probe-adapters` (AD-2/AD-3).

## Goals / Non-Goals

**Goals:**
- One source of truth for OpenOCD config-file paths (no renderer/adapter drift).
- `stm flash` reaches a real USB probe through the container and programs it.
- Host/OS/probe plumbing stays in the shim; core stays device-agnostic;
  adapters render from model + endpoint only.

**Non-Goals:**
- Live-proofing every matrix cell; only F411RE single-core is proven here.
- Reworking the probe *backends* or adding new ones.
- Non-USB probe transports (UART bootloader) — named as future work.

## Decisions

- **D1 — Config-path resolution is a model fact.** Add
  `OpenocdConfig.config_files()` (or a `DeviceView` equivalent) returning the
  ordered `(interface_path, board_or_target_path)`:
  `interface/<interface>` and (`board/<board>` if a board is declared else
  `target/<target>`). Rationale: the rule already exists once in
  `engine/templates/renderer.py:65-87`; copying it into the adapter is what
  caused the drift. Verify: unit test on the F411RE pack returns
  `("interface/stlink.cfg", "board/st_nucleo_f4.cfg")`; a grep shows the
  `board/`|`target/` decision appears once (in the model).
  Evidence: `packs/stm32f411re.yaml:22-24`, `packs/stm32wl55jc.yaml` (target-only).

- **D2 — Adapter consumes D1 and drops the inert address.** `render_argv` uses
  `device.openocd_interface`/`openocd_target` replaced by the resolved paths;
  the `-c "set PROBE_ADDRESS <path>"` line (`engine/adapters/openocd.py:200`) is
  removed because OpenOCD ignores it (it discovers the ST-Link via libusb).
  Verify: adapter argv test expects `["openocd","-f","interface/iface.cfg",
  "-f","board/board.cfg"]`; `rg "set PROBE_ADDRESS" engine/` empty.

- **D3 — `ProbeBinding` in the shim.** New shim type
  `ProbeBinding { selector: str, host_devices: tuple[str, ...] }`. Resolution
  enumerates sysfs `/sys/bus/usb/devices/*` (reading `idVendor`, `idProduct`,
  `serial`) to match `--vid`/`--pid`/`--serial` and to derive the real
  `/dev/bus/usb/<bus>/<dev>` node. `build_container_argv` emits `--device
  <host_devices[i]>:<host_devices[i]>` for each. `--device` passed explicitly
  wins; a serial/UART probe (no USB node) still yields its tty. Rationale:
  selection (which probe) and access (what the container needs) are different
  concerns; the current code collapses them into one tty path.
  Verify: unit test with a fixture sysfs root resolves VID/PID → a
  `/dev/bus/usb/...` node in `host_devices`; dry-run shows that node.
  Evidence: the `LIBUSB_ERROR_NO_DEVICE` vs success runs above.

- **D4 — `Endpoint` carries a selector, not a path.** `address` becomes the
  backend selector (USB serial, or `VID:PID`), `transport` the probe transport.
  OpenOCD renders selection only when a selector is present; probe-rs passes it
  to `--probe`. Rationale: a path is meaningless to `--probe` (probe-rs) and
  unused by OpenOCD stlink.
  Verify: `probe_rs` argv test passes the selector string; OpenOCD argv omits
  selection for the single-probe default.

- **D5 — macOS/non-Linux rules stay in the shim.** Existing documented limit
  (no Docker USB passthrough on Desktop) is preserved: no `--device` emitted,
  `--mode local` for probing. Verify: existing `test_shim_probe_macos_*` stays
  green or is updated to the new type.

## Risks / Trade-offs

- [Risk] sysfs enumeration differences (no stable `serial`, multiple probes) →
  Mitigation: match on VID/PID first, refine by serial; explicit `--device`
  always wins; unknown → clear error.
- [Risk] Changing `Endpoint` semantics ripples into req-006 tests that encode
  the old address-as-path behavior → Mitigation: update those expectations as
  part of this change; the registry/conformance tests define the contract.
- [Risk] D1 touches the renderer shared with req-008 → Mitigation: keep the
  renderer output byte-identical (test_cells stays green).

## Verification plan

- Unit: `pytest -k "openocd or shim or probe_rs or renderer"` green; new tests
  for D1 (model paths), D2 (adapter argv), D3 (binding), D4 (selector).
- Grep gates: `rg "set PROBE_ADDRESS" engine/` empty;
  `rg "by-id/usb-" engine/cli/shim.py` empty (no fabricated paths).
- Live acceptance: `uv run stm flash --mcu-config stm32f411re --project-dir
  /home/inumaki/Development/demo --device 0483:3752 --files
  stm32f411re-M4.elf` → exit 0 and `** Verified OK **` in the streamed log.
- `openspec validate req-012-openocd-probe-wiring` green; full `make test`
  green (merge gate).

## Open Questions

- Does `probe-rs --probe` accept `VID:PID` on all supported hosts, or only a
  serial? (Resolve during build with `probe-rs download --help`.)
- Should the shim expose the derived binding in `--dry-run` output for
  observability? (Proposed: yes, print `--device <usbnode>` only.)
