# Proposal

## Why

Verbs are the user's hands on the engine: `create/dev/build/flash/debug` orchestrate pack → model → adapter with zero hardware knowledge in commands (AD-6). Without them, the certified model has no invocation path — this is the story that makes the product operable.

Evidence: work-split view story 3; spec CAP-1..5 all assume invocation. Verify: `rg "Thin CLI verbs" _bmad-output/initiative-universal-mcu-env/architecture-universal-mcu-env/work-split-view.md`.

## What Changes

- `engine/cli/` with thin verbs: `create` (pack ref + name → project tree skeleton), `dev` (stateless container exec, interactive shell), `build`/`flash` (transparent: host shim → container exec, probe adapter, proof verdict), `debug` (adapter debug session attach).
- Host shim: `stm` entry point (Python console script via pyproject) resolving language → image, mounting project + probe endpoint, exec'ing the verb in-container; identical behavior inside/outside (same image, AD-8).
- Per-OS probe mapping in shim (AD-9): Linux `--device`, macOS documented limits.
- No adapters, no images, no templates in this change — verbs against stubbed adapter ports + model fixtures.

## Capabilities

### New Capabilities

- `cli-verbs`: thin orchestration verbs + host shim + per-OS probe mapping.

### Modified Capabilities

(none)

## Impact

- New code: `engine/cli/`, `stm` console script, shim logic. Tested with stub adapters + req-003/004 fixtures.
- Out of scope: real adapters (req-006), image builds (req-007), project template contents (shape only here).
