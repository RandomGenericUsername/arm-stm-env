---
id: task-017
title: "T17 — bind UART probes to their tty so a serial backend can flash in-container"
kind: task
status: done
lane: inherits
parent: req-022
links:
  openspec: none
  bmad: none
worktree: .worktrees/task-017/
branch: ticket/task-017-uart-tty-binding
---

# T17 — bind UART probes to their tty so a serial backend can flash in-container

## Parent

`req-022` — lane inherited from parent.

## Work

A USB-UART bridge is reached differently from a libusb probe: the kernel creates a **tty** node
(major 188) for it, and the container's private `/dev` does not have that node — so it must be
forwarded with `--device`, unlike a libusb device (major 189), which is reached through the USB
bus. The shim only produced USB nodes, so containerized `esptool` had no port.

`engine/cli/shim.py`:

- `_tty_for_usb()` resolves the tty from sysfs (the interface is a **sibling** of the device dir,
  and the name lives under its `tty/` class dir);
- `_binding_from_entry()` chooses the binding per transport — `uart-serial` → selector *and*
  forwarded node are the tty; anything else keeps the USB-node/bus behaviour;
- `transport` is threaded through `resolve_probe_binding`/`_autodetect`/`probe_endpoint`, and the
  pack's transport rides `ShimRequest.probe_transport`.

`engine/cli/main.py` resolves the transport from the pack (`probe_ref.transport`) for both the
local and container paths.

## Done-when

A `uart-serial` pack forwards its tty (not the USB bus), and the backend receives that same port
as its endpoint address; non-UART probes are unchanged. `make test` green.

## Evidence

2026-10-16 — branch `ticket/task-017-uart-tty-binding`:

- `make test` → **345 passed** (7 new tests in `engine/cli/tests/test_uart_binding.py`).
- Whole path, with a simulated bridge (`shim._SYSFS_USB` → a fake tree, driving `main()`) in auto
  mode:
  ```
  mu flash --mcu-config esp32cam --files a.bin b.bin c.bin --dry-run
    docker run --rm --device /dev/ttyUSB0:/dev/ttyUSB0 -e MU_PROBE_SERIAL=BR-1 … \
      python3 -m engine flash --lang c --mode local --project-dir /project \
        --mcu-config esp32cam --device /dev/ttyUSB0 --files a.bin b.bin c.bin
  ```
  → the container gets the **tty**, the inner engine gets the same path, so the backend renders
  `--port /dev/ttyUSB0` (previously `--port 1a86:7523`, an unusable selector).
- Non-UART probes unchanged: a `stlink` device still yields
  `-v /dev/bus/usb:/dev/bus/usb` + `--device-cgroup-rule c 189:* rmw`, with no tty.
- Degenerate case: a `uart-serial` device with no bound tty still falls back to the USB node.

**Open:** the live containerized flash itself (needs the board attached); macOS (Docker Desktop)
still cannot forward `/dev` nodes, so `--mode local` remains the documented path there.