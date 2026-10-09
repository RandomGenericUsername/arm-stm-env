"""Project renderer (req-008).

Pack model in -> project tree out. ``string.Template`` substitution only;
per-core contexts are pre-computed here and dual-core packs render by core
iteration, not template forks (design.md). The renderer consumes the
certified model ONLY (``Device.facets`` for fpu/linker/config-headers,
``Device.openocd`` for flash facts) and never re-reads pack YAML.
"""

from __future__ import annotations

import re
from pathlib import Path
from string import Template

from engine.core.model import Core, Device

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


def _oc_cfg_path(device: Device) -> str:
    """Board-vs-target config path from model facts (spike-001)."""
    oc = device.openocd
    if oc is None:
        return "target/stm32f4x.cfg"
    if oc.board:
        return f"board/{oc.board}"
    if "/" in oc.target:
        return oc.target
    return f"target/{oc.target}"


def _oc_flash_args(device: Device) -> str:
    """`openocd -f ...` args for flash-helper targets, from model facts."""
    oc = device.openocd
    if oc is None:
        return "-f interface/stlink.cfg -f target/stm32f4x.cfg"
    args = f"-f interface/{oc.interface} -f {_oc_cfg_path(device)}"
    if oc.dual_core and not oc.board:
        # Target-direct dual sessions (WL55JC) need the flag on the command
        # line; board cfgs (F4/H7) set DUAL_CORE themselves (spike-001).
        args += ' -c "set DUAL_CORE 1"'
    return args


def core_context(device: Device, core: Core, lang: str) -> dict:
    """Per-core substitution context (renderer-computed, template renders)."""
    facets = device.facets
    cpu = CPU_BY_CORE.get(core.name, core.name.lower())
    header = facets.config_header
    guard = re.sub(r"\W", "_", header).upper()
    return {
        "project": device.id,
        "device_id": device.id,
        "version": device.version,
        "core": core.name,
        "arch": core.arch,
        "cpu": cpu,
        "cpu_flags": f"-mcpu={cpu} -mthumb",
        "fpu_flags": _fpu_flags(facets.fpu_mode, facets.fpu_variant),
        "linker_script": facets.linker_for(core.name, device.id),
        "cmsis_include": "vendor/CMSIS/Include",
        "device_include": f"vendor/cmsis-device-{device.id}/Include",
        "startup_s": (
            f"vendor/cmsis-device-{device.id}/Source/Templates/gcc"
            f"/startup_{device.id}_{core.name}.s"
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
    "CMSIS_INC = -Ivendor/CMSIS/Include -I$device_include\n"
    "CONFIG_INC = -Iconfig\n"
    "CONFIG_DEF = -DUSE_$config_guard\n"
    "\n"
)

_MAKEFILE_CORE = Template(
    "# --- core $core ($arch) ---\n"
    "TARGET_$core = $project-$core\n"
    "CPU_FLAGS_$core = $cpu_flags\n"
    "FPU_FLAGS_$core = $fpu_flags\n"
    "CFLAGS_$core = $$(CPU_FLAGS_$core) $$(FPU_FLAGS_$core)$std_flags "
    "$$(CMSIS_INC) $$(CONFIG_INC) $$(CONFIG_DEF) -Os -ffunction-sections -fdata-sections -g3 -Wall\n"
    "LDSCRIPT_$core = linker/$linker_script\n"
    "STARTUP_$core = $startup_s\n"
    "SRCS_$core = src/main-$core.c\n"
    "OBJS_$core = build/$core/main-$core.o build/$core/startup-$core.o\n"
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
    "$$(TARGET_$core).elf: $$(OBJS_$core) $$(LDSCRIPT_$core)\n"
    "\t$compiler $$(CFLAGS_$core) -T$$(LDSCRIPT_$core) -Wl,--gc-sections "
    "-Wl,-Map=build/$core/$$(TARGET_$core).map --specs=nano.specs -o $$@ $$(OBJS_$core)\n"
    "\n"
    "$$(TARGET_$core).hex: $$(TARGET_$core).elf\n"
    "\t$$(OBJCOPY) -O ihex $$< $$@\n"
    "\n"
    "$$(TARGET_$core).bin: $$(TARGET_$core).elf\n"
    "\t$$(OBJCOPY) -O binary $$< $$@\n"
    "\n"
    "build-$core: $$(TARGET_$core).elf $$(TARGET_$core).hex $$(TARGET_$core).bin\n"
    "\t$$(SIZE) $$(TARGET_$core).elf\n"
    "\n"
    "flash-$core: build-$core\n"
    "\t$$(OPENOCD) $oc_flash_args -c \"program $$(TARGET_$core).elf verify reset exit\"\n"
    "\n"
    "clean-$core:\n"
    "\trm -rf build/$core $$(TARGET_$core).elf $$(TARGET_$core).hex $$(TARGET_$core).bin\n"
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
    "\n"
    "#ifndef USE_$config_guard\n"
    '#error "pack config header missing: build with -Iconfig (see config/OVERRIDES.md)"\n'
    "#endif\n"
    "\n"
    "int main(void)\n"
    "{\n"
    "    /* TODO: clock + peripheral init (defaults in config/$config_header). */\n"
    "    for (;;) {\n"
    '        __asm volatile ("wfi");\n'
    "    }\n"
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
    "opt-level = 0\n"
    "debug = true\n"
    "\n"
    "[profile.release]\n"
    'opt-level = "z"\n'
    "codegen-units = 1\n"
    "lto = true\n"
    "debug = true\n"
    "\n"
    "# Flash via probe-rs (single-core) or OpenOCD (see openocd.cfg):\n"
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
    "# $project openocd.cfg — generated from pack openocd facts (spike-001).\n"
    "# Probe: $probe_transport ($probe_address).\n"
    "# Flash helper: openocd $oc_flash_args -c \"program <elf> verify reset exit\"\n"
    "source [find interface/$interface]\n"
    "$dual_line$target_line\n"
)


def _render_openocd(device: Device) -> str:
    oc = device.openocd
    interface = oc.interface if oc else "stlink.cfg"
    dual = bool(oc and oc.dual_core)
    if oc and oc.board:
        target_line = f"source [find board/{oc.board}]"
    elif oc and "/" in oc.target:
        target_line = f"source [find {oc.target}]"
    elif oc:
        target_line = f"source [find target/{oc.target}]"
    else:
        target_line = "source [find target/stm32f4x.cfg]"
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
        target_line=target_line,
    )


