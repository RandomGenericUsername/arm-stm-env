# Adversary Review — architecture-universal-mcu-env (AD-11..AD-16 round)

Verdict: **FAIL** (holes exploitable while obeying every AD to the letter).

Scope of this pass: the seams introduced by AD-11 (`stacks` map), AD-12
(FlashPort/DebugPort), AD-13 (validators alongside packs), AD-14 (artifact
gating), AD-15 (verify matrix), plus their interactions with the pre-existing
ADs (AD-5, AD-7, AD-8, AD-9, AD-10). The 2026-10-08 adversary round (F1..F5,
archived) was closed; this round finds a new, overlapping class of ownership
holes created by the AD-11..AD-15 refactor — the same failure mode the
refactor was meant to remove.

Method: construct two units one level down, each AD-compliant on a literal
reading, then pair them. Every compatible-but-divergent pair below is a hole.

Grounding note (code is pre-R3): the shipped code already contradicts AD-11 —
no pack declares a `stacks` map (`packs/*.yaml`), the image lookup is
language-keyed (`engine/adapters/__init__.py:131-137`), and renderers / the
verify harness branch on the language string
(`engine/templates/renderer.py:29,676,1219,1227,1268`,
`engine/verify/e2e.py:57-59,334-337`). The ADs under review are aspirational;
the review therefore tests whether the AD text alone forbids divergent
implementations of the refactor.

## The two units

### Unit A — STM32 `make-cmsis` lane (literal AD reading, matches current tree)

- Frame declares `stacks: {c: make-cmsis, cpp: make-cmsis, rust: cargo-cortex}`
  **directly in the shared frame**; the core frame validator checks the map
  shape (`.memlog.md:30`).
- Stack ids are registered by the `stm32*` family; the id→(template, image,
  command) binding is registered with them.
- Image resolution keeps AD-8 verbatim: the **language flag** resolves the
  image via the core-owned lookup (`engine/adapters/__init__.py:128-145`); the
  stack only happens to coincide because language already keys the table.
- `probe:` is the frame's prepared-endpoint shape `{transport, address}`
  (`engine/core/loader.py:21,62`); `proof_rung` is a frame key.
- Verify cells are the **distinct resolved stacks** (deduped per pack).
- `ProofResult` payload: `pieces="name=ok,name=fail"`, `verified="n/m"`,
  `sessions="…"` (`engine/adapters/openocd.py:279-286`).
- Cache key image component = the AD-8 language-keyed image
  (`engine/core/cache.py:15-20`).

### Unit B — ESP32 `idf-cmake` lane (literal AD reading, matches the E1–E4 plan)

- Frame declares `stacks: {c: idf-cmake}` inside a **`build` family block**
  (spine line 186 leaves the location OPEN; AD-13 puts family data in packs).
