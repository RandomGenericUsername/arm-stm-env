---
id: bug-022
title: "Unshared Docker mount paths fail with raw daemon error (no preflight, no hint)"
kind: bug
status: done
lane: direct
severity: S3
links:
  openspec: none
  bmad: none
worktree: .worktrees/bug-022/
branch: ticket/bug-022-mount-preflight
repro: "mu build --project-dir ~/Desktop/personal/test-project (any project or checkout path Docker Desktop cannot share)"
observed: "docker: Error response from daemon: error while creating mount source path '/host_mnt/Users/.../Desktop: ... operation not permitted' — raw daemon stderr, exit passthrough, no hint"
expected: "mu exits 1 naming the offending mount path, why it is unusable, and the fix (move it / fix permissions / share it in Docker Desktop)"
---

# Unshared Docker mount paths fail with raw daemon error

## Repro

`mu build --project-dir ~/Desktop/personal/test-project` (any project or
checkout path the container runtime cannot mount — Docker Desktop File Sharing
on macOS, permissions/ownership/SELinux on Linux).

## Observed

`docker: Error response from daemon: error while creating mount source path
'/host_mnt/Users/.../Desktop: ... operation not permitted'` — raw daemon
stderr relayed verbatim, exit code passed through. No indication of which of
the three mounts failed (project, `engine/`, `packs/`), why, or how to fix it.
`engine/cli/main.py:457-462` streams the child verbatim and returns its code
untouched.

## Expected

`mu` exits 1 naming the offending mount path, why it is unusable, and the fix
(move it / fix ownership-permissions / share it in Docker Desktop).

## Fix notes

Root cause: `auto` mode never validates the `-v` mount specs in
`engine/cli/shim.py:343-349` before (or after) handing them to the daemon.

Fix (agreed 2026-10-15, no blocklist — a static `~/Desktop` denylist would
false-positive for users who explicitly shared it):

1. Universal preflight probe (all OSes, all verbs with container argv): one
   `docker run --rm` with the same `-v`/`-e`/`-w` specs + image, `true` as
   payload. Failure → parse offending path from daemon stderr
   (`/host_mnt/...` mapped back to host path), exit 1 with path + cause + fix.
2. Stderr fallback on the real run (tee, streaming preserved) for races the
   probe misses.
3. Regression tests with mocked `subprocess` (success / `operation not
   permitted` / unrelated daemon error); `make test` stays hermetic.

Evidence: macOS 14.8.5/arm64 investigation — `~/Desktop` (even nonexistent
subdirs) rejected at the parent prefix; `/tmp`, `~/Development` mount clean;
Docker exposes no file-sharing allowlist (`settings-store.json` has no sharing
keys), so probing the daemon is the only ground-truth check. Host-side
readability checks cannot work (the denial happens inside Docker's VM).
