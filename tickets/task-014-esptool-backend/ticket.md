---
id: task-014
title: "E2 — esptool probe backend (FlashPort only) + UART probe binding"
kind: task
status: done
lane: inherits
parent: req-022
links:
  openspec: none
  bmad: none
worktree: .worktrees/task-014/
branch: ticket/task-014-esptool-backend
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

## Evidence

2026-10-16 — branch `ticket/task-014-esptool-backend`:

- **`engine/adapters/esptool.py`** — `EsptoolAdapter(FlashPort)`; no `DebugPort` (AD-12). Argv is
  rendered from certified facts: offsets from the pack's `partitions` block in `ROLE_ORDER`
  (`bootloader`, `partition_table`, `app`), flash parameters from `esptool`, chip target from
  `sdkconfig`. Proof parses `Hash of data verified` (one per image) and fills the shared
  backend-comparable keys.
- Registered as a built-in backend (`get_adapter("esptool")`).
- **`idf-cmake` stack registered** with the digest-pinned image
  (`espressif/idf:v6.1@sha256:81893c71…`) — auto mode could not resolve an image without it, so
  this moves here from E3 (the template family stays in E3).
- **`DeviceView` now exposes family blocks** (`blocks` + `block_for`) — a generic passthrough so an
  adapter renders the facts its own family declares (AD-2/AD-13). This is the R2 leftover
  surfacing, and per AD-1's corollary it is a *framework* generalisation, not a brand special-case.
- `make test` → **329 passed**.
- Done-when (local mode is where the adapter argv is printed — auto mode prints the container argv):
  ```
  mu flash --mcu-config esp32cam --device /dev/ttyUSB0 \
    --files bootloader.bin partition-table.bin app.bin --mode local --dry-run
  esptool --chip esp32 --port /dev/ttyUSB0 --baud 460800 write-flash \
    --flash-mode dio --flash-size 4MB --flash-freq 40m \
    0x1000 bootloader.bin 0x8000 partition-table.bin 0x10000 app.bin
  ```
  (line-wrapped here; identical to the live spike-007 command.)
- Auto mode resolves the pinned image; `mu debug --mcu-config esp32cam …` is refused with
  `backend 'esptool' implements no debug port (AD-12)`.

**Gap, recorded not papered over:** containerized UART passthrough is **not** implemented — the
shim forwards a USB *node* (`/dev/bus/usb/…`) for USB probes, but esptool needs the **tty**
(`/dev/ttyUSB*`). Live flashing was proven host-side in spike-007, never inside a container.
Follow-up: resolve and forward the tty for `uart-serial` packs (extends AD-9's shim mapping).
