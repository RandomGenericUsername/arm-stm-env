# Design

## Context

See proposal.md. `resolve_probe_binding` returned `None` with no selector, and
the CLI rejected that. The resolution primitives (`_match_usb`,
`_usb_device_node`) already exist.

## Goals / Non-Goals

**Goals:** zero-config for the single-probe case; clear errors otherwise.

**Non-Goals:** probe VID list in packs; non-USB probes.

## Decisions

- **D1 — Auto-detect by probe VID.** `_PROBE_VIDS = ("0483",)` (all ST probes).
  Scan sysfs; 1 match → binding (selector = serial or `VID:PID`); 0 → `None`;
  >1 → `ValueError` listing `VID:PID(serial)`. Rationale: the shim is the host
  layer (AD-9) and holds probe/host knowledge; a VID list is the minimal signal.
- **D2 — Explicit selectors unchanged.** `--device` still wins; `--vid/--pid/
  --serial` still filter. Auto-detect only fills the no-selector case.
- **D3 — Message.** "no debug probe found; attach a board (or pass …)".

## Risks / Trade-offs

- [Risk] Hardcoded `0483` is ST-specific → Mitigation: documented; packs could
  declare the probe VID later.
- [Risk] Multiple probes now error where they previously errored differently →
  Mitigation: the new message lists the found probes + serials.

## Verification plan

- Unit: empty sysfs → `None`; one probe → binding; two → `ValueError`.
- Live: `mu dev` (no selector) → `--device /dev/bus/usb/003/045`.
- `make test` green; `openspec validate req-020-probe-autodetect` green.

## Open Questions

- Declare probe VID/PID in the pack's `probe` block?
