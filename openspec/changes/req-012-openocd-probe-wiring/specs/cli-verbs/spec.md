# Spec Delta

## Purpose

Probe host access is resolved in the shim into a binding that carries both the
backend selector and the host device nodes the container must receive.

## ADDED Requirements

### Requirement: Probe selectors resolve to a host binding

The shim SHALL resolve probe selectors to a binding carrying a backend selector
and the host device nodes the container must access. For a USB probe it SHALL
derive the real USB device node from sysfs, never a synthesized serial path.

Evidence: tty-only run → `LIBUSB_ERROR_NO_DEVICE`; USB node succeeds (2026-10-13, `0483:3752`). Verify: fixture-sysfs unit test; `rg "by-id/usb-" engine/cli/shim.py` empty.

#### Scenario: USB debug probe by VID/PID

- **WHEN** `--vid 0483 --pid 3752` matches one sysfs USB device
- **THEN** the binding's host devices include that device's `/dev/bus/usb/<bus>/<dev>` node, and the container argv carries `--device <node>:<node>`

#### Scenario: Explicit device wins

- **WHEN** `--device /dev/bus/usb/003/009` is passed with other selectors
- **THEN** the binding uses `/dev/bus/usb/003/009`

### Requirement: The endpoint address is a backend selector

The prepared `Endpoint` SHALL carry a backend-meaningful selector (e.g. USB
serial or `VID:PID`), not a host filesystem path; the probe transport SHALL be
recorded in `transport`.

Evidence: a path is inert for OpenOCD stlink (`engine/adapters/openocd.py:200`)
and invalid for `probe-rs --probe` (`engine/adapters/probe_rs.py:194-201`).
Verify: probe-rs argv test asserts the selector string; no `/dev/` value reaches
`Endpoint.address` for USB probes.

#### Scenario: Single probe default

- **WHEN** no selector is given and exactly one USB probe is present
- **THEN** the shim may omit backend selection and rely on the tool default
