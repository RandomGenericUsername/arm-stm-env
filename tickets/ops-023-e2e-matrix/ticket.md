---
id: ops-023
title: "Record the full e2e matrix (10 cells, both families)"
kind: ops-task
status: done
size: XS
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/ops-023/
branch: ticket/ops-023-e2e-matrix
---

# Record the full e2e matrix (10 cells, both families)

## Work

`docs/e2e-evidence.md` still recorded the pre-ESP32 9-cell matrix. Re-run the harness over every
declared cell and record the result, so the repo's evidence artifact matches the shipped matrix.

## Done-when

`docs/e2e-evidence.md` shows 10/10 green, including the ESP32 cell, and `make test` is green.

## Evidence

2026-10-16:

```
uv run python -m engine.verify.e2e --workdir /tmp/opencode/e2e-all \
  --evidence /tmp/opencode/e2e-all.md --keep
```

```
[PASS] stm32f411re/c   [PASS] stm32f411re/cpp   [PASS] stm32f411re/rust
[PASS] stm32h755/c     [PASS] stm32h755/cpp     [PASS] stm32h755/rust
[PASS] stm32wl55jc/c   [PASS] stm32wl55jc/cpp   [PASS] stm32wl55jc/rust
[PASS] esp32cam/c
10/10 green
```

Every cell compiled in its **stack's** pinned image (`make-cmsis` → `lang-cpp`, `cargo-cortex` →
`lang-rust`, `idf-cmake` → `espressif/idf:v6.1`); the dual-core STM32 packs produced both cores'
ELFs and the ESP32 cell produced its triple. `docs/e2e-evidence.md` is the recorded output.

`make test` → 345 passed.