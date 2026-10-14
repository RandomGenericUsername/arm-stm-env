"""Project renderer (req-008).

Pack model in -> project tree out. ``string.Template`` substitution only;
per-core contexts are pre-computed here and dual-core packs render by core
iteration, not template forks (design.md). The renderer consumes the
certified model ONLY (``Device.facets`` for fpu/linker/config-headers,
``Device.openocd`` for flash facts) and never re-reads pack YAML.
"""

from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path
from string import Template

from engine.core.model import Core, Device
from engine.templates.vendoring import VendorError, vendor

__all__ = [
    "CPU_BY_CORE",
    "RUST_PINS",
    "SUPPORTED_LANGS",
    "core_context",
    "render",
]

SUPPORTED_LANGS = ("c", "cpp", "rust")

# Core name -> gcc -mcpu value (renderer-owned map, no template fork).
CPU_BY_CORE = {
    "M4": "cortex-m4",
    "M7": "cortex-m7",
    "M0+": "cortex-m0plus",
}

# Pinned embedded crates, verified against the crates.io API 2026-10-09
# (max stable: cortex-m 0.7.9, cortex-m-rt 0.7.7, panic-halt 1.0.0;
# flip-link 0.1.12 matches the spike-003 toolchain table). Exact `=` pins
# so re-renders are reproducible. Sibling pins (0.6.x era) predate these
# and are NOT reused.
RUST_PINS = {
    "cortex-m": "=0.7.9",
    "cortex-m-rt": "=0.7.7",
    "panic-halt": "=1.0.0",
}
FLIP_LINK_PIN = "0.1.12"
# Toolchain recon (spike-003): rust stable 1.99.0 carries both thumbv7em
# targets as Tier-2 no_std.
RUST_VERSION = "1.99"


def _fpu_flags(mode: str, variant: str) -> str:
    if mode == "soft" or variant == "none":
        return "-mfloat-abi=soft"
    return f"-mfpu={variant} -mfloat-abi={mode}"


def _define_flags(macros: str | None) -> str:
    """Space-separated pack macros -> ``-D`` flags (dual-core cores need two)."""
    if not macros:
        return ""
    return " ".join(f"-D{m}" for m in macros.split())


def _oc_cfg_path(device: Device) -> str:
    """Board-vs-target config path, resolved by the model (bug-003)."""
    oc = device.openocd
    if oc is None:
        return "target/stm32f4x.cfg"
    return oc.config_files()[1]


def _oc_flash_args(device: Device) -> str:
    """`openocd -f ...` args for flash-helper targets, from model facts."""
    oc = device.openocd
    if oc is None:
        return "-f interface/stlink.cfg -f target/stm32f4x.cfg"
    interface, target = oc.config_files()
    args = f"-f {interface} -f {target}"
    if oc.dual_core and not oc.board:
        # Target-direct dual sessions (WL55JC) need the flag on the command
        # line; board cfgs (F4/H7) set DUAL_CORE themselves (spike-001).
        args += ' -c "set DUAL_CORE 1"'
    return args


def _sibling_sections(facets: DeviceFacets) -> tuple[str, str]:
    """(extra includes, main body) for a core with no LED example (ops-018).

    A volatile counter in a timed loop: set a breakpoint on ``counter++`` (or
    watch ``counter``) to prove the core is attached and steppable. No pin is
    touched, so a sibling core can't fight the primary core's LED example.
    """
    clock = facets.example_led.clock_hz if facets.example_led else 16_000_000
    # ~0.05 s half-period; loop ≈ 16 cycles/iter at -O (approximate).
    iters = round(0.05 * clock / 16)
    includes = (
        "#include <stdint.h>\n"
        "\n"
        f"#define DELAY_ITERS  {iters}UL  /* ~0.05 s @{clock} Hz; tune */\n"
        "\n"
        "/* Volatile so it survives -O and is watchable in a debug session. */\n"
        "volatile uint32_t counter = 0;\n"
        "\n"
        "static void delay_loop(void)\n"
        "{\n"
        "    for (volatile uint32_t i = 0; i < DELAY_ITERS; ++i) {\n"
        '        __asm volatile ("nop");\n'
        "    }\n"
        "}\n"
    )
    body = (
        "    /* Sibling-core bring-up: proves this core runs and is debuggable.\n"
        "       Breakpoint on `counter++` (or watch `counter`) — it advances. */\n"
        "    for (;;) {\n"
        "        counter++;\n"
        "        delay_loop();\n"
        "    }\n"
    )
    return includes, body


