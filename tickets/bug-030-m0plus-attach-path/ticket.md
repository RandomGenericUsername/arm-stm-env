---
id: bug-030
title: "WL55JC flash path never creates stm32wlx.cpu1; no generated way to attach the M0+ after make flash"
kind: bug
status: done
lane: direct
severity: S2
links:
  openspec: none
  bmad: []
worktree: .worktrees/bug-030/
branch: ticket/bug-030-m0plus-attach-and-cpu2boot-gate
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

## Fix

`engine/templates/renderer.py`:

- `_sibling_attach` (new): the sibling's `(slug, core, openocd_target)` when —
  and **only** when — the pack declares `facets.cpu2_boot` **and** a
  target-direct `openocd.dual_core` block (that is exactly the set of packs for
  which `probe/dual-core.cfg` is emitted, so the argv can only name a second core
  that will exist). `None` otherwise.
- `_sibling_debug_section` (new): renders `make debug-m0plus` into the
  Makefile — `SIBLING_OPENOCD` (interface, probe-serial, **dual-core**, target, in
  that order) then `init`, `arp_examine`, `targets stm32wlx.cpu1`, `poll`, `halt`,
  `reg pc`, `resume`, `exit`. No reset anywhere (bug-024).
- `_readme`: a `## Attaching the sibling core` section plus an `Attach M0+` row
  in the task table, with the same argv and the "do not add `reset run`" rule.

Two commands in the argv are **not** in the ticket's measured recipe and are
needed on the OpenOCD in the image (`0.12.0+dev-00664-gc8d973bda`):

- `targets stm32wlx.cpu1` — OpenOCD's generic `halt`/`reg`/`resume` always act on
  the **first** target (`stm32wlx.cpu0`), so `stm32wlx.cpu1 halt` is not a command
  and `halt` alone halted the M4 (measured: `pc: 0x080001da`).
- `poll` — without it `halt` reports `target was in unknown state when halt was
  requested` (the target was never polled, so it is still "unknown"). `reg` is
  also **not** a per-target command in this build; `reg pc` (unprefixed) is.
  `arp_halt` halts successfully but then errors out with the usage dump (exit 1).
- The trailing `resume` + `exit` make the target a non-destructive one-shot:
  checking the sibling leaves the board running, and `make` terminates.

## Evidence

Test evidence — `make test` → `uv run python -m pytest engine/ -q` →
**360 passed** (was 357; the two bug-028 `cpu2-boot.cfg` tests are replaced by
three bug-031 tests and three bug-030 tests).

Failing-as-expected on the pre-fix renderer (`git stash push --
engine/templates/renderer.py`): `uv run python -m pytest
engine/templates/tests/test_renderer.py -q -k "sibling or cpu2_boot"` →
`5 failed, 24 deselected`; all pass after the fix.

Rendered text (no hardware), `make flash`-compatible project:

```
# --- attach the released sibling (bug-023/024/030) ---
# `make flash` flashes single-core (the sibling is asleep at reset), so
# stm32wlx.cpu1 does not exist afterwards. probe/dual-core.cfg must be
# sourced BEFORE the target config (it reads DUAL_CORE while creating the
# second core). ATTACH ONLY -- no reset: ...
SIBLING_OPENOCD = -f interface/stlink-dap.cfg -f probe/probe-serial.cfg -f probe/dual-core.cfg -f target/stm32wlx.cfg

debug-m0plus:
	$(OPENOCD) $(SIBLING_OPENOCD) -c "init" -c "stm32wlx.cpu1 arp_examine" -c "targets stm32wlx.cpu1" -c "poll" -c "halt" -c "reg pc" -c "resume" -c "exit"
```

Hardware (NUCLEO-WL55JC `001C00374741500220383733`, image
`lang-cpp:15.3.rel2`): `make flash` (2× `Verified OK`) then `make debug-m0plus`,
**8 runs → 3 attach OK, 5 blocked by bug-027**:

```
run 1: flash ok=2/2 | sibling NOT released (bug-027)
run 2: flash ok=2/2 | sibling NOT released (bug-027)
run 3: flash ok=2/2 | sibling NOT released (bug-027)
run 4: flash ok=2/2 | debug-m0plus OK pc (/32): 0x0802017c
run 5: flash ok=2/2 | sibling NOT released (bug-027)
run 6: flash ok=2/2 | debug-m0plus OK pc (/32): 0x08020178
run 7: flash ok=2/2 | sibling NOT released (bug-027)
run 8: flash ok=2/2 | debug-m0plus OK pc (/32): 0x08020178
== runs=8 attach_ok=3 sibling_not_released=5 other=0
```

The 5 failures are `Error: Failed to read memory at 0xe000ed00` /
`Examination failed` on cpu1 — the M4 never released the sibling, i.e. **bug-027**
(the M4 boots from system memory), not this change: the same runs read
`PWR_CR4 = 0x00000000` with a frozen counter. The measured **bug-027 hit rate on
this board is 5/8 (62%) here**, above the ~47% recorded in bug-027 — one board,
small sample, reported as observed. `pc 0x0802017c/0x08020178` is inside the M0+
image (`main` delay loop), matching the `0x08020174` in this ticket's Observed.

Not verified: the gdb-interactive variant (dropping `resume`/`exit`) — only the
one-shot argv was run, and only via `make debug-m0plus`; the `.vscode` attach
configs (`Debug M0+ (OpenOCD)`) were not exercised, though their `configFiles`
no longer list the removed `probe/cpu2-boot.cfg`.

Refs: `req-026`, `bug-023`, `bug-024`, `bug-029`, `bug-031`.