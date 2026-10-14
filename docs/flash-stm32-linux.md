# Flashing STM32 on Linux (ST-Link) — no relogin needed

Target boards: Nucleo-F411RE, Nucleo-H755ZI-Q, Nucleo-WL55JC.
Tool path: `stm flash` (auto mode runs OpenOCD from the pinned image;
USB passthrough is automatic on Linux when you pass `--device`).

## 1. One-time USB access (udev, no relogin)

Write the rules file (covers ST-Link V2, V2-1, V3):

```sh
sudo tee /etc/udev/rules.d/49-stlink.rules > /dev/null <<'EOF'
# ST-Link V2
SUBSYSTEMS=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="3748", MODE="0666", GROUP="plugdev", TAG+="uaccess"
# ST-Link V2-1 (Nucleo boards)
SUBSYSTEMS=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="374b", MODE="0666", GROUP="plugdev", TAG+="uaccess"
# ST-Link V2-1 (Nucleo-F411RE and newer, observed 0483:3752)
SUBSYSTEMS=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="3752", MODE="0666", GROUP="plugdev", TAG+="uaccess"
# ST-Link V3
SUBSYSTEMS=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="374e", MODE="0666", GROUP="plugdev", TAG+="uaccess"
SUBSYSTEMS=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="374f", MODE="0666", GROUP="plugdev", TAG+="uaccess"
SUBSYSTEMS=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="3753", MODE="0666", GROUP="plugdev", TAG+="uaccess"
SUBSYSTEMS=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="3754", MODE="0666", GROUP="plugdev", TAG+="uaccess"
EOF
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Then **unplug + replug the board** (this is what activates the rules —
no reboot, no relogin). If your user isn't in `plugdev`/`dialout`,
avoid relogin with:

```sh
sudo usermod -aG plugdev,dialout $USER
newgrp plugdev   # refresh groups in this shell, no relogin
id -nG           # confirm plugdev/dialout listed
```

Verify the probe is visible:

```sh
lsusb -d 0483:                       # ST-Link enumerates
ls -l /dev/ttyACM* 2>/dev/null       # Nucleo virtual COM port (RTT/UART)
```

## 2. Flash via the tool (preferred — OpenOCD comes from the image)

```sh
uv run stm create --mcu-config stm32f411re --lang c --name demo --out-dir .
uv run stm build --project-dir ./demo
uv run stm flash --mcu-config stm32f411re --project-dir ./demo \
  --vid 0483 --pid 3752 --files stm32f411re-M4.elf
```

Select the probe as a **USB device** (`--vid`/`--pid`, or `--serial`); the shim
resolves the matching `/dev/bus/usb/<bus>/<dev>` node and forwards it into the
container automatically. Do **not** pass a serial tty (`/dev/ttyACM0`) as the
probe — that is the UART, not the debug interface, and OpenOCD reaches ST-Link
over USB. An explicit `--device <usb-node>` still wins if you need it.
`--verbose` saves the full tool log under `./demo/.stm/logs/`.

Note (Arch/EndeavourOS): the serial group is `uucp`, not `dialout`, and
`plugdev` may not exist — `MODE="0666"`+`uaccess` in the rules above is what
grants access; create the group or drop `GROUP="plugdev"` if `udevadm` warns.

## 3. Raw OpenOCD commands (fallback / diagnosis)

```sh
# F411RE (single M4)
openocd -f interface/stlink.cfg -f board/st_nucleo_f4.cfg \
  -c "program demo.elf verify reset exit"
# H755 (dual M7+M4 — MUST be stlink-dap + DUAL_CORE; HLA falls back to one core)
openocd -f interface/stlink-dap.cfg -f board/st_nucleo_h745zi.cfg \
  -c "program demo_m7.elf verify reset exit"
# WL55JC (no board file in fork; direct target + DUAL_CORE for both cores)
openocd -f interface/stlink.cfg -f target/stm32wlx.cfg \
  -c "set DUAL_CORE 1" -c "program demo.elf verify reset exit"
# Probe-only sanity check (no flash):
openocd -f interface/stlink.cfg -f board/st_nucleo_f4.cfg -c "init; targets; exit"
```

## 4. Common failures and fixes

| Symptom | Cause → fix |
|---|---|
| `Permission denied` on `/dev/ttyACM0` or probe | udev rules missing/stale → §1, then unplug/replug |
| `openocd: no device found` / empty `lsusb -d 0483:` | cable (charge-only cables!), USB 3.0 hub flakiness → replug, try a USB 2.0 port, another cable |
| `target not halted` / reset errors | reset config: add `-c "reset_config srst_only srst_nogate connect_assert_srst"`; hold NRST if needed |
| ST-Link firmware too old | upgrade via STM32CubeProgrammer (GUI) or `st-info --version` from stlink-tools to check |
| H755 second core missing / only one target | using HLA (`stlink.cfg`) instead of `stlink-dap.cfg` — dual-core needs DAP + DUAL_CORE |
| Multiple probes attached | pin one: `-c "hla_serial <serial>"` (HLA) or `stlink serial <serial>`; find serials via `lsusb -v` |
| Board disconnects mid-session | USB autosuspend: `echo -1 \| sudo tee /sys/bus/usb/devices/<dev>/power/autosuspend` |
| Serial gibberish / no output | baud mismatch (try 115200), wrong `/dev/ttyACM*` node, or firmware never reached `main` |

## 5. Record evidence (both outcomes matter)

Save everything and bring it back:

```sh
uv run stm flash --mcu-config <pack> --project-dir <dir> \
  --vid <vid> --pid <pid> --files <elf> --verbose 2>&1 | tee flash-<board>-$(date +%F).log
```

Success → which board/core/file/versions. Failure → open a `bug` ticket
with repro command + observed vs expected (see `tickets/_template/bug.md`).