def _main_sections(facets: DeviceFacets, primary: bool) -> tuple[str, str]:
    """(extra includes, main body) for ``src/main-<core>.c`` (req-014/req-015).

    A pack that declares ``example.led`` gets a self-contained blink of that
    on-board LED (raw registers + NOP half-period delay, no HAL) on the
    **primary** (first) core. Any other core (a dual-core sibling, or a pack
    with no LED fact) gets the ``_sibling_sections`` counter loop instead.
    """
    led = facets.example_led if primary else None
    if led is None:
        return _sibling_sections(facets)
    gpio, rcc = led.gpio_base, led.rcc_en_addr
    on_shift, off_shift = (
        (led.pin, led.pin + 16) if led.active == "high" else (led.pin + 16, led.pin)
    )
    # ~10 Hz: half-period ≈ 0.05 s; loop ≈ 16 cycles/iter at -O (approximate).
    iters = round(0.05 * led.clock_hz / 16)
    includes = (
        "#include <stdint.h>\n"
        "\n"
        "#define REG32(a)     (*(volatile uint32_t *)(a))\n"
        f"#define RCC_EN       REG32(0x{rcc:08X}UL)\n"
        f"#define GPIO_MODER   REG32(0x{gpio:08X}UL)\n"
        f"#define GPIO_BSRR    REG32(0x{gpio + 0x18:08X}UL)\n"
        "\n"
        f"#define LED_PIN      {led.pin}u\n"
        f"#define BSRR_ON      (1u << {on_shift})\n"
        f"#define BSRR_OFF     (1u << {off_shift})\n"
        f"#define DELAY_ITERS  {iters}UL  /* ~0.05 s @{led.clock_hz} Hz, ~10 Hz; tune */\n"
        "\n"
        "static void delay_half_period(void)\n"
        "{\n"
        "    for (volatile uint32_t i = 0; i < DELAY_ITERS; ++i) {\n"
        '        __asm volatile ("nop");\n'
        "    }\n"
        "}\n"
    )
    body = (
        f"    /* Example for this pack: blink the on-board LED "
        f"(P{led.port.upper()}{led.pin}, {led.active} active). */\n"
        f"    RCC_EN |= (1u << {led.rcc_en_bit});\n"
        "    GPIO_MODER &= ~(3u << (LED_PIN * 2));\n"
        "    GPIO_MODER |=  (1u << (LED_PIN * 2));\n"
        "\n"
        "    for (;;) {\n"
        "        GPIO_BSRR = BSRR_ON;\n"
        "        delay_half_period();\n"
        "        GPIO_BSRR = BSRR_OFF;\n"
        "        delay_half_period();\n"
        "    }\n"
    )
    return includes, body


def core_context(device: Device, core: Core, lang: str) -> dict:
    """Per-core substitution context (renderer-computed, template renders)."""
    facets = device.facets
    cpu = CPU_BY_CORE.get(core.name, core.name.lower())
    header = facets.config_header
    guard = re.sub(r"\W", "_", header).upper()
    example_includes, main_body = _main_sections(
        facets, device.cores[0].name == core.name
    )
    return {
        "project": device.id,
        "device_id": device.id,
        "version": device.version,
        "core": core.name,
        "arch": core.arch,
        "cpu": cpu,
        "cpu_flags": f"-mcpu={cpu} -mthumb",
        "fpu_flags": _fpu_flags(facets.fpu_mode, facets.fpu_variant),
        "define_flags": _define_flags(facets.define_for(core.name)),
        "linker_script": facets.linker_for(core.name, device.id),
        "cmsis_include": "vendor/CMSIS/CMSIS/Core/Include",
        "device_include": f"vendor/cmsis-device-{device.id}/Include",
        "startup_s": (
            f"vendor/cmsis-device-{device.id}/Source/Templates/gcc"
            f"/{facets.startup_for(core.name, device.id)}"
        ),
        "system_c": (
            f"vendor/cmsis-device-{device.id}/Source/Templates"
            f"/{facets.system_for(core.name, device.id)}"
        ),
        "config_header": header,
        "config_guard": guard,
        "config_library": facets.config_library,
        "config_defaults_source": facets.config_defaults_source,
        "lib_upper": re.sub(r"\W", "_", facets.config_library).upper(),
        "compiler": "$(CXX)" if lang == "cpp" else "$(CC)",
        "std_flags": " -std=c++17 -fno-exceptions -fno-rtti" if lang == "cpp" else "",
        "oc_interface": device.openocd.interface if device.openocd else "stlink.cfg",
        "oc_cfg_path": _oc_cfg_path(device),
        "oc_flash_args": _oc_flash_args(device),
        "oc_dual": bool(device.openocd and device.openocd.dual_core),
        "probe_transport": device.probe_ref.transport,
        "probe_address": device.probe_ref.address,
        "lang": lang,
        "example_includes": example_includes,
        "main_body": main_body,
    }


# --- C/C++ templates (authored fresh; sibling outputs were checklists) ---

_MAKEFILE_HEAD = Template(
    "# Makefile for $project — generated from pack $device_id v$version; do not edit by hand.\n"
    "# Toolchain: arm-none-eabi-gcc (see req-007 image). Per-core sections below;\n"
    "# `make build` / `make flash` / `make clean` drive every core.\n"
    "CC = arm-none-eabi-gcc\n"
    "CXX = arm-none-eabi-g++\n"
    "OBJCOPY = arm-none-eabi-objcopy\n"
    "SIZE = arm-none-eabi-size\n"
    "OPENOCD ?= openocd\n"
    "CMSIS_INC = -Ivendor/CMSIS/CMSIS/Core/Include -I$device_include\n"
    "CONFIG_INC = -Iconfig\n"
    "CONFIG_DEF = -DUSE_$config_guard\n"
    "\n"
)

