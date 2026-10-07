# Spec Delta

## Purpose

Worktree discipline guarantees no work ever lands directly on main and no work starts from a dirty tree, including trivial ops tasks that skip OpenSpec/BMAD ceremony.

## ADDED Requirements

### Requirement: Never work on main

All implementation and planning writes for an item SHALL happen in its worktree/branch. Direct commits to `main` are forbidden.

Evidence: user requirement "never work directly on main, always in worktrees". Verify: `git branch --show-current` inside any item worktree never outputs `main` during work.

#### Scenario: Main commit attempt

- **WHEN** an agent attempts to commit item work on main
- **THEN** the guard aborts with "work on ticket branch" before writing

### Requirement: Dirty main aborts

Before creating a worktree, the guard SHALL check `git status --porcelain` on main. Any output aborts with "main is dirty, address it first" — no stash-and-continue, no exceptions.

Evidence: user requirement "if main is dirty abort until I address it". Verify: dirty main + run guard → exit non-zero with the abort message; `git status --short` output included.

#### Scenario: Clean main proceeds

- **WHEN** main is clean
- **THEN** the guard creates `.worktrees/<item-id>/` on branch `ticket/<id>-<slug>` and records both in the item file

### Requirement: Trivial ops still obey git discipline

Ops tasks that skip OpenSpec/BMAD ceremony SHALL still pass the main-clean check and work in a worktree on a ticket branch.

Evidence: user decision "trivial can skip openspec/bmad but must follow the no-main/dirty/worktree/branch rule". Verify: a trivial ops change lands via ticket branch merge, never direct to main.

#### Scenario: Trivial fix flow

- **WHEN** a trivial ops task (e.g. bump an action version) is executed
- **THEN** it is built and committed on its ticket branch and merged to main, with the item file recording worktree and branch
