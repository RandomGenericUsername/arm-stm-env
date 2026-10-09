# Proposal

## Why

Images are where pinned toolchains become runnable: per-language OCI images (AD-8) with spike-003 versions, core-owned cache keys already in code, registry lookup already tested. Last story of the epic — after it, the full chain (pack → model → verb → adapter → image) exists end to end, modulo HW smoke.

Evidence: work-split view story 5; spike-003 version table + vanilla-GCC verdict. Verify: `rg "vanilla" tickets/spike-003-toolchain-recon/ticket.md | head -3`.

## What Changes

- `images/cpp.Dockerfile` (vanilla ARM GNU from new gitlab host, branch-pinned 15.3.rel2; ST OpenOCD fork pinned `c8d973b`; versions recorded in-image).
- `images/rust.Dockerfile` (Rust 1.99.0 + thumbv7em targets + probe-rs v0.32.0 + flip-link + ST OpenOCD fork; same pinning discipline).
- `images/README.md`: build commands, digest-recording procedure, CubeCLT decision status (gated: vanilla wins until license/URL proof).
- Builds are recipe-complete and review-verified; image *builds* run only where Docker exists (CI/later). No image binaries committed.

## Capabilities

### New Capabilities

- `container-images`: per-toolchain Dockerfiles with pinned toolchains + build procedure.

### Modified Capabilities

(none)

## Impact

- New: `images/` (+ README). No engine code changes expected (lookup already tested); cache-key wiring verified against image refs.
- Out of scope: running image builds here (no Docker guarantee on this machine — checked at build), CubeCLT adoption, Windows containers.
