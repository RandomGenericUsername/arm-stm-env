---
id: bug-007
title: "--verbose ignored in auto mode (no log file)"
kind: bug
status: done
lane: direct
severity: S2
links:
  openspec: []
  bmad: []
worktree: .worktrees/bug-007/
branch: ticket/bug-007-verbose-forward
repro: "mu flash --mcu-config stm32h411re --project-dir <proj> --vid 0483 --pid 3752 --files build/M4/x.elf --verbose"
observed: "no <proj>/.mu/logs/ file; container argv lacks --verbose (extra carried only --files)"
expected: "flash streams AND writes <proj>/.mu/logs/flash-<ts>.log"
---

# --verbose ignored in auto mode (no log file)

## Repro

```sh
mu flash --mcu-config stm32f411re --project-dir <proj> --vid 0483 --pid 3752 \
  --files build/M4/stm32f411re-M4.elf --verbose
```

## Observed

Streamed output appears, but **no `<proj>/.mu/logs/` file** is written — the
`auto` path built the container argv with only `--files`, so the in-container
run never saw `--verbose`.

## Expected

`--verbose` forwards into the container; the in-container adapter tees the tool
log to `<proj>/.mu/logs/flash-<timestamp>.log`.

## Fix notes

`engine/cli/main.py` `_run_verb`: append `--verbose` to the container `extra`
for `flash`/`debug` when the flag is set. Live 2026-10-14: flash `--verbose` →
`.mu/logs/flash-20261014-182730.log` written. Regression:
`test_verbs_verbose_forwarded_into_container`.