- The family's stack registry maps `idf-cmake` → template `idf-cmake`, image
  `espressif/idf:v6.1`, command `idf.py build`; the image lookup is keyed **by
  stack** (AD-11 line 108: "the resolved stack — never the language string —
  selects … the toolchain image").
- `probe:` is read as **connection requirements**
  `{vids: [10C4, 1A86], serial_pattern: …}` (AD-9/AD-14); the family registers
  autodetect IDs.
- `proof_for` lives on FlashPort and reports the programming result
  (`Hash of data verified.`); esptool implements FlashPort only, no DebugPort.
- Verify cells are one per **(pack, stack) per language**; IDF evidence is
  size/fit shape `{partitions, app_size, free}`.
- Cache key image component = the stack-resolved image.

Both units claim full AD-1…AD-16 compliance. They do not compose. The E1–E4
slice in `work-split-view.md:31-36` is Unit B; the delivered tree is Unit A.

---

## Findings

Each finding: the AD text, the two compliant units, the divergence, evidence,
and a proposed new/tightened AD.

### H1 — AD-11 vs AD-8: one image lookup, two legal keys — SEVERE

- **AD-8** (spine:90): "The top-level language flag resolves the image via a
  lookup interface owned by `core/`".
- **AD-11** (spine:108): "The resolved stack — never the language string —
  selects the template family, the toolchain image, and the build command."
- **Unit A** calls `image_for(lang)` (code: `main.py:419,472`, `shim.py:289`,
  `e2e.py:332`); **Unit B** calls `image_for(stack)`.
- **Divergence:** AD-8 says language *is* the key; AD-11 says the stack *is*
  the key. Neither amends the other. For `--lang c`, Unit A returns the single
  global `ghcr.io/…/lang-cpp:15.3.rel2` for both `stm32f411re` and `esp32cam`;
  Unit B returns `lang-cpp` for the STM32 stack and `espressif/idf:v6.1` for
  `idf-cmake`. The same invocation therefore builds an IDF app in an arm-gcc
  image (or an STM32 Make tree in an IDF image) — exactly the "impossible
  stack (an IDF build for an STM32 pack)" AD-11's *Prevents* line claims to
  stop — while both units obey every AD literally.
- **Evidence:** `engine/adapters/__init__.py:128-137` (language-keyed TABLE),
  `engine/cli/main.py:419`, `engine/verify/e2e.py:332`; spine:90 vs spine:108.
  `Verify:` construct the call sites and observe one key argument feeds a
  single global table.
- **Proposed (tighten AD-8, cross-ref AD-11):** the image-lookup key is the
  **resolved stack id**, not the language. Re-signature `ImageLookup.image_for`
  to `image_for(stack_id)`; core owns language→stack resolution (frame map +
  family stack registry) and is the *only* producer of a stack id. State that
  AD-8's "language flag" is superseded by AD-11.

### H2 — AD-13: family is not part of the registry key — two families own one block name — SEVERE

- **AD-13** (spine:120): "Family block validators live alongside `packs/`. A
  new brand adds validators + pack sections + adapters and requires **zero
  core diffs**."
- **Code:** `register(block_name, validator, families=…)` writes one global
  `_REGISTRY[block_name]` (`engine/core/registry.py:31-40`); dispatch is
  `validate_block(block_name, payload)` (`registry.py:54-56`) and the loader
  calls `validate_block(name, payload)` with **no family context**
  (`loader.py:70`). `FAMILY_BLOCKS` is written (`registry.py:38-40`) and never
  read for dispatch — write-only metadata.
- **Unit A** (stm32 family) registers `partitions` for external-QSPI memory
  partitions; **Unit B** (esp32 family) registers `partitions` for the IDF
  partition table. Both live in `packs/`, both register by family, both need
  zero core diffs.
- **Divergence:** whichever importer runs last wins globally; a stm32 pack is
  validated against the esp32 schema (or silently passes the wrong validator).
  Family membership is recorded but never consulted, so the two families are
  two owners of one entity (`the partitions block name`) with clashing shapes —
  which is the exact "one family's validators becoming the core by accident"
  AD-13 says it prevents.
- **Evidence:** `engine/core/registry.py:31-56` (flat, name-only key; no-read
  `FAMILY_BLOCKS`), `engine/core/loader.py:65-74`.
  `Verify:` `registry.register("partitions", a, families=("esp32",))` then
  `registry.register("partitions", b, families=("stm32f4",))`; both calls
  succeed and `validate_block("partitions", …)` runs `b`.
- **Proposed (tighten AD-13):** the registry key is **(family, block_name)**;
  `register(family, block_name, validator)`; the loader resolves the pack's
  family (explicit `family:` frame key or pack-id prefix) *before* dispatch and
  passes it to `validate_block`; `FAMILY_BLOCKS` becomes the dispatch index and
  is consulted. Cross-family reuse of a block name requires an explicit alias,
  never a silent overwrite.

### H3 — AD-11: where the `stacks` map lives is deferred, so its shape has two owners — SEVERE

- **AD-11 + Deferred** (spine:108, spine:186): "Where the `stacks` map lives —
  the shared frame vs a `build` family block — **open**; resolve at the R2/R3
  boundary." `.memlog.md:30`: "the frame validates the stacks map shape while
  the owning family registers the stack ids."
- **Unit A** puts `stacks:` in the shared frame (core-validated shape);
  **Unit B** puts it in a `build` family block (family-validated shape).
- **Divergence:** a pack authored for A is read by B as a frame with **no
  `stacks`** (loud error per AD-11) plus an extra block; a pack authored for B
  is read by A as a frame **missing** `stacks`. The map's shape validator
  itself has two owners (core frame vs family block), so the two units that
  wrote packs against different shapes cannot be loaded by each other. Both
  obey AD-11 and AD-13.
- **Evidence:** spine:186 states the question is open; `engine/core/loader.py:21`
  (`FRAME_KEYS` has no `stacks`); no pack declares one (`packs/*.yaml`).
- **Proposed (new AD, or tighten AD-11 + close the Deferred bullet):** the
  `stacks` map lives in the **shared frame** as device truth, core-validated as
  `language → non-empty stack-id string`; the id→(template, image, command)
  registry is family-owned under AD-13. A family `build`/`stacks` block
  re-declaring the map is rejected.

### H4 — AD-11 vs AD-5: who decides the stack — the pack or run config? — MAJOR

- **AD-5** (spine:72): "Language, pack reference, probe backend, and output are
  run config (CLI domain). … Shape is derived from pack data, never a
  parameter."
- **AD-11** (spine:108): "Each pack declares a `stacks` map … A (pack,
  language) pair with no declared stack is a loud error."
