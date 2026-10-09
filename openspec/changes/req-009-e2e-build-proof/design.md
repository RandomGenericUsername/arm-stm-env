# Design

## Context

See proposal.md. AD-7 (stateless exec), AD-8 (images), AD-10 (proof ladder — build proof is rung-0 evidence). Images exist with recorded digests; `make smoke` proves toolchains run.

## Goals / Non-Goals

**Goals:** harness + 9/9 green + evidence log.

**Non-Goals:** flashing, hardware, warnings policy change.

## Decisions

- **Harness as Python module** (`engine/verify/e2e.py`) driving `docker run` per cell (stateless, AD-7): render to tmp → mount → build → collect ELF/size/log. Same mechanic as future CI.
- **C/C++**: `make` in image, then `arm-none-eabi-size` parsed against pack map loaded via loader (single source of truth, no duplicated numbers).
- **Rust**: `cargo build --target <triple>` in image; `memory.x` byte-compared against pack origins/lengths.
- **Evidence log**: per-cell markdown (`docs/e2e-evidence.md` generated, git-tracked) with commands, exits, sizes, warnings.

## Risks / Trade-offs

- [Risk] Render bugs surface (templates never compiled) → Mitigation: expected; fixed in-branch as req-008 fixes, evidence preserved.
- [Risk] Docker slowness (amd64 emulation on ARM64 host) → Mitigation: sequential cells with per-cell timeouts; total budget documented.

## Verification plan

- Harness exit 0; evidence log complete; `openspec validate` green.

## Open Questions

None.
