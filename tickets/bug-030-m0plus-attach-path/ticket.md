---
id: bug-030
title: "WL55JC flash path never creates stm32wlx.cpu1; no generated way to attach the M0+ after make flash"
kind: bug
status: triage
lane: direct
severity: S2
links:
  openspec: none
  bmad: []
worktree: none
branch: none
repro: "make flash on a generated WL55JC project, then openocd -f probe/dual-core.cfg -f target/stm32wlx.cfg -c 'init' -c 'reset run'"
observed: "the Makefile flash targets (Makefile:55,103) never source probe/dual-core.cfg, so stm32wlx.cpu1 is unknown after make flash; forcing dual core with a reset fails ('Failed to read memory at 0xe000ed00', '[stm32wlx.cpu1] AP write error, reset will not halt', 'unknown/unexpected STLINK status code 0x11'). Attaching AFTER the M4 booted works: arp_examine -> Cortex-M0+ r0p1 detected, pc 0x08020174."
expected: "a documented, generated way to attach/debug the M0+ after make flash (e.g. a make debug-m0plus target or README recipe), since the pack declares dual_core: true"
---

# WL55JC flash path never creates `stm32wlx.cpu1`; no generated way to attach the M0+

## Repro

```sh
docker run --rm --device-cgroup-rule 'c 189:* rmw' -v /dev/bus/usb:/dev/bus/usb \
  -v <proj>:/project -w /project -e MU_PROBE_SERIAL=001C00374741500220383733 \
  ghcr.io/randomgenericusername/lang-cpp:15.3.rel2 make flash
openocd -f interface/stlink-dap.cfg -f probe/probe-serial.cfg \
         -f probe/dual-core.cfg -f target/stm32wlx.cfg -c 'init' -c 'reset run'
```

## Observed

- `DUAL_CORE` must be set **before** `target/stm32wlx.cfg`; the flash targets
  deliberately omit it (`engine/templates/renderer.py`), so after `make flash`
  `stm32wlx.cpu1` does not exist (`Target: stm32wlx.cpu1 is unknown`).
- Forcing dual core *with* a reset breaks the session: examination fails while the
  sibling is still in reset (`0xe000ed00`), and `reset` on the pair errors with
  `AP write error, reset will not halt` / STLINK status `0x11`.
- **Workaround that works:** attach *after* the M4 has booted, with no reset —
  `stm32wlx.cpu1 arp_examine` → `Cortex-M0+ r0p1 processor detected`,
  `pc: 0x08020174` (inside the M0+ `main` loop), `msp 0x2000fff8`.

## Expected

A generated, documented path to attach/debug the M0+ after `make flash`.

## Fix notes

Add a `debug-m0plus`-style recipe (sourcing `probe/dual-core.cfg`, **attach, never
reset** — mirroring `bug-024`'s attach-only rule) to the generated Makefile/README,
so the sibling is attachable without hand-assembled openocd argv.

Refs: `req-026`, `bug-023`, `bug-024`, `bug-029`.