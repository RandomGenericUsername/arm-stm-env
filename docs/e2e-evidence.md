# E2E build evidence (req-009) — 9/9 cells green

Rendered trees compile in the pinned images with zero host deps.
C/C++ cells inject harness-owned vendor stubs (see module docstring);
warnings are recorded per cell and never fail (warn-only policy).

## stm32f411re / c — PASS

- image: `ghcr.io/arm-stm-env/lang-cpp:15.3.rel2`
- cmd `make build (in ghcr.io/arm-stm-env/lang-cpp:15.3.rel2)` -> exit 0
- cmd `arm-none-eabi-size -B stm32f411re-M4.elf` -> exit 0
- note: vendor stubs injected: vendor/cmsis-device-stm32f411re/Source/Templates/gcc/startup_stm32f411re_M4.s
- `stm32f411re-M4.elf`: text=200 data=0 bss=0
  - flash: used 200 / avail 524288 (flash)
  - ram: used 0 / avail 131072 (ram)
- warnings:
    (none)

## stm32f411re / cpp — PASS

- image: `ghcr.io/arm-stm-env/lang-cpp:15.3.rel2`
- cmd `make build (in ghcr.io/arm-stm-env/lang-cpp:15.3.rel2)` -> exit 0
- cmd `arm-none-eabi-size -B stm32f411re-M4.elf` -> exit 0
- note: vendor stubs injected: vendor/cmsis-device-stm32f411re/Source/Templates/gcc/startup_stm32f411re_M4.s
- `stm32f411re-M4.elf`: text=200 data=0 bss=0
  - flash: used 200 / avail 524288 (flash)
  - ram: used 0 / avail 131072 (ram)
- warnings:
    (none)

## stm32f411re / rust — PASS

- image: `ghcr.io/arm-stm-env/lang-rust:1.99.0`
- cmd `cargo build --target thumbv7em-none-eabihf (in ghcr.io/arm-stm-env/lang-rust:1.99.0)` -> exit 0
- note: FLASH: origin=0x08000000 length=524288 matches pack; RAM: origin=0x20000000 length=131072 matches pack
- `target/thumbv7em-none-eabihf/debug/stm32f411re`: 825608 bytes (host stat, informational)
- warnings:
    warning: stm32f411re v0.1.0 (/work) ignoring invalid dependency `flip-link` which is missing a lib target

## stm32h755 / c — PASS

- image: `ghcr.io/arm-stm-env/lang-cpp:15.3.rel2`
- cmd `make build (in ghcr.io/arm-stm-env/lang-cpp:15.3.rel2)` -> exit 0
- cmd `arm-none-eabi-size -B stm32h755-M7.elf` -> exit 0
- cmd `arm-none-eabi-size -B stm32h755-M4.elf` -> exit 0
- note: vendor stubs injected: vendor/cmsis-device-stm32h755/Source/Templates/gcc/startup_stm32h755_M7.s, vendor/cmsis-device-stm32h755/Source/Templates/gcc/startup_stm32h755_M4.s
- `stm32h755-M7.elf`: text=200 data=0 bss=0
  - flash: used 200 / avail 1048576 (flash_m7)
  - ram: used 0 / avail 294912 (ram)
- `stm32h755-M4.elf`: text=200 data=0 bss=0
  - flash: used 200 / avail 1048576 (flash_m4)
  - ram: used 0 / avail 294912 (ram)
- warnings:
    (none)

## stm32h755 / cpp — PASS

- image: `ghcr.io/arm-stm-env/lang-cpp:15.3.rel2`
- cmd `make build (in ghcr.io/arm-stm-env/lang-cpp:15.3.rel2)` -> exit 0
- cmd `arm-none-eabi-size -B stm32h755-M7.elf` -> exit 0
- cmd `arm-none-eabi-size -B stm32h755-M4.elf` -> exit 0
- note: vendor stubs injected: vendor/cmsis-device-stm32h755/Source/Templates/gcc/startup_stm32h755_M7.s, vendor/cmsis-device-stm32h755/Source/Templates/gcc/startup_stm32h755_M4.s
- `stm32h755-M7.elf`: text=200 data=0 bss=0
  - flash: used 200 / avail 1048576 (flash_m7)
  - ram: used 0 / avail 294912 (ram)
