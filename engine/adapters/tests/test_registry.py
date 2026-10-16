"""Backend registry tests (task-003): CLI-visible selection without backend literals."""

import pytest

from engine.adapters import (
    ProbeAdapter,
    default_backend_name,
    get_adapter,
    register_backend,
)


def test_registry_default_resolves_without_naming_backend():
    adapter = get_adapter()
    assert isinstance(adapter, ProbeAdapter)
    assert default_backend_name() == "openocd"


def test_registry_probe_rs_resolves():
    assert isinstance(get_adapter("probe-rs"), ProbeAdapter)


def test_registry_unknown_backend_is_usage_error():
    with pytest.raises(ValueError, match="unknown probe backend"):
        get_adapter("nope")


def test_registry_custom_registration():
    class _Fake(ProbeAdapter):
        def render_argv(self, device, endpoint, pieces):
            return ["fake", *pieces]

        def flash(self, device, endpoint, pieces):
            return ()

        def proof_for(self, device, results, transcript):
            from engine.core.model import ProofResult

            return ProofResult(rung=device.proof_rung, payload={})

        def debug(self, device, endpoint):
            from engine.adapters import DebugHandle

            return DebugHandle(session_id="fake", endpoint=endpoint)

    register_backend("fake-test-only", _Fake)
    assert isinstance(get_adapter("fake-test-only"), _Fake)
