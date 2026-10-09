# Tasks

## 1. Harness

- [x] 1.1 `engine/verify/e2e.py` (render 9 cells → docker build/check per cell → collect ELF/size/warnings → evidence log to `docs/e2e-evidence.md`). Verify: harness runs end to end.
- [x] 1.2 Size/map assertions (C size vs pack map via loader; Rust memory.x byte-compare). Verify: assertions fire on fixture overflow (negative test).

## 2. Green run + fixes

- [x] 2.1 First full run; fix render bugs in-branch as req-008 fixes (evidence preserved). Verify: 9/9 green.
- [x] 2.2 Warnings recorded per cell; policy stays warn-only. Verify: log has warnings sections.

## 3. Integration checks

- [x] 3.1 `openspec validate` green + ticket update + link change. Verify: exits 0; boxes checkable.
