# Design

## Context

See proposal.md. AD-2 (render from model only), AD-4 (pack shapes), spike-002 (vendoring) + spike-004 (config flow). Sibling generators are evidence for shapes/file lists, never sources.

## Goals / Non-Goals

**Goals:** renderer + per-language templates + structural harness, 9 cells green.

**Non-Goals:** compiling output (next story), IDE files, other vendors.

## Decisions

- **`string.Template` (stdlib)** for substitution — templates stay dependency-free and placeholder leaks are greppable (`$`-syntax). Over Jinja2: no new dep for substitution-only needs; revisit if logic (loops/conditionals beyond dual-core) proves necessary.
- **One template set per language** (`templates/c/`, `templates/rust/`; cpp shares c with `-x c++`/flag delta), data-driven per pack. Dual-core handled by core-list iteration in the renderer, not template forks.
- **Sibling file lists as checklists**, content authored fresh: required outputs mirror what the siblings proved necessary (linker, startup refs, CMSIS wiring, Cargo/memory.x/build.rs, openocd.cfg from corrected values) without copying.
- **`config/` generation**: pack defaults copied in + `OVERRIDES.md` documenting project-wins order and `-I`/`-D` wiring for the build story.

## Risks / Trade-offs

- [Risk] `string.Template` too weak for dual-core variance → Mitigation: renderer pre-computes per-core contexts; revisit trigger is a second conditional need.
- [Risk] Authored-from-scratch output misses a file the toolchain needs → Mitigation: file-list checklist derived from both siblings' outputs; compile story will catch the rest.

## Verification plan

- Render-all-cells harness green (9 cells: files + placeholders + memory/pin greps).
- `openspec validate req-008-template-generation` green.

## Open Questions

None.