- **Unit A** treats the stack as purely pack-derived and rejects any run-config
  stack selector. **Unit B** treats the stack as run config *because* AD-11's
  resolution key includes `language`, which AD-5 assigns to run config — so it
  accepts `--stack idf-cmake` (or a user-config `stacks:` field; AGENTS.md
  "user-supplied configs (one source per invocation)") and builds an IDF tree
  from an STM32 pack.
- **Divergence:** under B, run config selects a stack the pack never declared —
  reintroducing the "impossible stack" AD-11 forbids, with a device-description
  source (the user config) overriding device truth, contrary to AD-5's
  one-source/whole-source rule. Both units quote AD-5 and AD-11 verbatim.
- **Evidence:** AD-5 line 72 vs AD-11 line 108; `main.py:68` already exposes
  `--lang` as run config ("image lookup key").
- **Proposed (tighten AD-11, cross-ref AD-5):** run config SHALL select only a
  **language**; the stack id is chosen **solely** by the pack's frame map. No
  run-config `--stack`, and a user-config `stacks:` field is a hard error
  ("whole-source replacement" only).

### H5 — AD-12: `proof_for` is on FlashPort, but AD-10 rungs 2/3 are DebugPort facts — SEVERE

- **AD-12** (spine:114): "Programming is **FlashPort** (`render_argv`, `flash`,
  `proof_for`, `last_transcript`); sessions are **DebugPort**
  (`debug`/`monitor`)."
- **AD-10** (spine:102): proof "prefers automated probe readback, then LED, then
  manual register inspection … adapters must fill every rung they certify
  comparably."
