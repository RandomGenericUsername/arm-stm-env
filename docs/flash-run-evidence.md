# Flash-run evidence (V1) — per-pack proof

Durable record that each **V1 matrix pack** completes create → build → **flash →
run** from a clean machine with the pack-declared observable proof. The build half
is `docs/e2e-evidence.md` (10/10 cells); this is the live flash/run half. The
proof ladder is probe readback first, LED second, manual register inspection as
fallback (`spec:69`).

| Pack (board) | Probe | OpenOCD target | Flash | Run proof | Recorded |
| --- | --- | --- | --- | --- | --- |
| `stm32f411re` (NUCLEO-F411RE) | `0483:3752` | `stlink.cfg` + `board/st_nucleo_f4.cfg` | `Verified OK` | LD2 (PA5) toggles ~1 Hz; PC in `delay_half_period` | 2026-10-14 |
| `stm32h755` (NUCLEO-H755ZI-Q) | `0483:3754` | `stlink-dap.cfg` + `board/st_nucleo_h745zi.cfg` (+ `DUAL_CORE`) | `Verified OK` ×2 (both banks) | M7 LD2 toggles; M4 `counter` increments | 2026-10-14 |
| `stm32wl55jc` (NUCLEO-WL55JC) | `0483:374e` | `stlink-dap.cfg` + `target/stm32wlx.cfg` | `Verified OK` ×2 (M0+ then M4) | M4 LD1 (PB15) toggles; `GPIOB_ODR` bit 15 flips | 2026-10-16 |

## How each was reproduced

Fresh project + fresh container, probe pinned by serial (containers get the whole
USB bus — bug-018):

```sh
# F411RE / H755ZI-Q: see docs/vscode-debug.md §9
mu create --name f411-clean --path ~/Desktop --mcu-config stm32f411re --lang c --vscode
docker run -d --name mu-f411 --device-cgroup-rule 'c 189:* rmw' \
  -v /dev/bus/usb:/dev/bus/usb -v ~/Desktop/f411-clean:/project \
  -e MU_PROBE_SERIAL=<serial> -w /project ghcr.io/randomgenericusername/lang-cpp:15.3.rel2 sleep infinity
docker exec mu-f411 bash -lc 'cd /project && make flash'

# WL55JC: dual-core, sibling-first flash (M0+ then M4 — bug-023)
mu create --mcu-config stm32wl55jc --lang c --name wl55-clean --path /tmp/opencode/wl55
mu build --project-dir /tmp/opencode/wl55/wl55-clean
docker run --rm --device-cgroup-rule 'c 189:* rmw' -v /dev/bus/usb:/dev/bus/usb \
  -v /tmp/opencode/wl55/wl55-clean:/project -w /project \
  -e MU_PROBE_SERIAL=001C00374741500220383733 \
  ghcr.io/randomgenericusername/lang-cpp:15.3.rel2 make flash
```

Probe readback (WL55JC run proof — the M4 LED pin, `0x48000414` = GPIOB_ODR):

```sh
openocd -f interface/stlink-dap.cfg -f probe/probe-serial.cfg -f target/stm32wlx.cfg \
  -c 'init' -c 'targets stm32wlx.cpu0' -c 'reset run' \
  -c 'mdw 0x48000414 1' -c 'sleep 260' -c 'mdw 0x48000414 1' ...
# → 0x48000414: 00008000 / 00008000 / 00008000 / 00000000 / 00000000  (PB15 toggles)
```

## Scope note

**Rust cells are build-parity only for V1** (`spike-008` decision, option c):
probe-rs flashes + runs the generated Rust images on F411RE/H755 (verified), but
the generated example is a bare `wfi` loop with no observable proof, so the V1
flash/run gate rests on the C/C++ LED proofs above. The build half of the Rust
cells is in `docs/e2e-evidence.md`.

## Sources

- `tickets/ops-020-clean-test-doc/ticket.md` + `docs/vscode-debug.md` §9 — F411RE, H755ZI-Q.
- `tickets/ops-027-wl55-clean-run/ticket.md` — WL55JC.
- `tickets/ops-023-e2e-matrix/ticket.md` + `docs/e2e-evidence.md` — the build half.
- `tickets/spike-008-rust-flash-run/ticket.md` — Rust scope.
