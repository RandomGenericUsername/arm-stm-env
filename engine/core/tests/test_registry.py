"""Registry tests (req-003 group 2.1): register/lookup/reject paths."""

import pytest

import engine.core.registry as registry


def _vb(block_name, payload, *, family="stm32f4"):
    registry.validate_block(block_name, payload, family=family)


def test_register_and_lookup_roundtrip():
    registry.register("demo", lambda payload: None, families=("testfam",))
    assert registry.get("testfam", "demo") is not None
    assert "demo" in registry.registered_blocks(family="testfam")


def test_lookup_unknown_names_the_block():
    with pytest.raises(registry.UnknownBlockError, match="nope_block"):
        registry.get("stm32f4", "nope_block")


def test_validate_block_unknown_names_the_block():
    with pytest.raises(registry.UnknownBlockError, match="mystery_block"):
        _vb("mystery_block", {"a": 1})


def test_validate_block_runs_registered_validator():
    seen = []
    registry.register("demo_runs", seen.append, families=("testfam",))
    _vb("demo_runs", {"x": 1}, family="testfam")
    assert seen == [{"x": 1}]


def _led(**over):
    base = {
        "port": "A", "pin": 5, "active": "high",
        "gpio_base": 0x40020000, "rcc_en_addr": 0x40023830, "rcc_en_bit": 0,
        "clock_hz": 16000000,
    }
    base.update(over)
    return {"led": base}


def test_example_block_accepts_led_fact():
    _vb("example", _led())
    _vb("example", _led(active="low"))  # active optional/varied


@pytest.mark.parametrize(
    "payload, match",
    [
        (_led(port="AA"), "port"),
        (_led(pin=20), "pin"),
        (_led(pin=True), "pin"),
        (_led(active="yes"), "active"),
        (_led(gpio_base=0), "gpio_base"),
        (_led(rcc_en_addr=0), "rcc_en_addr"),
        (_led(rcc_en_bit=99), "rcc_en_bit"),
        (_led(clock_hz=0), "clock_hz"),
        ({}, "non-empty"),
        ({"led": {}}, "port"),
    ],
)
def test_example_block_rejects_bad(payload, match):
    with pytest.raises(ValueError, match=match):
        _vb("example", payload)


def test_svd_block_validates():
    _vb("svd", {"M4": "stm32f4/STM32F411.svd"})
    with pytest.raises(ValueError, match="path"):
        _vb("svd", {"M4": ""})
    with pytest.raises(ValueError, match="non-empty"):
        _vb("svd", {})


def test_register_rejects_empty_name_and_non_callable():
    with pytest.raises(ValueError, match="non-empty"):
        registry.register("", lambda p: None, families=("testfam",))
    with pytest.raises(TypeError, match="callable"):
        registry.register("demo", "not-a-fn", families=("testfam",))


def test_builtin_openocd_block_registered():
    assert "openocd" in registry.registered_blocks(family="stm32f4")
    _vb("openocd", {"interface": "stlink.cfg", "board": "x"})
    with pytest.raises(ValueError, match="interface"):
        _vb("openocd", {"board": "x"})
