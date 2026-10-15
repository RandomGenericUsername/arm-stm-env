---
id: spike-007
title: "First non-STM32 board: what does an ESP32-CAM pack require of the framework?"
kind: spike
status: boxed
lane: direct
timebox: 4h
questions:
  - "Exact chip facts: which ESP32-CAM variant (AI-Thinker ESP32-D0WD?), and is UART/esptool flashing (no probe) confirmed with the owner's hardware?"
  - "Pack schema: which fields survive (cores, memory, example LED) and which break (arch triple, CMSIS startup/system/defines, OpenOCD blocks, SVD source, stm32hal config_headers, probe-rs settings)? Extend the schema or define a new pack-kind?"
  - "Probe backends: can the openocd/probe-rs adapter interface carry an esptool backend (serial transport, no USB node, different proof story), or does it need a new interface?"
  - "Toolchain image: ESP-IDF (xtensa + CMake/Ninja, GB-scale) or minimal xtensa-gcc + esptool? Pin version + source + checksum per the images/README pins table."
  - "Templates: can the Make/cargo project shape carry an ESP-IDF app (CMakeLists + sdkconfig + partition table), or is a new template family required?"
  - "Done criteria: what is 'cell green' for ESP32 (ELF? esptool image_info? UART boot log?) for docs/e2e-evidence.md?"
answered: []
open: []
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

> Spike stops at the box and reports `answered:` / `open:`. Implementation output from a spike is a failure. No second box without an explicit user call.
