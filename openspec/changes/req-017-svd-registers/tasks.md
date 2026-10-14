# Tasks

## 1. Schema + model

- [x] 1.1 `registry.py` `svd` block validator; `model.py` facets/view `svd`; `loader.py` reads it. Verify: `pytest -k registry`.
- [x] 1.2 Packs declare `svd` (F411, H755 CM7/CM4, WL CM4/CM0P). Verify: packs validate.

## 2. Generator

- [x] 2.1 `renderer.py`: `SVD_REPO`/`SVD_SHA`, `fetch_svds` (pinned URL, injectable opener), `svdFile` per core. Verify: `pytest -k vscode`.

## 3. Tests + live

- [x] 3.1 Registry + fetch (pinned URL) + `svdFile` tests. Verify: `pytest -q` (257 passed).
- [x] 3.2 Live: `mu create … stm32f411re --vscode` → `probe/STM32F411.svd` (856 KB) + `svdFile`. Verify: file listing + grep.
- [x] 3.3 `make test` + `openspec validate req-017-svd-registers` green; ticket/INDEX updated.
