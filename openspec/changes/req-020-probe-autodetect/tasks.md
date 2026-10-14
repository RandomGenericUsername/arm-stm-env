# Tasks

## 1. Shim

- [x] 1.1 `shim.py`: `_PROBE_VIDS` + `_autodetect`; no-selector branch calls it. Verify: `pytest -k binding`.
- [x] 1.2 `main.py`: "no debug probe found" message. Verify: `pytest -k verbs`.

## 2. Tests + live

- [x] 2.1 Empty → None; one → binding; two → ValueError. Verify: `pytest -q` (260 passed).
- [x] 2.2 Live: `mu dev` (no selector) → `--device /dev/bus/usb/003/045`. Verify: dry-run output.
- [x] 2.3 `make test` + `openspec validate req-020-probe-autodetect` green; ticket/INDEX updated.
