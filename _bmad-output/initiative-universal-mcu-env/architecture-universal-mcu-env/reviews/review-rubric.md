# Rubric review — architecture-universal-mcu-env (2026-10-16 update, AD-11..AD-16)

Scope: `architecture-universal-mcu-env.md` as an UPDATE — AD-11..AD-16 are new
(dated 2026-10-16); AD-1..AD-10 are pre-existing and reviewed only for
interaction with the new ADs. Supporting evidence: `.memlog.md`,
`work-split-view.md`, and the brownfield code under `engine/`.

Verdict: **FAIL (narrow)** — the six new ADs close the drift class the memlog
names (language flag conflation, ABC narrower than callers, STM32-only
renderer/vendoring/verify, dead `probe:` block) and largely resolve the earlier
F1–F5 ownership holes. But three structural problems remain: AD-13's stated
acceptance test is false against the codebase it supposedly ratifies (C1),
AD-8 and AD-11 are simultaneously in force and contradict on image selection
(C2), and the operational/environmental envelope is a whole silent dimension
(C3). Two more rules are unenforceable as written (H1, H5). Verify the failing
claims before planning the refactor slice (R1–R5), which is where these
questions must actually be settled.

---

## What the new ADs get right

- **AD-12/AD-13** resolve the adversary F1 (validator owner) and the
  ABC-narrower-than-callers defect: the FlashPort set
  (`render_argv`/`flash`/`proof_for`/`last_transcript`) is now written down and
  the port is split. Evidence: `engine/adapters/__init__.py:56-70` declares
  only `flash`/`debug`; callers use `render_argv`/`proof_for`/`last_transcript`
  (`engine/cli/main.py:315,323`; `engine/adapters/openocd.py:202`).
- **AD-11** fixes the real "language string conflates source, build system, and
  image" defect: `.memlog.md:23`; `engine/cli/main.py:216-220` and
  `engine/templates/renderer.py:1227` branch on `lang`.
- **AD-14** names the actually-dead pack `probe:` block: it is read by the
  loader (`engine/core/loader.py:62`) and rendered into comments
  (`renderer.py:284-285`) but never used by probe resolution
  (`engine/cli/shim.py:196-242` takes CLI selectors only).
- **AD-15** fixes the per-language builder assumption in the verify harness
  (`engine/verify/e2e.py:327-345` picks the builder by `lang`).
- **AD-16** gives the refactor a gate and dependency order; the work-split view
  maps it to R1–R5, one slice per AD.

---

## Critical

### C1 — AD-13 "zero core diffs for a new brand" is false against the model/loader it must ratify