- **Unit A:** FlashPort's `proof_for` produces the pack's readback rung by
  reading target memory (a JTAG/attach capability, i.e. DebugPort semantics),
  and implements DebugPort. **Unit B:** FlashPort's `proof_for` can only report
  the programming result (`Hash of data verified.`), and it declares DebugPort
  unimplemented (esptool; AD-12 "DebugPort only where the device supports
  attach"); its LED rung is not a `proof_for` output at all.
- **Divergence:** AD-12 binds the *single* `proof_for` to FlashPort, yet AD-10's
  preferred rungs require attach/readback. A FlashPort-only backend cannot
  certify "readback"/"manual register inspection" comparably, and each unit
  picks a different owner for the readback rung. The two ADs are unsatisfiable
  together, and each unit is literally compliant.
- **Evidence:** AD-12 line 114 vs AD-10 line 102; `openocd.py:267-286` fills the
  rung from the flash transcript only.
- **Proposed (tighten AD-12 + AD-10):** split proof by port —
  `FlashPort.program_proof_for` (programming evidence only) and
  `DebugPort.readback_proof_for` (readback/register evidence). The pack's
  `proof_rung` names the *required capability*; `flash` requires the port the
  rung needs and fails loudly (no fabricated proof) when the backend lacks it.

### H6 — AD-12: "device supports attach" has two owners; the fail-fast mechanism is undefined — MAJOR

- **AD-12** (spine:114): "a backend implements DebugPort only where the device
  supports attach. The CLI MUST fail a verb whose port the backend does not
  implement, never fabricate a handle."
- **Unit A:** attach capability is **device truth** in the pack; core gates the
  `debug` verb on it. **Unit B:** capability is a **backend** property; the CLI
  detects it by `isinstance(adapter, DebugPort)` / registry membership.
- **Divergence:** same device, two backends (openocd JTAG vs esptool UART). The
  pack is attach-capable, so Unit A lets `mu debug --probe esptool` proceed to
  a backend with no DebugPort — and the current ABC forces every backend to
  implement `debug` (`engine/adapters/__init__.py:68-70`), so a handle is
  returned (`openocd.py:261-265`, `probe_rs.py:227-231` both "fabricate" a
  deterministic handle by design). Unit B fails the verb. Both obey: AD-12
  names the device ("supports attach") *and* the backend ("implements DebugPort")
  as the decision site.
- **Evidence:** AD-12 line 114; `engine/adapters/__init__.py:56-70` (abstract
  `debug` on the always-implemented `ProbeAdapter`, no `DebugPort` type);
  `openocd.py:261-265`.
- **Proposed (tighten AD-12):** capability is the **conjunction** (pack
  capability ∧ backend port implementation). The pack declares
  `debug:`/attach capability (device truth, AD-2); a distinct `DebugPort` ABC
  is checked with `isinstance`; the base `ProbeAdapter` drops the mandatory
  `debug`, so a handle cannot be fabricated. The verb fails with a typed error
  when either side is absent.

### H7 — AD-14: one artifact path, two "corresponding facts"; the fact→artifact map is unowned — MAJOR

- **AD-14** (spine:126): "A renderer emits a tool artifact only when the model
  carries the corresponding fact (an `openocd` block → `openocd.cfg`; a
  family-declared vendor source → vendor tree)."
- **Unit A:** gates `probe/openocd.cfg` on the `openocd` block and the vendor
  tree on `startup`/`system`; **Unit B:** has no `openocd` block but emits a
  probe config (and IDF files) from its own family facts at the conventional
  probe path.
- **Divergence:** the artifact **path** is not bound to the fact name. The
  current renderer already writes `probe/openocd.cfg` and
  `probe/probe-serial.cfg` unconditionally and `vendor()` unconditionally for
  c/cpp (`engine/templates/renderer.py:1209,1213,1267`). Because AD-14 couples
  a *probe-tool* fact (`openocd` block) to all "corresponding" artifacts, a
  renderer reading "has `openocd` → emit the openocd-family artifacts" emits
  arm CMSIS into an xtensa tree if an ESP32 pack ever carries an `openocd`
  block (spike-007 explicitly parks JTAG but does not forbid the block). Two
  renderers, one path, different facts; both obey "emit only when the fact is
  carried".
- **Evidence:** AD-14 line 126; `renderer.py:1209,1213,1216-1218,1267`;
  `engine/adapters/probe_rs.py` and the E3 plan (`work-split-view.md:35`) show
  the same probe path is reused by a second family.
- **Proposed (tighten AD-14):** artifacts are declared by the **resolved stack
  + family block**; every artifact has exactly one owning `(family, block,
  field)` and a stack-scoped path; a fact→artifact map is registered like block
  validators, and no two facts may target one path. Probe-tool artifacts
  (`openocd.cfg`, `probe-serial.cfg`) are owned by the probe decision;
  toolchain/vendor artifacts are owned by the stack's template family only.

### H8 — AD-14 vs AD-9/frame: the `probe:` block has two shapes and two owners — MAJOR

- **AD-9** (spine:96): packs declare "connection requirements (VID/PID, serial
  pattern, or network)".
- **AD-14** (spine:126): "The pack's `probe:` block is the single source of
  connection requirements; the shim merges them with CLI selectors, and the
  family registers autodetect IDs."
- **Unit A:** `probe:` is the frame's prepared-endpoint shape
  `{transport, address}` (core-validated). **Unit B:** `probe:` is requirements
  `{vids: […], serial_pattern: …}` (family-validated).
- **Divergence:** `probe` is a core frame key (`loader.py:21`) whose validator
  requires `transport` + `address` (`loader.py:62`), so the frame accepts A and
  rejects B, while AD-14/AD-9 describe B. The shim today ignores the pack
  entirely and autodetects from a hardcoded `_PROBE_VIDS = ("0483",)`
  (`engine/cli/shim.py:64`; `.memlog.md:23` "the pack `probe:` block is dead").
  Plus "the shim merges them with CLI selectors" leaves merge semantics
  undefined, and AD-5 forbids field-level merge. Two owners of
  connection-requirement truth, two state-mutation paths (frame-validated
  endpoint vs family-validated requirements merged in the shim).
- **Evidence:** AD-9:96 vs AD-14:126; `loader.py:21,62`; `shim.py:64`;
  `.memlog.md:23`.
- **Proposed (tighten AD-9/AD-14):** `probe:` in the frame is **requirements**
  (core-owned schema: vids/pid_whitelist/serial_pattern/network); the
  *prepared* endpoint remains the core `Endpoint` produced only by the shim;
  the family registers autodetect IDs through the (family, key) registry of H2;
  CLI selectors **replace** (never merge with) pack requirements, per AD-5's
  whole-source rule.

