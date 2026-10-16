---
review: web-verify
artifact: architecture-universal-mcu-env.md
update: AD-11..AD-16 added 2026-10-16
reviewer: WEB-VERIFY subagent
date: 2026-10-16
verdict: conditional
---

# WEB-VERIFY review — `architecture-universal-mcu-env.md`

**Lens.** Every committed decision (AD-11..AD-16 + their memlog/work-split siblings) must be
web-researched or reality-checked, not asserted from training data. Current library/framework
versions must be confirmed; each named technology must still exist and fit; anything that could be
out of date must have been confirmed against the web, the project, or a current starter.

**Verdict: CONDITIONAL PASS.** Every code fact asserted by the spine/memlog holds against the actual
`engine/` tree. Every pinned version that is web-checkable is current and correct — **except one**:
the "esptool **v6**" claim carried in the cited spike evidence (spike-007) is wrong; no esptool 6.x
exists. The spine's AD-11..16 decisions themselves are sound and evidence-grounded. The stack ids,
validator relocation, VID registration, and the IDF digest pin are **plans** (correctly labelled as
such), not code — so they cannot be "verified in code" yet, only "verified as targets".

---

## Tier 1 — Findings that do NOT hold (action required)

### T1.1 — "esptool v6" does not exist (wrong version claim in cited evidence)

- **Claim (spike-007, cited by the memlog as the source for the IDF/ESP32 cell and by work-split E2/E3):**
  `esptool v6 via uvx` (`tickets/spike-007-esp32-cam/ticket.md:116`, `:19`), and the memlog's
  "`esptool` over UART" record (`.memlog.md:32`).
- **Evidence (web):** PyPI `esptool` latest = **5.6.0**; the release history contains **zero 6.x**
  versions (`sixCount: 0`). GitHub releases show `v5.5.0` (2026-10-08) as latest, then 5.4.0, 4.12.0,
  5.3.x, 5.2.0, … (`github.com/espressif/esptool/releases`).
- **Verify:** `uvx esptool version` (expect 5.x) — or fetch `https://pypi.org/pypi/esptool/json`.
- **Holds?** **NO.** "esptool v6" is a factual error, most likely a conflation of "ESP-IDF v6.1"
  with the flasher. The ESP32 work is otherwise correctly described; only the version label is wrong.
- **Action:** correct spike-007 and any downstream text to "esptool 5.x". This does not change any
  AD-11..16 decision.

---

## Tier 2 — Code facts asserted by the spine/memlog — all VERIFIED against `engine/`

These are the "reality-check the repo" items. Every one matches the code. Line cites are the
authoritative `file:line`.

