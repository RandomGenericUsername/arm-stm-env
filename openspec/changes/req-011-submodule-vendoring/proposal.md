# Proposal

## Why

Fresh `create`d C projects reference `vendor/...` paths that don't exist until someone hand-places CMSIS trees — every real build today needs the e2e stub workaround. Wiring pinned submodules into `create` closes the last gap between "renders" and "builds out of the box."

Evidence: e2e stub note (`engine/verify/e2e.py:10-17`); template vendor paths (`renderer.py:98-101`); upstream reachability verified 2026-10-13 (ls-remote + HTTP 200s, see spec).

## What Changes

- `create` initializes two pinned submodules per project: CMSIS core (`ARM-software/CMSIS_5` @ 5.9.0) at `vendor/CMSIS`, and the family device repo (`cmsis_device_f4@v2.6.9` / `h7@v1.9.0` / `wl@v1.4.0`) at `vendor/cmsis-device-<id>`.
- Network required at create time; failure is a clear error (no silent partial tree). Offline second-create behavior documented (submodule cache) but not implemented.
- No template path changes (references already match verified upstream layouts).

## Capabilities

### New Capabilities

- `submodule-vendoring`: pinned CMSIS submodule init at create time.

### Modified Capabilities

(none)

## Impact

- `create` gains submodule init (git CLI required on host); templates unchanged.
- Out of scope: offline submodule cache, non-STM32 vendors, submodule updates.
