---
id: ops-037
title: "Reject bug-029 (measurement error); record the spike-006 correction; file bug-030/031"
kind: ops-task
status: done
size: S
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/ops-037/
branch: ticket/ops-037-bug029-reject-file-new-bugs
---

# Reject bug-029 (measurement error); record the spike-006 correction; file bug-030/031

> `ops-task`; no `parent:`.

## Work

The bug-029/bug-027 investigation returned a result that **contradicts two of this
repo's earlier claims** — including one of my own. Verified both independently before acting.

- **bug-029 rejected**: the probe address was wrong. `0x2000C000` is GCC's
  `completed.1` (always 0); the CM0+ `counter` is at **`0x2000C01C`**
  (`arm-none-eabi-nm -S -n`). Re-verified on the bench: `PWR_CR4 = 0x00008000` written
  by the M4's own constructor and the counter advances `0x06 → 0x07`. **The CM0+ boots
  and runs; `bug-026`'s fix is complete end-to-end.**
- **C2BOOT is a boot-request bit, not a live gate** — clearing it does not stop a
  running CM0+ (counter keeps advancing across `mww … 0x00000000`).
- **`bug-027` is real and device-level**: 53% boot rate (18/34), measured at the reset
  vector, reproduces under probe-rs; needs a physical-reset test (blocked on the user).
- **New bugs filed:** `bug-030` (no generated attach path for the M0+), `bug-031`
  (`cpu2-boot.cfg` masks `bug-027`).
- Corrections recorded on `spike-006`, `bug-026` and `bug-027` so the record stops
  asserting the disproved "C2BOOT doesn't persist / double-faults" story.

## Evidence

`nm` output locating `counter`; five bench `reset run` attempts (3 booted → counter
advances, 2 stuck in ROM per bug-027 but counter still advancing); `arm-none-eabi-nm`
section ordering; `mdw` of `PWR_CR4`/`FLASH_SRRVR`/`OPTR`.

## Done-when

`bug-029` rejected with reason, corrections recorded, new bugs filed + dispatched. ✅