| # | Claim (spine/memlog) | Evidence (`file:line`) | Holds? |
| --- | --- | --- | --- |
| 2.1 | Family block validators still live in `core/` (R2 plans to relocate to `packs/`) | `engine/core/registry.py:88` `register("openocd", …, families=("stm32f4","stm32h7","stm32wl"))`; `:90` `_STM32_FAMILIES`; `:108-273` all `register(...)` calls (fpu/linker/startup/system/defines/config_headers/probe_settings/example/svd) live in `core/`; no validators under `packs/` (`rg` found none) | ✅ drift characterization is accurate |
| 2.2 | `esptool` / `idf-cmake` "stack ids" | No `stacks` map / stack ids exist anywhere under `engine/` (`rg 'idf-cmake\|make-cmsis\|cargo-cortex\|stacks'` → none). Memlog `.memlog.md:30` marks these as **"(assumption) … Confirm at the R2/R3 boundary."** | ⚠️ correctly labelled as a *plan/assumption*, not present in code |
| 2.3 | `espressif/idf:v6.1` digest pin | `docker buildx imagetools inspect espressif/idf:v6.1` → index `sha256:81893c71bb5e570088901f21def8684c25cd2a9020281bd01b843a7655edb18c`, amd64 `sha256:f81b6e07…94f218a`, arm64 `sha256:a460b1c8…4a3d0bf` — matches `spike-007:90`. Not yet referenced in `engine/` (work-split E3) | ✅ digest verified against the registry; ⚠️ pin is planned, not wired |
| 2.4 | `10C4` / `1A86` UART VIDs | Not in code (planned: `work-split-view.md:34`, `spike-007:109-111`). Values are correct: `10C4`=Silicon Labs CP210x, `1A86`=QinHeng CH340 | ✅ values correct; ⚠️ registration is planned |
| 2.5 | hardcoded `_PROBE_VIDS = ("0483",)` | `engine/cli/shim.py:64` — exact literal `_PROBE_VIDS = ("0483",)` with comment "STMicroelectronics probes all share 0483" | ✅ holds exactly |
| 2.6 | `ImageLookup` hardcoded table | `engine/adapters/__init__.py:128-137` `class DefaultImageLookup(ImageLookup)` with `TABLE = {"c"/"cpp": "…lang-cpp:15.3.rel2", "rust": "…lang-rust:1.99.0"}` | ✅ holds |
| 2.7 | Probe ABC declares only `flash`/`debug`; callers use `render_argv`/`proof_for`/`last_transcript` | `engine/adapters/__init__.py:56-69` `class ProbeAdapter(ABC)` with only `@abstractmethod flash(...)` + `@abstractmethod debug(...)`. Callers: `engine/adapters/openocd.py:204` `render_argv`, `:267` `proof_for`; `engine/adapters/probe_rs.py:177` `render_argv`, `:233` `proof_for`; `last_transcript` in `engine/cli/tests/test_verbs.py:156,219` | ✅ holds — ABC narrower than its callers |
| 2.8 | STM32-only assumptions in `engine/templates/renderer.py` | `:32-36` `CPU_BY_CORE` = only M4/M7/M0+; `:71` fallback `"target/stm32f4x.cfg"`; `:280` fallback `"stlink.cfg"`; `:807` fallback `("interface/stlink.cfg","target/stm32f4x.cfg")`; `:951` `SVD_REPO="modm-io/cmsis-svd-stm32"`; `:263-272` CMSIS-vendor paths; `:298-302` `arm-none-eabi-*` | ✅ holds |
| 2.9 | STM32-only assumptions in `engine/templates/vendoring.py` | `:41-45` `FAMILY_REPOS` = only `f4/h7/wl`; `:59-67` `_family_of()` matches only `stm32<fam>`; `:35-37` `CMSIS_5` core repo | ✅ holds |
| 2.10 | pack `probe:` block is dead — shim resolves from CLI flags only | `engine/cli/shim.py:196-242` `resolve_probe_binding()` uses only `device/vid/pid/serial` + `_autodetect`/`_PROBE_VIDS`; never reads any pack `probe:`/`probe_ref` | ✅ holds |
| 2.11 | verify harness is per-language, not `(pack, stack)` (AD-15 drift) | `engine/verify/e2e.py:44-45` `build_cpp_cell`/`build_rust_cell`; `:57` `PACK_IDS = ("stm32f411re","stm32h755","stm32wl55jc")`; `:335-337` dispatch on `lang`, not stack | ✅ holds |

**Verify (all in one):**
```
rg '_PROBE_VIDS' engine/cli/shim.py
rg -n 'class ProbeAdapter|def render_argv|def proof_for' engine/adapters/*.py
rg -n 'register\(' engine/core/registry.py
rg -n 'stm32f4x|stlink|modm-io/cmsis-svd-stm32' engine/templates/renderer.py
rg -n 'FAMILY_REPOS|stm32' engine/templates/vendoring.py
```

---

## Tier 3 — Pinned versions named anywhere — web-checked

