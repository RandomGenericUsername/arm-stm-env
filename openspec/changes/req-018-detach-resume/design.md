# Design

## Context

See proposal.md. cortex-debug ends a session by `interrupt → break-delete →
disconnect` (or `detach` on the "Disconnect" variant). OpenOCD leaves the core
halted unless it is resumed before the session ends.

## Goals / Non-Goals

**Goals:** the firmware keeps running after ending a debug session via detach.

**Non-Goals:** fixing plain "Stop" (disconnect) — upstream OpenOCD behaviour.

## Decisions

- **D1 — `gdb-detach` event config.** Generate `probe/resume-on-detach.cfg`:
  ```
  $_TARGETNAME configure -event gdb-detach { resume }
  ```
  and add it to `configFiles`. Rationale: the event fires on detach and resumes
  the target.
- **D2 — Verified live.** gdb `monitor reset run` then `detach` (with the cfg) →
  `stm32f4x.cpu curstate` = `running`; without it → `halted`. Baseline
  disconnect (no detach) → `halted` (the unfixable path).
- **D3 — Guidance in the file.** The cfg carries a comment telling the user to
  end with "Disconnect" (detach), not plain "Stop".

## Risks / Trade-offs

- [Risk] Plain "Stop" still halts → Mitigation: documented; upstream bug.
- [Risk] Dual-core: `$_TARGETNAME` is the last target → Mitigation: acceptable
  for now; per-core event wiring is a follow-up.

## Verification plan

- Unit: `render(..., vscode=True)` writes the cfg and lists it in `configFiles`.
- Live: `curstate` `running` after detach (design D).
- `make test` green; `openspec validate req-018-detach-resume` green.

## Open Questions

- cortex-debug `overridePreEndSessionCommands` to also resume on plain "Stop"?
