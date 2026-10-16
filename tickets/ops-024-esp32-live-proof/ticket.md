---
id: ops-024
title: "Record the live ESP32-CAM proof: containerized flash + boot log"
kind: ops-task
status: done
size: XS
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/ops-024/
branch: ticket/ops-024-esp32-live-proof
---

# Record the live ESP32-CAM proof: containerized flash + boot log

## Work

Close the last open item on `req-022`: prove flashing **through the container** (not just
host-side) and capture the run proof — the boot log and the app's own output.

## Done-when

`mu flash` programs the ESP32-CAM through the container and the flashed app runs; both are
recorded; `make test` green.

## Evidence

2026-10-16 — bench, PL2303 bridge (`067b:2303`) at `/dev/ttyUSB0`, board in download mode
(GPIO0→GND + RST):

```
mu flash --mcu-config esp32cam --device /dev/ttyUSB0 \
  --project-dir /tmp/opencode/esp32demo \
  --files build/bootloader/bootloader.bin build/partition_table/partition-table.bin build/esp32cam.bin
```

→ the container forwarded the tty (`--device /dev/ttyUSB0:/dev/ttyUSB0`) and `esptool` wrote all
three images:

```
Wrote 149120 bytes (84527 compressed) at 0x00010000 in 2.1 seconds (561.3 kbit/s).
Verifying written data...
Hash of data verified.
flash verdict: 3/3 OK (3 pieces) + proof rung 'uart-boot-log'
```

Then, with GPIO0 released and RST pulsed, a reader attached **before** the reset captured UART0
@115200:

```
I (49)  boot:  2 factory          factory app      00 00 00010000 00100000
I (149) boot: Loaded app from partition at offset 0x10000
I (192) app_init: ESP-IDF:          v6.1
I (169) cpu_start: GPIO 3 and 1 are used as console UART I/O pins
I (248) main_task: Calling app_main()
esp32cam: blink on GPIO33
```

The partition table reports `factory app` at `0x10000`, length `0x100000` — exactly the pack's
`partitions.app` and the fit bound the harness checks (`149120 / 1048576`).

**Chain proven end to end on real silicon:** `create` → `idf.py build` → containerized
`esptool` flash over the forwarded tty → boot → app output.

Notes for the record: the read must be **already attached** before reset (the ROM is silent in
download mode, and the run banner is emitted within milliseconds of reset); the PL2303 is not in
the pack's autodetect VIDs, so `--device /dev/ttyUSB0` was passed explicitly.
