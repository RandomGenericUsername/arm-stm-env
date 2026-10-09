"""Cache-key + adapter-boundary tests (req-003 group 2.3)."""

import pytest

from engine.core.cache import cache_key


def test_cache_key_stable_for_same_inputs():
    assert cache_key(image_digest="d1", project_hash="p1") == cache_key(
        image_digest="d1", project_hash="p1"
    )


def test_cache_key_digest_change_flips_key():
    before = cache_key(image_digest="d1", project_hash="p1")
    after = cache_key(image_digest="d2", project_hash="p1")
    assert before != after


def test_cache_key_project_change_flips_key():
    assert cache_key(image_digest="d1", project_hash="p1") != cache_key(
        image_digest="d1", project_hash="p2"
    )


def test_cache_key_rejects_empty_inputs():
    with pytest.raises(ValueError, match="image_digest"):
        cache_key(image_digest="", project_hash="p1")
    with pytest.raises(ValueError, match="project_hash"):
        cache_key(image_digest="d1", project_hash="")


def test_boundary_adapters_cannot_reach_loader():
    """Core exposes no loader to adapters: __init__ re-exports nothing loader-like.

    NOTE: engine/core/loader.py exists as a submodule, so `hasattr(pkg,
    "loader")` flips True once imported (Python parent-package attr). The
    enforceable boundary is static: the package __init__ must not re-export
    it, and reader views must carry no loader/path/raw-yaml fields.
    """
    import pathlib

    import engine.core as core

    init_src = pathlib.Path(core.__file__).read_text()
    assert "loader" not in init_src
    assert "safe_load" not in init_src
    # Reader views carry facts only: no loader/path/raw-yaml attributes.
    from engine.core.model import DeviceView

    assert not hasattr(DeviceView, "loader")
    assert not any(a in DeviceView.__dataclass_fields__ for a in ("pack_path", "raw_yaml", "loader"))
