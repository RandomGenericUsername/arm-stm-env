# Tasks

## 1. OpenOCD adapter

- [x] 1.1 `engine/adapters/openocd.py` rendering argv from model (interface/target/DUAL_CORE/endpoint) + transcript fixtures + result parsing. Verify: `pytest -k openocd` green; board-names grep empty.
- [x] 1.2 Proof-struct filling incl. H755 dual-session vectors. Verify: `pytest -k proof` green.

## 2. probe-rs skeleton + conformance

- [x] 2.1 `engine/adapters/probe_rs.py` (`--chip` rendering, output mapping, live proof OPEN). Verify: `pytest -k probe_rs` green.
- [x] 2.2 Port conformance (both adapters satisfy ABC) + cross-adapter comparability. Verify: `pytest -k conformance` green.

## 3. Integration checks

- [x] 3.1 Full suite green, zero live-probe claims, `openspec validate` green. Verify: exits 0; `rg -ri "live probe|real hardware|on-device" engine/adapters/` documents OPEN status only.
- [x] 3.2 Update req-006 ticket + link change. Verify: acceptance boxes checkable.
