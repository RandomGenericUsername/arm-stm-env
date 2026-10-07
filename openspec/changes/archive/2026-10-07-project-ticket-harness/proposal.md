# Proposal

## Why

BMAD and OpenSpec use different formats and directories (BMAD ticket tree under its output folder; OpenSpec `openspec/changes/`), so requirements tracked in either tool are invisible to the other. A project-owned index is needed that classifies each work item, sizes it, routes it to the right lane, and links wherever its detail lives.

Evidence: `openspec/changes/` holds per-change folders (`openspec list --json` → `"changes": []` on a fresh repo) while BMAD method help defines its own ticket tree (`tickets.toml` entries, plan-beside-toml) — two formats, no shared index. Verify: `openspec list --json; ls .agents/skills/bmod-method/help/ticketing-and-epics.md`.

## What Changes

- New `tickets/` index: item files with fixed `kind:` vocabulary (epic, requirement, bug, ops-task, spike), per-kind lifecycle, and links to BMAD artifacts and/or OpenSpec changes.
- New router (`/triage`): classifies kind first, sizes second, routes to lane (direct / single OpenSpec change / ticket + N changes / BMAD specialist advisory), asks the user explicitly when ambiguous.
- New worktree guard: no work on main, abort on dirty main, fresh `git worktree` + ticket branch per item.
- Locked decisions: bugs without repro are rejected (no parking); spike box set per spike at triage; epic BMAD split is advisory (user selects); trivial ops tasks may skip OpenSpec/BMAD but never skip git discipline.

## Capabilities

### New Capabilities

- `ticket-system`: item taxonomy, file format, INDEX, per-kind lifecycle and transitions.
- `task-router`: triage classification, sizing rubric, lane routing, explicit-ask behavior, BMAD-specialist advisory.
- `worktree-discipline`: main-clean guard, dirty-abort, worktree creation, branch naming, merge-back.

### Modified Capabilities

(none — greenfield, no existing specs.)

## Impact

- New dirs/files: `tickets/`, `tickets/INDEX.md`, router skill/command, `scripts/` guard helpers, `.worktrees/` (gitignored).
- Affects: `AGENTS.md` (routing section references the harness), `openspec/config.yaml` (unchanged rules, new capabilities own requirements).
- Out of scope: reference-sibling fetcher (`references.yaml`); actual BMAD specialist skills installation; any firmware/CLI implementation.
