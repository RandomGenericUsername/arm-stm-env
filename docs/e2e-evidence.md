# E2E build evidence (req-009) — 10/10 cells green

Rendered trees compile in the pinned images with zero host deps.
C/C++ cells inject harness-owned vendor stubs (see module docstring);
warnings are recorded per cell and never fail (warn-only policy).

## stm32f411re / c — PASS

- image: `ghcr.io/randomgenericusername/lang-cpp:15.3.rel2`
- stack: `make-cmsis` (template family `c-cmsis`)
- build evidence: `stack=make-cmsis; template_family=c-cmsis; commands=make build (in ghcr.io/randomgenericusername/lang-cpp:15.3.rel2) | arm-none-eabi-size -B build/M4/stm32f411re-M4.elf; exits=0,0; artifacts=; fits=flash=364/524288,ram=0/131072`
- cmd `make build (in ghcr.io/randomgenericusername/lang-cpp:15.3.rel2)` -> exit 0
- cmd `arm-none-eabi-size -B build/M4/stm32f411re-M4.elf` -> exit 0
- note: vendor stubs injected: vendor/cmsis-device-stm32f411re/Source/Templates/gcc/startup_stm32f411xe.s
- `build/M4/stm32f411re-M4.elf`: text=364 data=0 bss=0
  - flash: used 364 / avail 524288 (flash)
  - ram: used 0 / avail 131072 (ram)
- warnings:
    (none)

## stm32f411re / cpp — PASS

- image: `ghcr.io/randomgenericusername/lang-cpp:15.3.rel2`
- stack: `make-cmsis` (template family `c-cmsis`)
- build evidence: `stack=make-cmsis; template_family=c-cmsis; commands=make build (in ghcr.io/randomgenericusername/lang-cpp:15.3.rel2) | arm-none-eabi-size -B build/M4/stm32f411re-M4.elf; exits=0,0; artifacts=; fits=flash=364/524288,ram=0/131072`
- cmd `make build (in ghcr.io/randomgenericusername/lang-cpp:15.3.rel2)` -> exit 0
- cmd `arm-none-eabi-size -B build/M4/stm32f411re-M4.elf` -> exit 0
- note: vendor stubs injected: vendor/cmsis-device-stm32f411re/Source/Templates/gcc/startup_stm32f411xe.s
- `build/M4/stm32f411re-M4.elf`: text=364 data=0 bss=0
  - flash: used 364 / avail 524288 (flash)
  - ram: used 0 / avail 131072 (ram)
- warnings:
    (none)

## stm32f411re / rust — PASS

- image: `ghcr.io/randomgenericusername/lang-rust:1.99.0`
- stack: `cargo-cortex` (template family `rust-cortex`)
- build evidence: `stack=cargo-cortex; template_family=rust-cortex; commands=cargo build --target thumbv7em-none-eabihf (in ghcr.io/randomgenericusername/lang-rust:1.99.0); exits=0; artifacts=target/thumbv7em-none-eabihf/debug/stm32f411re=825608; fits=`
- cmd `cargo build --target thumbv7em-none-eabihf (in ghcr.io/randomgenericusername/lang-rust:1.99.0)` -> exit 0
- note: FLASH: origin=0x08000000 length=524288 matches pack; RAM: origin=0x20000000 length=131072 matches pack
- `target/thumbv7em-none-eabihf/debug/stm32f411re`: 825608 bytes (host stat, informational)
- warnings:
    warning: stm32f411re v0.1.0 (/work) ignoring invalid dependency `flip-link` which is missing a lib target

## stm32h755 / c — PASS

- image: `ghcr.io/randomgenericusername/lang-cpp:15.3.rel2`
- stack: `make-cmsis` (template family `c-cmsis`)
- build evidence: `stack=make-cmsis; template_family=c-cmsis; commands=make build (in ghcr.io/randomgenericusername/lang-cpp:15.3.rel2) | arm-none-eabi-size -B build/M7/stm32h755-M7.elf | arm-none-eabi-size -B build/M4/stm32h755-M4.elf; exits=0,0,0; artifacts=; fits=flash_m7=568/1048576,flash_m4=324/1048576,ram_m7=0/524288,ram_m4=4/294912`
- cmd `make build (in ghcr.io/randomgenericusername/lang-cpp:15.3.rel2)` -> exit 0
- cmd `arm-none-eabi-size -B build/M7/stm32h755-M7.elf` -> exit 0
- cmd `arm-none-eabi-size -B build/M4/stm32h755-M4.elf` -> exit 0
- note: vendor stubs injected: vendor/cmsis-device-stm32h755/Source/Templates/gcc/startup_stm32h755xx.s, vendor/cmsis-device-stm32h755/Source/Templates/gcc/startup_stm32h755xx.s
- `build/M7/stm32h755-M7.elf`: text=568 data=0 bss=0
  - flash: used 568 / avail 1048576 (flash_m7)
  - ram: used 0 / avail 524288 (ram_m7)
