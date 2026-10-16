---
id: ops-027
title: "WL55JC: record the clean-from-zero flash/run ritual (M4 LED) and settle the CM0+ scope"
kind: ops-task
status: proposed
size: S
lane: direct
links:
  openspec: none
  bmad: none
worktree: none
branch: none
---

# WL55JC: record the clean-from-zero flash/run ritual (M4 LED) and settle the CM0+ scope

> `ops-task`; no `parent:`.

## Work

V1's done-when is create → build → flash → run per pack **from clean machines per
pack proof rituals** (`tickets/epic-001-universal-framework/epic.md:30`,
`_bmad-output/initiative-universal-mcu-env/spec-universal-mcu-env/spec-universal-mcu-env.md:65-67`).
The recorded clean-from-zero ritual covers only F411RE + H755ZI-Q
(`docs/vscode-debug.md:156-161`); the WL55JC (third V1 board) has **no row**, even
though its M4 LED is proven live on the bench
(`tickets/bug-021-wl55-dual-core/ticket.md:51-52`).

1. Run `docs/vscode-debug.md` §9 ("Clean test from zero") for `stm32wl55jc` — fresh
   project + fresh container + real hardware — and record the result: probe
   openocd picks, `Verified OK` (both regions), M4 LED (PB15) toggling.
2. Settle the **CM0+ scope** for the V1 proof. The sibling core does not run
   standalone (`tickets/spike-006-wl55-cm0p-bringup/ticket.md`); it runs only under
   debug (`tickets/bug-023-sibling-attach/ticket.md:53`). Either it is a V1 gate
   (then it blocks closure) or it is a **recorded limitation** with the M4 LED as
   the pack proof ritual — `device-matrix.md:14` allows LED/RTT/UART. Record the
   decision and its basis here, and in the pack note if a limitation.

## Done-when

`docs/vscode-debug.md` §9 carries a WL55JC row reproducing `Verified OK` + M4 LED
from a clean machine, and the CM0+ gate-vs-limitation decision is recorded.
