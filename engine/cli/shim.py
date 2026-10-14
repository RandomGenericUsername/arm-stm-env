"""Shim helpers (req-005, groups 1-2; task-003 container fix): language ->
image, container argv, per-OS probe mapping.

``build_container_argv`` is the single place that turns a verb invocation
into the exact container command. ``--dry-run`` prints it without touching
the container runtime, so it works with no runtime installed.

Container contract (task-003, narrowed task-004): images ship toolchains only — no ``mu``,
no engine. So the container side runs ``python3 -m engine`` with exactly two
read-only mounts — the ``engine`` package and ``packs/`` — plus the project
read-write at ``/project`` (working dir). Container paths mirror the checkout
layout (``/opt/mu/{engine,packs}``) so ``__file__``-derived resolution
works unchanged. The project mount uses an absolute host path (relative paths
are invalid for the runtime).

Probe binding (shim only): selectors resolve to a ``ProbeBinding`` — a backend
selector plus the host device nodes to forward. Linux passes each host device as
``--device <node>:<node>`` (the USB node for a USB probe); macOS (Docker Desktop)
cannot forward USB nodes, so none are emitted there — run with ``--mode local``
on macOS. Explicit ``--device`` always wins over VID/PID/serial selectors.
"""

from __future__ import annotations

import shlex
from dataclasses import dataclass
from pathlib import Path

import engine
from engine.adapters import DefaultImageLookup, ImageLookup
from engine.core.model import Endpoint

__all__ = [
    "ProbeBinding",
    "ShimRequest",
    "build_container_argv",
    "engine_root",
    "format_argv",
    "interactive_args",
    "probe_endpoint",
    "repo_root",
    "resolve_probe_binding",
]

MODES = ("auto", "local")

#: Container path of the read-only repo mount (engine + packs resolve under it).
CONTAINER_REPO = "/opt/mu"

#: Container path of the read-write project mount (also the working dir).
CONTAINER_PROJECT = "/project"

#: Default sysfs root for USB device enumeration (overridable in tests).
_SYSFS_USB = Path("/sys/bus/usb/devices")

#: Debug-probe USB vendor IDs (host/probe knowledge — the shim is the host
#: layer, AD-9). STMicroelectronics probes all share 0483 (ST-Link V2-1,
#: STLINK-V3). Used only to auto-detect a *single* attached probe when no
#: selector is given (req-020).
_PROBE_VIDS = ("0483",)


@dataclass(frozen=True)
class ShimRequest:
    verb: str
    lang: str = "c"
    mode: str = "auto"
    project_dir: str = "."
    extra: tuple[str, ...] = ()
    device: str | None = None
    vid: str | None = None
    pid: str | None = None
    serial: str | None = None
    os_name: str = "linux"
    interactive: bool = False
    mcu_config: str | None = None


def engine_root() -> Path:
    """Directory containing the ``engine`` package (source checkout)."""
    return Path(engine.__file__).resolve().parent


def repo_root() -> Path:
    """Checkout root: parent of the ``engine`` package directory."""
    return engine_root().parent


def packs_dir() -> Path:
    """Shipped packs directory (single source; ``main.PACKS_DIR`` aliases this)."""
    return repo_root() / "packs"


@dataclass(frozen=True)
class ProbeBinding:
    """Resolved probe: backend selector + host device nodes for the container.

    ``selector`` is what a backend uses to pick the probe (USB serial or
    ``VID:PID``); ``host_devices`` are the host paths the container must be
    given (the USB device node) so a USB probe is reachable through libusb.
    """

    selector: str
    host_devices: tuple[str, ...] = ()


def _read_text(path: Path) -> str:
    try:
        return path.read_text().strip()
    except OSError:
        return ""


def _usb_device_node(entry: Path) -> str | None:
    """``/dev/bus/usb/<bus>/<dev>`` for a sysfs USB device dir, if resolvable."""
    bus, dev = _read_text(entry / "busnum"), _read_text(entry / "devnum")
    if bus.isdigit() and dev.isdigit():
        return f"/dev/bus/usb/{int(bus):03d}/{int(dev):03d}"
    return None


def _match_usb(sysfs_root: Path, vid: str | None, pid: str | None, serial: str | None):
    """First sysfs USB device matching the selectors: ``(entry, vid, pid, serial)`` or ``None``."""
    if not sysfs_root.is_dir():
        return None
    for entry in sorted(sysfs_root.iterdir()):
        if not (entry / "idVendor").is_file():
            continue  # interfaces (e.g. "3-9:1.0") carry no idVendor
        v = _read_text(entry / "idVendor").lower()
        p = _read_text(entry / "idProduct").lower()
        s = _read_text(entry / "serial")
        if vid and v != vid.lower():
            continue
        if pid and p != pid.lower():
            continue
        if serial and s != serial:
            continue
        return entry, v, p, s
    return None


def _autodetect(*, is_mac: bool, sysfs_root: Path | str | None) -> ProbeBinding | None:
    """Binding for the single attached probe, or ``None`` when none is attached.

    Raises when more than one probe is attached (ambiguous — the caller must
    pass a selector).
    """
    root = Path(sysfs_root) if sysfs_root else _SYSFS_USB
    found = []
    if root.is_dir():
        for entry in sorted(root.iterdir()):
            if (entry / "idVendor").is_file() and _read_text(entry / "idVendor").lower() in _PROBE_VIDS:
                found.append(entry)
    if not found:
        return None
    if len(found) > 1:
        desc = ", ".join(
            f"{_read_text(e / 'idVendor')}:{_read_text(e / 'idProduct')}"
            f"({_read_text(e / 'serial') or 'no serial'})"
            for e in found
        )
        raise ValueError(
            f"{len(found)} probes attached ({desc}); pass --serial or --vid/--pid to select one"
        )
    entry = found[0]
    v = _read_text(entry / "idVendor").lower()
    p = _read_text(entry / "idProduct").lower()
    s = _read_text(entry / "serial")
    node = _usb_device_node(entry)
    host = () if is_mac else ((node,) if node else ())
    return ProbeBinding(selector=s or f"{v}:{p}", host_devices=host)


