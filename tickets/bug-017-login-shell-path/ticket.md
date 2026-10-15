---
id: bug-017
title: "Image /etc/profile resets PATH -> login shells (VS Code tasks) lose the toolchain (Error 127)"
kind: bug
status: done
lane: direct
severity: S2
links:
  openspec: []
  bmad: []
worktree: .worktrees/bug-017/
branch: ticket/bug-017-login-shell-path
repro: "run the VS Code Build/Flash task in a freshly created container"
observed: "make: arm-none-eabi-size: No such file or directory -> make: *** [build-M4] Error 127"
expected: "the task builds/flashes"
---

# Image /etc/profile resets PATH

## Root cause

The image sets `ENV PATH=/opt/arm-gnu-toolchain/bin:...`, but its base image's
`/etc/profile` **unconditionally** resets `PATH`, and login shells source it:

```
sh -c    : PATH=/opt/arm-gnu-toolchain/bin:…        -> gcc found
bash -lc : PATH=/usr/local/sbin:/usr/local/bin:…    -> gcc MISSING
```

VS Code tasks run a **login** shell, so Build/Flash fail with `Error 127`.
(`mu build` uses a non-login shell, so it was unaffected; an older container
whose `/etc/profile` had been patched to `${PATH:-…}` masked this.)

## Fix

Re-export the image PATH from a `profile.d` script (sourced at the *end* of
`/etc/profile`), in both images:

```dockerfile
RUN printf 'export PATH="%s"\n' "$PATH" > /etc/profile.d/00-mu-path.sh
```

**Needs an image rebuild** (`make images`) before new containers pick it up.

## Evidence

- image `/etc/profile:5`: `PATH="/usr/local/sbin:…"` (unconditional);
  `mu-h755`'s (patched) reads `${PATH:-…}`.
- `/etc/profile` sources profile.d (`grep -c profile.d /etc/profile` → 2).
- throwaway container with the script mounted: `bash -lc` →
  `PATH=/opt/arm-gnu-toolchain/bin:…`, `command -v arm-none-eabi-gcc` → found.
- live: `docker exec mu-f411 bash -lc 'make flash'` → `Verified OK` (with the
  profile.d mount).
- Dockerfile edit itself is verified only by the mechanism above — rebuild to
  confirm in-image (`Evidence: MISSING — run make images`).

## Verify

```sh
make images   # then, in a fresh container: bash -lc 'command -v arm-none-eabi-gcc'
```
