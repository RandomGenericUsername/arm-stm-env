# Spec Delta

## Purpose

Created projects carry their own pinned CMSIS trees, so builds work offline-after-create with no hand-placed files and no per-project network fetch of unpinned sources.

## ADDED Requirements

### Requirement: Pinned submodules per family

`create` SHALL register `vendor/CMSIS` (CMSIS_5 @ 5.9.0) and `vendor/cmsis-device-<id>` (f4 @ v2.6.9, h7 @ v1.9.0, wl @ v1.4.0) as git submodules of the new project.

Evidence: ls-remote + HTTP 200 path checks 2026-10-13 (see design). Verify: fresh render has `.gitmodules` with exact pins; `git submodule status` clean after update.

#### Scenario: Pin recorded

- **WHEN** a project is created
- **THEN** `.gitmodules` names the exact tag SHAs, not branches

### Requirement: Referenced paths exist post-create

Every `vendor/...` path the Makefile references (core headers, device Include, gcc startup) SHALL exist after submodule init.

Evidence: HTTP 200s on all five probed paths. Verify: per-cell file-existence check in tests.

#### Scenario: Missing path fails loudly

- **WHEN** an upstream moves a referenced path
- **THEN** create fails with the missing path named (never a silent partial tree)

### Requirement: No network means clear error

Without network (or git) at create time, `create` SHALL exit non-zero naming the missing capability — never a half-vendored tree.

Evidence: current silent-missing behavior (stub workaround exists because of it). Verify: offline-simulated create test (unreachable remote) exits non-zero.

#### Scenario: Git missing

- **WHEN** `git` is absent on the host
- **THEN** create fails before rendering, naming `git` as the missing capability
