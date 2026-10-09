# Spec Delta

## Purpose

The engine core is the certified-facts foundation: it loads hardware packs, validates them against the frame plus registered family blocks, and hands adapters a model they can render from but never reinterpret.

## ADDED Requirements

### Requirement: Canonical model validates clean packs

The core SHALL load each day-one pack (F411RE, H755, WL55JC shapes) and accept it iff frame + registered family blocks validate; unknown blocks SHALL be rejected naming the block.

Evidence: AD-2/AD-4 (spine). Verify: `python -m pytest engine/core/tests/ -k pack` green on 3 fixture packs + 1 unknown-block rejection.

#### Scenario: Unknown block rejected

- **WHEN** a pack declares a family block with no registered validator
- **THEN** loading fails naming the block, before any adapter sees the model

### Requirement: Adapters receive model, never parse

The certified model SHALL be an immutable structure; adapter-facing access exposes facts only (no pack paths, no raw YAML). Any adapter-side device parsing SHALL fail review.

Evidence: AD-2 rule text. Verify: `rg "yaml\.safe_load|open\(.*\.yml" engine/adapters/ 2>/dev/null` — populated in later stories; core exposes no loader to adapters (import test).

#### Scenario: Certified handoff

- **WHEN** a valid pack loads
- **THEN** the emitted model is frozen (mutation raises) and carries provenance (pack id + version)

### Requirement: Endpoint and proof structs are core vocabulary

Probe endpoints and proof results SHALL be core-owned structs (transport + address; rung + evidence payload). Adapters fill them; stringly-typed endpoints SHALL be rejected at review.

Evidence: adversary F3 fix (spine AD-9/AD-10). Verify: struct definitions exist in `engine/core/` with total coverage over declared rungs.

#### Scenario: Comparable verdicts

- **WHEN** two adapters certify the same rung for one pack
- **THEN** their proof payloads compare field-for-field

### Requirement: Cache keys owned by core

Cache key format (image digest + project hash, bump invalidates) SHALL live in `core/`; adapters request keys, never invent them.

Evidence: adversary F5 fix (AD-7). Verify: key function unit-tested; digest change flips the key.

#### Scenario: Digest bump invalidates

- **WHEN** the image digest changes with the project unchanged
- **THEN** the cache key differs and stale entries are never reused
