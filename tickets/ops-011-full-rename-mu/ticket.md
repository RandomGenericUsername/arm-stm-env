---
id: ops-011
title: "Full rename to mu (repo, package, paths, image namespace)"
kind: ops-task
status: done
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/ops-011/
branch: ticket/ops-011-full-rename-mu
---

# Full rename to mu (repo, package, paths, image namespace)

> `ops-task`; no `parent:`.

## Work

Rename the repository and every **live** identifier to `mu`:

- GitHub repo already renamed → `RandomGenericUsername/mu` (old URLs redirect).
- `pyproject.toml` project name → `mu`; `Makefile` tool uninstall → `mu`.
- Container paths `/opt/arm-stm-env` → `/opt/mu` (`engine/cli/shim.py` + tests).
- Image namespace → `ghcr.io/randomgenericusername` (the GHCR owner **cannot**
  be `mu`: `mu` is a taken user/org login and the token lacks `admin:org`).
- Dockerfile LABELs `org.arm-stm-env.*` → `org.mu.*`.
- Docs/AGENTS/HANDOFF/README (repo name, clone URL), `engine/core/cache.py`
  key prefix, `engine/adapters/__init__.py` image table.

Unchanged: `stm32*` device names; historical tickets, OpenSpec changes, and
`docs/e2e-evidence.md` (records of past runs).

Evidence: `rg -n "arm[-_]stm[-_]env"` on live files enumerates the spots.
Verify: `rg "arm.stm.env" engine Makefile pyproject.toml README.md images AGENTS.md HANDOFF.md`
returns only `stm32`-unrelated hits (ideally none).

## Done-when

No live code/doc references `arm-stm-env`; images retagged to the new namespace;
tool reinstalled as `mu`; local dir renamed; `make test` green.
