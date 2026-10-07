---
id: task-004
title: "Dockerfile skeleton for dev image"
kind: task
status: ready
lane: inherits
parent: "req-011"
links:
  openspec: none
  bmad: none
worktree: none
branch: none
---

# Dockerfile skeleton for dev image

## Parent

`req-011` — lane inherited from parent; never routed to `bmad-advisory` on its own.

## Work

Write the Dockerfile skeleton for the dev image (base image + toolchain placeholder layers).

## Done-when

`docker build` of the skeleton image succeeds.
