---
id: ops-030
title: "Confirm image distribution for a clean machine (registry push state)"
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

# Confirm image distribution for a clean machine (registry push state)

> `ops-task`; no `parent:`.

## Work

V1 is proven "from clean machines" (`tickets/epic-001-universal-framework/epic.md:30`).
The clean ritual pulls the pinned image by name —
`ghcr.io/randomgenericusername/lang-cpp:15.3.rel2` (`docs/vscode-debug.md:148`) —
so a genuinely clean host must be able to pull it (or the documented path must
build it locally).

- Confirm the pinned images are published and anonymously pullable, **or** record
  that the clean-machine path builds them from the checkout (`make images`).
- `HANDOFF.md:42-45` flags "registry push (needs `write:packages` re-auth)" as an
  open thread; close it or record the decision.
- Note: anonymous GHCR manifest probes in this session returned `403` for both the
  real and a bogus repo, so the publish state is **inconclusive** from a generic
  host — verify with an authenticated `docker pull` / `gh` check.

## Done-when

The distribution path for a clean machine is stated and verified (pull works, or
build-from-checkout is the documented and tested path).
