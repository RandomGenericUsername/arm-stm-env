# Design

## Context

See proposal.md (Why). Current state: empty `tickets/` (greenfield), BMAD installed with only `bmad` + `bmad-build` skills (no analyst/PM/architect agents), OpenSpec spec-driven with zero specs (`openspec list --specs` → empty). Constraint: the harness must work now with two installed skills and grow when more BMAD skills arrive — missing-skill paths must degrade to explicit user choice, never invention.

## Goals / Non-Goals

**Goals:** one index format linking both tools; kind-first routing with four locked decisions honored; git guard that cannot be skipped by any lane.

**Non-Goals:** replacing BMAD/OpenSpec formats; auto-execution of BMAD advice; reference-sibling fetcher (separate change); firmware/CLI work.

## Decisions

- **Item files as Markdown + frontmatter under `tickets/<id>-<slug>/ticket.md`, index as `tickets/INDEX.md`.** Over BMAD `tickets.toml` (tool-owned, needs its skill) and JSON (unreadable in review). Markdown renders on GitHub and `rg` validates it with one-liners.
- **Router as OpenCode command `.opencode/commands/triage.md` delegating classification to a shared doc, not a new agents skill.** Alternative (`.agents/skills/`) considered: heavier, needs skills-CLI reinstall on every edit; command files are versioned plainly and every tool here reads `.opencode/`. If a second tool needs it, wrap later.
- **Guard as `scripts/worktree-guard.sh` (exit non-zero, machine-checkable) plus skill/command text.** Alternative (text-only rule) rejected: text rules were already proven bypassable under pressure in earlier harness tests; the script is the enforceable half.
- **Worktrees under `.worktrees/` (gitignored), branches `ticket/<id>-<slug>`.** Alternative (branches without worktrees) rejected: user explicitly requires worktrees.
- **INDEX.md as data, not prose: fixed per-entry fields (link, title, status, execution links; epics add `done/total` rollup + nested child lines; bugs add severity; spikes add timebox state).** Over a free-form board. Rationale: the index is machine-checkable (`rg` count + epic-line pattern), which is what makes the stale-index scenario enforceable.

## Risks / Trade-offs

- [Risk] Only `bmad`/`bmad-build` installed → BMAD-advisory lane has no specialist to call → Mitigation: router recommends, user selects; missing skill is stated plainly, advice deferred until skills are added.
- [Risk] Markdown frontmatter validation is `rg`-based, weaker than schema → Mitigation: guard script validates `kind:` + required fields per kind; `openspec validate` covers change side.
- [Risk] INDEX.md drifts from item files → Mitigation: completeness check is a spec scenario with a one-command verify; guard runs it pre-merge.

## Verification plan

- `openspec validate --change project-ticket-harness` passes (proposal + 3 specs + design + tasks).
- `bash scripts/worktree-guard.sh --check-clean` on clean main → exit 0; with dirty main (touch a file) → exit non-zero with abort message. Exact commands in tasks.md.
- `rg` one-liners from spec scenarios run green against fixture `tickets/` samples created during apply.

## Open Questions

None — kind set, lanes, advisory-vs-mandatory, trivial-ops exemption, and per-spike box were all decided in triage discussion.
