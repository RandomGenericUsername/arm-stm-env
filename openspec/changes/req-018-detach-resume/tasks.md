# Tasks

## 1. Generator

- [x] 1.1 `renderer.py`: `_RESUME_ON_DETACH` cfg written by `render(vscode=True)`; added to launch `configFiles`. Verify: `pytest -k vscode`.

## 2. Live + close-out

- [x] 2.1 Live: `curstate` = `running` after detach with the cfg; `halted` without. Verify: probe command output.
- [x] 2.2 `make test` + `openspec validate req-018-detach-resume` green; ticket/INDEX updated.
