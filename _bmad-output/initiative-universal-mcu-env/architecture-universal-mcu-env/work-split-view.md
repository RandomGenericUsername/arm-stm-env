# Work-split view — epic-001 children from the architecture

Each child cites governing ADs. Order is dependency order; spikes unblock the stories that need them.

## Stories

1. **Engine core + model validation** (`requirement`) — `core/` model, validation, family-block registry, endpoint/proof structs. Governed by AD-1, AD-2. Unblocks 2–5.
2. **Pack frame schema + 3 STM32 packs** (`requirement`) — frame validator, STM32 family blocks, F411RE/H755/WL55JC packs with re-verified OpenOCD targets and proof rungs. Governed by AD-4, AD-5, AD-10. Needs spike A output (OpenOCD targets).
3. **Thin CLI verbs + shim** (`requirement`) — create/dev/build/flash/debug orchestration, per-OS probe mapping, Python+uv packaging. Governed by AD-5, AD-6, AD-9.
4. **Probe adapters: OpenOCD (+ probe-rs second)** (`requirement`) — rendering from certified model, multi-piece results, proof payloads. Governed by AD-2, AD-3, AD-9, AD-10.
5. **Container images per toolchain + caches** (`requirement`) — cpp/rust images with pinned toolchains (incl. CubeCLT-vs-GCC decision, ST OpenOCD fork pin), core-owned cache keys, registry lookup. Governed by AD-7, AD-8.

## Spikes (per-spike boxes at triage)

- **A. Per-pack OpenOCD target verification** — re-verify every interface/target pair against current OpenOCD/ST fork (sibling configs suspect). Unblocks story 2.
- **B. C/C++ dependency mechanism** — Conan vs vcpkg vs CPM/FetchContent vs vendoring, with evidence; integration post-V1 unless cheap (brief mandate).
- **C. 2026 toolchain recon** — versions, URL schemes, CubeCLT terms; unblocks story 5. (Comparables recon already done 2026-10-08.)

## Explicitly not children (parked post-V1)

Pack validator/generators, Windows native lane, non-STM32 packs, IDE attach, cloud/team features.
