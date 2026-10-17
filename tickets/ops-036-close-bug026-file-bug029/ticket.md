---
id: ops-036
title: "Close bug-026 (verified + merged); file the residual as bug-029"
kind: ops-task
status: done
size: XS
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/ops-036/
branch: ticket/ops-036-close-bug026-file-bug029
---

# Close bug-026 (verified + merged); file the residual as bug-029

> `ops-task`; no `parent:`.

## Work

Orchestration close-out of the `bug-026` worker run.

- **Verified the fix independently** (not from the report): generated linker
  scripts carry `.init_array` between `.isr_vector` and `.text`; ELF section order
  `.isr_vector @0x08000000`, `.init_array @0x08000138`, `.text @0x08000144`;
  `__init_array_start/end` resolve; and **`mu_release_sibling` is back in the linked
  ELF** (was ABSENT before). Suite: 357 green. Merged as `c5e25a2`, then closed `done`.
- **Filed the residual as `bug-029`**: with the fix, `PWR_CR4` reads `0x00008000`
  in 3/6 resets (the M4's release write lands), but the CM0+ counter at `0x2000C000`
  stays 0 — so `req-026`'s acceptance ("CM0+ boots from 0x08020000 and the counter
  increments") is still unmet. Investigation dispatched.
- `req-026` → `in-progress` (bug-026 fixed; residual is bug-029).

## Done-when

`bug-026` done, `bug-029` filed and assigned, `req-026` in-progress, INDEX agrees. ✅