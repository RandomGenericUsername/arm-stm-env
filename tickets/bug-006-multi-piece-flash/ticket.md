---
id: bug-006
title: "Multi-piece flash drops pieces / exits non-zero (dual-core)"
kind: bug
status: done
lane: direct
severity: S1
links:
  openspec: []
  bmad: []
worktree: .worktrees/bug-006/
branch: ticket/bug-006-multi-piece-flash
repro: "mu flash --mcu-config stm32h755 --project-dir <h755-blink> --vid 0483 --pid 3754 --files build/M7/stm32h755-M7.elf build/M4/stm32h755-M4.elf"
observed: "each piece rendered as `program <f> verify reset exit`; a bare `reset exit` makes OpenOCD exit rc=1 → `flash verdict: FAILED 0/2`; later pieces never reached"
expected: "all pieces programmed to their own core; `flash verdict: 2/2 OK`"
---

# Multi-piece flash drops pieces / exits non-zero (dual-core)

## Repro

```sh
mu flash --mcu-config stm32h755 --project-dir <h755-blink> --vid 0483 --pid 3754 \
  --files build/M7/stm32h755-M7.elf build/M4/stm32h755-M4.elf
```

## Observed

Adapter rendered `program <piece> verify reset exit` per piece. Two failure modes:
- a per-piece `exit` stops OpenOCD after the first piece; and
- the replacement bare `reset exit` makes OpenOCD return **rc=1** (even though
  both images program + `** Verified OK **`), so `flash verdict: FAILED 0/2`.

Evidence: `openocd … -c targets -c "program M7 verify" -c "reset exit"` → rc=1;
`… -c "program M7 verify reset exit"` → rc=0.

## Expected

Both cores programmed in one invocation, verdict `2/2 OK`.

## Fix notes

- `engine/adapters/openocd.py`: select each piece's core target (`targets
  <name>`), emit `program <piece> verify reset` for non-last pieces and
  `… verify reset exit` only for the **last** (so OpenOCD exits 0 and no piece is
  dropped). `_piece_target()` maps piece index → core → target name.
- `packs/stm32h755.yaml`: `openocd.targets = {M7: stm32h7x.cpu0, M4:
  stm32h7x.cpu1}`; model/registry/loader carry it (`OpenocdConfig.targets`).
- Live 2026-10-14: 2-piece flash → `** Verified OK **` ×2, `flash verdict: 2/2 OK`.
  Regression: `test_openocd_argv_dual_core_selects_target_per_piece`.
