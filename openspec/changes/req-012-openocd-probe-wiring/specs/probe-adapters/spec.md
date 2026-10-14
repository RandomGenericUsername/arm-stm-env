# Spec Delta

## Purpose

The OpenOCD adapter renders config paths and probe selection from certified
model facts and the prepared endpoint — no drift from the renderer, no inert
address variable.

## ADDED Requirements

### Requirement: OpenOCD argv uses resolved config paths

The adapter SHALL build `-f` arguments from the model's resolved config-file
paths (`interface/<interface>`, and `board/<board>`|`target/<target>`), not from
raw pack filenames, so its argv matches the template renderer.

Evidence: adapter rendered `-f stlink.cfg -f st_nucleo_f4.cfg` for the F411RE
pack and OpenOCD failed with `Can't find stlink.cfg` (2026-10-13). Verify:
adapter argv test expects `["openocd","-f","interface/iface.cfg","-f","board/board.cfg"]`.

#### Scenario: F411RE single core

- **WHEN** the model carries `interface: stlink.cfg` + `board: st_nucleo_f4.cfg`
- **THEN** argv contains `-f interface/stlink.cfg` and `-f board/st_nucleo_f4.cfg`

### Requirement: Probe selection is a real selector, not an address variable

The adapter SHALL express probe selection only when the endpoint carries a
selector, through a mechanism the tool honors; it SHALL NOT emit an inert
`set PROBE_ADDRESS <path>` command.

Evidence: `set PROBE_ADDRESS` is ignored by OpenOCD stlink (libusb discovery),
so it provided false confidence of selection (`engine/adapters/openocd.py:200`).
Verify: `rg "set PROBE_ADDRESS" engine/` empty; adapter argv test omits it.

#### Scenario: Single probe default (no selector)

- **WHEN** the endpoint carries no selector
- **THEN** argv omits explicit probe selection and relies on the tool default

#### Scenario: Multiple probes attached

- **WHEN** the endpoint carries a serial selector and several probes are present
- **THEN** argv pins the intended probe via the backend's serial option
