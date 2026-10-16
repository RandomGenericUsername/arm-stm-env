# Web-verify review — architecture-universal-mcu-env.md (2026-10-08)

Scope: `architecture-universal-mcu-env.md:102-119` (Stack + Structural Seed) plus AD-3/AD-8 Deferred pins. Method: webfetch official sources same day; quotes below.

## 1. Python >= 3.11 — CURRENT but narrow
- Source: https://devguide.python.org/versions/
- Quote: "3.11 | ... | security | 2022-10-24 | *2027-10*" and "3.10 | ... | end-of-life | ... | 2026-10-01"; "After two years ... only security fixes are accepted and no more binaries are released."
- Finding: `>= 3.11` is valid (3.10 went EOL 2026-10-01, one week before this review) but 3.11 itself is already security-only with EOL 2027-10. No change required; consider `>= 3.12` for new code since 3.12/3.13 are also security phase and 3.14 is bugfix.
- Evidence: devguide table above. Verify: `curl -s https://devguide.python.org/versions/ | grep -A2 3.11`.

## 2. uv >= 0.12 (verified 0.12.23) — CURRENT, exact
- Source: https://github.com/astral-sh/uv/releases/tag/0.12.23 and https://docs.astral.sh/uv/
- Quote: "0.12.23 ... Released on 2026-10-03" / docs: "An extremely fast Python package and project manager, written in Rust."
- Finding: Pin is accurate to latest release 5 days before review. `>= 0.12` floor fits. No action.
- Verify: `curl -s https://github.com/astral-sh/uv/releases/latest | grep 0.12`.

## 3. OCI / Docker (AD-7, AD-8, Deferred "OCI runtime") — CURRENT
- Source: https://opencontainers.org/
- Quote: "the OCI currently contains three specifications: the Runtime Specification (runtime-spec), the Image Specification (image-spec) and the Distribution Specification (distribution-spec)"; news: "OCI Runtime Spec v1.3" (2025-11-04), "OCI Distribution Spec Conformance Redesign" (2026-04-06).
- Finding: "OCI image per toolchain family" (AD-8) and "OCI runtime (pinned per image...)" Deferred are the right vocabulary; standards are actively maintained, not stale. Gap (not error): arch defers runtime choice — fine, but record Docker-vs-Podman/nerdctl decision stays open.
- Verify: open https://opencontainers.org/ → About + Latest News.

## 4. OpenOCD ST fork — EXISTS, pin branch
- Source: https://github.com/STMicroelectronics/OpenOCD
- Quote: "STMicroelectronics customized version of OpenOCD supporting STM32 MCUs and MPUs"; "To be used within STM32CubeIDE, STMicroelectronics modified OpenOCD to support: All STM32 MCU and MPU devices / All ST-Link variants"; "STMicroelectronics is actively working at merging these modifications in the official OpenOCD. In the mean time, these modifications are available in this repository." Default branch observed: `openocd-cubeide-r7`.
- Finding: AD-3/Seed `adapters/probe/openocd` fits STM32 but MUST name the ST fork + branch (`openocd-cubeide-r7`) rather than bare upstream openocd, and note the stated upstream-merge intent so the pin is revisit-able. Upstream http://openocd.org/ remains the reference for vanilla builds.
- Verify: `gh repo view STMicroelectronics/OpenOCD --web`.

## 5. probe-rs — ACTIVE but UNNAMED in arch (gap)
- Source: https://probe.rs/docs/getting-started/installation/
- Quote: install via "curl ... https://github.com/probe-rs/probe-rs/releases/latest/download/probe-rs-tools-installer.sh | sh", "brew tap probe-rs/probe-rs", or "cargo install probe-rs-tools --locked"; ships "`probe-rs`, `cargo-flash` and `cargo-embed`".
- Finding: probe-rs is current and a legitimate modern alternative to OpenOCD/ST-Link for STM32 (and Rust story CAP-6). Arch Seed lists only `openocd, esptool, avrdude, stlink-fallback` (`:116-117`) — probe-rs absent. Not a factual error, but since this review lens requires it, record an explicit adopt/defer decision (e.g., V1 = ST OpenOCD fork; probe-rs as named alternative or Rust-lane default).
- Verify: `curl -s https://probe.rs/docs/getting-started/installation/ | grep -i 'cargo install'`.

## 6. esptool — CURRENT, fits ESP adapter
- Source: https://github.com/espressif/esptool
- Quote: "A Python-based, open-source, platform-independent serial utility for flashing, provisioning, and interacting with Espressif SoCs"; "Visit the documentation ... or run `esptool -h`."
- Finding: AD-3 naming esptool as the ESP flash path is correct and Espressif-maintained. No action.
- Verify: `pipx run esptool --help` or open repo README.

## 7. avrdude — CURRENT, fits AVR adapter
- Source: https://github.com/avrdudes/avrdude
- Quote: "AVRDUDE - AVR Downloader Uploader - is a program for downloading and uploading the on-chip memories of Microchip's AVR microcontrollers"; "Documentation for current and previous releases is on Github Pages"; "Starting with version 8, a GUI implementation has been added."
- Finding: Canonical home is now `avrdudes/avrdude` org (not the old savannah `nongnu` page training data may cite). AD-3 naming avrdude is correct. Recommend arch cite the `avrdudes` org URL when pins are added.
- Verify: `gh repo view avrdudes/avrdude --web`.

## 8. STM32CubeCLT — EXISTS, MISSING from arch (gap)
- Source: https://www.st.com/en/development-tools/stm32cubeclt.html (via search; direct fetch timed out 2026-10-08)
- Quote (search excerpt): "STM32CubeCLT is an all-in-one multi-OS command-line toolset ... includes GNU C/C++ for Arm toolchain executables, GDB debugger, and STM32CubeProgrammer"; community: "STM32CubeCLT 1.22.0 release ... Updated to align with STM32CubeIDE v2."
- Finding: Product is current (v1.22.0 aligns to CubeIDE v2). Arch never names CubeCLT — toolchain adapter (`:118` "image registry map + per-family build defs") and Deferred pins should state whether STM32 C/C++ images derive from CubeCLT or vanilla `gcc-arm-none-eabi` + upstream OpenOCD, including license/redistribution note for container images. This is the largest training-data risk: do not assume CubeCLT == CubeIDE-bundled GCC; verify version + EULA at image-definition time.
- Evidence: PARTIAL (search excerpt, not full page fetch — st.com fetch timed out). Verify: open https://www.st.com/en/development-tools/stm32cubeclt.html and record version + download EULA.

## Verdict: CONDITIONAL PASS
Stack (`Python >= 3.11`, `uv >= 0.12.23`) and adapter tools (ST OpenOCD fork, esptool, avrdude, OCI, probe-rs) all verify current against official sources. Required before spec: (a) pin ST OpenOCD fork branch, (b) name CubeCLT-vs-vanilla decision for STM32 toolchain images, (c) explicit probe-rs adopt/defer.
