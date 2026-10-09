"""probe-rs backend skeleton (req-006, group 2.1): model-only rendering.

``--chip`` renders strictly from the certified model fact ``device.id``
(the pack's own identifier) + endpoint address from the shim — no board
or chip names appear literally in this module. Exact probe-rs registry
chip strings (vendor ``...Tx`` suffixes) stay a pack concern for later.

Parser targets probe-rs ``download`` output at pinned version
:const:`PROBE_RS_VERSION` (v0.32.0 per spike-003); the parser is
isolated in this module so format drift lands here.

Subprocess boundary mirrors :mod:`engine.adapters.openocd`: an
injectable runner seam (``Callable[[argv], Transcript]``). Tests inject
fakes; production passes :func:`subprocess_runner`. No binary required
at test time.

Fixture outputs below are authored from documented output shapes
(erase/program success lines + ``Finished in ...`` summary + per-core
status lines) — marked FIXTURE, never live-probe claims. Live proof
stays OPEN: :meth:`ProbeRsAdapter.debug` returns a deterministic handle
bound to the shim endpoint, exactly like the OpenOCD adapter.
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
    "PROBE_RS_VERSION",
    "ProbeRsAdapter",
    "Runner",
    "Transcript",
    "VERIFY_OK_FIXTURE",
    "parse_output",
    "session_names",
    "subprocess_runner",
]

#: Pinned probe-rs version the parser targets (spike-003).
PROBE_RS_VERSION = "0.32.0"

#: One successful ``probe-rs download`` ends with a ``Finished in ...`` line.
_DONE_RE = re.compile(r"^Finished in ", re.MULTILINE)

#: probe-rs native per-core status line: ``Core <n>: <state>``.
_CORE_RE = re.compile(r"^Core (\d+)\s*:", re.MULTILINE)


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


# --- FIXTURE (not a live run): single-binary download transcript. --------
# Shape per probe-rs v0.32.0 ``download`` docs: erase/program progress
# lines, one ``Finished in ...`` summary line on success.
VERIFY_OK_FIXTURE = """\
Erasing ✔
Programming ✔
Finished in 1.23s
"""

# --- FIXTURE (not a live run): dual-core download transcript. ------------
# probe-rs native core status lines (``Core <n>:``) name sessions
# ``core-<n>`` — deliberately NOT the OpenOCD ``core<n>`` spelling, so
# the backend-specific divergence stays visible (see conformance test).
DUAL_CORE_FIXTURE = """\
Core 0: halted
Core 1: halted
Erasing ✔
Programming ✔
Finished in 1.10s
Erasing ✔
Programming ✔
Finished in 0.95s
"""


def session_names(transcript: Transcript) -> tuple[str, ...]:
    """Session names from ``Core <n>:`` status lines, in order."""
    return tuple(f"core-{n}" for n in _CORE_RE.findall(transcript.stdout))


def parse_output(
    pieces: Sequence[str], transcript: Transcript
) -> tuple[PieceResult, ...]:
    """Map one transcript to per-piece results, in piece order.

    Piece ``i`` passes iff the run exited 0 and at least ``i+1``
    ``Finished in ...`` summary lines are present.
    """
    finished = len(_DONE_RE.findall(transcript.stdout))
    results: list[PieceResult] = []
    for index, name in enumerate(pieces):
        ok = transcript.returncode == 0 and index < finished
        if ok:
            detail = "download-finished"
        elif transcript.returncode != 0:
            detail = f"exit rc={transcript.returncode}"
        else:
            detail = "missing Finished line"
        results.append(PieceResult(name=name, ok=ok, detail=detail))
    return tuple(results)


class ProbeRsAdapter(ProbeAdapter):
    """``ProbeAdapter`` via ``probe-rs download --chip <id>``."""

    def __init__(self, runner: Runner | None = None) -> None:
        self._runner = runner if runner is not None else subprocess_runner

    def render_argv(
        self,
        device: DeviceView,
        endpoint: Endpoint,
        pieces: Sequence[str],
    ) -> list[str]:
        """Build argv strictly from model facts + shim endpoint.

        ``--chip`` carries the certified pack id; ``--probe`` carries the
        shim endpoint address; each piece is a positional binary path
        (one ``download`` per piece, in order). Empty pack id raises.
        """
        if not device.id:
            raise ValueError("device model carries no pack id for '--chip'")
        argv = [
            "probe-rs",
            "download",
            "--chip",
            device.id,
            "--probe",
            endpoint.address,
        ]
        argv += list(pieces)
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
        return parse_output(pieces, transcript)

    def debug(self, device: DeviceView, endpoint: Endpoint) -> DebugHandle:
        # No live attach here (no probe claim): deterministic handle
        # bound to the shim endpoint; live sessions stay OPEN.
        self.render_argv(device, endpoint, ())
        return DebugHandle(session_id=f"probe-rs:{endpoint.address}", endpoint=endpoint)

    def proof_for(
        self,
        device: DeviceView,
        results: Sequence[PieceResult],
        transcript: Transcript,
    ) -> ProofResult:
        """Fill the core-owned proof struct for ``device.proof_rung``.

        Payload keys match the OpenOCD adapter exactly (generic,
        backend-comparable): ``pieces`` per-piece verdicts, ``verified``
        ok/total count, ``sessions`` examined session names ("" when
        none). ``sessions`` values are backend-native spellings and may
        diverge across backends (see conformance test); ``pieces`` and
        ``verified`` compare field-for-field.
        """
        results = tuple(results)
        passed = sum(1 for r in results if r.ok)
        payload = {
            "pieces": ",".join(f"{r.name}={'ok' if r.ok else 'fail'}" for r in results),
            "verified": f"{passed}/{len(results)}",
            "sessions": ",".join(session_names(transcript)),
        }
        return ProofResult(rung=device.proof_rung, payload=payload)
