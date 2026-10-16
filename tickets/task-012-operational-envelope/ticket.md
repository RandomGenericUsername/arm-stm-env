---
id: task-012
title: "R6 — name the operational envelope as one owned contract"
kind: task
status: proposed
lane: inherits
parent: req-021
links:
  openspec: none
  bmad: none
worktree: none
branch: none
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