- `build/M4/stm32h755-M4.elf`: text=324 data=0 bss=4
  - flash: used 324 / avail 1048576 (flash_m4)
  - ram: used 4 / avail 294912 (ram_m4)
- warnings:
    (none)

## stm32h755 / cpp — PASS

- image: `ghcr.io/randomgenericusername/lang-cpp:15.3.rel2`
- stack: `make-cmsis` (template family `c-cmsis`)
- build evidence: `stack=make-cmsis; template_family=c-cmsis; commands=make build (in ghcr.io/randomgenericusername/lang-cpp:15.3.rel2) | arm-none-eabi-size -B build/M7/stm32h755-M7.elf | arm-none-eabi-size -B build/M4/stm32h755-M4.elf; exits=0,0,0; artifacts=; fits=flash_m7=568/1048576,flash_m4=324/1048576,ram_m7=0/524288,ram_m4=4/294912`
- cmd `make build (in ghcr.io/randomgenericusername/lang-cpp:15.3.rel2)` -> exit 0
- cmd `arm-none-eabi-size -B build/M7/stm32h755-M7.elf` -> exit 0
- cmd `arm-none-eabi-size -B build/M4/stm32h755-M4.elf` -> exit 0
- note: vendor stubs injected: vendor/cmsis-device-stm32h755/Source/Templates/gcc/startup_stm32h755xx.s, vendor/cmsis-device-stm32h755/Source/Templates/gcc/startup_stm32h755xx.s
- `build/M7/stm32h755-M7.elf`: text=568 data=0 bss=0
  - flash: used 568 / avail 1048576 (flash_m7)
  - ram: used 0 / avail 524288 (ram_m7)
- `build/M4/stm32h755-M4.elf`: text=324 data=0 bss=4
  - flash: used 324 / avail 1048576 (flash_m4)
  - ram: used 4 / avail 294912 (ram_m4)
- warnings:
    (none)

## stm32h755 / rust — PASS

- image: `ghcr.io/randomgenericusername/lang-rust:1.99.0`
- stack: `cargo-cortex` (template family `rust-cortex`)
- build evidence: `stack=cargo-cortex; template_family=rust-cortex; commands=cargo build --target thumbv7em-none-eabihf (in ghcr.io/randomgenericusername/lang-rust:1.99.0); exits=0; artifacts=target/thumbv7em-none-eabihf/debug/stm32h755=825592; fits=`
- cmd `cargo build --target thumbv7em-none-eabihf (in ghcr.io/randomgenericusername/lang-rust:1.99.0)` -> exit 0
- note: FLASH_M7: origin=0x08000000 length=1048576 matches pack; FLASH_M4: origin=0x08100000 length=1048576 matches pack; RAM_M7: origin=0x24000000 length=524288 matches pack; RAM_M4: origin=0x30000000 length=294912 matches pack
- `target/thumbv7em-none-eabihf/debug/stm32h755`: 825592 bytes (host stat, informational)
- warnings:
    warning: stm32h755 v0.1.0 (/work) ignoring invalid dependency `flip-link` which is missing a lib target

## stm32wl55jc / c — PASS

- image: `ghcr.io/randomgenericusername/lang-cpp:15.3.rel2`
- stack: `make-cmsis` (template family `c-cmsis`)
- build evidence: `stack=make-cmsis; template_family=c-cmsis; commands=make build (in ghcr.io/randomgenericusername/lang-cpp:15.3.rel2) | arm-none-eabi-size -B build/M4/stm32wl55jc-M4.elf | arm-none-eabi-size -B build/M0+/stm32wl55jc-M0+.elf; exits=0,0,0; artifacts=; fits=flash_m4=328/131072,flash_m0plus=264/131072,ram_m4=0/49152,ram_m0plus=4/16384`
- cmd `make build (in ghcr.io/randomgenericusername/lang-cpp:15.3.rel2)` -> exit 0
- cmd `arm-none-eabi-size -B build/M4/stm32wl55jc-M4.elf` -> exit 0
- cmd `arm-none-eabi-size -B build/M0+/stm32wl55jc-M0+.elf` -> exit 0
- note: vendor stubs injected: vendor/cmsis-device-stm32wl55jc/Source/Templates/gcc/startup_stm32wl55xx_cm4.s, vendor/cmsis-device-stm32wl55jc/Source/Templates/gcc/startup_stm32wl55xx_cm0plus.s
- `build/M4/stm32wl55jc-M4.elf`: text=328 data=0 bss=0
  - flash: used 328 / avail 131072 (flash_m4)
  - ram: used 0 / avail 49152 (ram_m4)
- `build/M0+/stm32wl55jc-M0+.elf`: text=264 data=0 bss=4
  - flash: used 264 / avail 131072 (flash_m0plus)
  - ram: used 4 / avail 16384 (ram_m0plus)
