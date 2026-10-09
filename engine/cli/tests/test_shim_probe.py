"""Shim probe mapping + XOR tests (req-005, group 2.2)."""

import pytest

from engine.cli.main import main
from engine.cli.shim import (
    ShimRequest,
    build_container_argv,
    probe_docker_args,
    probe_endpoint,
    resolve_probe_device,
)


def test_shim_probe_linux_device_passthrough():
    node = resolve_probe_device(os_name="linux", device="/dev/ttyUSB0")
    assert node == "/dev/ttyUSB0"
    assert probe_docker_args(os_name="linux", device="/dev/ttyUSB0") == [
        "--device",
        "/dev/ttyUSB0:/dev/ttyUSB0",
    ]


def test_shim_probe_linux_vid_pid_serial_pattern():
    node = resolve_probe_device(os_name="linux", vid="1234", pid="5678")
    assert node == "/dev/serial/by-id/usb-1234_5678"
    node2 = resolve_probe_device(
        os_name="linux", vid="1234", pid="5678", serial="ABC"
    )
    assert node2 == "/dev/serial/by-id/usb-1234_5678_ABC"
    assert probe_docker_args(os_name="linux", vid="1234", pid="5678")[0] == "--device"


def test_shim_probe_explicit_device_wins_over_selectors():
    assert (
        resolve_probe_device(
            os_name="linux", device="/dev/ttyUSB1", vid="1", pid="2"
        )
        == "/dev/ttyUSB1"
    )


def test_shim_probe_macos_documented_limits():
    # macOS: serial maps to cu.* node but emits no --device (Docker Desktop limit).
    node = resolve_probe_device(os_name="darwin", serial="ABC123")
    assert node == "/dev/cu.usbserial-ABC123"
    assert probe_docker_args(os_name="darwin", serial="ABC123") == []
    assert probe_docker_args(os_name="darwin", device="/dev/cu.usbserial-X") == []
    # macOS: bare VID/PID without serial is rejected with a documented hint.
    with pytest.raises(ValueError, match="macOS probe limit"):
        resolve_probe_device(os_name="darwin", vid="1234", pid="5678")


def test_shim_probe_no_selector_gives_no_device_flag():
    assert resolve_probe_device(os_name="linux") is None
    assert probe_docker_args(os_name="linux") == []
    assert probe_endpoint(os_name="linux") is None


def test_shim_probe_endpoint_struct_prepared_in_shim():
    ep = probe_endpoint(os_name="linux", device="/dev/ttyUSB0")
    assert ep is not None and ep.address == "/dev/ttyUSB0"


def test_shim_probe_linux_dry_run_carries_device(capsys, monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Linux")
    assert main(["flash", "--device", "/dev/ttyUSB0", "--dry-run"]) == 0
    assert "--device /dev/ttyUSB0:/dev/ttyUSB0" in capsys.readouterr().out


def test_shim_probe_dry_run_argv_embeds_probe_flag():
    argv = build_container_argv(
        ShimRequest(verb="flash", device="/dev/ttyUSB0", os_name="linux")
    )
    assert "--device" in argv and "/dev/ttyUSB0:/dev/ttyUSB0" in argv
    argv_mac = build_container_argv(
        ShimRequest(verb="flash", device="/dev/cu.usbserial-X", os_name="darwin")
    )
    assert "--device" not in argv_mac


def test_shim_probe_xor_mcu_config_vs_individual_flags(capsys):
    code = main(["build", "--mcu-config", "cfg.yaml", "--mcu", "x", "--dry-run"])
    assert code == 2
    err = capsys.readouterr().err
    assert "usage" in err.lower() and "--mcu-config" in err


def test_shim_probe_xor_mcu_config_vs_probe_flags(capsys):
    code = main(
        ["flash", "--mcu-config", "cfg.yaml", "--device", "/dev/ttyUSB0", "--dry-run"]
    )
    assert code == 2
    assert "--mcu-config" in capsys.readouterr().err


def test_shim_probe_single_source_passes(capsys):
    assert main(["build", "--mcu-config", "cfg.yaml", "--dry-run"]) == 0
    capsys.readouterr()
    assert main(["build", "--mcu", "x", "--dry-run"]) == 0
    capsys.readouterr()
