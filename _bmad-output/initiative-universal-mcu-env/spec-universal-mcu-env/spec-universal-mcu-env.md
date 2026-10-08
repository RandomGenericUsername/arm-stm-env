---
id: SPEC-universal-mcu-env
companions:
  - device-matrix.md
sources:
  - ../../brief-universal-mcu-env/brief-universal-mcu-env.md
---

> **Canonical contract.** This SPEC and the files in `companions:` are the complete, preservation-validated contract for what to build, test, and validate. Source documents listed in frontmatter are for traceability — consult them only if you need narrative rationale or prose color this contract intentionally omits.

# Universal MCU dev framework

## Why

A vision to realize: solo firmware developers re-derive the same STM32 bring-up (toolchain install, CMSIS/linker/SVD hunting, probe config) per project, and existing tools either demand host-installed toolchains (PlatformIO, Arduino, Zephyr) or flash brilliantly but scaffold nothing (probe-rs). A single CLI owning scaffolding *and* zero-deps execution closes that gap, starting STM32 and designed vendor-neutral.

## Capabilities

- **CAP-1**
  - **intent:** User generates a complete project tree from a prebuilt hardware-pack reference plus a project name.
  - **success:** For every day-one pack × language cell, `create` produces a tree that builds without hand edits.
- **CAP-2**
  - **intent:** User opens an interactive shell inside the versioned container with toolchain and probe tools ready.
  - **success:** From the shell, `build` and probe detection succeed with no additional installs.
- **CAP-3**
  - **intent:** User builds and flashes an already-created project from a bare host with zero preinstalled dependencies.
  - **success:** Clean machine runs build → flash → observable run proof for every matrix cell.
- **CAP-4**
  - **intent:** User supplies a full custom device file or individual hardware flags as the single description source.
  - **success:** A custom-described device completes create → build for at least one core.
- **CAP-5**
  - **intent:** User selects the probe backend via CLI flag from pack-declared supported backends.
  - **success:** The same project flashes via OpenOCD and via a second shipped backend.
- **CAP-6**
  - **intent:** User declares C/C++ library dependencies reproducibly in a generated project.
  - **success:** Declared deps resolve pinned and rebuild offline from cache; mechanism chosen by evidence spike.

## Constraints

- Hexagonal vendor-neutral core; hardware packs, toolchains, probe backends are adapters — STM32 is the reference pack, never the core.
- Hardware pack (device truth) and run config (invocation) are strictly separated; language is top-level run config; project shape is derived from pack data.
- Exactly one device-description source per invocation: `--mcu-config` XOR individual flags.
- All toolchain/probe versions pinned; distribution is versioned OCI images plus thin host shim.
- The CLI engine and shim are Python; `python3 >= 3.11` is the single host prerequisite, with `uv` managing self-contained dependencies. All toolchain dependencies stay containerized — "zero deps" means zero toolchain deps.
- Linux/macOS day one; Windows deferred but not designed out.
- Evidence rule governs all product and technical claims.

## Non-goals

- Non-STM32 vendors, Windows native support, pack validator tooling, cloud builds, team/enterprise features, IDE plugins.

## Success signal

From a clean machine, each matrix cell completes create → build → flash and the board runs its program with the pack-defined observable proof.

- Proof ladder for run verification: automated probe readback first, LED second, manual register inspection as accepted fallback; each pack declares its rung.
