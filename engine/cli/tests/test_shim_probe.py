"""Shim probe binding + XOR tests (req-005 group 2.2; USB binding req-012)."""

import pytest

from engine.cli.main import main
from engine.cli.shim import (
    ProbeBinding,
    ShimRequest,
    build_container_argv,
    probe_endpoint,
    resolve_probe_binding,
)


def _fake_sysfs(tmp_path, *, vid="0483", pid="3752", serial="STL-1", bus="3", dev="9"):
    """One sysfs USB device dir (``/sys/bus/usb/devices/3-9``)."""
    root = tmp_path / "usb"
    d = root / f"{bus}-{dev}"
    d.mkdir(parents=True)
    (d / "idVendor").write_text(vid + "\n")
    (d / "idProduct").write_text(pid + "\n")
    if serial is not None:
        (d / "serial").write_text(serial + "\n")
    (d / "busnum").write_text(bus + "\n")
    (d / "devnum").write_text(dev + "\n")
    return root


def test_binding_explicit_device_linux():
    b = resolve_probe_binding(os_name="linux", device="/dev/ttyUSB0")
    assert b == ProbeBinding(selector="/dev/ttyUSB0", host_devices=("/dev/ttyUSB0",))


def test_binding_vid_pid_resolves_usb_node(tmp_path):
    root = _fake_sysfs(tmp_path)
    b = resolve_probe_binding(os_name="linux", vid="0483", pid="3752", sysfs_root=root)
    assert b is not None
    assert b.selector == "STL-1"  # serial preferred over VID:PID
    assert b.host_devices == ("/dev/bus/usb/003/009",)


def test_binding_vid_pid_without_serial_uses_vid_pid(tmp_path):
    root = _fake_sysfs(tmp_path, serial=None)
    b = resolve_probe_binding(os_name="linux", vid="0483", pid="3752", sysfs_root=root)
    assert b is not None and b.selector == "0483:3752"
    assert b.host_devices == ("/dev/bus/usb/003/009",)


def test_binding_unmatched_vid_pid_has_no_host_devices(tmp_path):
    root = _fake_sysfs(tmp_path)
    b = resolve_probe_binding(os_name="linux", vid="1234", pid="0000", sysfs_root=root)
    assert b is not None and b.host_devices == ()


def test_binding_no_selector_is_none(tmp_path):
    # No probe attached (fixture sysfs empty) -> None.
    empty = tmp_path / "empty"
    empty.mkdir()
    assert resolve_probe_binding(os_name="linux", sysfs_root=empty) is None
    assert probe_endpoint(os_name="linux", sysfs_root=empty) is None


def test_binding_autodetects_single_probe(tmp_path):
    """req-020: no selector + one attached probe -> use it."""
    root = _fake_sysfs(tmp_path)
    b = resolve_probe_binding(os_name="linux", sysfs_root=root)
    assert b is not None
    assert b.selector == "STL-1"
    assert b.host_devices == ("/dev/bus/usb/003/009",)


def test_binding_autodetect_ambiguous_raises(tmp_path):
    root = _fake_sysfs(tmp_path)
    _fake_sysfs(tmp_path, serial="STL-2", bus="3", dev="10")  # second probe
    with pytest.raises(ValueError, match="probes attached"):
        resolve_probe_binding(os_name="linux", sysfs_root=root)


def test_binding_macos_documented_limits():
    # macOS: selector kept, but no docker USB passthrough (Desktop limit).
    assert resolve_probe_binding(os_name="darwin", serial="ABC123") == ProbeBinding(
        selector="ABC123", host_devices=(), serial="ABC123"
    )
    assert resolve_probe_binding(
        os_name="darwin", device="/dev/cu.usbserial-X"
    ).host_devices == ()
    # macOS: bare VID/PID without serial is rejected with a documented hint.
    with pytest.raises(ValueError, match="macOS probe limit"):
        resolve_probe_binding(os_name="darwin", vid="0483", pid="3752")


def test_endpoint_address_is_selector_not_path(tmp_path):
    root = _fake_sysfs(tmp_path)
    ep = probe_endpoint(os_name="linux", vid="0483", pid="3752", sysfs_root=root)
    assert ep is not None and ep.address == "STL-1"


