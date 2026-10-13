"""``stm`` entry point (req-005, groups 1-2; task-003 verb wiring): five thin
verbs over argparse.

``create`` renders a project tree locally from a pack (loader + renderer).
``build`` runs the language toolchain locally (``make``/``cargo``);
``flash``/``debug`` resolve the pack + probe endpoint and drive the default
probe backend; ``dev`` spawns an interactive shell. ``--mode auto`` wraps
the same invocation for a container (engine mounted read-only, project
read-write); ``--mode local`` executes in-process — never re-execs ``stm``.
``--dry-run`` prints the exact command without executing (container argv in
``auto``, local toolchain command in ``local``) and needs no runtime.
Verbs carry no device knowledge.
One-source rule: ``--mcu-config`` XOR individual flags (``--mcu``,
``--device``/``--vid``/``--pid``/``--serial``); mixing exits 2.
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from engine.adapters import DefaultImageLookup, ProbeAdapter, get_adapter
from engine.cli.shim import (
    MODES,
    ShimRequest,
    build_container_argv,
    format_argv,
    packs_dir,
    probe_endpoint,
)
from engine.cli.verdict import render_flash_verdict
from engine.core.loader import FrameError, load_file
from engine.core.model import Device, DeviceView, Endpoint
from engine.templates.renderer import SUPPORTED_LANGS, render

__all__ = ["VERBS", "build_parser", "main", "probe_os"]

VERBS = ("create", "dev", "build", "flash", "debug")

INDIVIDUAL_FLAGS = ("mcu", "device", "vid", "pid", "serial")

# Packs shipped with the repo: single-sourced from the shim (container paths
# mirror this layout, so pack ids resolve identically inside and outside).
PACKS_DIR = packs_dir()


def probe_os() -> str:
    """Host OS key for probe mapping: ``linux`` or ``darwin``."""
    sys_name = platform.system().lower()
    if sys_name.startswith("darwin"):
        return "darwin"
    return "linux"


def _add_common(sub: argparse.ArgumentParser) -> None:
    sub.add_argument("--lang", default="c", help="source language (image lookup key)")
    sub.add_argument("--mode", default="auto", choices=MODES, help="exec mode")
    sub.add_argument("--project-dir", default=".", help="project root to mount")
    sub.add_argument(
        "--dry-run",
        action="store_true",
        help="print the exact container argv and exit",
    )
    sub.add_argument("--mcu-config", default=None, help="single-source config file")
    sub.add_argument("--mcu", default=None, help="individual selector (XOR --mcu-config)")


def _add_probe_flags(sub: argparse.ArgumentParser) -> None:
    sub.add_argument("--device", default=None, help="explicit probe device node")
    sub.add_argument("--vid", default=None, help="probe USB vendor id selector")
    sub.add_argument("--pid", default=None, help="probe USB product id selector")
    sub.add_argument("--serial", default=None, help="probe USB serial selector")


def _one_source_violation(args: argparse.Namespace) -> str | None:
    if args.mcu_config is None:
        return None
    mixed = [f"--{name}" for name in INDIVIDUAL_FLAGS if getattr(args, name, None)]
    if mixed:
        return (
            f"--mcu-config cannot be mixed with individual flag(s): "
            f"{', '.join(mixed)} (one source per invocation)"
        )
    return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="stm", description="device-agnostic MCU verbs")
    subs = parser.add_subparsers(dest="verb", required=True, metavar="verb")
    create = subs.add_parser("create", help="scaffold a project tree skeleton")
    create.add_argument("--name", required=True, help="project name")
    create.add_argument("--out-dir", default=".", help="parent dir; project renders to <out-dir>/<name>")
    _add_common(create)
    for verb, help_text in (
        ("dev", "containerized interactive dev env"),
        ("build", "transparent container build"),
        ("flash", "program pieces via the probe port + verdict (default backend)"),
        ("debug", "attach a debug session via the probe port (default backend)"),
    ):
        sub = subs.add_parser(verb, help=help_text)
        _add_common(sub)
        if verb in ("flash", "debug"):
            _add_probe_flags(sub)
        if verb == "flash":
            sub.add_argument(
                "--files",
                nargs="*",
                default=[],
                metavar="ELF",
                help="firmware image(s) to program, in order",
            )
    return parser


def _available_pack_ids() -> list[str]:
    if not PACKS_DIR.is_dir():
        return []
    return sorted(p.stem for p in PACKS_DIR.glob("*.yaml"))


def _resolve_pack(ref: str) -> Device:
    """Load a pack by file path or by shipped pack id."""
    candidate = Path(ref)
    if candidate.is_file():
        return load_file(candidate)
    by_id = PACKS_DIR / (ref[:-5] if ref.endswith(".yaml") else ref)
    by_id = by_id.with_suffix(".yaml")
    if by_id.is_file():
        return load_file(by_id)
    known = _available_pack_ids()
    hint = f" (known packs: {', '.join(known)})" if known else ""
    raise FileNotFoundError(f"unknown pack {ref!r}; not a file and no shipped pack by that id{hint}")


def _run_create(args: argparse.Namespace) -> int:
    if args.mcu_config is None:
        individual = [f"--{name}" for name in INDIVIDUAL_FLAGS if getattr(args, name, None)]
        if individual:
            print(
                "stm: error: the individual-flags path "
                f"({', '.join(individual)}) is not wired yet (follow-up); "
                "pass a single source via --mcu-config <pack-id-or-file>",
                file=sys.stderr,
            )
        else:
            print("stm: error: create requires --mcu-config <pack-id-or-file>", file=sys.stderr)
        return 2
    if args.lang not in SUPPORTED_LANGS:
        print(f"stm: error: unsupported lang {args.lang!r}; expected one of {SUPPORTED_LANGS}", file=sys.stderr)
        return 2
    try:
        device = _resolve_pack(args.mcu_config)
    except FileNotFoundError as exc:
        print(f"stm: error: {exc}", file=sys.stderr)
        return 2
    except (FrameError, ValueError, OSError) as exc:
        print(f"stm: error: invalid pack {args.mcu_config!r}: {exc}", file=sys.stderr)
        return 1
    out = Path(args.out_dir) / args.name
    if args.dry_run:
        print(f"would render {device.id} ({args.lang}) to {out}/")
        print("next: stm build --project-dir " + str(out))
        return 0
    try:
        written = render(device, args.lang, out)
    except ValueError as exc:
        print(f"stm: error: {exc}", file=sys.stderr)
        return 2
    print(f"created {len(written)} files in {out}/")
    for path in written:
        print(f"  {path}")
    print("next steps:")
    print(f"  cd {out} && stm build --project-dir .")
    return 0


def _local_tool_cmd(lang: str) -> list[str]:
    """Toolchain command implementing ``build`` for ``lang`` (local exec)."""
    if lang in ("c", "cpp"):
        return ["make", "build"]
    return ["cargo", "build"]


def _run_tool(cmd: list[str], cwd: str) -> int:
    """Run a toolchain command in ``cwd``; missing tool is exit 1, else passthrough."""
    try:
        completed = subprocess.run(cmd, cwd=cwd)
    except FileNotFoundError:
        print(
            f"stm: error: build tool not found: {cmd[0]} "
            f"(run inside the toolchain image or install it)",
            file=sys.stderr,
        )
        return 1
    return completed.returncode


def _run_build_local(args: argparse.Namespace) -> int:
    cmd = _local_tool_cmd(args.lang)
    if args.dry_run:
        print(f"cd {args.project_dir} && {format_argv(cmd)}")
        return 0
    return _run_tool(cmd, args.project_dir)


def _load_pack_or_exit(ref: str) -> Device | None:
    """Load a pack, printing usage errors; None means the caller already reported."""
    try:
        return _resolve_pack(ref)
    except FileNotFoundError as exc:
        print(f"stm: error: {exc}", file=sys.stderr)
        return None
    except (FrameError, ValueError, OSError) as exc:
        print(f"stm: error: invalid pack {ref!r}: {exc}", file=sys.stderr)
        return None


def _prepare_flash(args: argparse.Namespace) -> tuple[Device, Endpoint, ProbeAdapter] | None:
    """Resolve pack + endpoint for flash/debug; None means already reported."""
    if args.mcu_config is None:
        print("stm: error: this verb requires --mcu-config <pack-id-or-file>", file=sys.stderr)
        return None
    device = _load_pack_or_exit(args.mcu_config)
    if device is None:
        return None
    try:
        endpoint = probe_endpoint(
            os_name=probe_os(),
            device=getattr(args, "device", None),
            vid=getattr(args, "vid", None),
            pid=getattr(args, "pid", None),
            serial=getattr(args, "serial", None),
        )
    except ValueError as exc:
        print(f"stm: error: {exc}", file=sys.stderr)
        return None
    if endpoint is None:
        print(
            "stm: error: no probe selector given; pass --device, --vid/--pid, or --serial",
            file=sys.stderr,
        )
        return None
    return device, endpoint, get_adapter()


def _run_flash_local(args: argparse.Namespace) -> int:
    prepared = _prepare_flash(args)
    if prepared is None:
        return 2
    device, endpoint, adapter = prepared
    if not args.files:
        print("stm: error: flash requires --files <elf...>", file=sys.stderr)
        return 2
    view = DeviceView.of(device)
    if args.dry_run:
        print(format_argv(adapter.render_argv(view, endpoint, args.files)))
        return 0
    try:
        results = adapter.flash(view, endpoint, args.files)
    except FileNotFoundError:
        print("stm: error: probe tool not found (run inside the toolchain image)", file=sys.stderr)
        return 1
    print(render_flash_verdict(results))
    return 0 if all(r.ok for r in results) else 1


def _run_debug_local(args: argparse.Namespace) -> int:
    prepared = _prepare_flash(args)
    if prepared is None:
        return 2
    device, endpoint, adapter = prepared
    view = DeviceView.of(device)
    if args.dry_run:
        print(format_argv(adapter.render_argv(view, endpoint, ())))
        return 0
    handle = adapter.debug(view, endpoint)
    print(f"debug session: {handle.session_id} on {handle.endpoint.address}")
    print("note: live attach stays OPEN (no probe claim); session parameters above are reviewable")
    return 0


def _run_dev_local(args: argparse.Namespace) -> int:
    shell = os.environ.get("SHELL", "/bin/sh")
    if args.dry_run:
        print(shell)
        return 0
    try:
        completed = subprocess.run([shell])
    except FileNotFoundError:
        print(f"stm: error: shell not found: {shell}", file=sys.stderr)
        return 1
    return completed.returncode


def _run_local(args: argparse.Namespace) -> int:
    """Execute the verb in-process (never re-execs ``stm``)."""
    if args.verb == "build":
        return _run_build_local(args)
    if args.verb == "flash":
        return _run_flash_local(args)
    if args.verb == "debug":
        return _run_debug_local(args)
    if args.verb == "dev":
        return _run_dev_local(args)
    raise AssertionError(f"unhandled verb: {args.verb}")


def _mcu_config_outside_project(args: argparse.Namespace) -> str | None:
    """Reject ``--mcu-config`` files the container mount cannot see.

    Pack ids always resolve via the mounted repo; only on-host files outside
    the project mount are unusable in ``auto`` mode (``local`` reads host
    paths directly, so it is exempt).
    """
    ref = args.mcu_config
    if ref is None:
        return None
    candidate = Path(ref)
    if not candidate.is_file():
        return None
    try:
        candidate.resolve().relative_to(Path(args.project_dir).resolve())
    except ValueError:
        return (
            f"--mcu-config file {candidate} is outside --project-dir "
            f"{args.project_dir}; the container mounts only the project — "
            "place the file under the project or pass a pack id"
        )
    return None


def _run_verb(args: argparse.Namespace) -> int:
    try:
        DefaultImageLookup().image_for(args.lang)
    except ValueError as exc:
        print(f"stm: error: {exc}", file=sys.stderr)
        return 2
    violation = _one_source_violation(args)
    if violation is not None:
        build_parser().print_usage(sys.stderr)
        print(f"stm: error: {violation}", file=sys.stderr)
        return 2
    if args.verb == "create":
        return _run_create(args)
    if args.mode == "local":
        return _run_local(args)
    outside = _mcu_config_outside_project(args)
    if outside is not None:
        print(f"stm: error: {outside}", file=sys.stderr)
        return 2
    extra: list[str] = []
    if args.verb == "flash" and getattr(args, "files", None):
        extra = ["--files", *args.files]
    request = ShimRequest(
        verb=args.verb,
        lang=args.lang,
        mode=args.mode,
        project_dir=args.project_dir,
        extra=tuple(extra),
        device=getattr(args, "device", None),
        vid=getattr(args, "vid", None),
        pid=getattr(args, "pid", None),
        serial=getattr(args, "serial", None),
        os_name=probe_os(),
        interactive=(args.verb == "dev"),
        mcu_config=args.mcu_config,
    )
    try:
        argv = build_container_argv(request, lookup=DefaultImageLookup())
    except ValueError as exc:
        print(f"stm: error: {exc}", file=sys.stderr)
        return 2
    if args.dry_run:
        print(format_argv(argv))
        return 0
    if args.mode != "local" and shutil.which("docker") is None:
        print(
            "stm: error: container runtime 'docker' not found; "
            "install it or re-run with --dry-run to review the command",
            file=sys.stderr,
        )
        return 1
    try:
        completed = subprocess.run(argv)
    except FileNotFoundError:
        print(f"stm: error: executable not found: {argv[0]}", file=sys.stderr)
        return 1
    return completed.returncode


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return _run_verb(args)


if __name__ == "__main__":
    raise SystemExit(main())
