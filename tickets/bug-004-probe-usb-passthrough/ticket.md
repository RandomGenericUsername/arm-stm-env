---
id: bug-004
title: "stm flash container receives serial tty, not the ST-Link USB device"
kind: bug
status: done
lane: direct
severity: S1
links:
  openspec:
    - openspec/changes/req-012-openocd-probe-wiring
  bmad: []
worktree: .worktrees/req-012/
branch: ticket/req-012-openocd-probe-wiring
repro: "docker run --rm --device /dev/ttyACM0:/dev/ttyACM0 -v <demo>:/project:rw -w /project ghcr.io/arm-stm-env/lang-cpp:15.3.rel2 openocd -f interface/stlink.cfg -f board/st_nucleo_f4.cfg -c 'init; targets; exit'"
observed: "Error: libusb_open() failed with LIBUSB_ERROR_NO_DEVICE / Error: open failed"
expected: "openocd finds ST-LINK and verifies; only the USB node need be forwarded"
---

# stm flash container receives serial tty, not the ST-Link USB device

## Repro

With the board attached (`lsusb -d 0483:` → `0483:3752`), forward the serial tty
the shim currently resolves, and let OpenOCD open the probe:

```sh
docker run --rm \
  --device /dev/ttyACM0:/dev/ttyACM0 \
  -v /home/inumaki/Development/demo:/project:rw -w /project \
  ghcr.io/arm-stm-env/lang-cpp:15.3.rel2 \
  openocd -f interface/stlink.cfg -f board/st_nucleo_f4.cfg \
  -c "init; targets; exit"
```

## Observed

```
Error: libusb_open() failed with LIBUSB_ERROR_NO_DEVICE
Error: open failed
```

The same run with `--device /dev/bus/usb/003/009` instead reaches
`Info : STLINK V2J38M27 (API v2) VID:PID 0483:3752 … Examination succeed` and a
successful `** Verified OK **`.

## Expected

The shim forwards the probe's USB device node so OpenOCD reaches the ST-Link
from inside the container; no serial tty is required for a USB probe.

## Fix notes

Root cause: `engine/cli/shim.py:87-159` models a probe as a serial tty — it
synthesizes `/dev/serial/by-id/usb-<vid>_<pid>` paths that need not exist and
forwards that node via `probe_docker_args`. USB debug probes are reached through
libusb. Fix: resolve selectors to a `ProbeBinding {selector, host_devices}` by
enumerating sysfs and forward the USB node (D3/D4 in the linked change).
Regression: shim unit test with a fixture sysfs root asserting a
`/dev/bus/usb/...` host device. Live repro needs hardware, so the unit test is
the durable regression.

Fixed in req-012 (commit `4feb3bd`); regression in
`engine/cli/tests/test_shim_probe.py`. Live 2026-10-14:
`uv run stm flash --mcu-config stm32f411re --vid 0483 --pid 3752 …` →
`** Verified OK **`, verdict `1/1 OK` (board `0483:3752` →
`/dev/bus/usb/003/007`).
