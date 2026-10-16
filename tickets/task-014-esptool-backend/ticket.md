---
id: task-014
title: "E2 — esptool probe backend (FlashPort only) + UART probe binding"
kind: task
status: proposed
lane: inherits
parent: req-022
links:
  openspec: none
  bmad: none
worktree: none
branch: none
---

# E2 — esptool probe backend (FlashPort only) + UART probe binding

## Parent

`req-022` — lane inherited from parent.

## Work

Add `engine/adapters/esptool.py` implementing **FlashPort only** (no DebugPort — AD-12):
`render_argv` (`esptool --port <endpoint> --baud … write-flash <addr> <bin> …` from the pack's
declared offsets), `flash`, `proof_for` (parse `Hash of data verified.`), `last_transcript`.
Register UART autodetect VIDs (`10C4` CP210x, `1A86` CH340) via the R4 per-family mechanism, and
bind a `/dev/ttyUSB*` node as the endpoint.

## Done-when

`mu flash --mcu-config esp32cam --files … --dry-run` prints the correct esptool argv; transcript
parsing is unit-tested against the live spike-007 transcripts; `make test` green. Governed by
AD-3, AD-12, AD-14. Depends on R1, R4.
