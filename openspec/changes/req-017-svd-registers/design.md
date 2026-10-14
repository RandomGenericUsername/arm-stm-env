# Design

## Context

See proposal.md. req-016 left `svdFile` out because sourcing was open. ST's
`st.com/resource/en/svd/*.zip` returns **HTTP 000** (unreachable, confirmed
2026-10-14), so a mirror is required.

## Goals / Non-Goals

**Goals:** the Cortex-Debug register view works for the three shipped MCUs.

**Non-Goals:** offline SVD vendoring, SVD for Rust, non-ST SVDs.

## Decisions

- **D1 — Source: `modm-io/cmsis-svd-stm32`.** All three parts present, unzipped,
  **Apache-2.0**, GitHub-hosted (reachable). Contains `stm32f4/STM32F411.svd`,
  `stm32h7/STM32H755_CM{7,4}.svd`, `stm32wl/STM32WL5x_CM{4,0P}.svd`.
  `cmsis-svd/cmsis-svd-data` lacks WL55.
- **D2 — Commit-pinned fetch.** `SVD_SHA = e79021a…`; each file is fetched from
  `raw.githubusercontent.com/modm-io/cmsis-svd-stm32/<SHA>/<path>` at
  `create --vscode`. Reproducible (pinned), and consistent with the CMSIS
  submodule model (network at create). Offline create with `--vscode` fails loud
  (`VendorError`).
- **D3 — Local layout `probe/<name>.svd`.** SVD is probe/debug config, grouped
  with `probe/openocd.cfg`. `svdFile = ${workspaceFolder}/probe/<name>.svd`.
- **D4 — Per-core.** Each core's launch config gets its own SVD (H755 CM7/CM4,
  WL CM4/CM0P), so the register view matches the core being debugged.

## Risks / Trade-offs

- [Risk] `raw.githubusercontent.com` blocked → Mitigation: loud error naming the
  URL; offline-vendoring is a recorded follow-up.
- [Risk] SVD mirror drifts → Mitigation: commit-pinned SHA.

## Verification plan

- Unit: registry validates the `svd` block; `render(..., vscode=True)` puts
  `svdFile` in launch; `fetch_svds` builds the pinned URL and writes bytes
  (fake opener).
- Live: `mu create … stm32f411re --vscode` → `probe/STM32F411.svd` (856 KB,
  valid XML, Apache-2.0) + `svdFile` in launch.
- `make test` green; `openspec validate req-017-svd-registers` green.

## Open Questions

- Vendor SVDs into the repo for offline create? (sizes: F411 ~0.9 MB, H755 2×4 MB,
  WL ~1–2 MB).
