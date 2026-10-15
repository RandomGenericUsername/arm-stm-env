---
id: ops-019
title: "Document the VS Code debug flow (docs/vscode-debug.md)"
kind: ops-task
status: done
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/ops-019/
branch: ticket/ops-019-vscode-debug-docs
---

# Document the VS Code debug flow

> `ops-task`; no `parent:`.

## Work

The entire VS Code flow (create `--vscode` → `mu dev` → attach → tasks/launch
configs → SVD register view → dual-core → probe-by-serial) existed only in
ticket history and chat. Before this change
`grep -c -i "vscode" README.md docs/*.md` returned **0, 0, 0**, and generated
projects carried no README.

Added `docs/vscode-debug.md` (generate, container, attach, tasks, launch
configs, keys, SVD/Watch, probe-by-serial, expected behaviour, troubleshooting
for the four field bugs, and the no-VS-Code path), and linked it from
`README.md` — which also loses a stale "flash/run not yet proven without
hardware" claim (it is proven live on NUCLEO-F411RE and NUCLEO-H755ZI-Q).

## Done-when

`docs/vscode-debug.md` documents the flow end to end, is linked from the README,
and its troubleshooting table maps each field symptom to its ticket
(`bug-011/013/016/017/018`).

## Evidence

- `grep -c -i vscode README.md docs/*.md` → 0/0/0 before; README now links the doc.

## Open

A generated project `README.md` (each project documenting its own tasks/configs)
is still not emitted — follow-up if wanted.
