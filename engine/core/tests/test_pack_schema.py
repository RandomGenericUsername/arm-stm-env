"""Pack-schema tests (req-004 group 1): family-block validators + frame fields."""

import pytest

import engine.core.registry as registry
from engine.core.loader import FrameError, load_text, validate_frame
from engine.core.registry import UnknownBlockError

BASE = {
    "id": "stm32f411re",
    "version": "1.0.0",
    "_source_hash": "0" * 64,
    "cores": [{"name": "M4", "arch": "thumbv7em-none-eabihf"}],
    "memory": [{"name": "flash", "origin_hex": "0x08000000", "size": 524288}],
    "probe": {"transport": "stlink", "address": "openocd:stlink"},
    "proof_rung": "rung-1",
    "blocks": {},
}


def _doc_without(key):
    doc = {k: v for k, v in BASE.items() if k != key}
    return doc


# --- 1.1 family-block validators ---


def test_family_blocks_registered_for_stm32():
    for block in ("openocd", "fpu", "linker", "config_headers"):
        assert block in registry.registered_blocks()


def test_openocd_accepts_board_or_target_shapes():
    registry.validate_block("openocd", {"interface": "stlink.cfg", "board": "st_nucleo_f4"})
    registry.validate_block(
        "openocd",
        {"interface": "stlink.cfg", "target": "stm32wlx.cfg", "dual_core": True},
    )


def test_openocd_rejects_bad_shapes():
    with pytest.raises(ValueError, match="interface"):
        registry.validate_block("openocd", {"board": "x"})
    with pytest.raises(ValueError, match="board.*target"):
        registry.validate_block("openocd", {"interface": "stlink.cfg"})
    with pytest.raises(ValueError, match="dual_core"):
        registry.validate_block(
            "openocd", {"interface": "stlink.cfg", "target": "t.cfg", "dual_core": "yes"}
        )


def test_fpu_accepts_mode_variant():
    registry.validate_block("fpu", {"mode": "hard", "variant": "fpv4-sp-d16"})


def test_fpu_rejects_bad_shapes():
    with pytest.raises(ValueError, match="mode"):
        registry.validate_block("fpu", {"variant": "fpv4-sp-d16"})
    with pytest.raises(ValueError, match="variant"):
        registry.validate_block("fpu", {"mode": "hard"})
    with pytest.raises(ValueError, match="mode"):
        registry.validate_block("fpu", {"mode": "turbo", "variant": "fpv4-sp-d16"})


def test_linker_accepts_per_core_names():
    registry.validate_block("linker", {"M7": "stm32h755_m7.ld", "M4": "stm32h755_m4.ld"})


def test_linker_rejects_bad_shapes():
    with pytest.raises(ValueError, match="linker"):
        registry.validate_block("linker", {})
    with pytest.raises(ValueError, match="M4"):
        registry.validate_block("linker", {"M4": ""})


def test_config_headers_accepts_library_shape():
    registry.validate_block(
        "config_headers",
        {"library": "stm32hal", "header": "stm32_config.h", "defaults_source": "pack/defaults.h"},
    )


def test_config_headers_rejects_bad_shapes():
    with pytest.raises(ValueError, match="header"):
        registry.validate_block(
            "config_headers", {"library": "stm32hal", "defaults_source": "pack/defaults.h"}
        )
    with pytest.raises(ValueError, match="config_headers"):
        registry.validate_block("config_headers", "not-a-mapping")


def test_unknown_blocks_still_fail_closed():
    with pytest.raises(UnknownBlockError, match="mystery_block"):
        registry.validate_block("mystery_block", {"a": 1})


def test_full_pack_with_all_family_blocks_loads():
    text = """\
id: stm32wl55jc
version: '1.0.0'
cores:
  - {name: M4, arch: thumbv7em-none-eabihf}
  - {name: M0+, arch: thumbv6m-none-eabi}
memory:
  - {name: flash, origin_hex: '0x08000000', size: 1048576}
probe: {transport: stlink, address: 'openocd:stlink'}
proof_rung: rung-1
blocks:
  openocd: {interface: stlink.cfg, target: stm32wlx.cfg, dual_core: true}
  fpu: {mode: hard, variant: fpv4-sp-d16}
  linker: {M4: stm32wl55jc_m4.ld, M0+: stm32wl55jc_m0plus.ld}
  config_headers: {library: stm32hal, header: stm32_config.h, defaults_source: pack/defaults.h}
"""
    dev = load_text(text)
    assert dev.id == "stm32wl55jc"


# --- 1.2 frame-required-fields enforcement ---


@pytest.mark.parametrize(
    "missing", ["id", "cores", "memory", "probe", "proof_rung"]
)
def test_frame_missing_field_rejects_naming_it(missing):
    with pytest.raises(FrameError, match=missing):
        validate_frame(_doc_without(missing))


def test_frame_missing_version_rejects():
    doc = {k: v for k, v in BASE.items() if k != "version"}
    with pytest.raises(FrameError, match="version"):
        validate_frame(doc)
