---
id: bug-031
title: "probe/cpu2-boot.cfg writes C2BOOT on examine-end, masking bug-027 and invalidating sibling-release measurements"
kind: bug
status: done
lane: direct
severity: S3
links:
  openspec: none
  bmad: []
worktree: .worktrees/bug-030/
branch: ticket/bug-030-m0plus-attach-and-cpu2boot-gate
repro: "attach a WL55JC that is in the bug-027 ROM-stuck state, once with probe/cpu2-boot.cfg sourced and once without, and read PWR_CR4 (0x5800040C)"
observed: "with the file sourced, PWR_CR4 reads 0x00008000 in every session — including when the M4 never ran — so the CM0+ looks released when it was not; without it the same sessions read 0x00000000. The M4's own constructor alone is sufficient (counter 0x06->0x07->0x09 at 0x2000C01C), and clearing C2BOOT does not stop a running CM0+ (0x1d->0x24->0x27 across mww ... 0x00000000)."
expected: "probe/cpu2-boot.cfg is removed, or clearly marked 'diagnostics only — corrupts the sibling-release measurement'"
---

# `probe/cpu2-boot.cfg` masks `bug-027` and invalidates sibling-release measurements

## Repro

Attach the WL55JC twice — once with `-f probe/cpu2-boot.cfg`, once without — on a
board in the `bug-027` ROM-stuck state (M4 parked at `0x1fff2b9e`), then read
`PWR_CR4` (`0x5800040C`) and the CM0+ counter (`0x2000C01C`).

## Observed

- **With the file:** `PWR_CR4 = 0x00008000` in every session, even when the M4 never
  booted → the sibling looks released when it was not.
- **Without it:** the same sessions read `0x00000000` → the truth.
- The file's premise is **unnecessary**: the M4's `mu_release_sibling` constructor
  alone releases the sibling (counter `0x06 → 0x07 → 0x09`), and clearing C2BOOT does
  **not** stop an already-running CM0+ (`0x1d → 0x24 → 0x27`).

## Expected

`probe/cpu2-boot.cfg` is removed, or explicitly marked as a diagnostics-only aid
that corrupts the sibling-release measurement.

## Fix

`probe/cpu2-boot.cfg` is **removed from the render path** — the first option in
the ticket's Expected, and the smallest change that cannot silently mask
`bug-027` again: there is no opt-in knob left to forget, no env var, no target.

- `engine/templates/renderer.py`: `_cpu2_boot_cfg` deleted; the
  `write("probe/cpu2-boot.cfg", …)` call in `render()` replaced by a comment
  recording *why* (and that it masked bug-027); the file is dropped from the
  `.vscode` `configFiles` list too — leaving it there would abort every launch
  with a missing-file error.
- bug-028 is not regressed: that ticket's *masked* `mmw … set clear` was a
  fix to a write that no longer exists at all, which is strictly weaker. The
  "no ` mww `" and "no false premise" assertions are subsumed by the new
  test below.

## Evidence

Test evidence — `make test` → `uv run python -m pytest engine/ -q` →
**360 passed**. The two bug-028 `cpu2-boot.cfg` tests are replaced by:

- `test_cpu2_boot_cfg_is_not_emitted` — the file is absent from the written
  list and no longer appears in `.vscode/launch.json`.
- `test_cpu2_boot_cfg_write_absent_from_every_generated_tool_file` — no
  generated non-`.c` file mentions `0x5800040C`, while `src/main-M4.c` (the
  M4's own release constructor — the one write that must stay) still does.

Failing-as-expected on the pre-fix renderer (`git stash push --
engine/templates/renderer.py`): `uv run python -m pytest
engine/templates/tests/test_renderer.py -q -k "sibling or cpu2_boot"` →
`5 failed, 24 deselected` (both bug-031 tests among them); all pass after.

Hardware (NUCLEO-WL55JC `001C00374741500220383733`), generated project with
`probe/cpu2-boot.cfg` deleted: 10 × `openocd … -c "reset run" -c "sleep 1500"`
then `mdw 0x5800040c`, `mdw 0x2000C01c` twice:

```
run 1: PWR_CR4=00008000 counter 00000003 -> 00000004
run 2: PWR_CR4=00008000 counter 00000003 -> 00000004
run 3: PWR_CR4=00008000 counter 00000003 -> 00000004
run 4: PWR_CR4=00008000 counter 00000003 -> 00000004
run 5: PWR_CR4=00000000 counter 00000005 -> 00000005
run 6: PWR_CR4=00000000 counter 00000005 -> 00000005
run 7: PWR_CR4=00008000 counter 00000003 -> 00000004
run 8: PWR_CR4=00000000 counter 00000005 -> 00000005
run 9: PWR_CR4=00008000 counter 00000003 -> 00000004
run 10: PWR_CR4=00000000 counter 00000005 -> 00000005
== runs=10 C2BOOT_set=6 C2BOOT_clear=4 counter_advancing=6
```

`PWR_CR4.C2BOOT` is now a **truthful** signal: it is set in exactly the 6 runs
where the CM0+ counter advances and clear in exactly the 4 runs where it does
not — i.e. the bit is written by the M4's `mu_release_sibling` constructor and by
nothing else. The 4 clear runs are **bug-027** (the M4 boots from system memory,
never releases the sibling) and are now *visible* instead of masked — which is
the whole point of this ticket. This also re-confirms that removing the cfg costs
nothing: with no debugger write at all, the sibling still releases.

Refs: `bug-023`, `bug-028`, `bug-029`, `bug-027`, `bug-030`.