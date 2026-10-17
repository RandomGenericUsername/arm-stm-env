---
id: ops-033
title: "Formalize the compiler-warnings policy"
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

# Formalize the compiler-warnings policy

> `ops-task`; no `parent:`.

## Work

`HANDOFF.md:42-45` lists "warnings policy" as an open thread. In practice the e2e
harness already records warnings per cell and never fails on them — `docs/e2e-evidence.md:5`
("warnings are recorded per cell and never fail (warn-only policy)"). But no explicit
decision is recorded in one place.

- Record the policy (currently: **warn-only**, warnings surfaced in the evidence, build
  does not fail) in the harness doc / a one-line policy note.
- Decide whether an opt-in strict mode (`-Werror`) is wanted; if so, file it as a small
  requirement rather than silently changing the build.

## Done-when

The warnings policy is stated in one place and referenced by the verify harness;
the `HANDOFF.md` open thread is closed.