def test_container_argv_forwards_usb_bus(monkeypatch, tmp_path):
    """bug-018: pass the whole USB bus + serial, never a per-node --device."""
    root = _fake_sysfs(tmp_path)
    monkeypatch.setattr("engine.cli.shim._SYSFS_USB", root)
    argv = build_container_argv(
        ShimRequest(verb="flash", vid="0483", pid="3752", os_name="linux")
    )
    joined = " ".join(argv)
    assert "/dev/bus/usb:/dev/bus/usb" in joined
    assert "c 189:* rmw" in joined
    assert "MU_PROBE_SERIAL=STL-1" in argv
    # the stale-prone per-node passthrough is gone
    assert "/dev/bus/usb/003/009:/dev/bus/usb/003/009" not in joined
    assert "--device" in argv and "STL-1" in argv  # selector still forwarded


def test_container_argv_explicit_device(monkeypatch):
    argv = build_container_argv(
        ShimRequest(verb="flash", device="/dev/ttyUSB0", os_name="linux")
    )
    assert "/dev/ttyUSB0:/dev/ttyUSB0" in argv


def test_container_argv_macos_no_usb_passthrough():
    argv = build_container_argv(
        ShimRequest(verb="flash", serial="ABC", os_name="darwin")
    )
    assert "/dev/bus/usb" not in " ".join(argv)
    assert "ABC" in argv  # selector still forwarded for in-container use


def test_shim_probe_linux_dry_run_carries_bus(capsys, monkeypatch, tmp_path):
    root = _fake_sysfs(tmp_path)
    monkeypatch.setattr("engine.cli.shim._SYSFS_USB", root)
    monkeypatch.setattr("platform.system", lambda: "Linux")
    assert main(["flash", "--vid", "0483", "--pid", "3752", "--dry-run"]) == 0
    out = capsys.readouterr().out
    assert "/dev/bus/usb:/dev/bus/usb" in out
    assert "MU_PROBE_SERIAL=STL-1" in out


def test_dev_forwards_probe_bus(capsys, monkeypatch, tmp_path):
    """bug-018: `mu dev` hands the whole USB bus + the probe serial to the container."""
    root = _fake_sysfs(tmp_path)
    monkeypatch.setattr("engine.cli.shim._SYSFS_USB", root)
    monkeypatch.setattr("platform.system", lambda: "Linux")
    assert main(["dev", "--device", "/dev/bus/usb/003/009", "--dry-run"]) == 0
    out = capsys.readouterr().out
    assert "/dev/bus/usb:/dev/bus/usb" in out
    assert "MU_PROBE_SERIAL=STL-1" in out
    assert "/bin/bash" in out


def test_build_verb_carries_no_probe_device(monkeypatch, tmp_path):
    """bug-010: build must not resolve/forward a probe (--device is rejected)."""
    root = _fake_sysfs(tmp_path)
    monkeypatch.setattr("engine.cli.shim._SYSFS_USB", root)
    argv = build_container_argv(ShimRequest(verb="build", os_name="linux"))
    assert "--device" not in argv


def test_flash_verb_autodetects_probe_bus(monkeypatch, tmp_path):
    root = _fake_sysfs(tmp_path)
    monkeypatch.setattr("engine.cli.shim._SYSFS_USB", root)
    argv = build_container_argv(ShimRequest(verb="flash", os_name="linux"))
    assert "/dev/bus/usb:/dev/bus/usb" in " ".join(argv)
    assert "MU_PROBE_SERIAL=STL-1" in argv


def test_shim_probe_xor_mcu_config_vs_individual_flags(capsys):
    code = main(["build", "--mcu-config", "cfg.yaml", "--mcu", "x", "--dry-run"])
    assert code == 2
    err = capsys.readouterr().err
    assert "usage" in err.lower() and "--mcu-config" in err


def test_shim_probe_mcu_config_composes_with_probe_flags(capsys, tmp_path):
    # bug-001: probe selectors are run config, not device description —
    # --mcu-config + --device must compose, not violate XOR.
    proj = tmp_path / "proj"
    proj.mkdir()
    code = main(
        ["flash", "--mcu-config", "cfg.yaml", "--device", "/dev/ttyUSB0",
         "--project-dir", str(proj), "--files", "a.elf", "--dry-run"]
    )
    assert code == 0
    out = capsys.readouterr().out
    assert "--mcu-config cfg.yaml" in out and "--device /dev/ttyUSB0" in out


def test_shim_probe_single_source_passes(capsys):
    assert main(["build", "--mcu-config", "cfg.yaml", "--dry-run"]) == 0
    capsys.readouterr()
    assert main(["build", "--mcu", "x", "--dry-run"]) == 0
    capsys.readouterr()