**AD/section:** AD-13 (line 120: "A new brand adds validators + pack sections
+ adapters and requires **zero core diffs** — the AD-1 acceptance test") and
AD-13's "`core/` owns only the frame, the registry mechanism, and dispatch".

**Problem:** Relocating family block *validators* out of `core/` does not
remove the family-specific logic that lives in `core/`. `core/loader.py` name-
checks STM32 block names and writes STM32 defaults into `DeviceFacets`; the
facets struct itself defaults to `stm32hal` / `stm32_config.h`. A new brand
(ESP32: no `fpu`/`linker`/`openocd`/`config_headers`/`example`/`svd` blocks,
different facet shape) cannot load without editing `core/loader.py` and
`core/model.py` — i.e. with a core diff. AD-13's acceptance test therefore
cannot pass after R2, and AD-1's "core diffs are forbidden for brand additions"
is still violated by the loader.

**Evidence:**
- `engine/core/loader.py:89-140` — `fpu_block = blocks.get("fpu", {})` …
  `config_library=cfg_block.get("library", "stm32hal")`,
  `config_header=cfg_block.get("header", "stm32_config.h")`,
  `example_led`, `cpu2_boot`, `svd` are all STM32-specific extractions/defaults.
- `engine/core/model.py:215-232` — `DeviceFacets` defaults
  `config_library = "stm32hal"`, `config_header = "stm32_config.h"`,
  `config_defaults_source = "pack/defaults.h"`.
- `engine/core/registry.py:88,108,121,134,147,160,174,192,259,273` — all
  validators registered from `core/`, `families=("stm32f4","stm32h7","stm32wl")`.

**Suggested fix:** Either (a) widen AD-13's scope to "frame, registry
mechanism, dispatch, **and an opaque, family-owned facet bag with no
family-named fields or defaults in `core/`**", moving the `fpu`/`linker`/
`config_headers`/`example`/`svd`/`cpu2_boot` reading into `packs/`-shipped
code; or (b) keep AD-13 but redefine its acceptance test as "no core diff for
a *new pack in an existing family*", and add a separate AD covering how a new
*family* extends the model. As written the rule over-promises.

**Verify:** `rg -n 'stm32hal|stm32_config.h|cpu2_boot|example_led' engine/core`

---

### C2 — AD-8 and AD-11 are both in force and contradict on what selects the toolchain image

**AD/section:** AD-8 Rule (line 90: "The top-level language flag resolves the
image via a lookup interface owned by `core/`") vs AD-11 Rule (line 108: "The
resolved stack — never the language string — selects the template family, the
toolchain image, and the build command").

**Problem:** AD-11 lists AD-8 under **Binds** but never amends AD-8's text. A
unit may implement AD-8 literally (language → image; the current code does
exactly this at `engine/cli/main.py:419` via `DefaultImageLookup().image_for`)
while another implements AD-11 (stack → image). Both are compliant, and they
diverge on the same `--lang c` invocation. This is the F2 class the adversary
review already failed the spine for.

**Evidence:**
- `architecture-universal-mcu-env.md:90` (AD-8) vs `:108` (AD-11).
- `engine/adapters/__init__.py:128-148` — `DefaultImageLookup.TABLE` is keyed
  by language (`c`/`cpp`/`rust`) and is the current resolver.
- `engine/cli/main.py:419` — image resolved from `args.lang` before any pack load.

**Suggested fix:** Rewrite AD-8's resolution sentence to delegate: "One image
per stack; the top-level language flag selects the pack-declared stack, and the
resolved stack resolves the image via the core-owned lookup." Mark the old
AD-8 clause superseded so only one rule text describes the resolver.

**Verify:** `sed -n '86,108p' _bmad-output/initiative-universal-mcu-env/architecture-universal-mcu-env/architecture-universal-mcu-env.md`

---

### C3 — The operational/environmental envelope is a whole silent dimension

**AD/section:** Stack table (lines 149-154), AD-7 (lines 80-84), Deferred
(lines 179-188).

**Problem:** The spine authorizes "Python >= 3.11 / uv >= 0.12" and "one
stateless container exec", but the envelope the product actually runs in is
neither decided, deferred, nor opened: the container runtime (and whether
Podman/nerdctl are allowed), host `git` (required at `create` time for
vendoring), Linux probe access (`/sys/bus/usb`, device-cgroup rules,
udev/docker-group permissions), network at `create` (vendoring is online), and
the forced `--platform linux/amd64`. Per the rubric, a whole dimension left
silent — especially the operational/environmental envelope — is a finding.
This also means the spine does not ratify the brownfield: the code needs more
than python+uv, and the spine never says so.

**Evidence:**
- Runtime hardcoded: `engine/cli/shim.py:327` (`"docker", "run"`),
  `engine/cli/main.py:465-483` (`shutil.which("docker")`, `docker image inspect`).
- Host `git` required: `engine/templates/vendoring.py:181-185`; network at
  create: `:112-117`.
- Probe access model: `engine/cli/shim.py:58` (`/sys/bus/usb/devices`),
  `:313-318` (`--device-cgroup-rule`, `-v /dev/bus/usb`).
- Platform forced: `engine/verify/e2e.py:64,255` (`linux/amd64`).
- Spine says nothing: `architecture-universal-mcu-env.md:149-154` lists only
  Python and uv; Deferred `:182` mentions "OCI runtime" only inside a version-pin
  bullet.

**Suggested fix:** Add an AD (or an explicit, named Open Question) for the
execution envelope: the container runtime (docker-only vs OCI-compatible with a
named detection order), the full host prerequisite set (python, uv, git,
runtime, OS probe-access requirements), network-at-create, and arch/platform
policy for images and the verify harness.

**Verify:** `rg -n 'docker|which\("git"\)|/sys/bus/usb|linux/amd64' engine`

---

## High

### H1 — AD-11's "resolved stack selects the build command" is unenforceable where no pack is loaded

**AD/section:** AD-11 (line 108).

**Problem:** `mu build` and `mu dev` do not require or read a pack, and the
build command is chosen from `lang` alone; the project tree carries no stack id.
So `(pack, language) → stack` has no pack at build time. AD-11 never says how a
rendered project remembers its stack. Two units will persist it differently
(Makefile constant vs a manifest vs requiring `--mcu-config` on `build`) and
diverge on `mu build --project-dir .`.

**Evidence:**
- `engine/cli/main.py:216-220` — `_local_tool_cmd(lang)` returns
  `["make","build"]` / `["cargo","build"]` from `lang` only.
- `engine/cli/main.py:108-148` — `build`/`dev` do not require `--mcu-config`;
  `create` is the only verb that does (`:171-183`).
- `engine/templates/renderer.py:1191-1277` — no stack id is written to the tree.

**Suggested fix:** State that `create` persists the resolved stack id in the
tree (single source) and `build`/`dev`/verify re-read it; or require the pack on
those verbs. Either way AD-11 must name where the stack id lives after render.

**Verify:** `rg -n '_local_tool_cmd|mcu_config' engine/cli/main.py`

---

### H2 — AD-13 specifies *where* validators live but not *who imports/registers* them without core depending on packs

**AD/section:** AD-13 (lines 118-120) plus the dependency diagram (lines 34-40:
"PACKS --> CORE", "nothing device-specific is depended on *by* core").

**Problem:** Today registration is module-level inside `core/registry.py`
(`register(...)` on import). Moving validators to `packs/` requires a trigger:
does `core/` import `packs/` (violates the dependency direction), does the CLI
import them, or do `packs/` expose entry points? AD-13 leaves this open. Two
units pick different mechanisms; one violates AD-1. (This also changes
`packs/` from the "frame data" directory in AD-4/seed line 39 into executable
Python mounted read-only at `shim.py:337`.)

**Evidence:**
- `engine/core/registry.py:23-40` — `_REGISTRY`, `FAMILY_BLOCKS`, `register()`;
  registration happens at import of this module (`:88` etc.).
- `engine/core/loader.py:17` — `from engine.core.registry import …`;
  loader never imports `packs/`.
- `architecture-universal-mcu-env.md:34-40` — dependency direction asserts core
  does not depend on packs.

**Suggested fix:** Name the registration mechanism and its owner in AD-13
(e.g. `packs/` ships an entry-point group that a non-core bootstrap loads), and
say explicitly that `packs/` now contains executable validator code, not only
frame data (update the seed/AD-4 wording).

**Verify:** `rg -n 'register\(|import packs|entry.point' engine/core engine/cli`

---

### H3 — AD-14 reintroduces a field-level merge that AD-5 forbids, with no precedence

**AD/section:** AD-14 (line 126: "The pack's `probe:` block is the single
source of connection requirements; the shim merges them with CLI selectors")
vs AD-5 (line 72: "never field-level merge").

**Problem:** "Merge" is undefined for conflicts: pack declares VID `0483`, CLI
passes `--vid 1a86` — which wins, override or union? AD-9 already assigns
connection-requirement declaration to the shim mapping; AD-14 restates the
ownership. Two units resolve the same invocation to different probes.

**Evidence:**
- `architecture-universal-mcu-env.md:72` (AD-5) vs `:126` (AD-14).
- `engine/cli/shim.py:196-242` — `resolve_probe_binding` today takes CLI
  selectors only; `engine/cli/main.py:266-272` never passes `device.probe_ref`.

**Suggested fix:** State precedence and semantics explicitly (CLI selector
overrides the pack block as a whole value; no field union) and note this is
*selector resolution*, not the device-field merging AD-5 bans. Cross-reference
AD-9 rather than restating ownership.

**Verify:** `sed -n '68,76p;122,126p' _bmad-output/initiative-universal-mcu-env/architecture-universal-mcu-env/architecture-universal-mcu-env.md`

---

### H4 — AD-16 "behavior-preserving, rendered output unchanged, suite green" is contradicted by AD-12 and AD-14

**AD/section:** AD-16 (line 138).

**Problem:** AD-12 changes observable behavior (the CLI must *fail* a debug
verb whose port is absent, "never fabricate a handle"), while every current
backend fabricates a deterministic handle and a test asserts it. AD-14 makes
the currently-dead pack `probe:` block functional, so probe resolution changes.
AD-16 as written forbids both. Two units read "behavior-preserving" as (a) no
observable CLI change or (b) rendered-tree bytes byte-identical; they diverge.

**Evidence:**
- `engine/adapters/openocd.py:261-265` and `engine/adapters/probe_rs.py:227-231`
  — `debug()` returns a fabricated `DebugHandle` ("no live attach here").
- `engine/adapters/tests/test_conformance.py:92-98` — asserts the handle is
  returned; `:75` pins `__abstractmethods__ == {"flash","debug"}`.
- `engine/cli/shim.py:196-242` — pack `probe:` block not consulted (AD-14
  changes this).

**Suggested fix:** Scope AD-16's invariant to "rendered STM32 tree bytes
unchanged for existing packs", and explicitly allow the AD-12/AD-14 observable
changes to be pinned by updated tests in R1/R4.

**Verify:** `rg -n 'no live attach|def debug' engine/adapters`

---

### H5 — AD-14's artifact gate "a family-declared vendor source → vendor tree" has no model fact to gate on

**AD/section:** AD-14 (line 126).

**Problem:** Vendoring is keyed by the pack *id string prefix* in code, not by
any model block, and `DeviceFacets` has no vendor field. So the gate cannot be
enforced from "model facts" as written. Further, the entire C/C++ template
family is CMSIS/STM32 (arm-none-eabi-gcc, `cmsis_include`, `vendor/cmsis-device-<id>`,
`ENTRY(Reset_Handler)`); AD-14 gates only `openocd.cfg`, config headers and the
vendor tree, not the Makefile/linker, so an IDF C project would still emit the
STM32 family unless AD-11's stack selection rewrites the whole family.

**Evidence:**
- `engine/templates/vendoring.py:41-67` — `FAMILY_REPOS` + `_family_of(pack_id)`
  (string prefix), no model input.
- `engine/core/model.py:205-232` — `DeviceFacets` has no vendor field.
- `engine/templates/renderer.py:292-359` (Makefile `arm-none-eabi-*`),
  `:396-450` (`_LINKER` `ENTRY(Reset_Handler)`), `:900-1273` (CMSIS/vendor paths).

**Suggested fix:** Either name the model fact that gates vendoring (e.g. a
`vendor:` family block carried into the model) or move the family→vendor-repo
map behind the same core-owned registry AD-8/AD-13 use. State that the *stack*
selects the whole template family and AD-14 gates the STM32-only artifacts
inside it.

**Verify:** `rg -n 'FAMILY_REPOS|arm-none-eabi|vendor/cmsis-device' engine`

---

## Medium

### M1 — AD-15 conflates flash-proof keys with verify-harness (build) evidence, and puts the fit check per-stack

**AD/section:** AD-15 (lines 130-132).

**Problem:** AD-10's SUBSET-comparable keys (`pieces`, `verified`) are produced
by the *flash* proof structs, not the *build* verify harness, whose evidence has
no such keys. Also each stack registering "its size/fit check" makes fit a
per-stack concern, but fit is a pack/memory property — per-stack fit checks can
compute overflow differently.

**Evidence:**
- Proof keys: `engine/adapters/openocd.py:280-286`, `engine/adapters/probe_rs.py:249-254`.
- Verify evidence (no `pieces`/`verified`): `engine/verify/e2e.py:351-386`.
- Fit is pack/memory-owned: `engine/verify/e2e.py:157-197` (`pick_region`,
  `assert_fits`).

**Fix:** Split: each stack registers *build + size parser*; the pack/core owns
the fit comparison; and say which evidence carries `pieces`/`verified` (proof,
not build).

### M2 — The deferred `stacks` placement is itself a live divergence point, and the memlog assumption is absent from the spine

**AD/section:** AD-11 + Deferred (line 186).

**Problem:** "Where the `stacks` map lives — the shared frame vs a `build`
family block — open; resolve at the R2/R3 boundary" lets two units diverge:
frame placement (core validates shape) vs family-block placement (family
validator, AD-13), with different "zero core diffs" outcomes. R3 *is* the stack
axis, so this must be decided before the slice. `.memlog.md:30` records an
assumption ("the frame validates the stacks map shape while the owning family
registers the stack ids") that the spine omits.

**Evidence:** `architecture-universal-mcu-env.md:186`; `.memlog.md:30`;
`work-split-view.md:22`.

**Fix:** Decide before R3 and record the decision (and who registers `build`
blocks) in the spine, not only in the memlog.

### M3 — AD-12 names an undefined DebugPort method and misplaces `render_argv`

**AD/section:** AD-12 (line 114: "sessions are **DebugPort** (`debug`/`monitor`)").

**Problem:** `monitor` exists nowhere else — not in `VERBS`, not in the ABC,
only as OpenOCD `monitor <cmd>` strings. Also `render_argv` is assigned to
FlashPort, but `debug` uses it, so a DebugPort-shaped backend cannot render its
session argv. And "a backend implements DebugPort only where the device supports
attach" states a *per-device* capability as a *per-backend* property without
saying the pack declares attach support.

**Evidence:** `engine/cli/main.py:47` (`VERBS`);
`engine/adapters/__init__.py:56-70` (ABC has only `flash`/`debug`);
`engine/adapters/openocd.py:264` (`debug` calls `render_argv`);
`rg -n 'monitor' engine` → only gdb-command strings in `renderer.py`.

**Fix:** Define the exact method sets per port, say where attach-capability is
declared (pack), and either drop `monitor` or state it is not part of this
altitude.

### M4 — AD-12 "never fabricate a handle" is ambiguous against the deliberate no-live-claim handle

**AD/section:** AD-12 (line 114).

**Problem:** Current `debug()` intentionally returns a deterministic handle
("No live attach here (no probe claim)"). Read literally, AD-12 forbids that for
attach-capable backends too, which is broader than the port split intends.

**Evidence:** `engine/adapters/openocd.py:261-265`,
`engine/adapters/probe_rs.py:227-231`.

**Fix:** Distinguish "no DebugPort → fail the verb" from "DebugPort present but
live attach OPEN → documented placeholder handle".

### M5 — Multi-language image resolution remains deferred although AD-11 claims to key it

**AD/section:** Deferred (line 185) vs AD-11 (lines 104-108).

**Problem:** A project with C + Rust has two stacks and two images; no rule says
which image `build`/`dev` uses. AD-11 says the stack is the resolution key but
one invocation has no single stack. Divergence point left uncovered.

**Evidence:** `architecture-universal-mcu-env.md:185`; `engine/cli/main.py:419`
(single `image_for(args.lang)`).

**Fix:** Decide one image per invocation (per-stack exec) or an explicit
multi-image rule before the stack axis lands.

---

## Low

### L1 — Named tech slightly stale: uv note says 0.12.23, latest is 0.13.1

AD-11..16 add no external versions, but the Stack table's uv note
(`architecture-universal-mcu-env.md:154`) is behind. `>= 0.12` still admits
0.13.1, so no correctness break — refresh the "verified" note.
Evidence: GitHub API `astral-sh/uv` latest = `0.13.1` (published 2026-10-14).
Also verified current: ESP-IDF v6.1 (2026-08-27), probe-rs v0.32.0,
esptool v5.6.0, avrdude v8.3.
Verify: `curl -s https://api.github.com/repos/astral-sh/uv/releases/latest | rg tag_name`

### L2 — Stack id `idf-cmake` is imprecise for ESP-IDF

ESP-IDF builds via `idf.py` (a CMake+Ninja wrapper), not a bare CMake stack, so
the id `idf-cmake` implies a build command that does not exist. Prefer `idf` /
`idf-py` and let the stack register the actual command.
Evidence: `work-split-view.md:35` pins `espressif/idf:v6.1`; AD-11 line 108
names `idf-cmake`.

### L3 — `last_transcript` as a "port member" has no declared shape

AD-12 lists `last_transcript` among FlashPort members, but it is per-instance
mutable state, not a call (`engine/adapters/openocd.py:202`). Whether it is a
property or attribute is unspecified → minor interface divergence.
Verify: `rg -n 'last_transcript' engine`

---

## Rubric checklist

| Criterion | Result | Basis |
| --- | --- | --- |
| Fixes the real divergence points, misses none | **Partial** | Fixes the F1–F5 class; misses build-time stack identity (H1), multi-language image (M5), validator registration mechanism (H2), probe-merge precedence (H3). |
| Every AD Rule is enforceable and prevents its divergence | **Partial** | AD-13's acceptance test is false against the code (C1); AD-11 is unenforceable without a pack (H1); AD-14's vendor gate has no model fact (H5); AD-16's "behavior-preserving" contradicts AD-12/AD-14 (H4). |
| Nothing under Deferred could let two units diverge | **Fail** | `stacks` placement (M2), multi-language image (M5), OCI runtime inside a version bullet (C3). |
| Named tech is verified-current | **Pass (minor)** | Python/uv floor fine; uv note stale (L1); ESP-IDF v6.1 / probe-rs / esptool / avrdude verified current. |
| Ratifies rather than contradicts the brownfield | **Partial** | AD-12/AD-14 deliberately amend drift (good); AD-13's "zero core diffs" and the Stack table's python+uv-only envelope contradict the code (C1, C3). |
| Every owned dimension decided/deferred/open | **Fail** | Operational/environmental envelope silent (C3). |

---

## Bottom line

The update is directionally right and fixes the drift the memlog records, but
three items must be settled before the refactor slice is planned: **C1** (make
AD-13 match the model/loader reality or narrow its claim), **C2** (reconcile
AD-8 and AD-11 into one resolver rule), and **C3** (add the execution-envelope
dimension). H1–H5 are one-paragraph text fixes each.

## Evidence index

- Spine: `_bmad-output/initiative-universal-mcu-env/architecture-universal-mcu-env/architecture-universal-mcu-env.md` (AD-11..16 at `:104-138`; Deferred `:179-188`; Stack `:149-154`; dependency diagram `:34-40`).
- Rationale: `.memlog.md:23-31`; split: `work-split-view.md:14-36`.
- Code: `engine/core/loader.py:89-140`, `engine/core/model.py:205-232,293-347`,
  `engine/core/registry.py:23-88`, `engine/adapters/__init__.py:56-148`,
  `engine/adapters/openocd.py:202,261-286`, `engine/adapters/probe_rs.py:227-254`,
  `engine/cli/main.py:47,108-148,216-220,419,465-483`,
  `engine/cli/shim.py:58,196-242,304-341`, `engine/templates/renderer.py:263-359,396-450,1191-1277`,
  `engine/templates/vendoring.py:41-67,181-185`, `engine/verify/e2e.py:64,157-197,255,327-386`,
  `engine/adapters/tests/test_conformance.py:75,92-98`.
- External (2026-10-16): uv `0.13.1`, ESP-IDF `v6.1`, esptool `v5.6.0`,
  probe-rs `v0.32.0`, avrdude `v8.3` (GitHub releases API).