def _ld_regions(device: Device) -> str:
    lines = []
    for m in device.memory:
        access = "rx" if "flash" in m.name.lower() else "rwx"
        lines.append(f"  {m.name.upper()} ({access}) : ORIGIN = 0x{m.origin:08X}, LENGTH = {m.size}")
    return "\n".join(lines)


def _first_region(device: Device, want: str, fallback: str) -> str:
    for m in device.memory:
        if want in m.name.lower():
            return m.name.upper()
    return fallback


def _core_region(device: Device, core_name: str, want: str, fallback: str) -> str:
    """Per-core region: prefer a ``want`` region naming the core (M4 ->
    flash_m4 on dual-bank packs), else the first ``want`` region (shared
    single-region packs). Mirrors ``engine.verify.e2e.pick_region``."""
    for m in device.memory:
        if want in m.name.lower() and core_name.lower() in m.name.lower():
            return m.name.upper()
    return _first_region(device, want, fallback)


def _memoryx_regions(device: Device) -> str:
    names = {m.name.upper() for m in device.memory}
    lines = [_ld_regions(device)]
    # cortex-m-rt link.x requires FLASH + RAM: alias the first matching bank
    # when no region carries the exact name (e.g. dual-bank H755).
    if "FLASH" not in names:
        first = _first_region(device, "flash", device.memory[0].name.upper())
        src = next(m for m in device.memory if m.name.upper() == first)
        lines.append(f"  FLASH (rx) : ORIGIN = 0x{src.origin:08X}, LENGTH = {src.size}")
    if "RAM" not in names:
        first = _first_region(device, "ram", device.memory[0].name.upper())
        src = next(m for m in device.memory if m.name.upper() == first)
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


def render(pack_model: Device, lang: str, out_dir: str | Path) -> list[Path]:
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

    write("openocd.cfg", _render_openocd(pack_model))
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
                    regions=_ld_regions(pack_model),
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
