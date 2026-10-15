---
id: bug-018
title: "Containers bind a USB node number -> a replug breaks them (GDB Server Quit Unexpectedly)"
kind: bug
status: done
lane: direct
severity: S2
links:
  openspec: []
  bmad: []
worktree: .worktrees/bug-018/
branch: ticket/bug-018-usb-bus-binding
repro: "start a dev container, replug the board, run a Flash/debug task"
observed: "GDB Server Quit Unexpectedly / LIBUSB_ERROR_NO_DEVICE (open failed)"
expected: "the container keeps working across replugs and still picks the right probe"
---

# Containers bind a USB node number

## Root cause

Docker binds `--device` paths at container creation. `mu dev`/`flash`/`debug`
passed `/dev/bus/usb/<bus>/<dev>`; that node number changes on every replug, so
the container holds a stale path and the backend can't open the probe. Passing
just one node was also *how* the right probe got chosen — so mounting the whole
bus alone would have made selection ambiguous (two boards attached).

## Fix

- `build_container_argv`: for USB probes pass the **whole bus**
  (`--device-cgroup-rule 'c 189:* rmw'` + `-v /dev/bus/usb:/dev/bus/usb`) instead
  of one node; non-USB (tty) devices keep `--device`.
- `ProbeBinding.serial` (from sysfs, including explicit `--device` USB nodes) is
  forwarded as `-e MU_PROBE_SERIAL`.
- Generated `probe/probe-serial.cfg` (renderer-owned layout, written for every
  project) sets `adapter serial $env(MU_PROBE_SERIAL)`; wired into the Makefile
  flash args and the `launch.json` configFiles. Unset ⇒ OpenOCD picks (single probe).
- Dropped two invented board fallbacks (`stlink.cfg`/`stm32f4x.cfg`) that
  contradicted the repo's own "no invented fallback" rule (`linker_for`); a pack
  with no `openocd` block now raises loudly.

## Evidence

- `adapter serial` selects the right probe with **both boards visible**:
  F411 (HLA) → `0483:3752`; H755 (DAP) → `0483:3754`.
- dry-run argv: `--device-cgroup-rule 'c 189:* rmw' -v /dev/bus/usb:/dev/bus/usb
  … -e MU_PROBE_SERIAL=0672FF…`; no per-node `--device`.
- `_oc_flash_args`: `-f interface/stlink-dap.cfg -f board/st_nucleo_h745zi.cfg
  -f probe/probe-serial.cfg`; with `openocd=None` → `ValueError`.
- Tests: `test_shim_probe` (bus + serial), `test_renderer` (configFiles + serial
  cfg), `test_cells` (file list).

## Verify

```sh
make test
```
