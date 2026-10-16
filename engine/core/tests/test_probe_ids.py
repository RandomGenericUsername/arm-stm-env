"""Probe autodetect id registry tests (task-010, AD-14, AD-9).

The shim owns the per-OS mapping; *which* ids are probes is device truth and
comes from the families, not a hardcoded list in ``engine/cli/``.
"""

import pytest

from engine.core import probe_ids


def test_shipped_families_register_their_probe_vids():
    # ST-Link's vendor id arrives from the STM32 family module, not from cli/.
    assert "0483" in probe_ids.known_probe_vids()


def test_register_is_idempotent_and_conflicts_raise():
    probe_ids.register_probe_vids("tfam", ("beef",))
    assert "beef" in probe_ids.known_probe_vids()
    probe_ids.register_probe_vids("tfam", ("beef",))  # identical: no-op
    with pytest.raises(ValueError, match="already registered"):
        probe_ids.register_probe_vids("tfam", ("dead",))


def test_rejects_empty_and_non_hex_vids():
    with pytest.raises(ValueError):
        probe_ids.register_probe_vids("tfam2", ())
    with pytest.raises(ValueError):
        probe_ids.register_probe_vids("tfam2", ("ZZZZ",))
    with pytest.raises(ValueError):
        probe_ids.register_probe_vids("", ("beef",))
