---
id: spike-007
title: "First non-STM32 board: what does an ESP32-CAM pack require of the framework?"
kind: spike
status: reported
lane: direct
timebox: 4h
questions:
  - "Exact chip facts: which ESP32-CAM variant (AI-Thinker ESP32-D0WD?), and is UART/esptool flashing (no probe) confirmed with the owner's hardware?"
  - "Pack schema: which fields survive (cores, memory, example LED) and which break (arch triple, CMSIS startup/system/defines, OpenOCD blocks, SVD source, stm32hal config_headers, probe-rs settings)? Extend the schema or define a new pack-kind?"
  - "Probe backends: can the openocd/probe-rs adapter interface carry an esptool backend (serial transport, no USB node, different proof story), or does it need a new interface?"
  - "Toolchain image: ESP-IDF (xtensa + CMake/Ninja, GB-scale) or minimal xtensa-gcc + esptool? Pin version + source + checksum per the images/README pins table."
  - "Templates: can the Make/cargo project shape carry an ESP-IDF app (CMakeLists + sdkconfig + partition table), or is a new template family required?"
  - "Done criteria: what is 'cell green' for ESP32 (ELF? esptool image_info? UART boot log?) for docs/e2e-evidence.md?"
answered:
  - "Q1 chip facts: owner board CONFIRMED = Ferretronica ESP32-CAM + OV2640 (AI-Thinker-class: dual-core 240MHz/600DMIPS, 520KB SRAM + 4MB external PSRAM, 5V supply, PCB antenna, u.FL/FPC connectors — ferretronica.com product page). No onboard USB-UART (board class has none) — external FTDI required (5V, GND, TX->U0R/GPIO3, RX->U0T/GPIO1, GPIO0->GND + RST pulse for download mode). Console UART0 = GPIO1/3 @115200 8-N-1. Red LED = GPIO33 active-LOW; flash LED = GPIO4."
  - "Q2 pack schema: model frame holds (Core/MemoryRegion/Endpoint/probe_backend/proof_rung are free-form; xtensa-lx6, uart-serial, esptool pass validation). Registry is the gate: loader.py:68-74 rejects unknown blocks; registry.py:88-108 knows only stm32f4/h7/wl families. Verdict: EXTEND — register new block validators (esptool/partitions/sdkconfig) + families=('esp32',); do NOT reuse STM32 example (RCC/GPIO register model), fpu, config_headers (stm32hal defaults), or svd (cmsis-svd-stm32 repo) semantics."
  - "Q3 backends: ProbeAdapter ABC (adapters/__init__.py:56-70, flash->PieceResult + debug->handle) fits esptool with zero interface change — register a 3rd backend. New: argv (esptool --port <endpoint.address> --baud write-flash <addr> <bin>), output parser (Hash-verified/Wrote-N-bytes, not Verified-OK/Finished), ESP UART VID/PIDs (CP210x 10C4:EA60, CH340 1A86:7523) for autodetect, widen flash --files from ELF to bin+addr. /dev/ttyUSB --device forwarding already works (test_shim_probe.py:29-31). Verdict: EXTEND."
  - "Q4 image: ESP-IDF effectively mandatory (bare-metal xtensa void consensus: loses WiFi/BT/camera/flash-mmap/PSRAM init). Pin e.g. espressif/idf:v6.0.3 (stable v6.1 per docs; maintained v6.0.3/v5.5.5/v5.4.4) — official docker image with pinned tags exists (espressif/idf:vX.Y). Containerized per framework philosophy (AGENTS.md dual-mode spine): zero host deps preserved; host-transparent build/flash runs IDF image + device forwarding. Flash triple: 0x1000 bootloader.bin + 0x8000 partition-table.bin + 0x10000 app.bin; write-flash always MD5-verifies; verify-flash/read-flash available. OpenOCD/JTAG explicitly OUT of scope for bring-up."
  - "Q5 templates: NEW template family required — root CMakeLists.txt + main/CMakeLists.txt + sdkconfig.defaults (+ optional partitions.csv) instead of Makefile + linker/*.ld; xtensa toolchain via idf.py build|flash|monitor; no vendor/CMSIS, no startup/system/defines, no memory.x/link.x; new lang/kind key + image in DefaultImageLookup; new .vscode (no cortex-debug+openocd+SVD, no arm-none-eabi-gdb). Do NOT fork CPU_BY_CORE/Makefile/_LINKER/memory.x. Verdict: NEW-KIND."
  - "Q6 done criteria: NEW build_idf_cell in engine/verify — render CMake tree, docker run idf.py build in the IDF image, assert build/*.elf+*.bin exist + partition-table fit (offsets/sizes, not arm-none-eabi-size), optional esptool verify-flash as proof_rung, warn-only policy kept, evidence extended with idf cmd + bin sizes. e2e.py:57-62 CELLS gain (esp32cam,idf)."
  - "Q7 image pin (resolved 2026-10-16): espressif/idf ships BOTH linux/amd64 AND linux/arm64 (docker buildx imagetools inspect, cross-checked with the Hub tags API). Digest-pin candidate = v6.1 (docs /en/stable/ now serves v6.1), index sha256:81893c71…5edb18c. Fallbacks: v6.0.3 sha256:54278f2c…7a08f555, v5.5.6 sha256:bf72fe7a…614cac84. Per-arch digests + sources in the addendum."
  - "Q8 hardware confirmation (2026-10-16, owner's bench): live UART link proven — esptool v5.6.0 via `uvx` over a generic PL2303 USB-TTL (067b:2303, /dev/ttyUSB0) reports Chip type ESP32-D0WD (revision v1.0), 240MHz dual-core Wi-Fi/BT, MAC 30:83:98:57:5f:c4; flash-id → manufacturer 5e device 4016, 4MB (matches Q1). No probe; manual GPIO0→GND + RST for download mode. Caveat: 067b is NOT in the planned _PROBE_VIDS (10C4/1A86); it also threw transient -71/EPROTO before recovering (flaky)."
