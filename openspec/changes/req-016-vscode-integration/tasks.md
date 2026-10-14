# Tasks

## 1. Generator

- [x] 1.1 `engine/templates/renderer.py`: `_vscode_files(device)` (JSON via `json.dumps`) + `render(..., vscode=False)`. Verify: `pytest -k vscode`.
- [x] 1.2 `engine/cli/main.py`: `create --vscode` flag → `render(vscode=…)`. Verify: `mu create --help` shows `--vscode`.

## 2. Tests

- [x] 2.1 F411RE `--vscode` writes the four files; launch parses, config files + paths correct. Verify: `pytest -q`.
- [x] 2.2 H755 per-core launch names; `--vscode` off by default. Verify: `pytest -q` (255 passed).

## 3. Live + close-out

- [x] 3.1 `mu create --mcu-config stm32f411re --lang c --name vs --vscode` → four files, launch matches the hand-verified config. Verify: file listing + cat.
- [x] 3.2 `make test` + `openspec validate req-016-vscode-integration` green; ticket/INDEX updated.
