"""Registry tests (req-003 group 2.1): register/lookup/reject paths."""

import pytest

import engine.core.registry as registry


def test_register_and_lookup_roundtrip():
    registry.register("demo", lambda payload: None)
    assert registry.get("demo") is not None
    assert "demo" in registry.registered_blocks()


def test_lookup_unknown_names_the_block():
    with pytest.raises(registry.UnknownBlockError, match="nope_block"):
        registry.get("nope_block")


def test_validate_block_unknown_names_the_block():
    with pytest.raises(registry.UnknownBlockError, match="mystery_block"):
        registry.validate_block("mystery_block", {"a": 1})


def test_validate_block_runs_registered_validator():
    seen = []
    registry.register("demo", seen.append)
    registry.validate_block("demo", {"x": 1})
    assert seen == [{"x": 1}]


def test_register_rejects_empty_name_and_non_callable():
    with pytest.raises(ValueError, match="non-empty"):
        registry.register("", lambda p: None)
    with pytest.raises(TypeError, match="callable"):
        registry.register("demo", "not-a-fn")


def test_builtin_openocd_block_registered():
    assert "openocd" in registry.registered_blocks()
    registry.validate_block("openocd", {"interface": "stlink.cfg", "board": "x"})
    with pytest.raises(ValueError, match="interface"):
        registry.validate_block("openocd", {"board": "x"})
