---
title: "Universal MCU dev framework"
status: finalized
created: 2026-10-08
updated: 2026-10-08
---

# Product Brief: Universal MCU dev framework

## Vision

One CLI that takes you from zero to a running program on any supported MCU: it scaffolds projects from pre-created hardware configs (or your own), gives you an interactive development environment, and builds/flashes already-created projects — identically inside a container or transparently from a bare host. Linux and macOS day one; Windows is a deferred lane, kept possible by the container+shim design, not designed out.

## Users

Primary user today: the author (solo embedded developer, STM32 bench). Shipped as a product: other firmware developers adopt it per device-pack. No team workflows, no hosted service, no IDE lock-in.

## What it does (day one)

- `create` from a hardware pack reference (+ project name) for STM32 targets in C, C++, Rust. Day-one packs: Nucleo-F411RE, Nucleo-H755ZI-Q, Nucleo-WL55JC (carried over from sibling coverage).
- Interactive container dev environment per project (shell first; IDE attach later), with toolchain, probe tools, debug configs.
- `build` / `flash` on already-created projects from a bare host with zero preinstalled deps (host-transparent mode).
- User-supplied hardware config (`--config`) overriding/extending packs; in V1 the user is responsible for config correctness (own research), and the product ships prebuilt packs for author-owned MCUs. Pack config generators and pack validation tooling are parked post-V1 work, validation first.
- Device description comes from exactly one source: `--mcu-config` (prebuilt name or user file) XOR individual hardware flags (e.g. `--ram`). If a config was passed it is used overall, otherwise the individual params. Run-level flags (`--lang`, `--probe`, output, project name) always apply and are never part of this choice.
- C/C++ dependency story must reach parity with cargo: V1 mandates the need and carries a spike that selects the mechanism with evidence (Conan, vcpkg, CPM/FetchContent, or disciplined vendoring); integration is the first post-V1 epic unless the spike shows it folds cheaply into V1.

## Non-goals (day one)

- Non-STM32 vendors (later packs, same engine). Windows native support (nice-to-have lane; WSL2 path documented later). Pack validator tooling (later). Cloud builds, team/enterprise features, IDE plugins.

## Differentiators (evidenced)

- Config-driven scaffolding *plus* zero-host-deps dual-mode execution: PlatformIO/Arduino CLI do the former on host-installed toolchains; probe-rs does flashing brilliantly but scaffolds nothing; none ships a versioned container with an identical host shim (comparables recon, 2026-10-08 session).
- Strict separation: hardware pack (device truth) vs run config (invocation). Never merged.

## Constraints

- Universal-by-design: engine is vendor-neutral hexagonal core; hardware packs, toolchains, and probe backends are adapters. STM32 ships as the reference pack, not as the core.
- Probe backends are adapters: `flash`/`debug` verbs with shipped known-working configs (OpenOCD first, probe-rs second, ST-Link fallback). CLI `--probe` selects; pack declares supported backends.
- Language is top-level run config (`c|cpp|rust`), never part of the hardware pack. Project shape (single/dual-core) is derived from pack data, never a parameter.
- Distribution: versioned OCI toolchain images + thin host shim; one image serves interactive dev and transparent execution. All versions pinned (lesson from 2024-era sibling rot: unpinned OpenOCD/CubeCLT/master-tracking broke reproducibility).
- Evidence rule applies to all product and technical claims.

## Success criteria (V1)

Each day-one matrix cell (F411RE, H755 × C, C++, Rust, OpenOCD backend): `create` → `build` → `flash` from a clean machine, board runs the program with observable proof (LED/RTT/UART output per pack definition).

## Open unknowns

- Windows path (deferred lane). Pack authorship/validation workflow (later). Exact shim implementation language (architecture phase).
