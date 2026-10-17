---
id: req-026
title: "WL55JC CM0+ dual-core bring-up"
kind: requirement
status: in-progress
size: M
lane: bmad-advisory
parent: epic-002
links:
  openspec: none
  bmad: []
worktree: none
branch: none
---

# WL55JC CM0+ dual-core bring-up

## Requirement

Make the WL55JC CM0+ (cpu1) run standalone. Today it runs only under debug; its
standalone bring-up is open (`spike-006`). V1 treats this as a documented limitation
(`ops-027`) — this requirement carries the fix.

## Context

- `spike-006`: `PWR_CR4.C2BOOT` (0x5800040C bit 15) doesn't persist after the M4's
  runtime write; the CM0+ double-faults on boot. Suspects: GTZC/option bytes
  (`C2BOOT_LOCK`, `SRRVR`, `SFSA`), SRAM2 security, CPU2 clocking (HCLK2).
- The release constructor works (M4 runs it), and `stm32wlx.cpu1` examines under debug
  (`bug-021`, `bug-023`, `bug-024`).
- Investigation dispatched 2026-10-16 (spike-006 continuation); file a `bug` with the
  repro once the root cause is known.

## Acceptance

- [ ] The CM0+ boots and runs from `0x08020000` (probe readback / its counter advances),
      and debug attach works — proven live on NUCLEO-WL55JC.
