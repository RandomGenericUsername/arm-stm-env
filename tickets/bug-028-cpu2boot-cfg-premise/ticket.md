---
id: bug-028
title: "cpu2-boot.cfg asserts a false premise (CPU2 clears C2BOOT) and clobbers PWR_CR4 with a full-register write"
kind: bug
status: done
lane: direct
severity: S3
links:
  openspec: none
  bmad: []
worktree: .worktrees/bug-028/
branch: ticket/bug-028-cpu2boot-cfg-premise
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

## Fix

- `engine/templates/renderer.py:_cpu2_boot_cfg` (bug-023/028): comment now states
  the **measured** fact — C2BOOT is retained, the re-assert is defensive — and
  the write is **masked**: OpenOCD `mmw <addr> <set> <clear>` with
  `set == clear == value & mask`, so only bit 15 is forced and every other
  `PWR_CR4` bit is preserved. The hook (`examine-end` on cpu0) is kept: it is
  not shown to be harmful, and it makes the sibling examinable however the
  session got here.
- The mask comes from the pack fact (`packs/stm32wl55jc.yaml` `cpu2_boot.writes`
  `mask: 0x00008000`), not hardcoded — a multi-bit boot write stays masked to
  exactly those bits (asserted by test).
- Regression tests: `engine/templates/tests/test_renderer.py`
  `test_cpu2_boot_cfg_uses_masked_write_and_no_false_premise` (exact hook line,
  no ` mww `, no "clears C2BOOT when it idles", `RETAINED` present) and
  `test_cpu2_boot_cfg_masked_write_follows_pack_mask`.

## Evidence

Rendered a WL55JC project (no hardware, no flash):

```
uv run python -c "… renderer.render(load_file('packs/stm32wl55jc.yaml'), 'c', out) …"
--- probe/cpu2-boot.cfg ---
# stm32wl55jc probe/cpu2-boot.cfg — keep the sibling debuggable (bug-023/028).
# C2BOOT is RETAINED, not hardware-cleared: measured on WL55JC, PWR_CR4
# stayed 0x00008000 while the CM0+ ran (RM0453 has no auto-clear; the
# errata workaround clears it in software). The bug-023 'CPU2 clears
# C2BOOT when it idles' premise was false; this re-assert is defensive,
# so the sibling is examinable however the session got here.
# Masked write (mmw addr set clear) — bit 15 only. The previous full-register
# `mww` clobbered every other PWR_CR4 bit.
stm32wlx.cpu0 configure -event examine-end { mmw 0x5800040C 0x00008000 0x00008000 }
```

- Test evidence: `make test` → `357 passed in 1.11s` (was 355 before the two new
  tests).
- Failing-as-expected on the pre-fix renderer (`git stash push -- engine/templates/renderer.py`):
  `uv run python -m pytest engine/templates/tests/test_renderer.py -q -k cpu2`
  → `2 failed, 24 deselected`; both pass after the fix.
- Hardware re-verification: **not run** (the NUCLEO-WL55JC is not exclusively
  held by this task; this is a config-text change, and no claim here depends on
  a fresh flash).