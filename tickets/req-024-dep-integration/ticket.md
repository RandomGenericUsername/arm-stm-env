---
id: req-024
title: "C/C++ dependency integration (Conan 2 / CPM)"
kind: requirement
status: proposed
size: L
lane: bmad-advisory
parent: epic-002
links:
  openspec: none
  bmad: []
worktree: none
branch: none
---

# C/C++ dependency integration (Conan 2 / CPM)

## Requirement

Reach cargo-parity for C/C++ dependencies in generated projects — the post-V1 branch
of `spike-002` (`brief-universal-mcu-env.md:25`). Choose Conan 2.x, CPM/FetchContent, or
continue disciplined vendoring, and integrate it (or record a deferral).

## Context / evidence (Conan 2 measured live this session)

- Conan 2.33.0 has first-class bare-metal plumbing: `os=baremetal` in `settings.yml`,
  the host/build two-profile model, and a **`MakeDeps`** generator that emits
  `conandeps.mk` — a fit for mu's Make-based `make-cmsis` stack (`conan/tools/gnu/makedeps.py`).
- **ConanCenter has no bare-metal packages:** `conan search` → 0 for
  `cmsis`, `stm32`, `freertos`, `lvgl`, `littlefs`, `fatfs`, `nanopb`, `tinyusb`,
  `segger`; only `mbedtls` (22) and `cjson` (8) exist (host-oriented). So adopting
  Conan means authoring vendor recipes yourself.
- **CPM/FetchContent integrate CMake only**, and mu renders Make for STM32
  (`engine/adapters/toolchain/__init__.py:16-21`) — `spike-002:89-91`.

## Acceptance

- [ ] A chosen mechanism (with evidence) integrated into the generated C/C++ flow, **or**
      an explicit written deferral naming the trigger conditions.

## Triggers (spike-002:118-121)

- transitive conflicts in the dep graph → CPM (if CMake is adopted);
- prebuilt/host libs or registry scale → Conan 2.x (not vcpkg).
