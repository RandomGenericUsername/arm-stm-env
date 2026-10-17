---
id: bug-029
title: "CM0+ is released (C2BOOT=0x8000) but still does not run — sibling counter stays 0"
kind: bug
status: rejected
lane: direct
severity: S1
links:
  openspec: none
  bmad: []
worktree: none
branch: none
repro: "flash a generated WL55JC project (post-bug-026), then in openocd repeat 'reset run' + 'mdw 0x5800040C 1' until PWR_CR4 reads 0x00008000, then sample the CM0+ counter at 0x2000C000 several times"
observed: "PWR_CR4 = 0x00008000 (the M4 release write lands) in 3/6 runs, yet the CM0+ counter at 0x2000C000 stays 0x00000000 in every sample; in the flash session stm32wlx.cpu1 is not selectable ('Target: stm32wlx.cpu1 is unknown')"
expected: "the CM0+ boots from 0x08020000 and its counter increments (as spike-006 observed when C2BOOT was written by the debugger)"
---

# CM0+ is released (C2BOOT=0x8000) but still does not run

## Repro

```sh
docker run --rm --device-cgroup-rule 'c 189:* rmw' -v /dev/bus/usb:/dev/bus/usb \
  -v /tmp/opencode/v026/v26:/project -w /project \
  -e MU_PROBE_SERIAL=001C00374741500220383733 \
  ghcr.io/randomgenericusername/lang-cpp:15.3.rel2 make flash
# then repeat, until PWR_CR4 (0x5800040C) reads 0x00008000:
openocd … -c 'init' -c 'targets stm32wlx.cpu0' -c 'reset run' \
  -c 'mdw 0x5800040C 1' -c 'mdw 0x2000C000 1' ...
```

## Observed

- `PWR_CR4 = 0x00008000` in 3/6 runs → the M4 **did** run the release constructor
  (no debugger write: only `probe/probe-serial.cfg` was loaded; the `mww` in
  `probe/cpu2-boot.cfg` is not sourced during flash).
- Yet the CM0+ counter at `0x2000C000` reads `0x00000000` in every sample.
- In the flash session `stm32wlx.cpu1` is not selectable (`Target: stm32wlx.cpu1 is
  unknown`) — the flash path does not set `DUAL_CORE`.

`spike-006` showed the CM0+ **does** run when the *debugger* writes `C2BOOT`
(`mww 0x5800040C 0x8000` → `cpu1` examines, counter advances). So the residual is
specific to the M4's own release write, or to the session, not to the CM0+ itself.

## Expected

The CM0+ boots from `0x08020000` and its counter increments after `make flash`.

## Fix notes / open questions

- Does the constructor's **ordering / sequencing** matter (`FLASH_SRRVR.SBRV`
  `0x58004084` then `PWR_CR4.C2BOOT`), or a settle delay after the write?
- Is `bug-027` (M4 boots only ~2/6 after an OpenOCD `reset`) confounding this — in
  the runs that show `C2BOOT=0x8000`, is the CM0+ given time to boot before the
  counter is sampled?
- Is the counter address correct for this session, and does the counter live in a
  CM0+ RAM region that must be reachable while `cpu1` is out of reset?
- Would flashing with `DUAL_CORE=1` (so `cpu1` exists and can be examined) show the
  CM0+ actually halted/running rather than absent?

Refs: `bug-026`, `bug-027`, `spike-006`, `req-026`.
## Rejected (2026-10-16) — measurement error, not a product bug

The **probe address in this ticket is wrong**. `0x2000C000` is the first word of the
M0+ `.bss` — GCC's `completed.1` guard, always zero. The real `counter` is at
**`0x2000C01C`**:

```
$ arm-none-eabi-nm -S -n build/M0+/stm32wl55jc-M0+.elf
2000c000 b completed.1
2000c01c 00000004 B counter
```

Re-verified on the bench (post-`bug-026`, `cpu2-boot.cfg` NOT sourced): the CM0+
**boots and runs from the M4's own constructor** — `PWR_CR4 (0x5800040C) = 0x00008000`
and the counter advances `0x06 → 0x07` (3/3 attempts; the others hit `bug-027`).
Also measured: **C2BOOT is a boot-request bit, not a live gate** — clearing it does not
stop a running CM0+ (counter keeps advancing). So `bug-026`'s fix is complete
end-to-end and the sibling-release path works.

New work split out: `bug-030` (no generated attach path for the M0+),
`bug-031` (`cpu2-boot.cfg` masks `bug-027`). `bug-027` remains open.
