"""Pack-schema tests (req-004 group 1): family-block validators + frame fields."""

import pytest

import engine.core.registry as registry
from engine.core.loader import FrameError, load_text, validate_frame
from engine.core.registry import UnknownBlockError


def _validate(block_name, payload, *, family="stm32f4"):
    """Validate a block for the STM32F4 family (the common test case)."""
    registry.validate_block(block_name, payload, family=family)


STARTER_FAMILY = "stm32f4"

BASE = {
    "id": "stm32f411re",
    "version": "1.0.0",
    "family": STARTER_FAMILY,
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
        assert block in registry.registered_blocks(family="stm32f4")


def test_openocd_accepts_board_or_target_shapes():
    _validate("openocd", {"interface": "stlink.cfg", "board": "st_nucleo_f4"})
    _validate(
        "openocd",
        {"interface": "stlink.cfg", "target": "stm32wlx.cfg", "dual_core": True},
    )


def test_openocd_rejects_bad_shapes():
    with pytest.raises(ValueError, match="interface"):
        _validate("openocd", {"board": "x"})
    with pytest.raises(ValueError, match="board.*target"):
        _validate("openocd", {"interface": "stlink.cfg"})
    with pytest.raises(ValueError, match="dual_core"):
        _validate(
            "openocd", {"interface": "stlink.cfg", "target": "t.cfg", "dual_core": "yes"}
        )


def test_fpu_accepts_mode_variant():
    _validate("fpu", {"mode": "hard", "variant": "fpv4-sp-d16"})


def test_fpu_rejects_bad_shapes():
    with pytest.raises(ValueError, match="mode"):
        _validate("fpu", {"variant": "fpv4-sp-d16"})
    with pytest.raises(ValueError, match="variant"):
        _validate("fpu", {"mode": "hard"})
    with pytest.raises(ValueError, match="mode"):
        _validate("fpu", {"mode": "turbo", "variant": "fpv4-sp-d16"})


def test_linker_accepts_per_core_names():
    _validate("linker", {"M7": "stm32h755_m7.ld", "M4": "stm32h755_m4.ld"})


def test_linker_rejects_bad_shapes():
    with pytest.raises(ValueError, match="linker"):
        _validate("linker", {})
    with pytest.raises(ValueError, match="M4"):
        _validate("linker", {"M4": ""})


def test_config_headers_accepts_library_shape():
    _validate(
        "config_headers",
        {"library": "stm32hal", "header": "stm32_config.h", "defaults_source": "pack/defaults.h"},
    )


def test_config_headers_rejects_bad_shapes():
    with pytest.raises(ValueError, match="header"):
        _validate(
            "config_headers", {"library": "stm32hal", "defaults_source": "pack/defaults.h"}
        )
    with pytest.raises(ValueError, match="config_headers"):
        _validate("config_headers", "not-a-mapping")


def test_unknown_blocks_still_fail_closed():
    with pytest.raises(UnknownBlockError, match="mystery_block"):
        _validate("mystery_block", {"a": 1})


def test_full_pack_with_all_family_blocks_loads():
    text = """\
id: stm32wl55jc
version: '1.0.0'
family: stm32wl
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
    "missing", ["id", "version", "family", "cores", "memory", "probe", "proof_rung"]
)
def test_frame_missing_field_rejects_naming_it(missing):
    with pytest.raises(FrameError, match=missing):
        validate_frame(_doc_without(missing))


def test_frame_missing_version_rejects():
    doc = {k: v for k, v in BASE.items() if k != "version"}
    with pytest.raises(FrameError, match="version"):
        validate_frame(doc)


def test_probe_settings_accepts_backend_map():
    _validate("probe_settings", {"probe-rs": {"chip": "SOME-CHIP"}})


def test_probe_settings_rejects_bad_shapes():
    from engine.core import registry as _r

    with pytest.raises(ValueError, match="probe_settings"):
        _validate("probe_settings", "not-a-mapping")
    with pytest.raises(ValueError, match="probe_settings"):
        _validate("probe_settings", {"probe-rs": "not-a-mapping"})
    with pytest.raises(ValueError, match="probe_settings"):
        _validate("probe_settings", {"probe-rs": {"chip": ""}})


def test_startup_accepts_per_core_files():
    _validate("startup", {"M4": "startup_stm32f411xe.s"})


def test_startup_rejects_bad_shapes():
    import pytest as _pytest

    with _pytest.raises(ValueError, match="startup"):
        _validate("startup", "not-a-mapping")
    with _pytest.raises(ValueError, match="startup"):
        _validate("startup", {"M4": ""})


def test_system_accepts_per_core_files():
    _validate("system", {"M4": "system_stm32f4xx.c"})


def test_system_rejects_bad_shapes():
    import pytest as _pytest

    with _pytest.raises(ValueError, match="system"):
        _validate("system", "not-a-mapping")
    with _pytest.raises(ValueError, match="system"):
        _validate("system", {"M4": ""})


def test_defines_accepts_per_core_macros():
    _validate("defines", {"M4": "STM32F411xE"})


def test_defines_rejects_bad_shapes():
    import pytest as _pytest

    with _pytest.raises(ValueError, match="defines"):
        _validate("defines", "not-a-mapping")
    with _pytest.raises(ValueError, match="defines"):
        _validate("defines", {"M4": ""})


# --- 1.3 family qualification (task-008, AD-13) ---


def test_block_registered_for_another_family_is_rejected():
    from engine.core import registry as _r

    _r.register("test_only_block", lambda payload: None, families=("testfam",))
    _r.validate_block("test_only_block", {}, family="testfam")  # its own family: ok
    with pytest.raises(UnknownBlockError, match="test_only_block"):
        _r.validate_block("test_only_block", {}, family="stm32f4")


def test_re_registering_same_validator_is_idempotent():
    from engine.core import registry as _r

    _r.register("test_dup_block", lambda payload: None, families=("testdup",))
    _r.register("test_dup_block", _r.get("testdup", "test_dup_block"), families=("testdup",))


def test_same_family_block_cannot_take_a_second_validator():
    from engine.core import registry as _r

    _r.register("test_clash_block", lambda payload: None, families=("testclash",))
    with pytest.raises(_r.FamilyCollisionError):
        _r.register("test_clash_block", lambda payload: None, families=("testclash",))
