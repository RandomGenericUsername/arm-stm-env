---
id: req-016
title: "Generated .vscode/ for the container-attached debug flow (C/C++ first)"
kind: requirement
status: done
size: M
lane: openspec-single
links:
  openspec:
    - openspec/changes/req-016-vscode-integration
  bmad: []
worktree: .worktrees/req-016/
branch: ticket/req-016-vscode-integration
parent: epic-001
children: []
---

# Generated .vscode/ for the container-attached debug flow (C/C++ first)

## User value

`mu create --vscode` gives a project you can debug in VS Code with F5: tasks,
a per-core cortex-debug launch, settings, and extension recommendations — no
hand-writing. Works with `mu dev` + VS Code "Attach to Running Container"; all
tooling (OpenOCD, GDB) stays in the container.

## Acceptance

- [x] `create --vscode` writes `.vscode/{tasks,launch,settings,extensions}.json`; off by default. `Verify: pytest -k vscode`
- [x] `launch.json` per core, pack OpenOCD config files, in-container tool paths. `Verify: cat launch.json`
- [x] `make test` + `openspec validate req-016-vscode-integration` green (255 passed).

## Evidence

Sibling prior art `ArmDevelopmentEnvironment@main:setup/create_project/dual/.vscode/`;
container debug chain proven live 2026-10-14 (in-container gdb → openocd →
F411RE halt). Follow-ups recorded in the change design: `mu dev` probe flags,
vendored SVD, Rust configs, devcontainer zero-click install.
