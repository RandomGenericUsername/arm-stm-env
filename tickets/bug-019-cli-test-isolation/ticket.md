---
id: bug-019
title: "CLI tests depend on the host USB bus (fail when more than one probe is attached)"
kind: bug
status: done
lane: direct
severity: S3
links:
  openspec: []
  bmad: []
worktree: .worktrees/bug-019/
branch: ticket/bug-019-cli-test-isolation
repro: "attach two probes, then run make test"
observed: "6 failures: mu: error: 2 probes attached (…) in test_shim_lookup + test_verbs"
expected: "make test is green regardless of how many probes are attached"
---

# CLI tests depend on the host USB bus

## Root cause

`mu flash`/`debug`/`dev` auto-detect a probe from `/sys/bus/usb/devices`. The
CLI tests call `main([...])` with no selector, so on a dev machine with two
boards attached the resolution is ambiguous (`mu: error: 2 probes attached …`)
and those tests fail for reasons unrelated to the code under test.

## Fix

`engine/cli/tests/conftest.py`: an autouse fixture points
`engine.cli.shim._SYSFS_USB` at a synthetic single-probe sysfs. Tests that
exercise resolution directly pass their own `sysfs_root` (or monkeypatch
`_SYSFS_USB`), which overrides it.

## Evidence

- before: 6 failed (`test_shim_lookup`, `test_verbs[dev|flash|debug]`,
  `test_verbs_flash_files_forwarded_into_container`,
  `test_verbs_verbose_forwarded_into_container`) with two probes attached.
- after: `uv run pytest engine -q` → **264 passed** with the same two probes
  attached.

## Verify

```sh
make test
```
