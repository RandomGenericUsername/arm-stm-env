# Tasks

## 1. Ticket format and index

- [x] 1.1 Create `tickets/` layout with `ticket.md` template (frontmatter: id, title, kind, status, links, worktree, branch; per-kind fields: epic children/done-when, bug repro/observed/expected, spike timebox/questions, task REQUIRED parent + inherits lane; `ops-task` readable as `chore`). Verify: template file exists and a sample of each of the 6 kinds parses with the required fields present (`rg "^kind:" tickets/_template/`).
- [x] 1.2 Create `tickets/INDEX.md` with epics-children plus kind-grouped standalone sections, using the fixed entry format (link, title, status, execution links; epics: `done/total` rollup + nested child lines; bugs: severity; spikes: timebox state). Verify: entry count matches item files plus child lines and every epic line matches the rollup pattern (one-liner from spec scenario passes).
- [x] 1.3 Write per-kind lifecycle transitions doc (statuses per kind incl. bug rejection, spike answered/open report, epic rollup). Verify: each transition in the doc names its gate command.

## 2. Router (`/triage`)

- [x] 2.1 Write `.opencode/commands/triage.md`: kind-first classification, lane rubric (XS/S/M-multi/L-advisory), explicit-ask behavior, BMAD-advisory-never-autoexecutes. Verify: file exists; dry-run its rubric text against 4 fixture requests (XS fix, single feature, multi-part understood, architectural) and record the lane each maps to.
- [x] 2.2 Write router fixtures + expected lanes doc used by 2.1. Verify: all 4 fixtures map to the lanes in the spec scenarios.

## 3. Worktree guard

- [x] 3.1 Write `scripts/worktree-guard.sh` (main-clean check via `git status --porcelain`, dirty-abort message, worktree create on `ticket/<id>-<slug>`, record worktree/branch in item). Verify: clean main → exit 0 + worktree created; dirty main (fixture touch) → exit non-zero with "main is dirty" message; remove fixtures after.
- [x] 3.2 Gitignore `.worktrees/` and commit guard + template + router. Verify: `git check-ignore .worktrees/x` prints the path; `git status --short` clean after commit.

## 4. Integration checks

- [x] 4.1 Run `openspec validate --change project-ticket-harness` green. Verify: command exit 0, no warnings.
- [x] 4.2 End-to-end dry run: triage a fixture requirement → ticket → worktree guard → single OpenSpec change skeleton, all on a ticket branch off clean main. Verify: ticket links the change, branch is `ticket/<id>-<slug>`, main untouched (`git log --oneline main` unchanged).
- [x] 4.3 Update `AGENTS.md` routing section to point at `tickets/` + `/triage` + guard script. Verify: section present with paths.
