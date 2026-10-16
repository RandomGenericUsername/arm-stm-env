# device-matrix

Day-one shippable matrix. Each cell must complete create → build → flash → observable proof from a clean machine.

| Pack (board) | Cores | C | C++ | Rust | Probe backends shipped |
|---|---|---|---|---|---|
| Nucleo-F411RE (stm32f411re) | cortex-m4 | yes | yes | yes | openocd (`stlink.cfg` + `stm32f4x.cfg`) |
| Nucleo-H755ZI-Q (stm32h755) | cortex-m7 + cortex-m4 | yes | yes | yes | openocd (per-core cfgs; M4 target under review — sibling used `stm32f4x.cfg`, suspect) |
| Nucleo-WL55JC (stm32wl55jc) | cortex-m4 + cortex-m4 | yes | yes | yes | openocd (targets under review — sibling cfgs suspect, see source brief lineage) |
| ESP32-CAM (esp32cam) — first non-STM32, post-V1 | xtensa-lx6 (dual-core) | yes (`idf-cmake`) | — | — | esptool (UART, no probe; `0x1000`/`0x8000`/`0x10000`) |

Notes:
- Sibling reference: `mcu-configs/*.yml` field shapes (target, per-core core/architecture/memory/openocd) carry over; exact openocd targets re-verified per pack before V1.
- Proof ritual per pack: LED, RTT, or UART output — declared in each pack, pending Open Question resolution.
- Languages beyond C/C++/Rust and vendors beyond STM32 are later packs against the same engine; matrix grows, engine does not change. The ESP32 row is the first proof of that claim (CAP-7): it must land with zero `engine/core` diffs (AD-1).
