---
id: bug-028
title: "cpu2-boot.cfg asserts a false premise (CPU2 clears C2BOOT) and clobbers PWR_CR4 with a full-register write"
kind: bug
status: triage
lane: direct
severity: S3
links:
  openspec: none
  bmad: []
worktree: none
branch: none
repro: "read probe/cpu2-boot.cfg in a generated WL55JC project; measure PWR_CR4 (0x5800040C) while the CM0+ runs"
observed: "the generated cfg comments 'CPU2 clears C2BOOT when it idles' and does 'mww 0x5800040C 0x00008000' — a full-register write; but PWR_CR4 stayed 0x00008000 while the CM0+ ran (C2BOOT is retained per RM0453), so the premise is false and the write clobbers any other PWR_CR4 bits."
expected: "the cfg comment reflects C2BOOT retention, and the re-assert is masked (bit 15 only) or removed if unnecessary"
---

# cpu2-boot.cfg asserts a false premise and clobbers PWR_CR4

## Repro

```sh
cat probe/cpu2-boot.cfg      # generated WL55JC project
# and, with the CM0+ running: openocd … -c 'mdw 0x5800040c 1'   # PWR_CR4
```

## Observed

`engine/templates/renderer.py:850,865` generate:

```
# CPU2 clears C2BOOT when it idles, after which cpu1's examine fails;
stm32wlx.cpu0 configure -event examine-end { mww 0x5800040C 0x00008000 }
```

Measured: while the CM0+ ran (counter advancing), `PWR_CR4` stayed `0x00008000`
across sessions — **C2BOOT is retained** (RM0453; the errata workaround clears it
*in software*, there is no HW auto-clear). So the premise (from `bug-023` §4) is
false; the hook is dead code whose full-register `mww` would clobber other
`PWR_CR4` bits.

## Expected

The comment states the retained behavior, and any re-assert is masked to bit 15
(OpenOCD `mmw … 0x00008000 0x00008000`) — or the cfg is removed if unnecessary.

Refs: `bug-023`, `bug-026`, `spike-006`.