# Proposal

## Why

The generated `.vscode/launch.json` (req-016) has no `svdFile`, so Cortex-Debug
shows no **Peripheral Registers** view — you can't see/edit registers. The
sibling repos shipped this (`"svdFile": "STM32H755_CM4.svd"` +
`download_svd_files.sh`), and it's the most-used debug feature.

## What Changes

- New optional pack block **`svd`** = core -> SVD source path (e.g.
  `M4: stm32f4/STM32F411.svd`).
- `create --vscode` fetches the pack's SVDs from a **commit-pinned** source into
  `probe/` and adds `svdFile` to each core's launch config.
- Packs: `stm32f411re` (STM32F411), `stm32h755` (CM7 + CM4), `stm32wl55jc`
  (CM4 + CM0P).

## Capabilities

### Modified Capabilities

- `pack-schema`: optional `svd` block (per-core SVD path).
- `template-generation`: fetch pinned SVDs; `svdFile` per core in `launch.json`.

## Impact

- Code: `engine/core/{registry,model,loader}.py`,
  `engine/templates/renderer.py`, packs, tests.
- **Out of scope:** offline/vendored SVD copies (fetch needs network, like CMSIS
  vendoring), non-ST families, SVD for Rust.

Evidence: sibling prior art
`ArmDevelopmentEnvironment@main:setup/create_project/download_svd_files.sh`;
ST's own svd zips are unreachable (`HTTP 000`) so a pinned GitHub mirror is used.
