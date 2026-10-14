# Spec Delta

## Purpose

A single attached probe is used without any selector flags.

## ADDED Requirements

### Requirement: Probe resolution auto-detects a single probe

With no probe selector, the shim SHALL auto-detect the attached probe: exactly
one → use it; none → no binding; more than one → error naming the candidates and
requiring a selector. Explicit selectors SHALL still take precedence.

Evidence: req-020; live dry-run resolved `/dev/bus/usb/003/045` with no selector.
Verify: `resolve_probe_binding(os_name="linux")` against a fixture sysfs with one
probe → binding; empty → `None`; two → `ValueError`.

#### Scenario: One probe, no flags

- **WHEN** `mu dev` / `mu flash` runs with no selector and one probe attached
- **THEN** that probe's USB node is used automatically

#### Scenario: Several probes

- **WHEN** two probes are attached and no selector is given
- **THEN** the command fails naming both, and a selector is required

#### Scenario: No probe

- **WHEN** no probe is attached
- **THEN** the command fails with "no debug probe found; attach a board"
