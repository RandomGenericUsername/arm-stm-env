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
  - "Q1 chip facts: AI-Thinker ESP32-CAM = ESP32-D0WD (dual Xtensa LX6 @240MHz, 520KB SRAM, 4MB flash, design for 4MB PSRAM). NO onboard USB-UART — external FTDI required (5V, GND, TX->U0R/GPIO3, RX->U0T/GPIO1, GPIO0->GND + RST pulse for download mode). Console UART0 = GPIO1/3 @115200 8-N-1. Red LED = GPIO33 active-LOW; flash LED = GPIO4. Evidence: randomnerdtutorials ESP32-CAM pinout, esptool boot-mode-selection docs, handsontec/components101 datasheets."
  - "Q2 pack schema: model frame holds (Core/MemoryRegion/Endpoint/probe_backend/proof_rung are free-form; xtensa-lx6, uart-serial, esptool pass validation). Registry is the gate: loader.py:68-74 rejects unknown blocks; registry.py:88-108 knows only stm32f4/h7/wl families. Verdict: EXTEND — register new block validators (esptool/partitions/sdkconfig) + families=('esp32',); do NOT reuse STM32 example (RCC/GPIO register model), fpu, config_headers (stm32hal defaults), or svd (cmsis-svd-stm32 repo) semantics."
  - "Q3 backends: ProbeAdapter ABC (adapters/__init__.py:56-70, flash->PieceResult + debug->handle) fits esptool with zero interface change — register a 3rd backend. New: argv (esptool --port <endpoint.address> --baud write-flash <addr> <bin>), output parser (Hash-verified/Wrote-N-bytes, not Verified-OK/Finished), ESP UART VID/PIDs (CP210x 10C4:EA60, CH340 1A86:7523) for autodetect, widen flash --files from ELF to bin+addr. /dev/ttyUSB --device forwarding already works (test_shim_probe.py:29-31). Verdict: EXTEND."
  - "Q4 image: ESP-IDF effectively mandatory (bare-metal xtensa void consensus: loses WiFi/BT/camera/flash-mmap/PSRAM init). Pin e.g. espressif/idf:v6.0.3 (stable v6.1 per docs; maintained v6.0.3/v5.5.5/v5.4.4) — official docker image with pinned tags exists (espressif/idf:vX.Y). Breaks the one-image-per-language layout: it is per-vendor-SDK. Flash triple: 0x1000 bootloader.bin + 0x8000 partition-table.bin + 0x10000 app.bin; write-flash always MD5-verifies; verify-flash/read-flash available. OpenOCD/JTAG explicitly OUT of scope for bring-up."
  - "Q5 templates: NEW template family required — root CMakeLists.txt + main/CMakeLists.txt + sdkconfig.defaults (+ optional partitions.csv) instead of Makefile + linker/*.ld; xtensa toolchain via idf.py build|flash|monitor; no vendor/CMSIS, no startup/system/defines, no memory.x/link.x; new lang/kind key + image in DefaultImageLookup; new .vscode (no cortex-debug+openocd+SVD, no arm-none-eabi-gdb). Do NOT fork CPU_BY_CORE/Makefile/_LINKER/memory.x. Verdict: NEW-KIND."
  - "Q6 done criteria: NEW build_idf_cell in engine/verify — render CMake tree, docker run idf.py build in the IDF image, assert build/*.elf+*.bin exist + partition-table fit (offsets/sizes, not arm-none-eabi-size), optional esptool verify-flash as proof_rung, warn-only policy kept, evidence extended with idf cmd + bin sizes. e2e.py:57-62 CELLS gain (esp32cam,idf)."
open:
  - "Owner's exact CAM variant + hardware-in-hand UART flash confirmation (needs the physical board + FTDI on the owner's bench)."
  - "espressif/idf image arch support (linux/amd64 only, or arm64 too?) + digest pin — verify at build time on this Mac (cf. bug-022 preflight)."
  - "First-slice implementation ticket (suggested: pack YAML + esptool backend dry-run + docs, no image build yet) — follow-up req/task, out of spike scope."
  - "Rust via esp-hal 1.0 (no_std, supports classic ESP32) — noted as the future second-language path, not investigated."
links:
  openspec: none
  bmad: none
worktree: none
branch: none
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
