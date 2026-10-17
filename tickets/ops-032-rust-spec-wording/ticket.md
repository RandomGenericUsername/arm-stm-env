---
id: ops-032
title: "Amend the spec success signal for the Rust build-parity decision"
kind: ops-task
status: proposed
size: XS
lane: direct
links:
  openspec: none
  bmad: none
worktree: none
branch: none
---

# Amend the spec success signal for the Rust build-parity decision

> `ops-task`; no `parent:`.

## Work

The `spike-008` decision (2026-10-16) made **Rust build-parity for V1** — the flash/run
gate rests on the C/C++ LED proof per board. But the product artifacts still say every
cell flashes + runs:

- `_bmad-output/…/spec-universal-mcu-env/spec-universal-mcu-env.md:65-67` — "each V1
  matrix cell (3 STM32 boards × 3 languages) completes create → build → **flash** and
  the board runs".
- `_bmad-output/…/spec-universal-mcu-env/device-matrix.md:3` — "Each cell must complete
  create → build → **flash** → observable proof".

Amend both to reflect: **C/C++ = flash/run + observable proof; Rust = build-to-ELF
parity** (per `spike-008`, `docs/flash-run-evidence.md` "Scope note"). This edits a
finalized BMAD spec artifact — do it as a deliberate spec amendment (broad-scope rule),
not a silent doc tweak.

## Done-when

`spec:65-67` and `device-matrix.md:3` state the C/C++-vs-Rust distinction, and
`spike-008` links to the amendment.
