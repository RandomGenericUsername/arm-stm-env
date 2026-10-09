# Proposal

## Why

Rendered-but-never-compiled projects are the biggest unverified claim left: 153 unit tests prove structure, zero prove a toolchain accepts the output. Compiling all 9 cells in the pinned images retires that risk without hardware.

Evidence: req-008 renders trees; req-007 images run toolchains (smoke-proven). Verify: `make smoke` green on main.

## What Changes

- `engine/verify/` e2e harness: render all 9 cells to scratch → compile C/C++ via Make in `lang-cpp` image → `cargo build` Rust in `lang-rust` image → assert ELF + size-fits-map + memory.x consistency → per-cell evidence log.
- Warnings recorded per cell; warn-only policy initially (fail-on-warning is a later decision with baseline data).
- No template changes expected; any render bug found becomes a req-008 fix in the same branch.

## Capabilities

### New Capabilities

- `e2e-build-proof`: in-image compilation proof for all cells + evidence log.

### Modified Capabilities

(none)

## Impact

- New: `engine/verify/` harness + docs. Needs Docker (present here); CI-deferred otherwise.
- Out of scope: flashing, hardware, warnings-as-errors.
