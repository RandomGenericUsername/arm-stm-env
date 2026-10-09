# Spec Delta

## Purpose

Container images make pinned toolchains runnable and addressable: one image per toolchain family, built from recorded versions, resolved by the core-owned lookup.

## ADDED Requirements

### Requirement: Dockerfiles pin every toolchain

Each image SHALL pin: base image digest, toolchain version + source URL, OpenOCD fork SHA, and language extras (Rust targets, probe-rs). An unpinned `latest` or bare-upstream reference SHALL fail review.

Evidence: spike-003 table; AD-8. Verify: `rg -i "latest|:stable" images/*.Dockerfile` empty; every `FROM`/URL carries a digest, tag, or SHA.

#### Scenario: Pin audit

- **WHEN** review runs the pin grep
- **THEN** zero unpinned references across `images/`

### Requirement: Language resolves to image

The core lookup SHALL resolve `c/cpp` → cpp image and `rust` → rust image, matching the refs already tested in req-005.

Evidence: req-005 lookup tests. Verify: existing `pytest -k shim_lookup` still green (no changes to refs without updating tests).

#### Scenario: Ref change propagates

- **WHEN** an image ref changes
- **THEN** lookup tests + docs update in the same change

### Requirement: Build procedure is documented and re-runnable

`images/README.md` SHALL give exact build commands + digest recording; CubeCLT stays gated with its unblock conditions named.

Evidence: spike-003 OPEN items. Verify: README lists build commands, digest procedure, and CubeCLT gate conditions.

#### Scenario: Fresh-machine rebuild

- **WHEN** a new machine follows README build commands
- **THEN** it produces the recorded digests (modulo base-image updates, which are re-recorded)