### H9 — AD-15: cell identity and evidence schema are both unowned — MAJOR

- **AD-15** (spine:132): "The verify harness enumerates `(pack, stack)` cells.
  Each stack registers its build plus its size/fit check. Evidence keeps the
  AD-10 SUBSET-comparable keys (`pieces`, `verified`)."
- **Unit A:** cells are the **distinct resolved stacks** (deduped); evidence
  keys are `pieces`/`verified` (literal AD-15) filled from a proof result, plus
  file size. **Unit B:** cells are one per **(pack, stack) per language** (so
  `c` and `cpp` sharing `make-cmsis` yield two identical-stack cells); IDF
  evidence is `{partitions, app_size, free}` and arm evidence is
  `{text,data,bss,flash_used,…}` (`e2e.py:74-88,376-379`) — neither is
  `pieces`/`verified`.
- **Divergence:** AD-11 resolves a stack from `(pack, language)`, but AD-15's
  cell key is `(pack, stack)`, so the two units disagree on the cell count and
  identity (deduped vs per-language). Worse, `pieces`/`verified` are AD-10
  *flash-proof* keys, not build/size evidence, so no build cell can literally
  carry them; each stack invents its own size/fit schema and the cells are not
  comparable — defeating AD-15's "a third build system can register".
- **Evidence:** AD-15:132; `e2e.py:57-59` (cells `(pack, lang)`), `74-88`
  (`ElfInfo`), `365` (evidence header `pack / lang`).
- **Proposed (tighten AD-15):** cell identity is the **resolved stack**
  (deduped per pack); each stack registers a typed evidence adapter with a
  declared key set; build/size keys are separate from AD-10 flash-proof keys
  (do not overload `pieces`/`verified`); the harness compares only within a
  shared key schema, with cross-stack comparison on an explicit common subset
  (pack id, stack id, pass/fail, artifact digest).

### H10 — AD-11 cascades into the AD-7 cache key: two producers of `image_digest` — MAJOR

- **AD-7** (spine:84): caches are "keyed by image digest plus project hash …
  image bump invalidates".
- **Unit A:** derives `image_digest` from the AD-8 language-keyed image
  (before stack resolution). **Unit B:** derives it from the stack-resolved
  image.
- **Divergence:** editing a pack's `stacks` map is a real AD-11 event (language
  unchanged, stack/image changed). Under B the cache invalidates; under A it
  does **not**, so AD-7's "image bump invalidates" is violated in Unit A while
  obeying both ADs. Two writers of one cache key silently diverge.
- **Evidence:** `engine/core/cache.py:15-20`; `main.py:472`, `shim.py:289`
  compute the image from the language before any stack axis exists.
- **Proposed (tighten AD-7/AD-11):** the cache key's image component is the
  **resolved stack's image digest**; core resolves the stack once and is a
  mandatory input to `cache_key`; the language never feeds the cache key.

### H11 — AD-11: the id→(template, image, command) registry has no declared owner — MAJOR

- **AD-11** (spine:108): the resolved stack "selects the template family, the
  toolchain image, and the build command." **AD-13** + `.memlog.md:30`: stack
  ids are registered by family; the frame validates the map shape.
- **Unit A:** registers all three bindings in `core/` (shared vocabulary,
  AD-1) — so a brand needs a core diff, failing AD-1's acceptance test.
  **Unit B:** registers all three in the family (AD-13) — `make-cmsis` is a
  global string any family may redefine.
- **Divergence:** two families registering `make-cmsis` produce two templates/
  images/commands; the H2 collision recurs on stack ids. No AD assigns the
  registry, so both placements are compliant.
- **Evidence:** AD-11:108; `engine/adapters/__init__.py:128-137` (the image
  table is core); `engine/cli/main.py:216-220` (the build command is a language
  branch in the CLI).
- **Proposed (tighten AD-11/AD-13):** stack ids are **(family, stack-id)**
  qualified; the registry mechanism is core, entries are family-owned; within
  one entry the template-family, image, and command bindings each have exactly
  one owner (template+command: the family stack entry; image: the H1 lookup).

### H12 — AD-12/AD-10/AD-15: `ProofResult` payload value-shape is unowned — MAJOR

