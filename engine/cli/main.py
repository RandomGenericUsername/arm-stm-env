"""``stm`` entry point (req-005, groups 1-2): five thin verbs over argparse.

``create`` renders a project tree locally from a pack (loader + renderer);
the other verbs resolve language -> image through the lookup port and exec
the verb in that image. ``--dry-run`` prints the exact container argv without
requiring a container runtime (for ``create``: the render plan, no writes).
Verbs carry no device knowledge.
One-source rule: ``--mcu-config`` XOR individual flags (``--mcu``,
``--device``/``--vid``/``--pid``/``--serial``); mixing exits 2.
"""

from __future__ import annotations

import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from engine.adapters import DefaultImageLookup
from engine.cli.shim import MODES, ShimRequest, build_container_argv, format_argv
from engine.core.loader import FrameError, load_file
from engine.core.model import Device
from engine.templates.renderer import SUPPORTED_LANGS, render

__all__ = ["VERBS", "build_parser", "main", "probe_os"]

VERBS = ("create", "dev", "build", "flash", "debug")

INDIVIDUAL_FLAGS = ("mcu", "device", "vid", "pid", "serial")

# Packs shipped with the repo: <repo-root>/packs/<pack-id>.yaml.
PACKS_DIR = Path(__file__).resolve().parents[2] / "packs"


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
        ("flash", "program pieces via the probe port + verdict"),
        ("debug", "attach a debug session via the probe port"),
    ):
        sub = subs.add_parser(verb, help=help_text)
        _add_common(sub)
        if verb in ("flash", "debug"):
            _add_probe_flags(sub)
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


def _run_verb(args: argparse.Namespace) -> int:
    violation = _one_source_violation(args)
    if violation is not None:
        build_parser().print_usage(sys.stderr)
        print(f"stm: error: {violation}", file=sys.stderr)
        return 2
    if args.verb == "create":
        return _run_create(args)
    extra: list[str] = []
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
