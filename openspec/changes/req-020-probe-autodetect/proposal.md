# Proposal

## Why

The CLI *requires* a probe selector (`--device`/`--vid`/`--pid`/`--serial`) even
when exactly one probe is attached — so `mu dev`/`mu flash` fail with "no probe
selector given" and the user must know the probe's USB VID:PID (`0483:3752` vs
`0483:3754`). That is not transparent. It should only be needed to disambiguate
when several probes are attached.

## What Changes

- **No selector → auto-detect the single attached probe.** The shim scans sysfs
  for debug-probe VIDs (ST probes share `0483`); exactly one → use it; none →
  error "no debug probe found"; more than one → error listing them, requiring a
  selector.
- The "no probe selector" error becomes "no debug probe found; attach a board".

## Capabilities

### Modified Capabilities

- `cli-verbs`: probe resolution auto-detects a single probe.

## Impact

- Code: `engine/cli/shim.py` (`_autodetect`, `_PROBE_VIDS`),
  `engine/cli/main.py` (message), tests.
- **Out of scope:** moving the probe VID list into packs (a future refinement —
  the shim is the host layer, AD-9).

Evidence: 2026-10-14 — `mu dev --project-dir … --dry-run` with one probe and no
selector resolved `/dev/bus/usb/003/045`.
