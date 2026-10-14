---
id: spike-005
title: "H755 single-step doesn't advance (stlink-dap)"
kind: spike
status: consumed
lane: direct
timebox: 3h
questions:
  - "Why does gdb single-step (`stepi`/`next`) not advance on the H755 (both cores) via stlink-dap?"
  - "Is it the ST OpenOCD fork, the STLINK-V3, gdb 16.3, or the config?"
  - "Does the F411RE (HLA `stlink`) step normally (i.e. is this H7/DAP-specific)?"
links:
  openspec: none
  bmad: none
worktree: none
branch: none
---

# H755 single-step doesn't advance (stlink-dap)

## Findings (2026-10-14)

`F5` → *Debug M7* on the H755 attaches and **runs/halts**, but **stepping does
not advance**: the PC never moves.

Reproduced from the container (no VS Code), so it is not a cortex-debug/UI issue:

```
# M7 (cpu0, port 3333)
monitor reset halt → pc 0x80002f8 (Reset_Handler)
stepi              → pc 0x80002f8   (unchanged)
stepi              → pc 0x80002f8   (unchanged)

# M4 (cpu1, port 3334)
reset → pc 0x810029c ; stepi → 0x810029c ; stepi → 0x810029c

# also broken WITHOUT probe/resume-on-detach.cfg
```

- Affects **both** H7 cores → not M7-specific.
- `run`/`halt`/`flash`/`verify` all work (the blink runs); only single-step is dead.
- Not our resume cfg (reproduced with and without it).
- Sibling lesson: sibling repos never debugged the H755 (their `launch.json`
  pointed at `stm32f4x.cfg`) — no prior art to copy.

## Open / next

- Confirm the F411RE (HLA `stlink`) steps normally → scope to H7/DAP if so.
- Try `interface/stlink.cfg` (HLA) on the H7 cpu0 as a stepping fallback.
- Check the ST-fork `stlink-dap` step path / OpenOCD `-d3` for step errors.
- Check gdb version interactions (16.3.90).

Implementation output is a failure for a spike; file a `bug` once the cause is
known.
