# Tasks

## 1. Scaffold + model

- [x] 1.1 Scaffold `engine/` package (`pyproject.toml`, uv-managed, `engine/core/` layout) with `uv sync --locked` green. Verify: `uv sync --frozen` succeeds from clean checkout; `python -c "import engine.core"` works.
- [x] 1.2 Implement frozen dataclass model (device, cores, memory regions, probe ref, proof rung, provenance) + endpoint/proof structs. Verify: `python -m pytest engine/core/tests/test_model.py` — construction, frozen-mutation raises, struct coverage.

## 2. Loading + validation

- [x] 2.1 Loader + frame validator + family-block registry (unknown block = hard error naming block). Verify: `pytest -k registry` — register/lookup/reject paths.
- [x] 2.2 Author 3 STM32 fixtures from spike-001-corrected values + 1 negative fixture (unknown block). Verify: `pytest -k pack` — 3 accept, 1 rejects naming the block.
- [x] 2.3 Cache-key function (image digest + project hash, bump flips) + adapter-facing reader views (no loader exposure; import test). Verify: `pytest -k cache` and `pytest -k boundary`.

## 3. Integration checks

- [x] 3.1 Full `pytest` green + lockfile committed. Verify: `python -m pytest engine/core/tests/` exit 0; `uv.lock` present.
- [x] 3.2 Update req-003 ticket (acceptance evidence, status) + link change. Verify: ticket acceptance boxes checkable against test output.