_MAKEFILE_CORE = Template(
    "# --- core $core ($arch) ---\n"
    "TARGET_$core = $project-$core\n"
    "OUT_$core = build/$core/$$(TARGET_$core)\n"
    "CPU_FLAGS_$core = $cpu_flags\n"
    "FPU_FLAGS_$core = $fpu_flags\n"
    "CFLAGS_$core = $$(CPU_FLAGS_$core) $$(FPU_FLAGS_$core)$std_flags $define_flags "
    "$$(CMSIS_INC) $$(CONFIG_INC) $$(CONFIG_DEF) -Os -ffunction-sections -fdata-sections -g3 -Wall\n"
    "LDSCRIPT_$core = linker/$linker_script\n"
    "STARTUP_$core = $startup_s\n"
    "SYSTEM_C_$core = $system_c\n"
    "SRCS_$core = src/main-$core.c\n"
    "OBJS_$core = build/$core/main-$core.o build/$core/startup-$core.o build/$core/system-$core.o\n"
    "\n"
    "build/$core/main-$core.o: src/main-$core.c config/$config_header\n"
    "\t@mkdir -p $$(@D)\n"
    "\t$compiler $$(CFLAGS_$core) -c -o $$@ $$<\n"
    "\n"
    "# Vendor startup assembly stays in its submodule (see Startup/NOTE.md);\n"
    "# this rule assembles it straight from vendor/ — never copied.\n"
    "build/$core/startup-$core.o: $$(STARTUP_$core)\n"
    "\t@mkdir -p $$(@D)\n"
    "\t$compiler $$(CFLAGS_$core) -c -o $$@ $$<\n"
    "\n"
    "# Vendor system file (SystemInit) compiles from its submodule likewise.\n"
    "build/$core/system-$core.o: $$(SYSTEM_C_$core)\n"
    "\t@mkdir -p $$(@D)\n"
    "\t$compiler $$(CFLAGS_$core) -c -o $$@ $$<\n"
    "\n"
    "# Final artifacts land under build/$core/ — nothing generated at the root.\n"
    "$$(OUT_$core).elf: $$(OBJS_$core) $$(LDSCRIPT_$core)\n"
    "\t@mkdir -p $$(@D)\n"
    "\t$compiler $$(CFLAGS_$core) -T$$(LDSCRIPT_$core) -Wl,--gc-sections "
    "-Wl,-Map=$$(@:.elf=.map) --specs=nano.specs -o $$@ $$(OBJS_$core)\n"
    "\n"
    "$$(OUT_$core).hex: $$(OUT_$core).elf\n"
    "\t$$(OBJCOPY) -O ihex $$< $$@\n"
    "\n"
    "$$(OUT_$core).bin: $$(OUT_$core).elf\n"
    "\t$$(OBJCOPY) -O binary $$< $$@\n"
    "\n"
    "build-$core: $$(OUT_$core).elf $$(OUT_$core).hex $$(OUT_$core).bin\n"
    "\t$$(SIZE) $$(OUT_$core).elf\n"
    "\n"
    "flash-$core: build-$core\n"
    "\t$$(OPENOCD) $oc_flash_args -c \"program $$(OUT_$core).elf verify reset exit\"\n"
    "\n"
    "clean-$core:\n"
    "\trm -rf build/$core\n"
    "\n"
)

_MAKEFILE_FOOT = Template(
    "ALL_BUILD = $build_targets\n"
    "ALL_FLASH = $flash_targets\n"
    "ALL_CLEAN = $clean_targets\n"
    "\n"
    "all: build\n"
    "\n"
    "build: $$(ALL_BUILD)\n"
    "\n"
    "flash: $$(ALL_FLASH)\n"
    "\n"
    "clean: $$(ALL_CLEAN)\n"
    "\n"
    ".PHONY: all build flash clean $build_targets $flash_targets $clean_targets\n"
)

_MAIN_C = Template(
    "/* $project / $core ($arch) — generated bring-up. */\n"
    "/* Reset flow: the vendor startup file ($startup_s, assembled from its\n"
    "   submodule — see Startup/NOTE.md) provides Reset_Handler, which runs\n"
    "   SystemInit and then calls main() below. This file owns application\n"
    "   init only. */\n"
    '#include "$config_header"\n'
    "$example_includes"
    "\n"
    "#ifndef USE_$config_guard\n"
    '#error "pack config header missing: build with -Iconfig (see config/OVERRIDES.md)"\n'
    "#endif\n"
    "\n"
    "int main(void)\n"
    "{\n"
    "$main_body"
    "}\n"
)