- **AD-12** (spine:114) puts `proof_for` on FlashPort; **AD-10** (spine:102)
  demands comparable rungs; **AD-15** (spine:132) names only the *keys*
  `pieces`/`verified`. `ProofResult` is an untyped bag of string pairs
  (`engine/core/model.py:152-170`).
- **Unit A:** `pieces="boot=ok,part=ok,app=ok"`, `verified="3/3"`
  (`openocd.py:281-283`). **Unit B:** `pieces="boot,part,app"` (names only),
  `verified="ok"` (boolean), or a stringified `{"passed":3,"total":3}`.
- **Divergence:** both units implement FlashPort, both "keep `pieces`/
  `verified`", both satisfy AD-15's key list — yet a cross-backend verdict diff
  is impossible because the value grammars differ. The conformance test's
  SUBSET rule (`engine/adapters/tests/test_conformance.py:101-127`) is a test
  decision, not an AD, so a new backend is not bound by it.
- **Evidence:** `model.py:152-170` (no schema); `openocd.py:279-286` vs any
  alternative encoding; `test_conformance.py:8-13` (SUBSET decided in a test).
- **Proposed (new AD):** the `ProofResult` payload schema is core-owned and
  versioned: a declared key enum with value grammars — `pieces` is an ordered
  list of `(name, bool)` pairs, `verified` is `(ok:int, total:int)`,
  backend-specific keys are namespaced (`x-<backend>-…`) and excluded from
  comparison. Move the SUBSET rule from the test into the AD.

### H13 — AD-16: "behavior-preserving" is undefined against the AD-8 interface change — MINOR

- **AD-16** (spine:138): the stack axis "SHALL land on the STM32-only tree
  first — behavior-preserving, rendered output unchanged".
- **H1** requires the image-lookup key to change language→stack, which changes
  the `ImageLookup` interface (`engine/adapters/__init__.py:120,139`) and every
  call site (`main.py:419,472`, `shim.py:289`, `e2e.py:332`).
- **Unit A** reads "behavior-preserving" as output-bytes-only and changes the
  key. **Unit B** reads it as interface-preserving and keeps `image_for(lang)`
  while adding a parallel stack lookup. Both obey.
- **Evidence:** AD-16:138; the call sites above.
- **Proposed (tighten AD-16):** define "behavior-preserving" as
  **rendered-output byte-identical, public port signatures change only
  additively**; name R3's expected interface delta explicitly.

---

## Summary

| # | Seam | Tier | Hole | Owner after fix |
| --- | --- | --- | --- | --- |
| H1 | AD-11 ↔ AD-8 | SEVERE | image lookup keyed by language *or* stack | core stack resolution (key = stack id) |
| H2 | AD-13 | SEVERE | family not in registry key; block-name collision | `(family, block_name)` registry |
| H3 | AD-11 | SEVERE | `stacks` map location deferred → two shapes | shared frame (core-validated) |
| H4 | AD-11 ↔ AD-5 | MAJOR | run config can select a stack | pack-only stack selection |
| H5 | AD-12 ↔ AD-10 | SEVERE | `proof_for` on FlashPort vs attach rungs | split proof by port |
| H6 | AD-12 | MAJOR | attach-capability has two owners; fabrication path | pack ∧ backend, hard `isinstance` |
| H7 | AD-14 | MAJOR | one artifact path, many facts | stack+family artifact registry |
| H8 | AD-14 ↔ AD-9 | MAJOR | `probe:` two shapes/two owners; undefined merge | frame requirements + shim endpoint, replace-only |
| H9 | AD-15 | MAJOR | cell identity + evidence schema unowned | stack-keyed typed evidence |
| H10 | AD-11 ↔ AD-7 | MAJOR | two producers of `image_digest` | stack-resolved digest into cache key |
| H11 | AD-11 ↔ AD-13 | MAJOR | id→(template,image,command) registry unowned | (family, stack-id) registry |
| H12 | AD-12/10/15 | MAJOR | `ProofResult` value-shape unowned | core-owned versioned payload schema |
| H13 | AD-16 | MINOR | "behavior-preserving" undefined vs port change | define output + interface rule |

Verdict: **FAIL** — four SEVERE and eight MAJOR compatible-but-divergent pairs.
As in the 2026-10-08 round, all are closeable by tightening the ADs (one owner
+ one schema per entity); none requires a new paradigm. Recommend adding
AD-17..AD-20 (or tightening AD-7/8/9/11/12/13/14/15/16) at the R2/R3 boundary
before the stack axis lands, and closing the Deferred bullet at spine:186.
