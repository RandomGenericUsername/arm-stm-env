# Tasks

## 1. Vendoring helper

- [x] 1.1 `engine/templates/vendoring.py` (pin table, submodule add + detached checkout, loud errors). Verify: `pytest -k vendor` green incl. offline simulation (unreachable remote → non-zero naming it).
- [x] 1.2 Wire into `render()` end (C/C++ langs only; Rust needs no vendor tree). Verify: render tests still green.

## 2. Live proof

- [x] 2.1 Fresh render in /tmp git repo → submodule init → stub-free container build green. Verify: ELF produced with no stubs injected.
- [x] 2.2 `openspec validate` green + ticket update. Verify: exits 0; boxes checkable.
