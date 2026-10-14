---
id: bug-010
title: "mu build broken: probe auto-detect forwards --device to build"
kind: bug
status: done
lane: direct
severity: S1
links:
  openspec: []
  bmad: []
worktree: .worktrees/bug-010/
branch: ticket/bug-010-build-probe-gate
repro: "mu build --project-dir <project>   # one probe attached"
observed: "mu: error: unrecognized arguments: --device <serial>"
expected: "build runs (no probe involvement)"
---

# mu build broken: probe auto-detect forwards --device to build

## Repro

```sh
mu build --project-dir ~/Desktop/h755-clean   # with a probe attached
```

## Observed

```
mu: error: unrecognized arguments: --device 0023004B3132511438363431
```

`req-020` made `build_container_argv` auto-detect a probe for **every** verb, so
it injected `--device <selector>` into the container's `build` invocation — which
has no `--device` flag. Regression: `mu build` (auto mode) stopped working.

## Expected

`build` runs normally; the probe is irrelevant to it.

## Fix notes

`engine/cli/shim.py` `build_container_argv`: resolve the probe binding only for
verbs that use it (`flash`, `debug`, `dev`); `build` gets no binding, no
`--device`. Regression tests: build argv has no `--device`; flash still
auto-detects. Live: `mu build --project-dir ~/Desktop/h755-clean` → ELF.
