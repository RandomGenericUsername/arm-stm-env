---
id: ops-027
title: "WL55JC: record the clean-from-zero flash/run ritual (M4 LED) and settle the CM0+ scope"
kind: ops-task
status: done
size: S
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/ops-027/
branch: ticket/ops-027-wl55-clean-run
---

# WL55JC: record the clean-from-zero flash/run ritual (M4 LED) and settle the CM0+ scope

> `ops-task`; no `parent:`.

## Work

V1's done-when is create → build → flash → run per pack **from clean machines per
pack proof rituals** (`tickets/epic-001-universal-framework/epic.md:30`,
`spec-universal-mcu-env.md:65-67`). The recorded clean-from-zero ritual covered only
F411RE + H755ZI-Q (`docs/vscode-debug.md:156-161`); the WL55JC had no row.

1. Ran `docs/vscode-debug.md` §9 for `stm32wl55jc` — fresh project + fresh
   container + real hardware.
2. Settled the CM0+ scope (below).

## Evidence (2026-10-16, NUCLEO-WL55JC, probe `0483:374e` serial `001C00374741500220383733`)

- `uv run mu create --mcu-config stm32wl55jc --lang c --name wl55-clean` → M4 + M0+ trees.
- `uv run mu build --project-dir …/wl55-clean` → both ELFs
  (`build/M4/stm32wl55jc-M4.elf` = 824 B text; `build/M0+/stm32wl55jc-M0+.elf` = 640 B text).
- Fresh container, probe pinned by serial:
  `docker run … -e MU_PROBE_SERIAL=001C0037… lang-cpp:15.3.rel2 make flash` →
  **`** Verified OK **` ×2** (M0+ then M4 — sibling-first order, bug-023), rc 0.
  OpenOCD log: `STLINK V3J12M3 … VID:PID 0483:374E`, `flash size = 256 KiB`,
  `stm32wlx.cpu0 Cortex-M4 r0p1 processor detected`.
- **Run proof (probe readback, the top rung — `spec:69`):** `GPIOB_ODR` (`0x48000414`)
  samples alternate `00008000` ↔ `00000000` → **PB15 toggling** (~2 Hz).
  PB15 = on-board LD1 (UM2592), declared by `packs/stm32wl55jc.yaml` (`ops-017`).
  ```
  openocd -f interface/stlink-dap.cfg -f probe/probe-serial.cfg -f target/stm32wlx.cfg \
    -c 'init' -c 'targets stm32wlx.cpu0' -c 'reset run' \
    -c 'mdw 0x48000414 1' -c 'sleep 260' -c 'mdw 0x48000414 1' … 
  → 0x48000414: 00008000 / 00008000 / 00008000 / 00000000 / 00000000
  ```

## CM0+ scope decision

**The V1 gate is satisfied by the M4 LED; the CM0+ standalone run is a documented
limitation (not a gate).** Basis: the WL55 pack's declared proof ritual is the M4
LED blink (`ops-017`; `device-matrix.md:14` accepts LED, and `spec:69` puts probe
readback first — satisfied above). The CM0+ sibling runs only under debug
(`bug-023:53`); its standalone bring-up stays open in `spike-006` (C2BOOT doesn't
persist, CM0+ double-faults) as a **post-V1** dual-core item. Flag for override if
a live CM0+ proof is intended as a gate.

## Done-when

`docs/vscode-debug.md` §9 carries a WL55JC row reproducing `Verified OK` + the M4
LED from a clean machine, and the CM0+ gate-vs-limitation decision is recorded. ✅