def resolve_probe_binding(
    *,
    os_name: str,
    device: str | None = None,
    vid: str | None = None,
    pid: str | None = None,
    serial: str | None = None,
    sysfs_root: Path | str | None = None,
) -> ProbeBinding | None:
    """Resolve a probe selector to a binding (shim only).

    Explicit ``device`` wins and is used verbatim as both the selector and the
    host device. VID/PID/serial selectors enumerate sysfs to find the USB device
    and derive its ``/dev/bus/usb/<bus>/<dev>`` node; the backend selector is
    the device serial when present, else ``VID:PID``. With **no selector**, a
    single attached probe is auto-detected (``None`` when none is attached; a
    ``ValueError`` when several are). macOS (Docker Desktop) cannot forward USB
    nodes, so ``host_devices`` is empty there (use ``--mode local``).
    """
    is_mac = os_name.lower().startswith(("darwin", "mac"))
    if device:
        return ProbeBinding(selector=device, host_devices=() if is_mac else (device,))
    if not (vid or pid or serial):
        return _autodetect(is_mac=is_mac, sysfs_root=sysfs_root)
    if is_mac and not serial:
        raise ValueError(
            "macOS probe limit: automatic VID/PID mapping unsupported; "
            "pass --device /dev/(cu|tty).usb* explicitly or use --mode local"
        )
    root = Path(sysfs_root) if sysfs_root else _SYSFS_USB
    match = _match_usb(root, vid, pid, serial)
    if match is None:
        # No sysfs match (unplugged/unknown): keep a usable selector so the
        # backend single-probe default still applies; nothing to forward.
        selector = serial or (f"{vid}:{pid}" if vid and pid else (vid or pid or "probe"))
        return ProbeBinding(selector=selector, host_devices=())
    entry, v, p, s = match
    selector = s or f"{v}:{p}"
    node = _usb_device_node(entry)
    host = () if is_mac else ((node,) if node else ())
    return ProbeBinding(selector=selector, host_devices=host)


def probe_endpoint(
    *,
    os_name: str,
    device: str | None = None,
    vid: str | None = None,
    pid: str | None = None,
    serial: str | None = None,
    sysfs_root: Path | str | None = None,
) -> Endpoint | None:
    """Prepare the endpoint struct handed to core/adapters (shim only).

    ``address`` carries the backend selector (serial / ``VID:PID`` / explicit
    device), never a synthesized serial path for a USB probe.
    """
    binding = resolve_probe_binding(
        os_name=os_name,
        device=device,
        vid=vid,
        pid=pid,
        serial=serial,
        sysfs_root=sysfs_root,
    )
    if binding is None:
        return None
    return Endpoint(transport="probe", address=binding.selector)


def build_container_argv(
    request: ShimRequest, *, lookup: ImageLookup | None = None
) -> list[str]:
    """Return the exact ``docker run`` argv for ``request``.

    The image carries toolchains only, so the container side runs the engine
    from the read-only repo mount: ``python3 -m engine <verb> ... --mode
    local`` with ``--project-dir /project``. The probe binding resolves on the
    host: its USB device node(s) become docker ``--device`` flags, and the
    selector forwards into the container as ``--device`` (pack ids resolve via
    the mounted repo; ``--mcu-config`` files must live under the project —
    enforced by the caller).
    ``local`` mode executes in-process and never builds argv: it raises
    :class:`ValueError`. Unknown mode/lang raises :class:`ValueError`.
    """
    if request.mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}, got {request.mode!r}")
    if request.mode == "local":
        raise ValueError("local mode executes in-process; no container argv exists")
    if not request.verb:
        raise ValueError("verb must be non-empty")
    image = (lookup or DefaultImageLookup()).image_for(request.lang)
    project_abs = Path(request.project_dir).resolve()
    binding = resolve_probe_binding(
        os_name=request.os_name,
        device=request.device,
        vid=request.vid,
        pid=request.pid,
        serial=request.serial,
    )
    docker_devices: list[str] = []
    if binding is not None:
        for node in binding.host_devices:
            docker_devices += ["--device", f"{node}:{node}"]
    inner: list[str] = ["python3", "-m", "engine"]
    if request.verb == "dev":
        inner = ["/bin/bash"]
    else:
        inner += [request.verb, "--lang", request.lang, "--mode", "local"]
        inner += ["--project-dir", CONTAINER_PROJECT]
        if request.mcu_config is not None:
            inner += ["--mcu-config", request.mcu_config]
        if binding is not None:
            inner += ["--device", binding.selector]
        inner += list(request.extra)
    return [
        "docker",
        "run",
        "--rm",
        *interactive_args(request),
        *docker_devices,
        "-v",
        f"{project_abs}:{CONTAINER_PROJECT}:rw",
        "-v",
        f"{engine_root()}:{CONTAINER_REPO}/engine:ro",
        "-v",
        f"{packs_dir()}:{CONTAINER_REPO}/packs:ro",
        "-e",
        "PYTHONPATH=/opt/mu",
        "-w",
        CONTAINER_PROJECT,
        image,
        *inner,
    ]


def interactive_args(request: ShimRequest) -> list[str]:
    """``-it`` exactly when the verb needs an interactive terminal."""
    return ["-it"] if request.interactive else []


def format_argv(argv: list[str]) -> str:
    """Shell-quoted rendering of argv for ``--dry-run`` output."""
    return shlex.join(argv)
