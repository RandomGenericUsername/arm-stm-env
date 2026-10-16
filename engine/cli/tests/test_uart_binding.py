"""UART tty probe-binding tests (task-017, AD-9).

A USB-UART bridge is reached through a **tty** node (major 188) that the
container's private ``/dev`` lacks, so it must be forwarded — unlike a libusb
probe, which is reached through the USB bus (major 189).
"""

from engine.cli.shim import (
    ShimRequest,
    build_container_argv,
    probe_endpoint,
    resolve_probe_binding,
)


def _usb_uart(tmp_path, *, vid="1a86", pid="7523", serial="BR-1", tty="ttyUSB0",
              bus="3", dev="9"):
    """A fake sysfs USB device, optionally with a bound tty interface."""
    root = tmp_path / "usb"
    device = root / f"{bus}-{dev}"
    device.mkdir(parents=True)
    (device / "idVendor").write_text(vid + "\n")
    (device / "idProduct").write_text(pid + "\n")
    (device / "serial").write_text(serial + "\n")
    (device / "busnum").write_text(bus + "\n")
    (device / "devnum").write_text(dev + "\n")
    if tty:
        # In sysfs the interface is a SIBLING of the device dir.
        (root / f"{bus}-{dev}:1.0" / tty / "tty" / tty).mkdir(parents=True)
    return root


def test_uart_transport_binds_the_tty(tmp_path):
    root = _usb_uart(tmp_path)
    binding = resolve_probe_binding(
        os_name="linux", vid="1a86", pid="7523", sysfs_root=root,
        transport="uart-serial",
    )
    assert binding.selector == "/dev/ttyUSB0"          # what the backend's --port needs
    assert binding.host_devices == ("/dev/ttyUSB0",)   # what docker must forward
    assert binding.serial == "BR-1"


def test_probe_endpoint_address_is_the_tty_for_uart(tmp_path):
    root = _usb_uart(tmp_path)
    endpoint = probe_endpoint(
        os_name="linux", vid="1a86", pid="7523", sysfs_root=root,
        transport="uart-serial",
    )
    assert endpoint is not None and endpoint.address == "/dev/ttyUSB0"


def test_autodetect_also_resolves_the_tty(tmp_path):
    root = _usb_uart(tmp_path)
    binding = resolve_probe_binding(os_name="linux", sysfs_root=root, transport="uart-serial")
    assert binding.selector == "/dev/ttyUSB0"
    assert binding.host_devices == ("/dev/ttyUSB0",)


def test_non_uart_transport_keeps_the_usb_node(tmp_path):
    root = _usb_uart(tmp_path, vid="0483", pid="3752")
    binding = resolve_probe_binding(
        os_name="linux", vid="0483", pid="3752", sysfs_root=root, transport="stlink",
    )
    assert binding.host_devices == ("/dev/bus/usb/003/009",)


def test_uart_without_a_bound_tty_falls_back_to_the_usb_node(tmp_path):
    root = _usb_uart(tmp_path, tty=None)
    binding = resolve_probe_binding(
        os_name="linux", vid="1a86", pid="7523", sysfs_root=root,
        transport="uart-serial",
    )
    assert binding.host_devices == ("/dev/bus/usb/003/009",)


def test_container_argv_forwards_the_tty(monkeypatch, tmp_path):
    root = _usb_uart(tmp_path)
    monkeypatch.setattr("engine.cli.shim._SYSFS_USB", root)
    argv = build_container_argv(
        ShimRequest(verb="flash", stack="idf-cmake", vid="1a86", pid="7523",
                    os_name="linux", probe_transport="uart-serial")
    )
    joined = " ".join(argv)
    assert "/dev/ttyUSB0:/dev/ttyUSB0" in joined
    assert "--device" in argv
    assert "/dev/bus/usb" not in joined          # not the libusb bus path
    assert "MU_PROBE_SERIAL=BR-1" in argv
    assert "--device /dev/ttyUSB0" in " ".join(argv)
    # the in-container engine is told the same port
    assert argv[argv.index("--device", argv.index("python3")) + 1] == "/dev/ttyUSB0"


def test_container_argv_for_a_libusb_probe_still_uses_the_bus(monkeypatch, tmp_path):
    root = _usb_uart(tmp_path, vid="0483", pid="3752")
    monkeypatch.setattr("engine.cli.shim._SYSFS_USB", root)
    argv = build_container_argv(
        ShimRequest(verb="flash", stack="make-cmsis", vid="0483", pid="3752",
                    os_name="linux", probe_transport="stlink")
    )
    joined = " ".join(argv)
    assert "/dev/bus/usb:/dev/bus/usb" in joined
    assert "c 189:* rmw" in joined
    assert "/dev/ttyUSB0" not in joined
