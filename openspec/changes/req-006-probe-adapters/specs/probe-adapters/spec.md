# Spec Delta

## Purpose

Probe adapters translate certified device models into tool invocations and tool output into comparable proof — never parsing device semantics themselves.

## ADDED Requirements

### Requirement: OpenOCD renders from model only

The adapter SHALL build argv strictly from model fields (interface/target/DUAL_CORE from the pack's openocd block + endpoint address from shim). No hardcoded board names in adapter code.

Evidence: AD-2/AD-3. Verify: `rg -i "nucleo|f411|h755|wl55" engine/adapters/openocd.py` empty.

#### Scenario: H755 dual session

- **WHEN** the model carries stlink-dap + h745zi board + DUAL_CORE
- **THEN** argv contains both `-f` files and the dual-core session flag, verified against faked transcript

### Requirement: Results map to proof structs comparably

Per-piece results SHALL fill the core-owned proof struct (rung + payload); OpenOCD and probe-rs payloads for the same rung SHALL compare field-for-field.

Evidence: AD-9/AD-10 + F3 fix. Verify: cross-adapter comparability test.

#### Scenario: Same rung both backends

- **WHEN** OpenOCD and probe-rs adapters certify readback for one model
- **THEN** payloads are field-equal

### Requirement: HW smoke stays explicitly open

Anything requiring a physical probe SHALL be marked OPEN (not faked into green): live flash, live readback bytes, DUAL_CORE session reality.

Evidence: no probe on this machine (spike-001 open thread). Verify: test suite has zero tests claiming live-probe results; OPEN list in ticket.

#### Scenario: Future probe run

- **WHEN** a physical probe becomes available
- **THEN** the recorded fixtures replay against live runs before any live claim ships
