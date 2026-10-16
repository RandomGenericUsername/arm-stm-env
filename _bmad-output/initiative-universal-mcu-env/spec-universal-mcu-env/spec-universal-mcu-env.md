---
id: SPEC-universal-mcu-env
companions:
  - ../architecture-universal-mcu-env/architecture-universal-mcu-env.md
  - ../architecture-universal-mcu-env/work-split-view.md
  - device-matrix.md
sources:
  - ../../brief-universal-mcu-env/brief-universal-mcu-env.md
---

> **Canonical contract.** This SPEC and the files in `companions:` are the complete, preservation-validated contract for what to build, test, and validate. Source documents listed in frontmatter are for traceability — consult them only if you need narrative rationale or prose color this contract intentionally omits.

# Universal MCU dev framework

## Why

A vision to realize: solo firmware developers re-derive the same MCU bring-up (toolchain install, CMSIS/linker/SVD hunting, probe config) per project, and existing tools either demand host-installed toolchains (PlatformIO, Arduino, Zephyr) or flash brilliantly but scaffold nothing (probe-rs). A single CLI owning scaffolding *and* zero-deps execution closes that gap, starting STM32 and designed vendor-neutral so a second vendor (ESP32 first) proves the core never became STM32.

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
- **CAP-7**
  - **intent:** Adding a new device family forces the *engine to be improved*, not bent — and then the family lands as a pure addition.
  - **success:** The ESP32 effort first generalises the engine (the R1–R6 refactor: stack axis, port split, validator relocation, artifact gating, verify axis — AD-11…AD-17), after which the ESP32 family (pack + `esptool` backend + `idf-cmake` template + verify cell) lands with **zero `engine/core` diffs** — the AD-1 acceptance test.
- **CAP-8**
  - **intent:** A device with no debug-attach support still completes build, flash, and run proof.
  - **success:** `esptool` flashes an ESP32-D0WD over UART at the pack-declared offsets and reports an AD-10 proof with no DebugPort implemented.

## Constraints

- Hexagonal vendor-neutral core; hardware packs, toolchains, probe backends are adapters — STM32 is the reference pack, never the core. A new brand ships an adapter plus pack sections; core diffs are forbidden for brand additions (AD-1, AD-13).
- Hardware pack (device truth) and run config (invocation) are strictly separated; project shape is derived from pack data (AD-5).
- The build stack is pack-declared and language-keyed (a `stacks` map in the shared frame); the resolved stack — never the language flag — selects the template family, toolchain image, and build command (AD-11, AD-8).
- The probe port splits into FlashPort (programming) and DebugPort (sessions); a backend implements DebugPort only where the device supports attach, and the CLI fails a verb rather than fabricating a handle (AD-12).
- Exactly one device-description source per invocation: `--mcu-config` XOR individual flags.
- All toolchain/probe versions pinned; distribution is versioned OCI images plus thin host shim.
- The CLI engine and shim are Python; `python3 >= 3.11` is the single host prerequisite, with `uv` managing self-contained dependencies. All toolchain dependencies stay containerized — "zero deps" means zero toolchain deps.
- Operational envelope is named and owned: container runtime, host tools (git, network for vendoring), USB/sysfs access, and the pinned container platform (AD-17).
- Linux/macOS day one; Windows deferred but not designed out.
- Evidence rule governs all product and technical claims.

## Non-goals

- Windows native support, pack validator tooling, cloud builds, team/enterprise features, IDE plugins.
- For ESP32 bring-up specifically: bare-metal xtensa (no ESP-IDF), OpenOCD/JTAG debugging, and the Rust `esp-hal` path (AD-11 backends: `idf-cmake` only).

## Success signal

From a clean machine, each matrix cell completes create → build → flash and the board runs its program with the pack-defined observable proof — including the first non-STM32 cell (ESP32-CAM: `idf-cmake` build, `esptool` UART flash, UART boot log), which must land without a single `engine/core` change.

- Proof ladder for run verification: automated probe readback first, LED second, manual register inspection as accepted fallback; each pack declares its rung.

## Open Questions

- Is the ESP32 cell a V1-matrix commitment or a post-V1 proof-of-generality? The architecture (AD-16) sequences the refactor first; the ESP32 slices (E1–E4) are ticketed separately.
