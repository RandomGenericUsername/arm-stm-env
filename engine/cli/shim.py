"""Shim helpers (req-005, groups 1-2; task-003 container fix): language ->
image, container argv, per-OS probe mapping.

``build_container_argv`` is the single place that turns a verb invocation
into the exact container command. ``--dry-run`` prints it without touching
the container runtime, so it works with no runtime installed.

Container contract (task-003, narrowed task-004): images ship toolchains only — no ``stm``,
no engine. So the container side runs ``python3 -m engine`` with exactly two
read-only mounts — the ``engine`` package and ``packs/`` — plus the project
read-write at ``/project`` (working dir). Container paths mirror the checkout
layout (``/opt/arm-stm-env/{engine,packs}``) so ``__file__``-derived resolution
works unchanged. The project mount uses an absolute host path (relative paths
are invalid for the runtime).

Probe mapping (shim only): Linux passes the resolved node through as
``--device <node>:<node>``; macOS (Docker Desktop) cannot forward USB
nodes, so no ``--device`` flag is emitted there — run with ``--mode local``
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
    "ShimRequest",
    "build_container_argv",
    "engine_root",
    "format_argv",
    "interactive_args",
    "probe_docker_args",
    "probe_endpoint",
    "repo_root",
    "resolve_probe_device",
]

MODES = ("auto", "local")

#: Container path of the read-only repo mount (engine + packs resolve under it).
CONTAINER_REPO = "/opt/arm-stm-env"

#: Container path of the read-write project mount (also the working dir).
CONTAINER_PROJECT = "/project"

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
    """Return the exact ``docker run`` argv for ``request``.

    The image carries toolchains only, so the container side runs the engine
    from the read-only repo mount: ``python3 -m engine <verb> ... --mode
    local`` with ``--project-dir /project``. Selectors and ``--mcu-config``
    forward as-is (pack ids resolve via the mounted repo; ``--mcu-config``
    files must live under the project — enforced by the caller).
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
    inner: list[str] = ["python3", "-m", "engine"]
    if request.verb == "dev":
        inner = ["/bin/bash"]
    else:
        inner += [request.verb, "--lang", request.lang, "--mode", "local"]
        inner += ["--project-dir", CONTAINER_PROJECT]
        if request.mcu_config is not None:
            inner += ["--mcu-config", request.mcu_config]
        for flag, value in (
            ("--device", request.device),
            ("--vid", request.vid),
            ("--pid", request.pid),
            ("--serial", request.serial),
        ):
            if value is not None:
                inner += [flag, value]
        inner += list(request.extra)
    return [
        "docker",
        "run",
        "--rm",
        *interactive_args(request),
        *probe_docker_args(
            os_name=request.os_name,
            device=request.device,
            vid=request.vid,
            pid=request.pid,
            serial=request.serial,
        ),
        "-v",
        f"{project_abs}:{CONTAINER_PROJECT}:rw",
        "-v",
        f"{engine_root()}:{CONTAINER_REPO}/engine:ro",
        "-v",
        f"{packs_dir()}:{CONTAINER_REPO}/packs:ro",
        "-e",
        "PYTHONPATH=/opt/arm-stm-env",
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
