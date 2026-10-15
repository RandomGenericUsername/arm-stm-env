---
id: bug-020
title: "bug-017's profile.d RUN sits before the toolchain layers -> every image rebuild is a full rebuild"
kind: bug
status: done
lane: direct
severity: S3
links:
  openspec: []
  bmad: []
worktree: .worktrees/bug-020/
branch: ticket/bug-020-dockerfile-layer-order
repro: "make image-cpp after bug-017"
observed: "the RUN added right after ENV invalidates the apt/toolchain/OpenOCD layers -> full multi-GB rebuild"
expected: "only the trailing PATH layer rebuilds; the expensive layers stay cached"
---

# Dockerfile layer order

## Root cause

bug-017 added the `/etc/profile.d/00-mu-path.sh` RUN immediately after the `ENV`
block, so it invalidates **every** later layer — apt, the ARM toolchain download
and the OpenOCD build. A one-line fix therefore forced a full ~GB rebuild.

## Fix

Move that RUN to the end of both Dockerfiles (just before `CMD`), where `$PATH`
still carries the toolchain. The expensive layers stay cached, so the rebuild is
a single tiny layer.

## Evidence

- `make image-cpp` after the move → only the trailing layer builds (the
  toolchain/OpenOCD layers are cache hits).
- The generated script content is unchanged: `bash -lc 'command -v
  arm-none-eabi-gcc'` still resolves (same `$PATH` at build time).