| Technology (where named) | Claim | Web / registry result | Holds? |
| --- | --- | --- | --- |
| `espressif/idf:v6.1` (memlog:32, work-split E3) | v6.1, digest-pinned, amd64+arm64 | Docs `/en/stable/` title = **"ESP-IDF … v6.1"**; `docker buildx imagetools inspect` confirms both platforms + digest `81893c71…5edb18c` | ✅ |
| `esptool` (spine :29/:164; spike-007) | "esptool **v6**" | Latest stable **5.6.0**; no 6.x on PyPI or GitHub | ❌ **see T1.1** |
| probe-rs (spine :164) | named adapter, no version | Latest **0.32.0** (2026-07-22); active repo `probe-rs/probe-rs` | ✅ exists and fits |
| OpenOCD ST fork (spine :164, :182) | "pins the ST fork/branch, not bare upstream" | `STMicroelectronics/OpenOCD` exists; branch `openocd-cubeide-r7` updated 2026-04-14; tags to `openocd-cubeide-v1.19.0` | ✅ exists; ⚠️ branch is a moving target — pin a **tag**, not the branch |
| ARM GNU toolchain (`lang-cpp:15.3.rel2`, spine :183 "vanilla ARM GCC") | 15.3.rel2 | `gcc-arm-embedded` current = **15.3.rel2** (browsed 2026-10-15); `arm-none-eabi-gcc-action` added 15.3.Rel2 2026-10-09 | ✅ current |
| Rust (`lang-rust:1.99.0`, renderer `RUST_VERSION="1.99"`) | 1.99 stable | **1.99.0** stable 2026-10-01; **1.99.1** point release 2026-10-15 | ✅ (1.99.1 now exists) |
| uv (spine :154) | ">= 0.12 (verified 0.12.23)" | 0.12.23 **exists** on PyPI; latest is now **0.13.1** | ✅ floor valid; ⚠️ behind current |
| STM32CubeCLT (spine :183) | v1.22.0 verified 2026-10-08 | Released **2026-06-30** (RN0132 Rev 14) | ✅ |
| Python (spine :153) | >= 3.11 | Current CPython well past 3.11 | ✅ |
| `cortex-m` =0.7.9, `cortex-m-rt` =0.7.7, `panic-halt` =1.0.0, `flip-link` 0.1.12 (renderer :43-48) | "verified against crates.io API 2026-10-09" | crates.io `max_stable`: **0.7.9 / 0.7.7 / 1.0.0 / 0.1.12** — exact match | ✅ |

**Verify:** `docker buildx imagetools inspect espressif/idf:v6.1`; `curl -s https://pypi.org/pypi/esptool/json`;
`curl -s https://crates.io/api/v1/crates/cortex-m | jq .crate.max_stable_version`.

---

## Tier 4 — Minor / context notes (no decision impact)

- **T4.1** The memlog/work-split correctly self-label the not-yet-implemented seams (stack ids =
  "assumption", validator relocation = R2, VID registration = E2, IDF pin = E3). No false
  "already done" claim was found. This is the right posture for an ADOPTED-decision spine.
- **T4.2** Structural Seed (`spine:158-166`) draws `engine/packs/` and `engine/adapters/probe/`, but the
  real tree is `packs/` at repo root and a **flat** `engine/adapters/` (`openocd.py`, `probe_rs.py`).
  The seed is a target tree (AD-13 moves validators to `packs/`), so this is a rendering nit, not a defect.
- **T4.3** The digest pin is registry-verified but not pull-verified (`spike-007:94-96` already flags
  this: "verified from the registry, not from a local pull"). A `docker pull` recording `RepoDigests`
  is still owed before the image is wired.
- **T4.4** `067b` (PL2303) is correctly excluded from `_PROBE_VIDS` (`spike-007:141-145`); correctly
  note that the live cell used a PL2303 rather than a planned CP210x/CH340.

---

## Summary

- **Holds:** all 11 code-fact assertions (Tier 2) verified against `engine/`; all pinned versions
  current/correct **except** esptool (Tier 3); the IDF v6.1 digest pin verified against the registry.
- **Does not hold:** T1.1 — "esptool v6" (no such release; latest 5.6.0). Fix the cited evidence.
- **Cannot be code-verified yet (correctly labelled as plans):** stack ids, validator relocation,
  `10C4`/`1A86` registration, IDF image wiring — all carry memlog/work-split labels marking them as
  future work.
- **Verdict: conditional** — clear T1.1 (docs-only correction) and optionally record a real
  `docker pull` of `espressif/idf:v6.1`; then AD-11..16 are web/reality-verified.
