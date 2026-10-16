# Adversary Review — architecture-universal-mcu-env

Verdict: FAIL (holes exploitable while obeying every AD to the letter)

## Method

Constructed two units one level down, each AD-compliant on a literal reading,
then paired them. Every compatible-but-divergent pair below is a hole.

## Unit A — STM32/OpenOCD lane (AD-compliant reading)

- Core owns `core/model.py` vocabulary; pack loader in `core/` validates shared
  frame, then calls `packs/stm32/validate.py` (treated as "owning family"
  code inside `packs/`) for family blocks.
- Toolchain image map lives in `core/images.py`: `{cpp: <image>, rust: <image>}`
  as shared vocabulary.
- Shim hands endpoint as POSIX path string (e.g. `/dev/ttyACM0`).
  OpenOCD probe adapter renders `openocd -f interface/stlink …` from certified model.
- Proof result = `{rung, readback_sha256}`; pack declares `proof_rung: readback`.
- Cache volume key = `cache-<toolchain>-<image-tag>`; user overlay replaces
  whole pack source per "provenance: pack wins unless user file replaces the source".

## Unit B — ESP32/esptool lane (AD-compliant reading)

- Core owns vocabulary; pack loader in `core/` validates shared frame, then
  delegates family-block validation to the esptool *adapter*
  (`adapters/probe/esptool/validate.py`) as the "owning family".
- Image map lives in `adapters/toolchain/registry.py` as "per-family build defs";
  language flag looks it up there.
- Shim hands endpoint as struct `{transport: usb|net, pattern, host, port}`.
  esptool adapter renders `esptool --port <endpoint.pattern> …` from certified model.
- Proof result = `{rung, log_snippet}`; pack declares `proof: {ritual: readback}`.
  LED/manual fallback accepted per ladder without readback bytes.
- Cache volume key = `cache-<language>-<project-hash>`; user file merges
  selected fields over pack truth.

Both units claim full AD-1…AD-10 compliance. They do not compose.

## Findings (each: AD citation + exact rule text + divergence)

### F1 — Family-block validator owner undefined (AD-2 vs AD-4) — SEVERE

- AD-2 rule: "The core validates one canonical device model at pack load.
  Adapters receive the certified model and own only tool rendering from it;
  no adapter parses, guesses, or re-derives device semantics."
- AD-4 rule: "Family-specific needs (fuses, partitions, image lists) live in
  typed blocks each validated by its owning family; unknown blocks are rejected."
- Hole: "owning family" is not bound to `core/` vs `packs/` vs `adapters/`.
  Unit A validates family blocks in `packs/` before certification (adapter never
  parses). Unit B validates them inside the probe adapter after certification
  (adapter parses its own block, calls it rendering). Both quote AD-2+AD-4
  verbatim. Result: two owners of one entity (certified model), conflicting
  state-mutation paths (validate-then-certify vs certify-then-adapter-validates),
  and no shared registry of block names — Unit A rejects `esp_partitions` as
  unknown while Unit B accepts it; Unit B rejects `stm32_option_bytes` while
  Unit A accepts it.

### F2 — Image registry map has two legal owners (AD-1 vs AD-8) — SEVERE

- AD-1 rule: "Only `core/` may define shared vocabulary. … core diffs are
  forbidden for brand additions."
- AD-8 rule: "One OCI image per toolchain family (`cpp`, `rust`, later
  `avr`/`esp`). The top-level language flag resolves the image via a registry map."
