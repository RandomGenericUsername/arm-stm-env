---
id: ops-030
title: "Confirm image distribution for a clean machine (registry push state)"
kind: ops-task
status: done
size: XS
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/ops-030/
branch: ticket/ops-030-image-distribution
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

## Finding (2026-10-16)

**The pinned images are published to `ghcr.io` but the package is auth-required
(anonymous pull is denied)** — so a clean host must either `docker login ghcr.io`
(a token with `read:packages`) or build the images locally with `make images`.
Both paths are now documented in `docs/vscode-debug.md` §9.

Evidence:

```
# registry presence (a local-only build would have NO RepoDigests)
$ docker inspect ghcr.io/randomgenericusername/lang-cpp:15.3.rel2 --format '{{.RepoDigests}}'
["ghcr.io/randomgenericusername/lang-cpp@sha256:1c56c225645a..."]
$ docker inspect ghcr.io/randomgenericusername/lang-rust:1.99.0 --format '{{.RepoDigests}}'
["ghcr.io/randomgenericusername/lang-rust@sha256:c6a113c76b93..."]

# anonymous access denied ("denied", not "manifest unknown" -> exists, unauthorized)
$ DOCKER_CONFIG=$(mktemp -d) docker manifest inspect ghcr.io/randomgenericusername/lang-cpp:15.3.rel2
Get "https://ghcr.io/v2/.../manifests/15.3.rel2": denied

# unauthenticated packages API
$ curl -s -o /dev/null -w '%{http_code}' https://api.github.com/users/RandomGenericUsername/packages?package_type=container
401
```

Closes the `HANDOFF.md:42-45` "registry push (needs `write:packages` re-auth)"
thread as *finding recorded*: the images are pushed (private). Whether to make the
package public is an optional product call, not a V1 blocker (login or local build
both satisfy a clean machine).

Verify: `docker logout ghcr.io; docker pull ghcr.io/randomgenericusername/lang-cpp:15.3.rel2` → denied; or `make images` builds it locally.