_LINKER = Template(
    "/* $project / $core ($arch) — generated from the pack memory map. */\n"
    "/* Entry comes from the vendor startup file (see Startup/NOTE.md). */\n"
    "OUTPUT_FORMAT(\"elf32-littlearm\", \"elf32-bigarm\", \"elf32-littlearm\")\n"
    "OUTPUT_ARCH(arm)\n"
    "ENTRY(Reset_Handler)\n"
    "\n"
    "MEMORY\n"
    "{\n"
    "$regions\n"
    "}\n"
    "\n"
    "/* Stack top: end of the first RAM region. */\n"
    "_estack = ORIGIN($ram_region) + LENGTH($ram_region);\n"
    "_stack_start = _estack;\n"
    "\n"
    "SECTIONS\n"
    "{\n"
    "    .isr_vector :\n"
    "    {\n"
    "        KEEP(*(.isr_vector))\n"
    "        KEEP(*(.vectors))\n"
    "    } >$flash_region\n"
    "\n"
    "    .text :\n"
    "    {\n"
    "        *(.text*)\n"
    "        KEEP(*(.init))\n"
    "        KEEP(*(.fini))\n"
    "        *(.rodata*)\n"
    "        *(.ARM*)\n"
    "        . = ALIGN(4);\n"
    "    } >$flash_region\n"
    "\n"
    "    .data : AT(LOADADDR(.text) + SIZEOF(.text))\n"
    "    {\n"
    "        . = ALIGN(4);\n"
    "        _sdata = .;\n"
    "        *(.data*)\n"
    "        . = ALIGN(4);\n"
    "        _edata = .;\n"
    "        _sidata = LOADADDR(.data);\n"
    "    } >$ram_region\n"
    "\n"
    "    .bss :\n"
    "    {\n"
    "        . = ALIGN(4);\n"
    "        _sbss = .;\n"
    "        *(.bss*)\n"
    "        *(COMMON)\n"
    "        . = ALIGN(4);\n"
    "        _ebss = .;\n"
    "    } >$ram_region\n"
    "}\n"
)

_STARTUP_NOTE = Template(
    "# Startup assembly for $project\n"
    "\n"
    "The Reset_Handler / vector table live in ST's CMSIS-device startup file,\n"
    "which stays in its vendored submodule (disciplined vendoring, spike-002:\n"
    "submodule trees stay pristine — nothing is copied into this project).\n"
    "The Makefile assembles it in place via `STARTUP_<CORE>` and links the\n"
    "object with the application.\n"
    "\n"
    "## Per-core sources (pick the exact file the submodule ships)\n"
    "\n"
    "$rows\n"
    "Submodule filenames vary by family (e.g. `...xe.s` vs `...xg.s`); if the\n"
    "path above does not match, update the one `STARTUP_<CORE>` line in the\n"
    "Makefile — no other change is needed.\n"
    "\n"
    "## Reset flow\n"
    "\n"
    "`Reset_Handler` (startup) -> `SystemInit` (CMSIS system file) -> `main()`\n"
    "(`src/main-<CORE>.c`). The linker script (`linker/`) places `.isr_vector`\n"
    "at the flash origin via `ENTRY(Reset_Handler)`.\n"
)

_CONFIG_H = Template(
    "/* $config_library defaults for $project — pack-owned copy, project wins. */\n"
    "/* Source of these defaults: $defaults_source (informational). To tune a\n"
    "   value, define it in your own project header BEFORE this file is read\n"
    "   (see config/OVERRIDES.md); every default below is guarded so a prior\n"
    "   definition always takes precedence. */\n"
    "#pragma once\n"
    "\n"
    "#ifndef $header_guard\n"
    "#define $header_guard\n"
    "\n"
    "#define ${lib_upper}_CONFIG_VERSION 1\n"
    "\n"
    "/* SysTick rate assumed by pack delay helpers. */\n"
    "#ifndef ${lib_upper}_TICK_HZ\n"
    "#define ${lib_upper}_TICK_HZ 1000\n"
    "#endif\n"
    "\n"
    "/* HSE crystal value assumed by the pack clock setup. */\n"
    "#ifndef ${lib_upper}_HSE_VALUE\n"
    "#define ${lib_upper}_HSE_VALUE 8000000\n"
    "#endif\n"
    "\n"
    "#endif /* $header_guard */\n"
)

_OVERRIDES = Template(
    "# Config overrides for $project\n"
    "\n"
    "Pack library: `$config_library` — defaults in `config/$config_header`\n"
    "(copied from `$defaults_source` at render time).\n"
    "\n"
    "## Order (project-file-wins)\n"
    "\n"
    "1. Your project header / definitions (highest precedence).\n"
    "2. Pack defaults in `config/$config_header` (fill the rest).\n"
    "\n"
    "Every default in the pack header is `#ifndef`-guarded, so defining a\n"
    "symbol first always wins — never edit the generated default in place\n"
    "for a whole-source replacement, hand the build your own header instead.\n"
    "\n"
    "## Wiring\n"
    "\n"
    "- C/C++: `-Iconfig` comes FIRST on the command line (before any vendor\n"
    "  include dir), so `#include \"$config_header\"` resolves here.\n"
    "  `-DUSE_$config_guard` selects this pack's config (the Makefile sets\n"
    "  both; `src/main-*.c` fails fast without the `-D`).\n"
    "- Rust: `build.rs` re-tracks `config/$config_header`\n"
    "  (`cargo:rerun-if-changed`) and declares `cfg($rust_cfg)` for\n"
    "  project-level selection; set it via `RUSTFLAGS=\"--cfg $rust_cfg\"`\n"
    "  when the project overrides a default. The header itself is\n"
    "  informational for Rust builds — the source of truth stays in code.\n"
)

# --- Rust templates (authored fresh; sibling outputs were checklists) ---

