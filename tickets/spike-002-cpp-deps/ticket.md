---
id: spike-002
title: "C/C++ dependency mechanism"
kind: spike
status: reporting
parent: epic-001
timebox: "4h"
links:
  openspec: none
  bmad: []
worktree: ""
branch: ""
---

## Questions

1. Conan vs vcpkg vs CPM/FetchContent vs disciplined vendoring for bare-metal STM32 C/C++ — which fits versioned-container distribution with offline rebuild?
2. Does the winner fold cheaply into V1 or stay post-V1?

## Findings

### Answered

**Conan 2.x** — fullest cargo-parity (ranges + lockfiles + revisions), first-class
cross-compile, explicit air-gap story, heaviest container/tooling cost.
- Pinning: `conan.lock` snapshots exact version+revision; ranges resolve against it.
  Evidence: https://docs.conan.io/2/tutorial/versioning/lockfiles.html —
  "Lockfiles are a mechanism to achieve reproducible dependencies, even when new
  versions or revisions of those dependencies are created."
  Verify: `curl -s https://docs.conan.io/2/tutorial/versioning/lockfiles.html | grep -i lockfile | head -3`
- Bare-metal: two-profile host/build model (`--profile:host`/`--profile:build`,
  `[buildenv]` CC/CXX/LD) fits arm-none-eabi cross toolchains.
  Evidence: https://docs.conan.io/2/tutorial/consuming_packages/cross_building_with_conan.html —
  "Conan can model that case using two different profiles, one for the machine that
  builds the application ... and another for the machine that runs those binaries".
  Verify: same-page grep for `profile:host`.
- Offline: `conan cache save/restore` moves .tgz between caches; doc names
  "air-gapped setups" explicitly — but flags it EXPERIMENTAL/transitory, not storage.
  Evidence: https://docs.conan.io/2/devops/save_restore.html —
  "For air-gapped setups, in which packages can only be transferred via client side."
  + "This feature is experimental and subject to breaking changes."
- Integrates via generators (`CMakeToolchain`, `CMakeDeps` in conanfile.py shown on the
  cross-building page); also documents a Makefile integration page.
  Evidence: same cross-building page conanfile.py (`generators = "CMakeToolchain", "CMakeDeps"`).
- Cost: needs Python+Conan in image, profiles per target, and recipes for bare-metal
  libs (STM32 HAL/CMSIS are NOT in ConanCenter as turnkey bare-metal packages —
  Evidence: MISSING — run `conan search` / browse conan.io/center to confirm; do not
  treat as fact).

**vcpkg** — strong versioning + offline assets, but desktop/host-oriented; bare-metal
is custom-triplet work.
- Pinning: baseline + `version>=` minimum-selection + `overrides`; versions registry
  maps versions to git-tree objects.
  Evidence: https://learn.microsoft.com/vcpkg/users/versioning.concepts —
  "The baseline gives you hassle-free, conflict-free dependency management with full
  reproducibility." Verify: fetch page, grep `builtin-baseline`.
- Offline: asset caching mirrors sources; binary caching reuses builds.
  Evidence: https://learn.microsoft.com/vcpkg/get_started/overview —
  "Asset caching allows vcpkg to work in air-gapped and offline environments".
  Detail Evidence: https://learn.microsoft.com/vcpkg/users/assetcaching (`x-azurl`,
  `x-block-origin`, `file://` mirror support).
- Bare-metal: triplets capture target env; `VCPKG_CHAINLOAD_TOOLCHAIN_FILE` overrides
  compiler detection — the hook a `arm-none-eabi` custom triplet would use.
  Evidence: https://learn.microsoft.com/vcpkg/users/triplets —
  "Specifies an alternate CMake toolchain file to use. This (if set) will override
  all other compiler detection logic."
  No stock bare-metal arm-none-eabi triplet found in fetched docs —
  Evidence: MISSING — run `ls triplets/community/` in a vcpkg checkout to confirm.
- Integrates: CMake toolchain/MSBuild/manual ("any build and project system",
  overview page). Cost: full vcpkg clone + source builds bloat versioned images;
  baseline pins whole-registry commit — coarse for firmware.

**CPM/FetchContent** — CMake-native, lightest manager; pinning + offline are real but
thinner than cargo.
- Pinning: `GIT_TAG`/commit hash or `URL`+`URL_HASH`; package-lock file support.
  Evidence: https://github.com/cpm-cmake/CPM.cmake —
  "By versioning dependencies via git commits or tags it is ensured that a project
  will always be buildable." + "Supply chain security best practice: ... always
  prefer specifying immutable git commit hashes". Lock: `CPMUsePackageLock(package-lock.cmake)`.
- Offline: `CPM_SOURCE_CACHE` pre-seeded cache allows offline configure; upstream
  FetchContent has `FETCHCONTENT_FULLY_DISCONNECTED` (post-first-configure).
  Evidence: CPM README — "This will also allow projects to be configured offline, as
  long as the dependencies have been added to the cache before."
  (cmake.org FetchContent page fetched for `FETCHCONTENT_FULLY_DISCONNECTED` semantics.)
- Bare-metal fitness: configure-time source builds under the project's own toolchain
  file — good fit, zero registry; but "No pre-built binaries ... all dependencies are
  initially downloaded and built from scratch" and "Dependent on good CMakeLists"
  (CPM README Limitations) — STM32 vendor packs often lack usable CMakeLists.
- Integrates: CMake ONLY (`CPMAddPackage` in CMakeLists). No CMake decision in-repo
  yet (glob `**/CMakeLists.txt` → no files; grep tickets for CMake/Makefile → no
  matches) — adopting CPM pre-commits V1 to CMake.

**Disciplined vendoring (git submodules)** — exact-commit pinning, zero tooling,
build-system-neutral; manual transitive burden.
- Pinning: superproject records submodule as gitlink (mode `160000`) = exact commit.
  Evidence: https://git-scm.com/book/en/v2/Git-Tools-Submodules —
  "Git sees it as a particular commit from that repository." + `.gitmodules`
  "is version-controlled ... pushed and pulled with the rest of your project".
- Offline/container: fully offline once cloned (`--recurse-submodules`); bakes into
  versioned image as plain files; needs only git. No manager, no registry, no daemon.
- Cost: no version resolution ("first-version-wins" N/A — human resolves), upstream
  update = manual commit bump; nested-submodule and detached-HEAD footguns documented
  on the same page. Fine for a handful of slow-moving firmware deps (HAL, CMSIS, tiny libs).

### Open

- Whether STM32 HAL/CMSIS exist as usable Conan/vcpkg ports (else both require
  authoring recipes/ports — decisive cost question). Next: browse conan.io/center +
  vcpkg ports registry.
- V1 build-system choice (CMake vs Make) — gates CPM viability.

## Recommendation

**Pick disciplined vendoring (git submodules) for V1; integration = cheap-enough-for-V1.**
One-line reason: exact-commit pinning + zero container footprint + build-system-neutral,
and the V1 dep set is a handful of slow-moving firmware sources where cargo-style
resolution buys nothing.
Post-V1 triggers: dep graph grows transitive conflicts → adopt CPM (if CMake chosen)
for lockfile ergonomics; need prebuilt/host libs or registry scale → Conan 2.x is the
cargo-parity destination (lockfiles+revisions, host/build profiles, cache save/restore),
NOT vcpkg (host/desktop-oriented, no evidenced bare-metal story).