- `stm32h755-M4.elf`: text=200 data=0 bss=0
  - flash: used 200 / avail 1048576 (flash_m4)
  - ram: used 0 / avail 294912 (ram)
- warnings:
    (none)

## stm32h755 / rust — PASS

- image: `ghcr.io/arm-stm-env/lang-rust:1.99.0`
- cmd `cargo build --target thumbv7em-none-eabihf (in ghcr.io/arm-stm-env/lang-rust:1.99.0)` -> exit 0
- note: FLASH_M7: origin=0x08000000 length=1048576 matches pack; FLASH_M4: origin=0x08100000 length=1048576 matches pack; RAM: origin=0x10000000 length=294912 matches pack
- `target/thumbv7em-none-eabihf/debug/stm32h755`: 825592 bytes (host stat, informational)
- warnings:
    warning: stm32h755 v0.1.0 (/work) ignoring invalid dependency `flip-link` which is missing a lib target

## stm32wl55jc / c — PASS

- image: `ghcr.io/arm-stm-env/lang-cpp:15.3.rel2`
- cmd `make build (in ghcr.io/arm-stm-env/lang-cpp:15.3.rel2)` -> exit 0
- cmd `arm-none-eabi-size -B stm32wl55jc-M4.elf` -> exit 0
- cmd `arm-none-eabi-size -B stm32wl55jc-M0+.elf` -> exit 0
- note: vendor stubs injected: vendor/cmsis-device-stm32wl55jc/Source/Templates/gcc/startup_stm32wl55jc_M4.s, vendor/cmsis-device-stm32wl55jc/Source/Templates/gcc/startup_stm32wl55jc_M0+.s
- `stm32wl55jc-M4.elf`: text=184 data=0 bss=0
  - flash: used 184 / avail 1048576 (flash)
  - ram: used 0 / avail 131072 (ram)
- `stm32wl55jc-M0+.elf`: text=180 data=0 bss=0
  - flash: used 180 / avail 1048576 (flash)
  - ram: used 0 / avail 131072 (ram)
- warnings:
    (none)

## stm32wl55jc / cpp — PASS

- image: `ghcr.io/arm-stm-env/lang-cpp:15.3.rel2`
- cmd `make build (in ghcr.io/arm-stm-env/lang-cpp:15.3.rel2)` -> exit 0
- cmd `arm-none-eabi-size -B stm32wl55jc-M4.elf` -> exit 0
- cmd `arm-none-eabi-size -B stm32wl55jc-M0+.elf` -> exit 0
- note: vendor stubs injected: vendor/cmsis-device-stm32wl55jc/Source/Templates/gcc/startup_stm32wl55jc_M4.s, vendor/cmsis-device-stm32wl55jc/Source/Templates/gcc/startup_stm32wl55jc_M0+.s
- `stm32wl55jc-M4.elf`: text=184 data=0 bss=0
  - flash: used 184 / avail 1048576 (flash)
  - ram: used 0 / avail 131072 (ram)
- `stm32wl55jc-M0+.elf`: text=180 data=0 bss=0
  - flash: used 180 / avail 1048576 (flash)
  - ram: used 0 / avail 131072 (ram)
- warnings:
    (none)

## stm32wl55jc / rust — PASS

- image: `ghcr.io/arm-stm-env/lang-rust:1.99.0`
- cmd `cargo build --target thumbv7em-none-eabi (in ghcr.io/arm-stm-env/lang-rust:1.99.0)` -> exit 0
- note: FLASH: origin=0x08000000 length=1048576 matches pack; RAM: origin=0x20000000 length=131072 matches pack
- `target/thumbv7em-none-eabi/debug/stm32wl55jc`: 830972 bytes (host stat, informational)
- warnings:
    warning: stm32wl55jc v0.1.0 (/work) ignoring invalid dependency `flip-link` which is missing a lib target