_CARGO = Template(
    "[package]\n"
    'name = "$project"\n'
    'version = "0.1.0"\n'
    'edition = "2021"\n'
    'rust-version = "$rust_version"\n'
    'build = "build.rs"\n'
    "\n"
    "# Pinned embedded deps (see RUST_PINS in the renderer; versions verified\n"
    "# against crates.io — exact `=` pins for reproducible renders).\n"
    "[dependencies]\n"
    'cortex-m = "$pin_cortex_m"\n'
    'cortex-m-rt = "$pin_cortex_m_rt"\n'
    'panic-halt = "$pin_panic_halt"\n'
    "\n"
    "[build-dependencies]\n"
    'flip-link = "$flip_link"\n'
    "\n"
    "[profile.dev]\n"
    "# no_std targets cannot unwind: abort is required on stable (bug-002).\n"
    'panic = "abort"\n'
    "opt-level = 0\n"
    "debug = true\n"
    "\n"
    "[profile.release]\n"
    'panic = "abort"\n'
    'opt-level = "z"\n'
    "codegen-units = 1\n"
    "lto = true\n"
    "debug = true\n"
    "\n"
    "# Flash via probe-rs (single-core) or OpenOCD (see probe/openocd.cfg):\n"
    "#   probe-rs run --chip <exact-part> target/$arch/release/$project\n"
)

_MEMORY_X = Template(
    "/* $project memory.x — generated from the pack memory map. */\n"
    "/* cortex-m-rt's link script requires FLASH + RAM regions; dual-bank\n"
    "   packs keep their per-bank regions and gain same-origin aliases. */\n"
    "MEMORY\n"
    "{\n"
    "$regions\n"
    "}\n"
    "\n"
    "/* Stack top: end of RAM. */\n"
    "_stack_start = ORIGIN(RAM) + LENGTH(RAM);\n"
)

_BUILD_RS = Template(
    "//! $project build.rs — memory.x placement + link args + config wiring.\n"
    "//! Authored fresh (stdlib only, no build-script helpers needed).\n"
    "use std::env;\n"
    "use std::fs;\n"
    "use std::path::PathBuf;\n"
    "\n"
    "fn main() {\n"
    "    // Place memory.x where the linker always finds it (required for\n"
    "    // workspaces / non-trivial layouts; harmless otherwise).\n"
    "    let out = PathBuf::from(env::var(\"OUT_DIR\").unwrap());\n"
    "    fs::copy(\"memory.x\", out.join(\"memory.x\")).unwrap();\n"
    "    println!(\"cargo:rustc-link-search={}\", out.display());\n"
    "    // cortex-m-rt provides link.x; flip-link (see Cargo.toml) moves the\n"
    "    // stack below .bss at link time.\n"
    "    println!(\"cargo:rustc-link-arg=-Tlink.x\");\n"
    "    // Rebuild when the memory map or the pack config header changes.\n"
    "    println!(\"cargo:rerun-if-changed=memory.x\");\n"
    "    println!(\"cargo:rerun-if-changed=config/$config_header\");\n"
    "    // Declared project-level cfg for config selection (set it with\n"
    "    // RUSTFLAGS=\"--cfg $rust_cfg\" when overriding a pack default;\n"
    "    // see config/OVERRIDES.md).\n"
    "    println!(\"cargo:rustc-check-cfg=cfg($rust_cfg)\");\n"
    "}\n"
)

_MAIN_RS = Template(
    "//! $project ($arch) — generated no_std bring-up.\n"
    "//! Reset flow: cortex-m-rt links memory.x with this entry; the vector\n"
    "//! table comes from cortex-m-rt, the stack top from `_stack_start`.\n"
    "//! Pack config defaults live in config/$config_header (informational\n"
    "//! for Rust builds — see config/OVERRIDES.md).\n"
    "#![no_std]\n"
    "#![no_main]\n"
    "\n"
    "use cortex_m_rt::entry;\n"
    "use panic_halt as _;\n"
    "\n"
    "#[entry]\n"
    "fn main() -> ! {\n"
    "    // TODO: peripheral init.\n"
    "    loop {\n"
    "        cortex_m::asm::wfi();\n"
    "    }\n"
    "}\n"
)

_OPENOCD = Template(
    "# $project probe/openocd.cfg — generated from pack openocd facts (spike-001).\n"
    "# Probe: $probe_transport ($probe_address).\n"
    "# Flash helper: openocd $oc_flash_args -c \"program <elf> verify reset exit\"\n"
    "source [find $interface]\n"
    "$dual_line$target_line\n"
)


def _render_openocd(device: Device) -> str:
    oc = device.openocd
    if oc is None:
        interface, target = "interface/stlink.cfg", "target/stm32f4x.cfg"
    else:
        interface, target = oc.config_files()
    dual = bool(oc and oc.dual_core)
    if dual and not (oc and oc.board):
        # Target-direct dual sessions (WL55JC): the target file only creates
        # the second core when DUAL_CORE is set (spike-001 finding 3).
        dual_line = "set DUAL_CORE 1\n"
    elif dual:
        dual_line = "# board cfg drives both cores (DUAL_CORE set by the board file)\n"
    else:
        dual_line = "# single-core session\n"
    return _OPENOCD.substitute(
        project=device.id,
        probe_transport=device.probe_ref.transport,
        probe_address=device.probe_ref.address,
        interface=interface,
        oc_flash_args=_oc_flash_args(device),
        dual_line=dual_line,
        target_line=f"source [find {target}]",
    )


