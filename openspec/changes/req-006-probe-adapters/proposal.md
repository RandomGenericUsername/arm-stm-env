# Proposal

## Why

Adapters are where certified models become device effects: OpenOCD rendering (first backend) plus the probe-rs second path, both filling core-owned structs. Without them, verbs end at dry-run — this story makes `flash` real (modulo HW smoke, which needs a probe).

Evidence: work-split view story 4; port ABCs already in `engine/adapters/__init__.py` (req-005). Verify: `rg "class ProbeAdapter" engine/adapters/__init__.py`.

## What Changes

- `OpenOCDAdapter` implementing `ProbeAdapter`: renders `openocd -f <interface> -f <target>` (+ DUAL_CORE serial flows) from the certified model, parses per-piece results, fills proof structs. Spike-001 corrected targets are the test vectors.
- `ProbeRSAdapter` skeleton (second backend): chip-arg rendering + result mapping; defers live-probe proof to HW smoke (OPEN).
- Conformance tests against the port ABCs; subprocess faked (no OpenOCD binary required); HW smoke explicitly out of scope (no probe on this machine).

## Capabilities

### New Capabilities

- `probe-adapters`: OpenOCD rendering + probe-rs skeleton, port conformance.

### Modified Capabilities

(none)

## Impact

- New code: `engine/adapters/openocd.py`, `engine/adapters/probe_rs.py`, conformance tests.
- Out of scope: HW smoke test, images (req-007), esptool/avrdude adapters (later packs).
