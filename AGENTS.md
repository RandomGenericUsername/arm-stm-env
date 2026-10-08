# AGENTS.md — arm-stm-env operating contract

Canonical agent instructions for this repo. Claude (`CLAUDE.md` symlinks here), OpenCode, and all BMAD/OpenSpec skills must follow this.

## 1. Evidence rule (hard requirement)

No suggestion "in the air". Every technical claim, recommendation, or design decision must carry testable evidence — at least one of:

- **Doc evidence:** file path + line range, or commit SHA, or URL + quoted section. Example: `ArmDevelopmentEnvironment@last-branch: setup/create_project/create_project.py:120-180`.
- **Prototype evidence:** a script/command in-repo that runs and prints the validating output. State the exact command and observed result.
- **Test evidence:** `command run → result` (exit code + key output). Failing-as-expected counts if it validates the claim.

Format: any non-trivial claim gets an `Evidence:` line and a `Verify:` line (how to reproduce in one command). If evidence doesn't exist yet, say `Evidence: MISSING — run <X> to produce it` and do not present the claim as fact.

## 2. How we work here

- Greenfield, requirements-first. Old repos (`../ArmDevelopmentEnvironment`, `../rust-embedded-environment`) are lessons only — cite them as evidence, never copy blindly.
- Target: universal device framework (STM32 first as reference pack), device-agnostic core + device packs + user-supplied configs (one source per invocation, whole-source replacement).
- Dual-mode CLI is the spine: (a) containerized interactive dev env, (b) host-transparent `compile/build/flash` with zero host deps.
- Prefer executed output over recalled text. Read files, run commands (`rg`, `git log`, `docker`, `cargo`, `openspec validate`), paste results.
- When findings contradict an earlier claim, state the discrepancy and trust the evidence.

## 3. OpenSpec + BMAD routing (via tickets)

- All work starts as a ticket in `tickets/` (`_template/`, vocab + rollup in `INDEX.md`, flow in `LIFECYCLE.md`). Triage with `/triage` (lanes in `tickets/_fixtures/router-lanes.md`).
- Broad scope (product, requirements, architecture, cross-device design) → BMAD. Only installed skills: `bmad`, `bmad-build` — say so when a step needs a missing skill instead of improvising.
- Bounded slices (one proposal + spec + design + tasks) → OpenSpec (`/opsx-propose`, `/opsx-apply`, `/opsx-archive`). Artifact rules in `openspec/config.yaml` restate this evidence rule per artifact.
- Never work on main: `scripts/worktree-guard.sh create <id> <slug>` scaffolds `ticket/<id>-<slug>` + worktree, aborts when dirty. Record worktree/branch in the ticket.
- Keep changes small, verifiable, committable. Never mix planning edits with implementation in one turn.