def _regions_for(device: Device, core_name: str | None = None) -> tuple[MemoryRegion, ...]:
    """Memory regions visible to ``core_name`` (bug-014).

    A region tagged ``cores:`` belongs only to those cores; untagged regions are
    shared by every core, so single-core packs are unaffected. ``None`` returns
    every region (used by the Rust single-tree ``memory.x``).
    """
    if core_name is None:
        return tuple(device.memory)
    return tuple(m for m in device.memory if m.applies_to(core_name))


def _ld_regions(device: Device, core_name: str | None = None) -> str:
    lines = []
    for m in _regions_for(device, core_name):
        access = "rx" if "flash" in m.name.lower() else "rwx"
        lines.append(f"  {m.name.upper()} ({access}) : ORIGIN = 0x{m.origin:08X}, LENGTH = {m.size}")
    return "\n".join(lines)


def _first_region(regions: tuple[MemoryRegion, ...], want: str, fallback: str) -> str:
    for m in regions:
        if want in m.name.lower():
            return m.name.upper()
    return fallback


def _core_region(device: Device, core_name: str, want: str, fallback: str) -> str:
    """Per-core region: prefer a ``want`` region naming the core (M4 ->
    flash_m4 on dual-bank packs), else the first ``want`` region the core can
    see (shared single-region packs). Mirrors ``engine.verify.e2e.pick_region``."""
    regions = _regions_for(device, core_name)
    for m in regions:
        if want in m.name.lower() and core_name.lower() in m.name.lower():
            return m.name.upper()
    return _first_region(regions, want, fallback)


def _memoryx_regions(device: Device) -> str:
    regions = _regions_for(device)
    names = {m.name.upper() for m in regions}
    lines = [_ld_regions(device)]
    # cortex-m-rt link.x requires FLASH + RAM: alias the first matching bank
    # when no region carries the exact name (e.g. dual-bank H755).
    if "FLASH" not in names:
        first = _first_region(regions, "flash", regions[0].name.upper())
        src = next(m for m in regions if m.name.upper() == first)
        lines.append(f"  FLASH (rx) : ORIGIN = 0x{src.origin:08X}, LENGTH = {src.size}")
    if "RAM" not in names:
        first = _first_region(regions, "ram", regions[0].name.upper())
        src = next(m for m in regions if m.name.upper() == first)
        lines.append(f"  RAM (rwx) : ORIGIN = 0x{src.origin:08X}, LENGTH = {src.size}")
    return "\n".join(lines)


def _config_ctx(device: Device) -> dict:
    facets = device.facets
    header = facets.config_header
    return {
        "project": device.id,
        "config_library": facets.config_library,
        "config_header": header,
        "config_guard": re.sub(r"\W", "_", header).upper(),
        "header_guard": (re.sub(r"\W", "_", header).upper() + "_"),
        "lib_upper": re.sub(r"\W", "_", facets.config_library).upper(),
        "defaults_source": facets.config_defaults_source,
        "rust_cfg": re.sub(r"\W", "_", facets.config_library).lower() + "_project_config",
    }


_GITIGNORE = (
    "# Generated by mu — build outputs and tool logs.\n"
    "build/\n"
    ".mu/\n"
)

def _resume_on_detach(device: Device) -> str:
    """OpenOCD config that resumes the target when the debugger detaches.

    Stock OpenOCD leaves Cortex-M halted on detach (cortex-debug #894). F4-style
    target configs define ``_TARGETNAME`` (guarded so an undefined variable is a
    no-op, not an error that kills the server — bug-009); dual-core packs declare
    their OpenOCD target names (``openocd.targets``, bug-006), so the event is
    set on each explicitly.
    """
    header = (
        "# Generated by mu — resume the target when the debugger detaches.\n"
        "# Stock OpenOCD leaves Cortex-M halted on detach (cortex-debug #894).\n"
        "# End the session with 'Disconnect' (detach) to keep the firmware running;\n"
        "# plain 'Stop' disconnects without detach and leaves it halted.\n"
    )
    targets = [name for _core, name in device.openocd.targets] if device.openocd else []
    if targets:
        body = "".join(
            f"{name} configure -event gdb-detach {{ resume }}\n" for name in targets
        )
    else:
        body = (
            "# Guarded: some target configs (H7 DAP, WL) define no _TARGETNAME —\n"
            "# a no-op there rather than an error that quits the server.\n"
            "if {[info exists _TARGETNAME]} {\n"
            "    $_TARGETNAME configure -event gdb-detach { resume }\n"
            "}\n"
        )
    return header + body

_GCC_PROBLEM_MATCHER = {
    "owner": "cpp",
    "fileLocation": ["relative", "${workspaceFolder}"],
    "pattern": {
        "regexp": "^(.*):(\\d+):(\\d+):\\s+(warning|error):\\s+(.*)$",
        "file": 1,
        "line": 2,
        "column": 3,
        "severity": 4,
        "message": 5,
    },
}


#: Pinned SVD source (Apache-2.0), commit-pinned for reproducibility (req-017).
SVD_REPO = "modm-io/cmsis-svd-stm32"
SVD_SHA = "e79021accd49bf19bd0b16065f5471fb073ff3ac"


def _svd_local_name(path: str) -> str:
    return Path(path).name


def _svd_file_for(device: Device, core_name: str) -> str | None:
    for name, path in device.facets.svd:
        if name == core_name:
            return f"probe/{_svd_local_name(path)}"
    return None


