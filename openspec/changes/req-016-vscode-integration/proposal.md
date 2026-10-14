# Proposal

## Why

`mu` projects have no editor integration: after `mu create` you get a bare tree
with no tasks, no debug launch, and no extension hints — you hand-write
`.vscode/` yourself (as done 2026-10-14 for the F411RE blink). The sibling
`ArmDevelopmentEnvironment` proves the value (generated tasks/launch/settings +
per-core SVD), and `mu` already has the facts to generate it: the pack's OpenOCD
interface/target and per-core ELFs.

The target flow: `mu create --vscode` → `mu dev` (container) → VS Code **attaches
to the running container** → F5 debugs. Everything (OpenOCD, GDB) runs in the
container; no host toolchain.

## What Changes

- `mu create --vscode` also renders `.vscode/{tasks,launch,settings,extensions}.json`.
- **tasks**: Build/Clean/Flash calling `make` (the in-container toolchain is
  present) with a gcc problemMatcher; per-core flash tasks.
- **launch**: one cortex-debug config **per core** (`Debug <core> (OpenOCD)`),
  each with that core's ELF, the pack's resolved OpenOCD config files, and the
  **in-container** `openocdPath`/`gdbPath`.
- **settings**: pins `cortex-debug.gdbPath`/`openocdPath` to the in-container tools.
- **extensions**: recommends `marus25.cortex-debug` (+ cpptools) so VS Code offers
  one-click install (the recommendations mechanism).

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `template-generation`: generated `.vscode/` behind `--vscode` (C/C++).
- `cli-verbs`: `create` gains `--vscode`.

## Impact

- Code: `engine/templates/renderer.py` (`_vscode_files`), `engine/cli/main.py`
  (`--vscode`), tests.
- **Out of scope (first slice):** Rust `.vscode/`, vendored SVD files
  (`svdFile`), `devcontainer.json`, SWO/ITM, and dual-core target *selection*
  inside one launch config.

Evidence: sibling configs
(`ArmDevelopmentEnvironment@main:setup/create_project/dual/.vscode/*`), container
debug chain proven live 2026-10-14 (in-container gdb → openocd → target).
