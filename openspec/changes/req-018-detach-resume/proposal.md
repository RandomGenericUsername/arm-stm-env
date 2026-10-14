# Proposal

## Why

After stopping a Cortex-Debug session the firmware stays **halted** — a blinking
LED freezes on/off. Cause: stock OpenOCD does not implement a proper GDB
`detach` and leaves Cortex-M in debug mode (cortex-debug issue **#894**; the
maintainer: "no [client-side] workaround"). Confirmed live 2026-10-14:
`stm32f4x.cpu curstate` = `halted` after a plain disconnect, `running` after a
resume-before-detach.

## What Changes

- `create --vscode` also writes **`probe/resume-on-detach.cfg`**
  (`$_TARGETNAME configure -event gdb-detach { resume }`) and adds it to each
  launch config's `configFiles`.
- Docs/comment in the file: end the session with **"Disconnect"** (detach) to
  keep the firmware running.

## Capabilities

### Modified Capabilities

- `template-generation`: emit `probe/resume-on-detach.cfg` + wire it into launch.

## Impact

- Code: `engine/templates/renderer.py`, tests. No pack/model change.
- **Out of scope:** making cortex-debug's plain "Stop" (disconnect, no detach)
  resume — that path cannot be fixed client-side (upstream OpenOCD bug).

Evidence: cortex-debug #894; live `curstate` probe (design D).
