---
id: bug-003
title: "Flash fails on second run without power cycle"
kind: bug
status: repro-confirmed
lane: openspec-single
severity: S2
links:
  openspec: none
  bmad: none
worktree: none
branch: none
repro: "flash --probe stlink --image build/fw.elf (twice in a row)"
observed: "Second run exits 1: 'target not halted'"
expected: "Second run exits 0, verifies OK"
---

# Flash fails on second run without power cycle

## Repro

`flash --probe stlink --image build/fw.elf` (twice in a row)

## Observed

Second run exits 1: `target not halted`.

## Expected

Second run exits 0, verifies OK.

## Fix notes

Suspect missing reset/halt before second attach. Needs regression test flashing twice.
