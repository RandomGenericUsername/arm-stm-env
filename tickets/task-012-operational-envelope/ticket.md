---
id: task-012
title: "R6 — name the operational envelope as one owned contract"
kind: task
status: done
lane: inherits
parent: req-021
links:
  openspec: none
  bmad: none
worktree: .worktrees/task-012/
branch: ticket/task-012-envelope
---

# R6 — name the operational envelope as one owned contract

## Parent

`req-021` — lane inherited from parent.

## Work

State the operating envelope in one place (AD-17) and make each part owned: the container runtime
(`docker` is hardcoded at `engine/cli/shim.py:327`, `engine/cli/main.py:474`), the host tools
`create` needs (git, network for vendoring — `engine/templates/vendoring.py:181`), USB/sysfs access
and the container cgroup/permission model for probes (`/sys/bus/usb`, `--device-cgroup-rule`), and
the pinned container platform (`linux/amd64`, `engine/verify/e2e.py:255`). Add a non-docker/Windows
lane to Deferred.

## Done-when

The envelope is documented in one owned place and the deferred lanes are explicit. Governed by AD-17.

## Evidence

2026-10-16 — branch `ticket/task-012-envelope`:

- **`engine/core/envelope.py`** — the one owned place: `CONTAINER_RUNTIME`,
  `CONTAINER_PLATFORM`, `HOST_GIT`, `SYSFS_USB`, `USB_BUS_ROOT`, `USB_CGROUP_RULE`,
  with the **deferred lanes** named in its docstring (Windows native; any non-Docker
  runtime; non-`CONTAINER_PLATFORM` images).
- **Wired, not documented-and-ignored**: `engine/cli/shim.py` (runtime, sysfs root, USB bus
  root, cgroup rule), `engine/cli/main.py` (`which(CONTAINER_RUNTIME)`, image inspect),
  `engine/verify/e2e.py` (platform + runtime), `engine/templates/vendoring.py` (`HOST_GIT`).
- No scattered literals remain:
  `rg '"docker"|"c 189:\* rmw"|"linux/amd64"|which\("git"\)"|"/sys/bus/usb/devices"' engine/ --glob '*.py'`
  filtered to exclude the envelope/tests → **NONE**.
- **Ownership proven**: `test_changing_the_envelope_runtime_changes_the_argv` monkeypatches
  `engine.cli.shim.CONTAINER_RUNTIME` and the built container argv follows — the shim reads the
  constant instead of hardcoding the binary.
- `make test` → **309 passed**.
