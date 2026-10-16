# Work-split view — from the architecture spine

Each item cites governing ADs. Order is dependency order. Refreshed 2026-10-16 after the ESP32
bring-up (spike-007) exposed spine/code drift; the refactor slice (AD-16) gates the new-device slice.

## Delivered — epic-001 children (23/23 done)

1. **Engine core + model validation** — `core/` model, validation, family-block registry, endpoint/proof structs. AD-1, AD-2.
2. **Pack frame schema + 3 STM32 packs** — frame validator, STM32 family blocks, F411RE/H755/WL55JC packs, re-verified OpenOCD targets, proof rungs. AD-4, AD-5, AD-10.
3. **Thin CLI verbs + shim** — create/dev/build/flash/debug orchestration, per-OS probe mapping. AD-5, AD-6, AD-9.
4. **Probe adapters: OpenOCD (+ probe-rs)** — rendering from the certified model, multi-piece results, proof payloads. AD-2, AD-3, AD-9, AD-10.
5. **Container images per toolchain + caches** — cpp/rust images, core-owned cache keys, registry lookup. AD-7, AD-8.

## Refactor slice — seam separation on the STM32 tree (AD-16 gate)

Behavior-preserving: suite green, rendered output unchanged. **These land before any new-device work.**

| # | Slice | Governed by | Acceptance |
| --- | --- | --- | --- |
| R1 | Split the probe port: FlashPort + DebugPort; per-port proof-rung ownership; re-pin the conformance test; CLI fails a verb whose port is unimplemented | AD-12 | both backends re-conform; supported paths unchanged |
| R2 | Relocate family block validators `core/` → `packs/`; registry keys qualified by (family, block); loader attaches blocks generically | AD-13 | tests prove a pure move + no key collisions |
| R3 | Pack-declared `stacks` map (in the shared frame) + toolchain registry (image + build command keyed by stack); rendered tree persists its stack id | AD-11, AD-8 | language no longer selects toolchain |
| R4 | Gate artifact emission on model facts; pack `probe:` block becomes functional (CLI replaces pack requirements wholesale; per-family VID registration) | AD-14, AD-9 | STM32 trees byte-identical |
| R5 | Verify matrix → `(pack, stack)`; per-stack build + fit check in a shared build-evidence envelope | AD-15, AD-10 | a third build system can register |
| R6 | Name the operational envelope (container runtime, host git/network, USB + cgroup model, platform) as one owned contract | AD-17 | the envelope is stated, not per-lane |

## New-device slice — ESP32 (first non-STM32 board)

Lands **after** the refactor, as pure additions (no core diffs). Live reference already exists:
spike-007 (ESP32-D0WD rev1.0, 4 MB flash, IDF v6.1 triple flashed + blink @115200).

| # | Slice | Governed by | Note |
| --- | --- | --- | --- |
| E1 | `packs/esp32cam.yaml` + esp32 family block validators (`esptool`/`partitions`/`sdkconfig`) | AD-4, AD-13 | validators ship with the pack, not core |
| E2 | `esptool` probe backend (**FlashPort only**, no DebugPort) + UART probe binding + `10C4`/`1A86` VID registration | AD-3, AD-12, AD-14 | programs `(addr, bin)` triples; `Hash of data verified.` is the proof |
| E3 | `idf-cmake` template family (CMakeLists + sdkconfig + partitions); gate OpenOCD/CMSIS artifacts off | AD-11, AD-14 | image `espressif/idf:v6.1` (digest-pinned, amd64+arm64) |
| E4 | `build_idf_cell` in the verify harness | AD-15 | evidence keys stay AD-10 comparable |

## Spikes

- **A. Per-pack OpenOCD target verification** — closed; consumes into story 2.
- **B. C/C++ dependency mechanism** — closed (vendoring chosen).
- **C. 2026 toolchain recon** — closed (vanilla GCC; CubeCLT gated on license proof).
- **D. ESP32-CAM pack requirements** (spike-007) — reported; live bring-up green, incorporation planned above.

## Explicitly not children (parked)

Pack validator/generators, Windows native lane, IDE attach, cloud/team features. **Non-STM32 packs are
no longer parked** — this reverses the original park; ESP32 is now the new-device slice above.
