"""Shim helpers (req-005, groups 1-2): language -> image, container argv,
per-OS probe mapping.

``build_container_argv`` is the single place that turns a verb invocation
into the exact container command. ``--dry-run`` prints it without touching
the container runtime, so it works with no runtime installed.

Probe mapping (shim only): Linux passes the resolved node through as
``--device <node>:<node>``; macOS (Docker Desktop) cannot forward USB
nodes, so no ``--device`` flag is emitted there — run with ``--mode local``
on macOS. Explicit ``--device`` always wins over VID/PID/serial selectors.
"""

from __future__ import annotations

import shlex
from dataclasses import dataclass

from engine.adapters import DefaultImageLookup, ImageLookup
from engine.core.model import Endpoint

__all__ = [
    "ShimRequest",
    "build_container_argv",
    "format_argv",
    "probe_docker_args",
    "probe_endpoint",
    "resolve_probe_device",
]

MODES = ("auto", "local")

#: Placeholder used when only part of a VID:PID pair is given.
_UNKNOWN_ID = "0000"


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


def resolve_probe_device(
    *,
    os_name: str,
    device: str | None = None,
    vid: str | None = None,
    pid: str | None = None,
    serial: str | None = None,
) -> str | None:
    """Resolve a probe selector to a device node (shim only).

    Explicit ``device`` always wins. With VID/PID/serial selectors,
    Linux synthesizes a stable ``/dev/serial/by-id/`` node; macOS maps a
    serial to ``/dev/cu.usbserial-<serial>`` and rejects bare VID/PID
    (documented limit: no stable VID/PID -> node mapping on macOS —
    pass ``--device`` explicitly). No selector -> ``None``.
    """
    if device:
        return device
    if not (vid or pid or serial):
        return None
    os_key = os_name.lower()
    if os_key.startswith("darwin") or os_key.startswith("mac"):
        if serial:
            return f"/dev/cu.usbserial-{serial}"
        raise ValueError(
            "macOS probe limit: automatic VID/PID mapping unsupported; "
            "pass --device /dev/(cu|tty).usb* explicitly or use --mode local"
        )
    node = f"usb-{vid or _UNKNOWN_ID}_{pid or _UNKNOWN_ID}"
    if serial:
        node += f"_{serial}"
    return f"/dev/serial/by-id/{node}"


def probe_docker_args(
    *,
    os_name: str,
    device: str | None = None,
    vid: str | None = None,
    pid: str | None = None,
    serial: str | None = None,
) -> list[str]:
    """Return ``docker run`` device flags for a probe selector.

    Linux emits ``["--device", "<node>:<node>"]``; macOS emits ``[]``
    (documented Docker Desktop limit — the endpoint is still prepared
    for ``--mode local`` runs). No selector -> ``[]``.
    """
    node = resolve_probe_device(
        os_name=os_name, device=device, vid=vid, pid=pid, serial=serial
    )
    if node is None:
        return []
    if os_name.lower().startswith(("darwin", "mac")):
        return []
    return ["--device", f"{node}:{node}"]


def probe_endpoint(
    *,
    os_name: str,
    device: str | None = None,
    vid: str | None = None,
    pid: str | None = None,
    serial: str | None = None,
) -> Endpoint | None:
    """Prepare the endpoint struct handed to core/adapters (shim only)."""
    node = resolve_probe_device(
        os_name=os_name, device=device, vid=vid, pid=pid, serial=serial
    )
    if node is None:
        return None
    return Endpoint(transport="probe", address=node)


def build_container_argv(
    request: ShimRequest, *, lookup: ImageLookup | None = None
) -> list[str]:
    """Return the exact argv to exec for ``request``.

    ``auto`` mode wraps the verb in a ``docker run`` of the looked-up image;
    ``local`` mode (inside-container runs) execs the verb directly with the
    same language resolution. Unknown mode/lang raises :class:`ValueError`.
    """
    if request.mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}, got {request.mode!r}")
    if not request.verb:
        raise ValueError("verb must be non-empty")
    image = (lookup or DefaultImageLookup()).image_for(request.lang)
    inner = ["stm", request.verb, "--lang", request.lang, *request.extra]
    if request.mode == "local":
        return inner
    return [
        "docker",
        "run",
        "--rm",
        *probe_docker_args(
            os_name=request.os_name,
            device=request.device,
            vid=request.vid,
            pid=request.pid,
            serial=request.serial,
        ),
        "-v",
        f"{request.project_dir}:/project",
        image,
        *inner,
    ]


def format_argv(argv: list[str]) -> str:
    """Shell-quoted rendering of argv for ``--dry-run`` output."""
    return shlex.join(argv)
