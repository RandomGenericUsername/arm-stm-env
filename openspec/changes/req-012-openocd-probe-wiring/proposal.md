# Proposal

## Why

`stm flash` cannot program a board over the container path. Two independent
defects were reproduced live on 2026-10-13 with an official NUCLEO-F411RE
(ST-LINK/V2.1, `0483:3752`). Each defect lives in a different layer, and each
was proven in isolation:

- **Engine — OpenOCD config paths are rendered unprefixed.** The adapter emits
  bare filenames; OpenOCD only resolves them under `interface/` and
  `board/`|`target/`.
  Evidence: `OpenOCDAdapter().render_argv(...)` for `packs/stm32f411re.yaml` →
  `['openocd', '-f', 'stlink.cfg', '-f', 'st_nucleo_f4.cfg', …]`
  (`engine/adapters/openocd.py:191-197`). Repro:
  `docker run --rm ghcr.io/arm-stm-env/lang-cpp:15.3.rel2 openocd -f stlink.cfg -c exit`
  → `embedded:startup.tcl:28: Error: Can't find stlink.cfg`.
  The template renderer already does this correctly
  (`engine/templates/renderer.py:65-87,471-481`) and its tests assert the
  prefixed paths (`engine/templates/tests/test_cells.py:34`); the adapter has no
  shared source, so the two drifted. The adapter test encodes the bug
  (`engine/adapters/tests/test_openocd.py:72`).
  Retraction: the initial theory (missing `OPENOCD_SCRIPTS` in the image) is
  **wrong** — `openocd -c "echo [find interface/stlink.cfg]"` resolves
  `/usr/local/bin/../share/openocd/scripts/interface/stlink.cfg` with the env
  unset. No image change is required.

- **Shim — the probe is modeled as a serial tty, not a USB device.** The shim
  resolves any selector to a tty-ish node and forwards only that to the
  container; USB debug probes are reached through libusb.
  Evidence: `engine/cli/shim.py:87-159`. Repro (scripts path irrelevant here):
  `docker run --rm --device /dev/ttyACM0:/dev/ttyACM0 -v <demo>:/project:rw -w /project ghcr.io/arm-stm-env/lang-cpp:15.3.rel2 openocd -f interface/stlink.cfg -f board/st_nucleo_f4.cfg -c "init; targets; exit"`
  → `Error: libusb_open() failed with LIBUSB_ERROR_NO_DEVICE / Error: open
  failed`; passing `--device /dev/bus/usb/003/009` instead → `Info : STLINK
  V2J38M27 … Examination succeed` and a successful
  `program … ** Verified OK **`. The shim also fabricates paths that need not
  exist (`/dev/serial/by-id/usb-<vid>_<pid>`, `engine/cli/shim.py:115-118`;
  asserted in `engine/cli/tests/test_shim_probe.py:25-26`).

## What Changes

- **Model is the single source of truth for OpenOCD config paths.** Add a
  resolved config-file fact (`interface/<interface>` + `board/<board>` when a
  board is declared, else `target/<target>`) to the model/reader view. The
  renderer and the OpenOCD adapter both consume it; the duplicate prefix logic
  in `engine/templates/renderer.py` is removed.
- **OpenOCD adapter renders config paths + probe selection from the model.** It
  consumes the resolved paths and replaces the inert
  `-c "set PROBE_ADDRESS <path>"` with a real selector (or nothing for the
  single-probe default).
- **Shim resolves a `ProbeBinding`.** Selectors (`--device`/`--vid`/`--pid`/
  `--serial`) resolve to `{selector, host_devices}` by enumerating sysfs
  (`/sys/bus/usb/devices/*`); the container receives the **USB device node(s)**
  as `--device`. The endpoint address becomes a backend selector, not a path.
- **probe-rs** receives that selector via `--probe`.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `engine-core`: OpenOCD config-file paths become a resolved model fact.
- `cli-verbs`: probe selectors resolve to a host binding carrying USB device
  nodes for the container.
- `probe-adapters`: OpenOCD argv uses resolved config paths and a real probe
  selector; no inert address variable.

## Impact

- Code (later change, not this one): `engine/core/model.py`,
  `engine/templates/renderer.py`, `engine/adapters/openocd.py`,
  `engine/adapters/probe_rs.py`, `engine/cli/shim.py` + their tests; docs
  (`docs/flash-stm32-linux.md` is tty-centric and must be corrected).
- **Out of scope:** live run proof beyond a single F411RE flash (H755/WL55
  dual-core remain OPEN); non-Linux hosts; non-USB (UART bootloader) probes;
  any image change (retracted above).
