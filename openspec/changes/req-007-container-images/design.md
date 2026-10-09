# Design

## Context

See proposal.md. AD-7/AD-8; spike-003 versions (ARM 15.3.rel2 gitlab host, Rust 1.99.0, probe-rs v0.32.0, flip-link v0.1.12, cargo-generate v0.25.0, ST fork c8d973b); req-005 lookup refs (`ghcr.io/arm-stm-env/lang-<x>:latest` — to be replaced by pinned refs here).

## Goals / Non-Goals

**Goals:** two pinned Dockerfiles + README; lookup refs updated to pinned values with tests green.

**Non-Goals:** running builds (Docker-dependent), CubeCLT, Windows images.

## Decisions

- **Debian-base slim images** (bookworm-slim digest-pinned at authoring; digest re-recorded at build).
- **ARM GNU from new gitlab host**, release branch 15.3.rel2, checksum verified at build from published SHA file (spike-003 OPEN closed at build if reachable, else recorded still-OPEN).
- **ST OpenOCD fork built from source** at pinned SHA `c8d973b` (verified 2026-10-08) — never distro openocd, never bare upstream.
- **Rust via rustup** pinned 1.99.0 + `thumbv7em-none-eabihf`, `thumbv7em-none-eabi` + probe-rs v0.32.0 install.
- **Lookup refs become digest/tag-pinned** (`ghcr.io/arm-stm-env/lang-cpp:<ver>` style); req-005 tests updated in same change.

## Risks / Trade-offs

- [Risk] No Docker here → Dockerfiles review-verified only (hadolint-style pin grep + line review), builds deferred to CI/HW machine → Mitigation: recipe exactness is the deliverable; build execution is a later task with a Docker host.
- [Risk] ARM 15.x checksums unreachable → Mitigation: build records what was verified; anything unverified stays OPEN in README.

## Verification plan

- Pin grep empty; `openspec validate` green; full pytest green (lookup tests cover new refs).
- `docker --version` probe recorded (builds run iff Docker present, else documented skip).

## Open Questions

None.