- warnings:
    (none)

## stm32wl55jc / cpp — PASS

- image: `ghcr.io/randomgenericusername/lang-cpp:15.3.rel2`
- stack: `make-cmsis` (template family `c-cmsis`)
- build evidence: `stack=make-cmsis; template_family=c-cmsis; commands=make build (in ghcr.io/randomgenericusername/lang-cpp:15.3.rel2) | arm-none-eabi-size -B build/M4/stm32wl55jc-M4.elf | arm-none-eabi-size -B build/M0+/stm32wl55jc-M0+.elf; exits=0,0,0; artifacts=; fits=flash_m4=328/131072,flash_m0plus=264/131072,ram_m4=0/49152,ram_m0plus=4/16384`
- cmd `make build (in ghcr.io/randomgenericusername/lang-cpp:15.3.rel2)` -> exit 0
- cmd `arm-none-eabi-size -B build/M4/stm32wl55jc-M4.elf` -> exit 0
- cmd `arm-none-eabi-size -B build/M0+/stm32wl55jc-M0+.elf` -> exit 0
- note: vendor stubs injected: vendor/cmsis-device-stm32wl55jc/Source/Templates/gcc/startup_stm32wl55xx_cm4.s, vendor/cmsis-device-stm32wl55jc/Source/Templates/gcc/startup_stm32wl55xx_cm0plus.s
- `build/M4/stm32wl55jc-M4.elf`: text=328 data=0 bss=0
  - flash: used 328 / avail 131072 (flash_m4)
  - ram: used 0 / avail 49152 (ram_m4)
- `build/M0+/stm32wl55jc-M0+.elf`: text=264 data=0 bss=4
  - flash: used 264 / avail 131072 (flash_m0plus)
  - ram: used 4 / avail 16384 (ram_m0plus)
- warnings:
    (none)

## stm32wl55jc / rust — PASS

- image: `ghcr.io/randomgenericusername/lang-rust:1.99.0`
- stack: `cargo-cortex` (template family `rust-cortex`)
- build evidence: `stack=cargo-cortex; template_family=rust-cortex; commands=cargo build --target thumbv7em-none-eabi (in ghcr.io/randomgenericusername/lang-rust:1.99.0); exits=0; artifacts=target/thumbv7em-none-eabi/debug/stm32wl55jc=830972; fits=`
- cmd `cargo build --target thumbv7em-none-eabi (in ghcr.io/randomgenericusername/lang-rust:1.99.0)` -> exit 0
- note: FLASH_M4: origin=0x08000000 length=131072 matches pack; FLASH_M0PLUS: origin=0x08020000 length=131072 matches pack; RAM_M4: origin=0x20000000 length=49152 matches pack; RAM_M0PLUS: origin=0x2000C000 length=16384 matches pack
- `target/thumbv7em-none-eabi/debug/stm32wl55jc`: 830972 bytes (host stat, informational)
- warnings:
    warning: stm32wl55jc v0.1.0 (/work) ignoring invalid dependency `flip-link` which is missing a lib target

## esp32cam / c — PASS

- image: `espressif/idf:v6.1@sha256:81893c71bb5e570088901f21def8684c25cd2a9020281bd01b843a7655edb18c`
- stack: `idf-cmake` (template family `idf-cmake`)
- build evidence: `stack=idf-cmake; template_family=idf-cmake; commands=idf.py build (in espressif/idf:v6.1@sha256:81893c71bb5e570088901f21def8684c25cd2a9020281bd01b843a7655edb18c); exits=0; artifacts=build/bootloader/bootloader.bin=26176,build/partition_table/partition-table.bin=3072,build/esp32cam.bin=149120; fits=factory=149120/1048576`
- cmd `idf.py build (in espressif/idf:v6.1@sha256:81893c71bb5e570088901f21def8684c25cd2a9020281bd01b843a7655edb18c)` -> exit 0
- note: app 149120 B / 1048576 B factory partition; triple: bootloader.bin, partition-table.bin, esp32cam.bin
- `build/bootloader/bootloader.bin`: 26176 bytes (host stat, informational)
- `build/partition_table/partition-table.bin`: 3072 bytes (host stat, informational)
- `build/esp32cam.bin`: text=149120 data=0 bss=0
  - flash: used 149120 / avail 1048576 (factory)
  - ram: used 0 / avail 0 ()
- warnings:
    CMake Warning at /opt/esp/idf/tools/cmake/component_validation.cmake:106 (message):
    CMake Warning at /opt/esp/idf/tools/cmake/component_validation.cmake:106 (message):
    CMake Warning at /opt/esp/idf/tools/cmake/component_validation.cmake:106 (message):
    CMake Warning at /opt/esp/idf/tools/cmake/component_validation.cmake:106 (message):
    CMake Warning at /opt/esp/idf/tools/cmake/component_validation.cmake:106 (message):
