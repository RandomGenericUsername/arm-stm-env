# Tasks

## 1. Verbs + ports

- [x] 1.1 Adapter port ABCs (`ProbeAdapter`, image-lookup interface) + stub implementations in tests. Verify: `pytest -k ports` — stubs conform.
- [x] 1.2 Five thin verbs (create/dev/build/flash/debug) with argparse + `--dry-run` printing container argv. Verify: `pytest -k verbs` + `stm build --dry-run` works without Docker.
- [x] 1.3 No-hardware-knowledge gate test. Verify: device-name grep over `engine/cli/` empty.

## 2. Shim

- [x] 2.1 Language→image lookup via core interface + identical resolution both modes. Verify: `pytest -k shim_lookup`.
- [x] 2.2 Per-OS probe mapping (Linux `--device`, macOS documented limits) + XOR enforcement (`--mcu-config` vs flags). Verify: `pytest -k shim_probe` + mixed-flags CLI test exits 2 with usage.
- [x] 2.3 Flash verdict rendering from multi-piece stub results (3/3 OK + rung). Verify: `pytest -k verdict`.

## 3. Integration checks

- [x] 3.1 Full suite green + `openspec validate req-005-cli-verbs` green + `stm` console script installed. Verify: exits 0; `stm --help` renders.
- [x] 3.2 Update req-005 ticket + link change. Verify: acceptance boxes checkable.
