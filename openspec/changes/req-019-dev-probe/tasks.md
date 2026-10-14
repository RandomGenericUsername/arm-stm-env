# Tasks

## 1. CLI

- [x] 1.1 `main.py`: `_add_probe_selectors` shared; `dev` gets the selectors. Verify: `mu dev --help` shows them.
- [x] 1.2 Test: `dev --device` dry-run forwards `--device <node>:<node>`. Verify: `pytest -k dev`.

## 2. Live + close-out

- [x] 2.1 Live: `mu dev --vid 0483 --pid 3754 --dry-run` → `--device /dev/bus/usb/003/045`. Verify: dry-run output.
- [x] 2.2 `make test` + `openspec validate req-019-dev-probe` green; ticket/INDEX updated.