open:
  - "First-slice implementation ticket (suggested: pack YAML + esptool backend dry-run + docs, no image build yet) — follow-up req/task, out of spike scope."
  - "Rust via esp-hal 1.0 (no_std, supports classic ESP32) — noted as the future second-language path, not investigated."
links:
  openspec: none
  bmad:
    - _bmad-output/initiative-universal-mcu-env/architecture-universal-mcu-env/architecture-universal-mcu-env.md
worktree: none
branch: ticket/spike-007-esp32-cam
---

# First non-STM32 board: ESP32-CAM

## Questions

- Exact chip facts: which ESP32-CAM variant (AI-Thinker ESP32-D0WD?), and is UART/esptool flashing (no probe) confirmed with the owner's hardware?
- Pack schema: which fields survive and which break? Extend the schema or define a new pack-kind?
- Probe backends: can the adapter interface carry an esptool backend, or does it need a new interface?
- Toolchain image: ESP-IDF or minimal xtensa-gcc + esptool? Pin per the images pins table.
- Templates: can the Make/cargo project shape carry an ESP-IDF app, or is a new template family required?
- Done criteria: what is "cell green" for ESP32 for docs/e2e-evidence.md?

## Findings

### Answered

- (question → finding)

### Open

- (unanswered question + what was tried)

### Verdict

Extend the framework, no new pack-kind: model frame + adapter ABC + CLI serial
plumbing all hold; register ESP32 blocks/backends/image/template-family. Only
the template family and the verify cell are new-kind. Explicitly out of scope
for bring-up: OpenOCD/JTAG debugging, bare-metal xtensa, Rust/esp-hal.
Suggested first slice (follow-up ticket): pack YAML + esptool backend dry-run
+ docs, no image build yet.

> Spike stops at the box and reports `answered:` / `open:`. Implementation output from a spike is a failure. No second box without an explicit user call.

## Addendum (2026-10-16) — main sync + open-item resolution

Branch state fixed first: `ticket/spike-007-esp32-cam` was 3 ahead / 6 behind
`main`, synced by merge `1eb9407` (`origin/main` `3ea9fac` is now an ancestor),
`make test` → **276 passed**. No source changes on this branch — the sync only
carried ops-022/bug-023/bug-024 into `engine/templates/renderer.py` +
`packs/stm32wl55jc.yaml`, none of which the ESP32 work touches.
`Verify: git log --oneline -1 && make test`.

