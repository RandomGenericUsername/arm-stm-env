"""CLI test isolation from the host USB bus (bug-019).

``mu flash``/``debug``/``dev`` resolve a probe, and with no selector they
auto-detect from ``/sys/bus/usb/devices``. On a dev machine with two boards
attached that is ambiguous — ``mu: error: 2 probes attached …`` — so every test
that calls ``main([...])`` without a selector failed for reasons unrelated to
the code under test.

Point the shim at a synthetic single-probe sysfs so the CLI suite is
host-independent. Tests that exercise resolution directly pass their own
``sysfs_root`` (or monkeypatch ``_SYSFS_USB`` themselves), which overrides this.
"""

import pytest


@pytest.fixture(autouse=True)
def _isolate_probe_sysfs(tmp_path, monkeypatch):
    root = tmp_path / "sysfs-usb"
    entry = root / "3-1"
    entry.mkdir(parents=True)
    (entry / "idVendor").write_text("0483\n")
    (entry / "idProduct").write_text("3752\n")
    (entry / "busnum").write_text("3\n")
    (entry / "devnum").write_text("9\n")
    (entry / "serial").write_text("TEST-PROBE\n")
    monkeypatch.setattr("engine.cli.shim._SYSFS_USB", root)
