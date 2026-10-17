---
id: bug-031
title: "probe/cpu2-boot.cfg writes C2BOOT on examine-end, masking bug-027 and invalidating sibling-release measurements"
kind: bug
status: triage
lane: direct
severity: S3
links:
  openspec: none
  bmad: []
worktree: none
branch: none
repro: "attach a WL55JC that is in the bug-027 ROM-stuck state, once with probe/cpu2-boot.cfg sourced and once without, and read PWR_CR4 (0x5800040C)"
observed: "with the file sourced, PWR_CR4 reads 0x00008000 in every session — including when the M4 never ran — so the CM0+ looks released when it was not; without it the same sessions read 0x00000000. The M4's own constructor alone is sufficient (counter 0x06->0x07->0x09 at 0x2000C01C), and clearing C2BOOT does not stop a running CM0+ (0x1d->0x24->0x27 across mww ... 0x00000000)."
expected: "probe/cpu2-boot.cfg is removed, or clearly marked 'diagnostics only — corrupts the sibling-release measurement'"
---

# `probe/cpu2-boot.cfg` masks `bug-027` and invalidates sibling-release measurements

## Repro

Attach the WL55JC twice — once with `-f probe/cpu2-boot.cfg`, once without — on a
board in the `bug-027` ROM-stuck state (M4 parked at `0x1fff2b9e`), then read
`PWR_CR4` (`0x5800040C`) and the CM0+ counter (`0x2000C01C`).

## Observed

- **With the file:** `PWR_CR4 = 0x00008000` in every session, even when the M4 never
  booted → the sibling looks released when it was not.
- **Without it:** the same sessions read `0x00000000` → the truth.
- The file's premise is **unnecessary**: the M4's `mu_release_sibling` constructor
  alone releases the sibling (counter `0x06 → 0x07 → 0x09`), and clearing C2BOOT does
  **not** stop an already-running CM0+ (`0x1d → 0x24 → 0x27`).

## Expected

`probe/cpu2-boot.cfg` is removed, or explicitly marked as a diagnostics-only aid
that corrupts the sibling-release measurement.

## Fix notes

`C2BOOT` is a **boot-request bit, not a live gate** (measured). If the file is kept
for the attach path, gate it behind an explicit opt-in (env var / separate target)
so routine attach does not silently set it.

Refs: `bug-023`, `bug-028`, `bug-029`, `bug-027`.