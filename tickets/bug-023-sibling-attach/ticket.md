---
id: bug-023
title: "WL55JC: released sibling can't be launched, primary's reset hides it, flash order boots it into an unflashed image"
kind: bug
status: done
lane: direct
severity: S2
links:
  openspec: []
  bmad: []
worktree: .worktrees/bug-023/
branch: ticket/bug-023-sibling-attach
repro: "WL55JC: make flash, then F5 -> Debug M0+ (or Debug M4+M0+)"
observed: "CM0+ launch aborts / cpu1 'unknown'; and make flash leaves the CM0+ double-faulted (booted before its image was programmed)"
expected: "both cores flash, run, and are debuggable"
---

# WL55JC sibling flow (bug-021 follow-up)

`bug-021` made the WL55's M4 work; three sibling-flow problems remained, all
reproduced on hardware.

## Root causes

1. **A released sibling cannot be *launched*.** cortex-debug's launch does
   `monitor reset halt`; on cpu1 that gives
   `AP write error, reset will not halt` → `Examination failed` → cpu1 `unknown`.
   (The cortex-debug wiki's rule for ST dual-core: attach the woken core.)
2. **The primary's reset hides the sibling.** `reset halt` on cpu0 leaves cpu1
   `unknown` until the primary runs again (the CM0+ only boots once CPU1 is
   running and has set `C2BOOT`).
3. **Flash order boots the sibling into an unflashed image.** `make flash` ran
   the primary first; its reset runs the release constructor, so the CM0+ booted
   at `0x08020000` *before* that image was programmed → double fault → lockup.
4. **CPU2 clears `C2BOOT` when it idles** → later cpu1 examines fail
   (`Failed to read memory at 0xe000ed00`).

## Fix

- Emit the release as a **constructor** (`mu_release_sibling`, runs during C-runtime
  init *before* `main`) so it happens however the debugger halts.
- Sibling configs become `request: attach` (+ `postAttachCommands` for the
  maskisr workaround, since attach runs postAttachCommands not postLaunchCommands).
- The chained compound's child gets `delayMs` (let the primary release it).
- Flash order: **siblings first, then the primary** (`ALL_FLASH = flash-M0+ flash-M4`).
- Generated `probe/cpu2-boot.cfg` re-asserts the boot bit on cpu0's
  `examine-end`, so cpu1 stays examinable (needs `openocd.targets`, added to the pack).

## Evidence

- After a fresh `make flash` (sibling-first): cpu1 → `Cortex-M0+ r0p1 processor
  detected`, `Examination succeed`; M0+ `counter` @0x2000c000 increments
  `2 → 3 → 4`; M4 LED (PB15) toggles.
- `Debug M0+` attach flow (halt + maskisr): `pc 0x80200d4 → stepi → 0x80200d6 →
  0x80200d8`, `next` advancing.
- `uv run pytest engine -q` → 276 passed.

## Open

- The **sequence** `Debug M4` then `Debug M0+` in one session is still fragile:
  the primary's `reset halt` leaves cpu1 `unknown` until the primary runs again,
  so the compound (`Debug M4+M0+`) may need the M4 continued (or a retry) before
  the child attaches. `reset-end` re-assert + `arp_examine` was tried and did
  **not** fix it.
