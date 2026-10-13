# Design

## Context

See proposal.md. Spike-002 vendoring pick; sibling fetch evidence (svn CMSIS + curl cmsis_device_* per project — replaced, not copied). `git` required on host (already is: engine runs from a checkout).

## Goals / Non-Goals

**Goals:** submodule init in `create`, pins recorded, loud failures.

**Non-Goals:** offline cache, updates, other vendors.

## Decisions

- **Upstream pins (verified 2026-10-13):** `ARM-software/CMSIS_5` tag `5.9.0`; `cmsis_device_f4` `v2.6.9`; `cmsis_device_h7` `v1.9.0`; `cmsis_device_wl` `v1.4.0`. Verified: ls-remote heads/tags resolve; HTTP 200 on `CMSIS/Core/Include/core_cm4.h`, `f4/Include/stm32f411xe.h`, `f4/.../startup_stm32f411xe.s`, `h7/.../startup_stm32h755xx.s`, `wl/.../startup_stm32wl55xx_cm4.s`.
- **Mechanism:** `git submodule add -b <tag>? ` — no: tags, so `git submodule add <url> <path>` then `git -C <path> checkout <tag>` (submodule add records branch tracking by default; explicit checkout pins detached SHA; `.gitmodules` + gitlink recorded). Helper in `engine/templates/vendoring.py`, invoked at end of `render()`.
- **Non-git out-dirs:** if `out` isn't in a repo, `git submodule add` fails — surface its stderr + hint (`git init` first or pass `--no-vendor`? no new flags in V1: error names the fix).
- **No template changes:** referenced paths already match verified layouts.

## Risks / Trade-offs

- [Risk] Upstream moves paths post-pin → Mitigation: tags are immutable; breakage surfaces as loud create error naming the path.
- [Risk] Network at create → Mitigation: spec-mandated clear error; offline cache deferred with reason recorded.

## Verification plan

- Unit: pins recorded in `.gitmodules`; missing-path and offline simulations fail loud.
- Live: fresh render in /tmp git repo → submodules init → stub-free container build green.

## Open Questions

None.
