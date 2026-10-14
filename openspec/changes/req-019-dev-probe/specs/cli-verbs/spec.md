# Spec Delta

## Purpose

`dev` can be given the probe so its container holds the USB node.

## ADDED Requirements

### Requirement: dev accepts probe selectors

`mu dev` SHALL accept `--device`/`--vid`/`--pid`/`--serial` and SHALL pass the
resolved probe USB node to the dev container as `--device`, exactly like
`flash`/`debug`.

Evidence: req-019; the shim already resolves the binding for every verb. Verify:
`mu dev --vid … --pid … --dry-run` shows `--device /dev/bus/usb/<bus>/<dev>`.

#### Scenario: Dev container gets the probe

- **WHEN** `mu dev --vid 0483 --pid 3754` runs
- **THEN** the container argv carries `--device /dev/bus/usb/<bus>/<dev>`

#### Scenario: No selector, no device flag

- **WHEN** `mu dev` runs with no probe selector
- **THEN** no `--device` flag is emitted (unchanged behaviour)