- Structural seed: "`adapters/toolchain/` # image registry map + per-family build defs".
- Hole: AD-8 names a "registry map" but never assigns it; AD-1 says shared
  vocabulary lives in `core/`, seed puts the map in `adapters/toolchain/`.
  Unit A puts the map in `core/` (shared vocab, needs core diff per brand —
  violates AD-1's "no core diffs" spirit while obeying its letter). Unit B puts
  it in `adapters/toolchain/` (brand addition without core diff, but shared
  lookup now lives outside `core/`). Clashing shared-data shapes follow:
  `core/images.py: {cpp: image}` vs `adapters/toolchain/registry.py:
  {language, version, project-languages[]}` — multi-language resolution
  (explicitly Deferred: "Image registry choice and multi-language project
  image resolution") has no arbiter, so one lane pulls `cpp:<ver>` and the
  other pulls `esp:<ver>` for the same `--language cpp` flag shape.

### F3 — Probe endpoint shape unconstrained; two adapters read one proof differently (AD-9 + AD-10 + AD-6) — SEVERE

- AD-9 rule: "Packs declare connection requirements (VID/PID, serial pattern,
  or network). The shim maps them per OS and hands core/adapters a prepared endpoint."
- AD-10 rule: "Run proof prefers automated probe readback, then LED, then manual
  register inspection as accepted fallback. Each pack declares its rung."
- AD-6 rule: "The adapter interface carries multi-piece results and proof back."
- Hole: neither the endpoint type nor the proof-result schema is fixed as shared
  vocabulary. Unit A endpoint = path string; Unit B endpoint = struct — both
  satisfy "prepared endpoint". Unit A proof = `{rung, readback_sha256}`;
  Unit B proof = `{rung, log_snippet}` with manual inspection as fallback —
  both satisfy "declares its rung" + "carries proof back". Nothing stops the
  OpenOCD adapter certifying rung-1 (hash) and the esptool adapter certifying
  rung-1 (log line) for the same pack, with the core unable to compare them.
  "Errors carry verb + adapter + proof-attempt" (conventions table) without a
  typed proof-attempt enum makes cross-adapter verdicts incomparable.

### F4 — User-overlay merge point contradicts "never merge" (AD-5 vs CAP-4 map) — MAJOR

- AD-5 rule: "Language, pack reference, probe backend, and output are run config
  (CLI domain). Exactly one device-description source per invocation:
  `--mcu-config` XOR individual flags. Shape is derived from pack data,
  never a parameter."
- Conventions: "provenance: pack wins unless user file replaces the source".
- Map: "CAP-4 user-config | `core` validation + packs | AD-4, AD-5".
- Hole: AD-5 forbids merging and mandates XOR sourcing, but CAP-4 requires a
  user-config overlay (memory/linker/SVD/probe per repo contract) and the map
  places it in `core` validation + packs. Unit A reads "replaces the source" as
  whole-file replacement (no merge, XOR-clean). Unit B reads it as field-level
  overlay (merge user fields over pack truth, still "one source" after merge).
  Both obey the letter. Who validates the merged shape — core re-validation
  (AD-2) or family owner (AD-4)? — is unanswered, so the same `--mcu-config`
  either fails validation (A) or flashes with silently overridden memory
  origins (B): conflicting state-mutation paths to the device.

### F5 — Cache-identity and "nothing of value in container" leave cross-lane drift (AD-7) — MAJOR

- AD-7 rule: "Every verb including `dev` is one stateless container exec;
  images carry full toolchains; caches persist in named volumes; the project
  bind-mounts. Nothing of value lives only in a container."
- Hole: volume naming, keying, and invalidation owner are unspecified. Unit A keys
  by image tag, Unit B by language+project hash — both are "named volumes" with
  "stateless exec". A `dev` shell that installs a dep (CAP-6 spike-pending)
  persists it in one lane's cache and is invisible/stale in the other, while
  both claim "nothing of value lives only in a container". No AD assigns cache
  ownership (core? toolchain adapter? shim?), so two toolchain adapters share
  no invalidation protocol and diverge silently.

## What would close the holes (for the judge, not a second proposal)

- Bind each AD gap to exactly one owner + one schema: family-block registry
  (names, schemas, validator location) in `core/`; endpoint struct + proof-result
  struct as `core/` vocabulary with adapter renderers total over it; image-map
  owner (either `core/` with a brand-registration port, or adapter with a
  core-owned lookup interface — pick one); user-overlay merge semantics +
  re-validation order; cache key/owner/invalidation rule.
- Until then the spine permits at least five compatible-but-divergent pairs;
  downstream specs built on either unit will be mutually unimplementable.
