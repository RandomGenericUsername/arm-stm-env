# arm-stm-env

Greenfield unified STM32 development environment (C / C++ / Rust). Baseline lessons from `../ArmDevelopmentEnvironment@last-branch` + `../rust-embedded-environment@recover-branch` — no code reuse, requirements-first.

## Core intent (do not lose)

Dual-mode CLI:
1. **Containerized dev env** — `cli create/dev` provisions interactive container env (toolchain + CMSIS/SVD fetcher + build/flash/debug + VSCode).
2. **Host-transparent** — on bare host with zero deps, `cli compile/build/flash` delegates into container (cf. Rust `compile_project.sh --path --arch --output-dir`). Must work on cloned project without host setup.

Selector: `--lang c|cpp|rust --mcu f411re|h755|wl55jc --name <proj>`

## Tooling here

- BMAD-METHOD: `.agents/skills/` (`bmad`, `bmod-method`, `bmod-core-tools`, `bmad-build`). Run `bmad setup` in agent, then `bmad-build`.
- OpenSpec: `openspec/` (spec-driven). Start: `/opsx-propose "your idea"`.
- See `openspec/config.yaml`, `skills-lock.json`.

## Status

Empty scaffold. Next: requirements + 2026 technical background + architecture, then bootstrap.
