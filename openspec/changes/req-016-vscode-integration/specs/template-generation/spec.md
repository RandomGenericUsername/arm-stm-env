# Spec Delta

## Purpose

`create --vscode` projects a container-ready `.vscode/` from the certified model.

## ADDED Requirements

### Requirement: create generates .vscode/ on request

`mu create --vscode` SHALL render `.vscode/{tasks,launch,settings,extensions}.json`
for C/C++, with a per-core cortex-debug `launch.json` from pack facts and
in-container tool paths. Without `--vscode`, no `.vscode/` SHALL be written.

Evidence: container debug chain proven live 2026-10-14. Verify: `render(device,
"c", tmp, vscode=True)` writes the four files; `launch.json` parses.

#### Scenario: F411RE single core

- **WHEN** `stm32f411re` renders with `--vscode`
- **THEN** `.vscode/launch.json` has one `Debug M4 (OpenOCD)` config with
  `configFiles ["interface/stlink.cfg","board/st_nucleo_f4.cfg"]` and the
  in-container gdb/openocd paths

#### Scenario: H755 dual core

- **WHEN** `stm32h755` renders with `--vscode`
- **THEN** `launch.json` has `Debug M7 (OpenOCD)` and `Debug M4 (OpenOCD)`, each
  pointing at its own ELF

#### Scenario: Default stays bare

- **WHEN** `create` runs without `--vscode`
- **THEN** no `.vscode/` directory is written
