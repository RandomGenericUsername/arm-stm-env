---
id: bug-003
title: "OpenOCD adapter renders unprefixed config paths (Can't find stlink.cfg)"
kind: bug
status: in-progress
lane: direct
severity: S1
links:
  openspec:
    - openspec/changes/req-012-openocd-probe-wiring
  bmad: []
worktree: .worktrees/req-012/
branch: ticket/req-012-openocd-probe-wiring
repro: "docker run --rm ghcr.io/arm-stm-env/lang-cpp:15.3.rel2 openocd -f stlink.cfg -c exit"
observed: "embedded:startup.tcl:28: Error: Can't find stlink.cfg"
expected: "config resolves; `-f interface/stlink.cfg -f board/st_nucleo_f4.cfg` loads"
---

# OpenOCD adapter renders unprefixed config paths (Can't find stlink.cfg)

## Repro

The adapter emits bare filenames:

```sh
uv run python -c "
from engine.core.loader import load_file
from engine.core.model import DeviceView, Endpoint
from engine.adapters.openocd import OpenOCDAdapter
d = load_file('packs/stm32f411re.yaml')
print(OpenOCDAdapter().render_argv(DeviceView.of(d), Endpoint('probe','/dev/ttyACM0'), ['stm32f411re-M4.elf']))
"
```

Minimal container repro of the resulting OpenOCD failure:

```sh
docker run --rm ghcr.io/arm-stm-env/lang-cpp:15.3.rel2 openocd -f stlink.cfg -c exit
```

## Observed

Adapter argv: `['openocd', '-f', 'stlink.cfg', '-f', 'st_nucleo_f4.cfg', …]`.
OpenOCD: `embedded:startup.tcl:28: Error: Can't find stlink.cfg`.
Via the tool: `uv run stm flash …` → `flash verdict: FAILED 0/1 OK`.

## Expected

argv renders `-f interface/stlink.cfg -f board/st_nucleo_f4.cfg` (matching the
template renderer), OpenOCD loads them, programs, and prints `** Verified OK **`.

## Fix notes

Root cause: model→argv drift. The `board/`|`target/` + `interface/` prefix
decision lives only in `engine/templates/renderer.py:65-87`; the adapter
(`engine/adapters/openocd.py:191-197`) re-derives nothing and passes raw pack
filenames. Fix: make the resolved config paths a model fact consumed by both
(D1/D2 in the linked change). Regression: adapter argv test asserting prefixed
paths (the current `engine/adapters/tests/test_openocd.py:72` encodes the bug).
Not an image issue — `openocd -c "echo [find interface/stlink.cfg]"` resolves
without `OPENOCD_SCRIPTS`.
