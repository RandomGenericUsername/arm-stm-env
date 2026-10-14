# Design

## Context

See proposal.md. `mu` already resolves OpenOCD config files and per-core ELF
paths (req-012/ops-015), and the container carries OpenOCD + GDB (verified
2026-10-14). The `.vscode/` files are pure projections of those facts.

## Goals / Non-Goals

**Goals:** a generated `.vscode/` that makes F5 debug work in the attached
container, per core, from pack facts.

**Non-Goals:** Rust configs, SVD/registers, devcontainer lifecycle, SWO/ITM,
dual-core single-session target switching.

## Decisions

- **D1 — JSON built in Python, not `string.Template`.** `.vscode/*.json` is
  generated with `json.dumps` (`_vscode_files`), so it can never emit invalid
  JSON. Rationale: the sibling hand-embedded JSON in shell heredocs; we render
  from the model instead.
- **D2 — In-container tool paths.** `gdbPath=/opt/arm-gnu-toolchain/bin/arm-none-eabi-gdb`,
  `openocdPath=/usr/local/bin/openocd` (verified in the lang-cpp image). Valid
  because the window is attached to the `mu dev` container. This is the key
  divergence from the sibling, which hardcodes host paths.
- **D3 — tasks call `make`, not `mu`.** Inside the dev container the toolchain is
  local, so the generated Makefile's `build`/`clean`/`flash` targets are the
  direct path (matches the sibling). `mu` (docker) is for the host, not here.
- **D4 — launch per core.** One cortex-debug config per `device.cores`, each with
  `build/<core>/<device>-<core>.elf` and the pack's `config_files()`
  (`interface/…` + `board/…|target/…`). Per-core matches the sibling's intent but
  uses the correct config files (the sibling shipped `stm32f4x.cfg` on an H755 —
  bug we must not copy).
- **D5 — extensions via recommendations.** `.vscode/extensions.json`
  `recommendations` → VS Code's one-click "Install recommended extensions".
  Rationale: attach-to-running-container has no zero-click channel (that needs a
  `devcontainer.json`); recommendations is the honest mechanism. Flagged as an
  open question.

## Risks / Trade-offs

- [Risk] attach flow means `extensions.json` prompts (one click), not silent →
  Mitigation: acceptable; documented. `devcontainer.json` is a future option.
- [Risk] container holds a stale USB node after replug → Mitigation: out of
  scope; `mu dev` probe flags (gap found during validation) is a prerequisite
  follow-up.
- [Risk] dual-core debug needs target selection → Mitigation: per-core ELF today;
  target-select refinement is a follow-up.

## Verification plan

- Unit: `render(..., vscode=True)` writes the four files; `launch.json` parses,
  per-core names/executables, pack config files; `--vscode` off by default.
- Live: `mu create --mcu-config stm32f411re --lang c --name vs --vscode` → files
  present, `launch.json` matches the hand-verified config.
- `make test` green; `openspec validate req-016-vscode-integration` green.

## Open Questions

- Zero-click extension install via a generated `devcontainer.json`?
- Vendored SVD sourcing (st.com unreachable historically) — pin per MCU.
- `mu dev` probe flags (needed for the USB node to reach the dev container).