def fetch_svds(device: Device, out_dir: str | Path, *, opener=None) -> list[Path]:
    """Download the pack's pinned SVD files into ``probe/`` (req-017)."""
    opener = opener or urllib.request.urlopen
    out = Path(out_dir)
    written: list[Path] = []
    for _core, path in device.facets.svd:
        dest = out / "probe" / _svd_local_name(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        url = f"https://raw.githubusercontent.com/{SVD_REPO}/{SVD_SHA}/{path}"
        try:
            with opener(url) as resp:
                dest.write_bytes(resp.read())
        except Exception as exc:
            raise VendorError(f"svd: failed to fetch {path} ({url}): {exc}") from exc
        written.append(dest)
    return written


# Cortex-M Rust target triples. OpenOCD's ``cortex_m`` command group (used by
# the bug-011 single-step workaround) only exists for Cortex-M targets, so the
# workaround must not be emitted for other architectures (bug-012).
_CORTEX_M_ARCH_PREFIXES = ("thumbv6m", "thumbv7m", "thumbv7em", "thumbv8m")


def _is_cortex_m(arch: str) -> bool:
    """True when ``arch`` is a Cortex-M Rust target triple."""
    return arch.startswith(_CORTEX_M_ARCH_PREFIXES)


def _processor_index(device: Device, core: Core, index: int) -> int:
    """OpenOCD processor index for ``core`` (bug-013).

    Prefers the pack's declared OpenOCD target name (``…cpuN``); falls back to
    the core's position in ``device.cores``, which matches OpenOCD's cpu0/cpu1
    creation order for the packs we ship.
    """
    oc = device.openocd
    if oc is not None:
        for name, target_name in oc.targets:
            if name == core.name:
                match = re.search(r"(\d+)$", target_name)
                if match:
                    return int(match.group(1))
    return index


def _vscode_files(device: Device) -> dict[str, str]:
    """Generated ``.vscode/`` for the container-attached flow (req-016/017).

    Tool paths are the **in-container** locations (the window is attached to the
    ``mu dev`` container). ``launch.json`` is per-core, with the pack's resolved
    OpenOCD config files, each core's ELF, and its SVD for the register view.
    Built as JSON, never string-templated, so the output is always valid.
    """
    oc = device.openocd
    iface, target = (
        oc.config_files() if oc else ("interface/stlink.cfg", "target/stm32f4x.cfg")
    )
    gdb = "/opt/arm-gnu-toolchain/bin/arm-none-eabi-gdb"
    openocd = "/usr/local/bin/openocd"

    cores = list(device.cores)
    multi_core = len(cores) > 1

    configurations = []
    for index, core in enumerate(device.cores):
        elf = f"build/{core.name}/{device.id}-{core.name}.elf"
        config = {
            "name": f"Debug {core.name} (OpenOCD)",
            "type": "cortex-debug",
            "request": "launch",
            "servertype": "openocd",
            "cwd": "${workspaceFolder}",
            "executable": "${workspaceFolder}/" + elf,
            "runToEntryPoint": "main",
            "configFiles": [iface, target, "probe/resume-on-detach.cfg"],
            "openocdPath": openocd,
            "gdbPath": gdb,
        }
        if multi_core:
            # bug-013: OpenOCD exposes one gdb server per core (…cpu0, …cpu1);
            # cortex-debug connects to the port for `targetProcessor`, so a
            # per-core config without it would attach every session to cpu0.
            config["numberOfProcessors"] = len(cores)
            config["targetProcessor"] = _processor_index(device, core, index)
        if _is_cortex_m(core.arch):
            # bug-011: OpenOCD never advances the PC on a Cortex-M single-step
            # unless interrupts are masked for the duration of the step
            # (J-Link/ST-Link GDB servers do this by default; OpenOCD must be
            # told). `steponly` masks only during a step, so normal run keeps
            # interrupts enabled. These commands run after OpenOCD's
            # `reset halt` (target halted) and before `runToEntryPoint`.
            # bug-012: gated to Cortex-M — the `cortex_m` command group does
            # not exist on other architectures (e.g. RISC-V), where it would
            # error and abort the launch.
            config["postLaunchCommands"] = ["monitor cortex_m maskisr steponly"]
        svd = _svd_file_for(device, core.name)
        if svd is not None:
            config["svdFile"] = "${workspaceFolder}/" + svd
        configurations.append(config)

    if multi_core:
        # bug-013: a compound config that starts OpenOCD once (primary = the
        # boot core, cores[0]) and shares it with the other cores, so both can
        # be debugged at once. OpenOCD shares one gdb server across the device's
        # cores, so the chained launches stay attached (`detached` false).
        compound = dict(configurations[0])
        compound["name"] = "Debug " + "+".join(c.name for c in cores) + " (OpenOCD)"
        compound["chainedConfigurations"] = {
            "enabled": True,
            "waitOnEvent": "postInit",
            "detached": False,
            "lifecycleManagedByParent": True,
            "launches": [
                {"name": f"Debug {core.name} (OpenOCD)"} for core in cores[1:]
            ],
        }
        configurations.append(compound)

    tasks = [
        {
            "label": "Build",
            "type": "process",
            "command": "make",
            "args": ["build"],
            "group": {"kind": "build", "isDefault": True},
            "problemMatcher": _GCC_PROBLEM_MATCHER,
        },
        {
            "label": "Clean",
            "type": "process",
            "command": "make",
            "args": ["clean"],
            "problemMatcher": [],
        },
        {
            "label": "Flash",
            "type": "process",
            "command": "make",
            "args": ["flash"],
            "dependsOrder": "sequence",
            "dependsOn": ["Clean", "Build"],
        },
    ]
    for core in device.cores:
        tasks.append(
            {
                "label": f"Flash {core.name}",
                "type": "process",
                "command": "make",
                "args": [f"flash-{core.name}"],
                "problemMatcher": [],
            }
        )

    def j(obj: object) -> str:
        return json.dumps(obj, indent=2) + "\n"

    return {
        ".vscode/launch.json": j({"version": "0.2.0", "configurations": configurations}),
        ".vscode/tasks.json": j({"version": "2.0.0", "tasks": tasks}),
        ".vscode/settings.json": j(
            {"cortex-debug.gdbPath": gdb, "cortex-debug.openocdPath": openocd}
        ),
        ".vscode/extensions.json": j(
            {"recommendations": ["marus25.cortex-debug", "ms-vscode.cpptools"]}
        ),
    }


def render(
    pack_model: Device, lang: str, out_dir: str | Path, *, vscode: bool = False
) -> list[Path]:
    """Render a project tree; return the list of files written (sorted)."""
    if lang not in SUPPORTED_LANGS:
        raise ValueError(f"unsupported lang {lang!r}; expected one of {SUPPORTED_LANGS}")
    out = Path(out_dir)
    cfg = _config_ctx(pack_model)
    written: list[Path] = []

    def write(rel: str, text: str) -> None:
        path = out / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        written.append(path)

    write(".gitignore", _GITIGNORE)
    write("probe/openocd.cfg", _render_openocd(pack_model))
    if vscode and lang in ("c", "cpp"):
        written.extend(fetch_svds(pack_model, out))
        write("probe/resume-on-detach.cfg", _resume_on_detach(pack_model))
        for rel, text in _vscode_files(pack_model).items():
            write(rel, text)
    write("config/OVERRIDES.md", _OVERRIDES.substitute(cfg))
    write(f"config/{cfg['config_header']}", _CONFIG_H.substitute(cfg))

    if lang in ("c", "cpp"):
        ext = "c"  # cpp shares the c template set; flag delta lives in context
        sections: list[str] = []
        rows: list[str] = []
        for core in pack_model.cores:  # dual-core via iteration, no fork
            ctx = core_context(pack_model, core, lang)
            sections.append(_MAKEFILE_CORE.substitute(ctx))
            rows.append(f"- `{core.name}`: `{ctx['startup_s']}`")
            write(f"src/main-{core.name}.{ext}", _MAIN_C.substitute(ctx))
            flash_region = _core_region(pack_model, core.name, "flash", pack_model.memory[0].name.upper())
            ram_region = _core_region(pack_model, core.name, "ram", pack_model.memory[0].name.upper())
            write(
                f"linker/{ctx['linker_script']}",
                _LINKER.substitute(
                    project=ctx["project"],
                    core=ctx["core"],
                    arch=ctx["arch"],
                    regions=_ld_regions(pack_model, core.name),
                    flash_region=flash_region,
                    ram_region=ram_region,
                ),
            )
        head_ctx = core_context(pack_model, pack_model.cores[0], lang)
        write("Makefile", _MAKEFILE_HEAD.substitute(head_ctx) + "\n".join(sections) + _MAKEFILE_FOOT.substitute(
            build_targets=" ".join(f"build-{c.name}" for c in pack_model.cores),
            flash_targets=" ".join(f"flash-{c.name}" for c in pack_model.cores),
            clean_targets=" ".join(f"clean-{c.name}" for c in pack_model.cores),
        ))
        write("Startup/NOTE.md", _STARTUP_NOTE.substitute(project=pack_model.id, rows="\n".join(rows) + "\n"))
        # Pinned CMSIS submodules for C/C++ only (strict: VendorError
        # propagates so `create` fails loud with no partial tree — spec
        # "No network means clear error"; Rust carries no vendor tree).
        vendor(pack_model.id, out)
    else:  # rust: single tree, memory.x covers every region
        arch = pack_model.cores[0].arch
        write(
            "Cargo.toml",
            _CARGO.substitute(
                project=pack_model.id,
                arch=arch,
                rust_version=RUST_VERSION,
                pin_cortex_m=RUST_PINS["cortex-m"],
                pin_cortex_m_rt=RUST_PINS["cortex-m-rt"],
                pin_panic_halt=RUST_PINS["panic-halt"],
                flip_link=FLIP_LINK_PIN,
            ),
        )
        write("memory.x", _MEMORY_X.substitute(project=pack_model.id, regions=_memoryx_regions(pack_model)))
        write(
            "build.rs",
            _BUILD_RS.substitute(project=pack_model.id, config_header=cfg["config_header"], rust_cfg=cfg["rust_cfg"]),
        )
        write(
            "src/main.rs",
            _MAIN_RS.substitute(project=pack_model.id, arch=arch, config_header=cfg["config_header"]),
        )

    return sorted(written)
