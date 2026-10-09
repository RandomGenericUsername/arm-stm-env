"""OpenOCD probe backend (req-006, groups 1.1-1.2): model-only rendering.

Argv is built strictly from certified model fields (interface/target/
dual-core flag via :class:`engine.core.model.DeviceView` + endpoint
address from the shim) — no board or chip names appear in this module.

Subprocess boundary: :class:`OpenOCDAdapter` shells the ``openocd``
binary through an injectable runner seam (a ``Callable[[argv],
Transcript]``). Tests inject fakes; production passes
:func:`subprocess_runner` (real ``subprocess``). No binary is required
at test time.

Transcript fixtures below are authored from documented output formats
(OpenOCD User's Guide: ``** Verified OK **`` programming lines,
``Info : <target> examined`` session lines) — they are marked
FIXTURE and are never live-probe claims. Live runs stay OPEN.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from typing import Callable, Sequence

from engine.adapters import DebugHandle, PieceResult, ProbeAdapter
from engine.core.model import DeviceView, Endpoint, ProofResult

__all__ = [
    "DUAL_CORE_FIXTURE",
    "OpenOCDAdapter",
    "Runner",
    "Transcript",
    "VERIFY_OK_FIXTURE",
    "parse_transcript",
    "session_names",
    "subprocess_runner",
]

#: Extra ``-c`` command rendered when the model carries DUAL_CORE: lists
#: session targets so each core's session line lands in the transcript.
DUAL_CORE_TCL = "targets"

#: OpenOCD flash-programming success line (User's Guide format).
_VERIFY_OK_RE = re.compile(r"\*\* Verified OK \*\*")

#: OpenOCD session line format: ``Info : <name> examined``.
_SESSION_RE = re.compile(r"^Info\s*:\s*(\S+)\s+examined", re.MULTILINE)


@dataclass(frozen=True)
class Transcript:
    """Captured tool run: argv + exit code + text streams."""

    argv: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str = ""


#: Runner seam: argv in, transcript out. Fake in tests, subprocess in prod.
Runner = Callable[[Sequence[str]], Transcript]


def subprocess_runner(argv: Sequence[str]) -> Transcript:
    """Production runner: exec argv via ``subprocess``, capture output."""
    completed = subprocess.run(list(argv), capture_output=True, text=True)
    return Transcript(
        argv=tuple(argv),
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


# --- FIXTURE (not a live run): single-core verify-OK transcript. --------
# Format per OpenOCD User's Guide ("** Programming Started **" /
# "** Verified OK **" flash programming lines).
VERIFY_OK_FIXTURE = """\
Open On-Chip Debugger
** Programming Started **
** Programming Finished **
** Verified OK **
shutdown command invoked
"""

# --- FIXTURE (not a live run): dual-core session transcript. ------------
# Session lines per OpenOCD "Info : <target> examined" format, one
# "** Verified OK **" programming line per core session.
DUAL_CORE_FIXTURE = """\
Open On-Chip Debugger
Info : core0 examined
Info : core1 examined
** Programming Started **
** Verified OK **
** Programming Started **
** Verified OK **
shutdown command invoked
"""


def session_names(transcript: Transcript) -> tuple[str, ...]:
    """Target names from ``Info : <name> examined`` session lines, in order."""
    return tuple(_SESSION_RE.findall(transcript.stdout))


def parse_transcript(
    pieces: Sequence[str], transcript: Transcript
) -> tuple[PieceResult, ...]:
    """Map one transcript to per-piece results, in piece order.

    Piece ``i`` passes iff the run exited 0 and at least ``i+1``
    ``** Verified OK **`` lines are present.
    """
    verified = len(_VERIFY_OK_RE.findall(transcript.stdout))
    results: list[PieceResult] = []
    for index, name in enumerate(pieces):
        ok = transcript.returncode == 0 and index < verified
        if ok:
            detail = "verified-ok"
        elif transcript.returncode != 0:
            detail = f"exit rc={transcript.returncode}"
        else:
            detail = "missing Verified OK line"
        results.append(PieceResult(name=name, ok=ok, detail=detail))
    return tuple(results)


class OpenOCDAdapter(ProbeAdapter):
    """``ProbeAdapter`` via ``openocd -f <interface> -f <target>``."""

    def __init__(self, runner: Runner | None = None) -> None:
        self._runner = runner if runner is not None else subprocess_runner

    def render_argv(
        self,
        device: DeviceView,
        endpoint: Endpoint,
        pieces: Sequence[str],
    ) -> list[str]:
        """Build argv strictly from model fields + shim endpoint.

        ``-f`` files come from the certified openocd block; the endpoint
        address rides a ``-c set`` pass-through; each piece adds a
        ``program <piece> verify reset exit`` step; DUAL_CORE models add
        the session-listing command. Missing openocd facts raise.
        """
        if not device.openocd_interface:
            raise ValueError("device model carries no openocd 'interface' fact")
        if not device.openocd_target:
            raise ValueError("device model carries no openocd board/target fact")
        argv = [
            "openocd",
            "-f",
            device.openocd_interface,
            "-f",
            device.openocd_target,
        ]
        if device.openocd_dual_core:
            argv += ["-c", DUAL_CORE_TCL]
        argv += ["-c", f"set PROBE_ADDRESS {endpoint.address}"]
        for piece in pieces:
            argv += ["-c", f"program {piece} verify reset exit"]
        return argv

    def flash(
        self,
        device: DeviceView,
        endpoint: Endpoint,
        pieces: Sequence[str],
    ) -> Sequence[PieceResult]:
        pieces = tuple(pieces)
        if not pieces:
            return ()
        transcript = self._runner(self.render_argv(device, endpoint, pieces))
        return parse_transcript(pieces, transcript)

    def debug(self, device: DeviceView, endpoint: Endpoint) -> DebugHandle:
        # No live attach here (no probe claim): deterministic handle
        # bound to the shim endpoint; live sessions stay OPEN.
        self.render_argv(device, endpoint, ())
        return DebugHandle(session_id=f"openocd:{endpoint.address}", endpoint=endpoint)

    def proof_for(
        self,
        device: DeviceView,
        results: Sequence[PieceResult],
        transcript: Transcript,
    ) -> ProofResult:
        """Fill the core-owned proof struct for ``device.proof_rung``.

        Payload keys (generic, backend-comparable): ``pieces`` per-piece
        verdicts, ``verified`` ok/total count, ``sessions`` examined
        session names ("" when none).
        """
        results = tuple(results)
        passed = sum(1 for r in results if r.ok)
        payload = {
            "pieces": ",".join(f"{r.name}={'ok' if r.ok else 'fail'}" for r in results),
            "verified": f"{passed}/{len(results)}",
            "sessions": ",".join(session_names(transcript)),
        }
        return ProofResult(rung=device.proof_rung, payload=payload)
