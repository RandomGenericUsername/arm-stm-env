# Tasks

## 1. Streaming runners

- [x] 1.1 Extend both `subprocess_runner`s (`stream`, `log_path`; plain path byte-identical). Verify: unit tests with real `python -c` tool.
- [x] 1.2 Adapter constructor kwargs + fakes-safe dispatch. Verify: conformance suite green.

## 2. CLI wiring

- [x] 2.1 `--verbose` flag + per-run log path + always-stream construction. Verify: main tests (log dir created, kwargs plumbed).
- [x] 2.2 Full suite green + gate scan clean. Verify: 228 passed, no forbidden literals in `cli/`.
