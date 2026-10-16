"""Operational-envelope tests (task-012, AD-17).

The envelope is the single owner of these facts: changing a constant here must
change the behaviour (that is the difference between "documented" and "owned").
"""

from engine.cli.shim import ShimRequest, build_container_argv
from engine.core import envelope


def test_envelope_documents_the_deferred_lanes():
    doc = envelope.__doc__ or ""
    assert "Windows" in doc
    assert "Docker" in doc
    assert "CONTAINER_PLATFORM" in doc  # the pinned image platform is named


def test_container_argv_runtime_is_the_envelope_constant():
    argv = build_container_argv(
        ShimRequest(verb="build", lang="c", stack="make-cmsis", project_dir=".")
    )
    assert argv[0] == envelope.CONTAINER_RUNTIME


def test_changing_the_envelope_runtime_changes_the_argv(monkeypatch):
    """Ownership: the shim reads the constant, it does not hardcode the binary."""
    monkeypatch.setattr("engine.cli.shim.CONTAINER_RUNTIME", "podman-test")
    argv = build_container_argv(
        ShimRequest(verb="build", lang="c", stack="make-cmsis", project_dir=".")
    )
    assert argv[0] == "podman-test"


def test_usb_passthrough_uses_the_envelope_constants(monkeypatch, tmp_path):
    root = tmp_path / "usb" / "3-9"
    root.mkdir(parents=True)
    (root / "idVendor").write_text("0483\n")
    (root / "idProduct").write_text("3752\n")
    (root / "busnum").write_text("3\n")
    (root / "devnum").write_text("9\n")
    monkeypatch.setattr("engine.cli.shim._SYSFS_USB", tmp_path / "usb")

    argv = build_container_argv(
        ShimRequest(verb="flash", stack="make-cmsis", vid="0483", pid="3752",
                    os_name="linux")
    )
    joined = " ".join(argv)
    assert envelope.USB_CGROUP_RULE in joined
    assert f"{envelope.USB_BUS_ROOT}:{envelope.USB_BUS_ROOT}" in joined