**Resolved — IDF image arch + digest pin (was `open:` #2):**

- `espressif/idf` publishes **both** `linux/amd64` and `linux/arm64`.
  `Evidence:` `docker buildx imagetools inspect espressif/idf:v6.1` →
  `MediaType: application/vnd.oci.image.index.v1+json` with `Platform:
  linux/amd64` + `Platform: linux/arm64`; the Hub tags API reports the same for
  v6.1 / v6.0.3 / v5.5.6 (`curl https://hub.docker.com/v2/repositories/espressif/idf/tags/`).
  `Verify: docker buildx imagetools inspect espressif/idf:v6.1`
- Docs `/en/stable/` now serves **v6.1** (footer `esp32 v6.1`, source
  `espressif/esp-idf/blob/v6.1/docs/en/versions.rst`) ⇒ pin candidate `v6.1`.
  `Evidence:` `docs.espressif.com/projects/esp-idf/en/stable/esp32/versions.html`.
- Digests (index + per-arch), cross-checked with `docker buildx imagetools inspect`:

  | tag | index digest | linux/amd64 | linux/arm64 |
  |---|---|---|---|
  | `v6.1` | `sha256:81893c71…5edb18c` | `sha256:f81b6e07…94f218a` | `sha256:a460b1c8…4a3d0bf` |
  | `v6.0.3` | `sha256:54278f2c…7a08f555` | `sha256:01ab23e2…ade05a1e` | `sha256:da1f22c1…299f0fa` |
  | `v5.5.6` | `sha256:bf72fe7a…614cac84` | `sha256:851f136a…e78cfb3` | `sha256:26776964…5b223c112` |

- Caveat: verified from the registry, not from a local pull/build. A real
  `docker pull`/build that records `RepoDigests` is still owed when the IDF
  image is added (cf. bug-022 preflight).

**Re-verified supporting facts (sources):**

- esptool argv + verify: `esptool --port <PORT> [-b BAUD] write-flash <addr>
  <file> …`; post-write MD5 check, `verify-flash`, and `merge-bin` for a single
  image. `Evidence:` `docs.espressif.com/projects/esptool/en/latest/esp32/esptool/basic-commands.html`.
- Serial: 115200, 8-N-1, flow control none, **3.3V only**.
  `Evidence:` `.../esptool/serial-connection.html`.
- ESP32-CAM (AI-Thinker class): GPIO33 red LED **active-low**, GPIO4 flash LED,
  GPIO1/3 = UART0 TX/RX, GPIO0→GND = download mode.
  `Evidence:` `randomnerdtutorials.com/esp32-cam-ai-thinker-pinout/` +
  `SeeedDocument/forum_doc/reg/ESP32_CAM_V1.6.pdf`.
- Autodetect gap in this repo: `engine/cli/shim.py:64` is `_PROBE_VIDS =
  ("0483",)` (ST-Link only), so esptool UART autodetect will need `10C4`
  (CP210x) + `1A86` (CH340) added.
  `Evidence:` `engine/cli/shim.py:61-64`.

**Hardware confirmation (2026-10-16, owner's bench — closes the last Q1 item):**

- esptool v5.6.0 (run via `uvx esptool`, no host install) over a generic PL2303
  USB-TTL dongle (`067b:2303`, `/dev/ttyUSB0`) talked to the board:
  `Chip type: ESP32-D0WD (revision v1.0)`, 240MHz, dual-core Wi-Fi/BT,
  `MAC 30:83:98:57:5f:c4`; `flash-id` → `Manufacturer 5e, Device 4016,
  Detected flash size: 4MB` — matches Q1 (ESP32-D0WD, 4MB external flash).
  `Verify: uvx esptool --port /dev/ttyUSB0 chip-id` (+ `flash-id`).
- Wiring: `+5V→5V`, `GND→GND`, `TXD→GPIO3`, `RXD→GPIO1`; download mode by
  `GPIO0→GND` + RST pulse (this board has no auto-reset circuit). No probe.
- **Write path proven (2026-10-16):** the full 4 MB image was written to `0x0`
  with `write-flash` → esptool reported `Hash of data verified.`; an
  independent `read-flash` + `cmp` came back byte-identical (sha256
  `c34ef152…`). Backup taken first, so the operation is reversible and the
  board's content is unchanged. Download mode must be re-entered per session —
  the cable has no DTR/RTS wiring, so esptool's "hard reset" never reaches the
  board.
  `Verify: uvx esptool --port /dev/ttyUSB0 --baud 460800 write-flash 0x0 <backup>; uvx esptool … read-flash 0 0x400000 <out>; cmp <backup> <out>`
- **Target stack proven end-to-end (2026-10-16):** in `espressif/idf:v6.1`,
  `idf.py build` produced the ESP32 triple — bootloader 26176 B @`0x1000`,
  partition-table 3072 B @`0x8000`, app (`esp32cam_blink`) 149088 B @`0x10000`
  (86% of the 1 MB app partition free). All three flashed with `write-flash` →
  `Hash of data verified.` each; the app booted and printed
  `mu/esp32cam: blink N` over UART0 @115200 (captured live; GPIO33 red LED
  blinking). This is the concrete **ESP32 "cell green"** reference for the
  future verify cell.
  `Verify: docker run --rm -v <proj>:/project -w /project espressif/idf:v6.1 bash -lc "idf.py set-target esp32 && idf.py build"` then `uvx esptool --chip esp32 -p /dev/ttyUSB0 -b 460800 write-flash --flash-mode dio --flash-size 4MB 0x1000 build/bootloader/bootloader.bin 0x8000 build/partition_table/partition-table.bin 0x10000 build/<app>.bin`
- Caveat: the PL2303 is **not** in the planned `_PROBE_VIDS`
  (`engine/cli/shim.py:64` → 10C4/1A86). It repeatedly wedge-dumped into
  `-71`/`EPROTO` control-transfer errors (`journalctl -k | rg pl2303`) that only
  a **physical USB replug** cleared (observed twice) — a working but unreliable
  bridge; do **not** add `067b`. CH340/CP210x remain the default.

Still open: the first-slice implementation ticket (pack YAML + esptool backend
dry-run + docs, pinned to `espressif/idf:v6.1`); the Rust/esp-hal path. The
framework separation this spike's findings forced is tracked in `req-021`
(spine AD-8 amended, AD-11…AD-17) — the pre-ESP32 refactor gate.
