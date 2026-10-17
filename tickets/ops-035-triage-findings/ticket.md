---
id: ops-035
title: "Triage the two dispatched investigations; file the resulting bugs/verdict"
kind: ops-task
status: done
size: S
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/ops-035/
branch: ticket/ops-035-triage-findings
---

# Triage the two dispatched investigations; file the resulting bugs/verdict

> `ops-task`; no `parent:`.

## Work

Two background investigations were dispatched (spike-006 CM0+, CubeCLT). Their
findings were independently re-verified and filed:

- **`bug-026`** (S1) — `_LINKER` emits no `.init_array` / `__init_array_start/end`,
  so `__libc_init_array` runs nothing and `--gc-sections` drops
  `mu_release_sibling`; the CM0+ is never released. Reproduced:
  `objdump -t main-M4.o` shows the ctor, the ELF does not; `PWR_CR4=0` after flash.
- **`bug-027`** (S2) — M4 app starts only ~2/6 after an OpenOCD `reset` (sits in
  ROM at `0x1fff2cc0`); independent of bug-026.
- **`bug-028`** (S3) — `cpu2-boot.cfg` false premise ("CPU2 clears C2BOOT") and a
  clobbering full-register `mww 0x5800040C`.
- **`req-027`** — CubeCLT verdict recorded (exclude from images; optional host
  tool), with the SLA0048 evidence.

Fixes are dispatched to subagents; this ticket is the management/triage record.

## Evidence

Re-verified in-repo: `objdump`/`nm`/section check on the generated WL55JC ELF;
`PWR_CR4` readback; `images/cpp.Dockerfile` pins; SLA0048 clauses fetched via
reader proxy (st.com direct = curl 92/HTTP 000).

## Done-when

Findings filed as tickets and routed for execution. ✅