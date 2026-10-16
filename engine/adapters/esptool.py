"""esptool probe backend (task-014, E2): ESP-family UART flashing.

**FlashPort only.** ESP32 bring-up has no JTAG attach (spike-007), so this
backend implements no :class:`engine.adapters.DebugPort`; the CLI fails the
``debug`` verb for it rather than fabricating a handle (AD-12).

Everything is rendered from certified model facts: the pack's ``partitions``
block names the offsets, its ``esptool`` block the flash parameters, and its
``sdkconfig`` block the chip target. No chip or board name appears literally in
this module.

Subprocess boundary mirrors the other backends (an injectable runner seam).
The transcript fixtures are authored from documented esptool output and the
live spike-007 run; they are marked FIXTURE, never live claims.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

from engine.adapters import FlashPort, PieceResult
from engine.core.model import DeviceView, Endpoint, ProofResult

__all__ = [
    "VERIFY_FIXTURE",
    "EsptoolAdapter",
    "Runner",
    "Transcript",
    "parse_transcript",
    "subprocess_runner",
]

#: The pack's ``partitions`` roles, in the order esptool writes them (this is
#: what ``idf.py flash`` does for the stock layout).
ROLE_ORDER = ("bootloader", "partition_table", "app")

#: esptool success line after each written image (verified live in spike-007).
_HASH_VERIFIED_RE = re.compile(r"Hash of data verified")


@dataclass(frozen=True)
class Transcript:
    """Captured tool run: argv + exit code + text streams."""

    argv: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str = ""


#: Runner seam: argv in, transcript out. Fake in tests, subprocess in prod.
Runner = Callable[[Sequence[str]], Transcript]


def subprocess_runner(
    argv: Sequence[str],
    *,
    stream: bool = False,
    log_path: str | Path | None = None,
) -> Transcript:
    """Production runner: exec argv via ``subprocess``, capture output.

    ``stream=True`` passes tool output through live (merged stdout+stderr) while
    still capturing it; ``log_path`` tees the same bytes to a file.
    """
    if not stream and log_path is None:
        completed = subprocess.run(list(argv), capture_output=True, text=True)
        return Transcript(
            argv=tuple(argv),
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
    proc = subprocess.Popen(
        list(argv), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    chunks: list[str] = []
    log_fh = open(str(log_path), "a") if log_path is not None else None
    try:
        assert proc.stdout is not None
        for line in proc.stdout:
            print(line, end="", flush=True)
            chunks.append(line)
            if log_fh is not None:
                log_fh.write(line)
    finally:
        if log_fh is not None:
            log_fh.close()
    return Transcript(
        argv=tuple(argv),
        returncode=proc.wait(),
        stdout="".join(chunks),
        stderr="",
    )


# --- FIXTURE (not a live run): three-image flash transcript. -------------
# Shape per esptool docs + the spike-007 live run: one "Hash of data verified."
# line per written image.
VERIFY_FIXTURE = """\
esptool v5.6.0
Writing at 0x00001000... (100 %)
Wrote 26176 bytes at 0x00001000 in 0.8 seconds.
Hash of data verified.
Wrote 3072 bytes at 0x00008000 in 0.1 seconds.
Hash of data verified.
Wrote 149088 bytes at 0x00010000 in 2.1 seconds.
Hash of data verified.
Leaving...
"""


def parse_transcript(
    pieces: Sequence[str], transcript: Transcript
) -> tuple[PieceResult, ...]:
    """Map one transcript to per-piece results, in piece order.

    Piece ``i`` passes iff the run exited 0 and at least ``i+1``
    ``Hash of data verified`` lines are present (esptool verifies each image).
    """
    verified = len(_HASH_VERIFIED_RE.findall(transcript.stdout))
    results: list[PieceResult] = []
    for index, name in enumerate(pieces):
        ok = transcript.returncode == 0 and index < verified
        if ok:
            detail = "hash-verified"
        elif transcript.returncode != 0:
            detail = f"exit rc={transcript.returncode}"
        else:
            detail = "missing 'Hash of data verified' line"
        results.append(PieceResult(name=name, ok=ok, detail=detail))
    return tuple(results)


class EsptoolAdapter(FlashPort):
    """``FlashPort`` via ``esptool … write-flash <addr> <bin> …``."""

    def __init__(
        self,
        runner: Runner | None = None,
        *,
        stream: bool = False,
        log_path: str | Path | None = None,
    ) -> None:
        self._runner = runner if runner is not None else subprocess_runner
        self._stream = stream
        self._log_path = log_path
        self.last_transcript: Transcript | None = None

    def render_argv(
        self,
        device: DeviceView,
        endpoint: Endpoint,
        pieces: Sequence[str],
    ) -> list[str]:
        """Build argv strictly from model facts + the shim endpoint.

        Offsets come from the pack's ``partitions`` block, matched to ``pieces``
        in :data:`ROLE_ORDER`; flash parameters from its ``esptool`` block; the
        chip target from ``sdkconfig``. A missing fact raises (no invented
        default).
        """
        layout = device.block_for("partitions")
        if not isinstance(layout, dict) or not layout:
            raise ValueError(
                f"device model carries no 'partitions' block; cannot derive "
                f"flash offsets for pack {device.id!r}"
            )
        esptool = device.block_for("esptool") or {}
        sdkconfig = device.block_for("sdkconfig") or {}

        pieces = tuple(pieces)
        if len(pieces) > len(ROLE_ORDER):
            raise ValueError(
                f"esptool writes at most {len(ROLE_ORDER)} images "
                f"({', '.join(ROLE_ORDER)}); got {len(pieces)}"
            )

        argv = ["esptool"]
        target = sdkconfig.get("target") if isinstance(sdkconfig, dict) else None
        if target:
            argv += ["--chip", str(target)]
        argv += ["--port", endpoint.address]
        baud = esptool.get("baud") if isinstance(esptool, dict) else None
        if baud:
            argv += ["--baud", str(baud)]
        argv.append("write-flash")
        for key, flag in (
            ("flash_mode", "--flash-mode"),
            ("flash_size", "--flash-size"),
            ("flash_freq", "--flash-freq"),
        ):
            value = esptool.get(key) if isinstance(esptool, dict) else None
            if value:
                argv += [flag, str(value)]
        for role, piece in zip(ROLE_ORDER, pieces):
            offset = layout.get(role)
            if offset is None or offset == "":
                raise ValueError(
                    f"pack {device.id!r} declares no {role!r} offset in its "
                    "'partitions' block"
                )
            argv += [str(offset), piece]
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
        argv = self.render_argv(device, endpoint, pieces)
        if self._stream or self._log_path is not None:
            if self._runner is not subprocess_runner:
                raise ValueError(
                    "streaming requires the default subprocess runner "
                    "(injected fakes capture instead)"
                )
            transcript = subprocess_runner(argv, stream=self._stream, log_path=self._log_path)
        else:
            transcript = self._runner(argv)
        self.last_transcript = transcript
        return parse_transcript(pieces, transcript)

    def proof_for(
        self,
        device: DeviceView,
        results: Sequence[PieceResult],
        transcript: object,
    ) -> ProofResult:
        """Fill the core-owned proof struct for ``device.proof_rung``.

        Payload keys match the other backends (generic, backend-comparable):
        ``pieces`` per-piece verdicts, ``verified`` ok/total, ``sessions`` —
        empty here, since esptool has no attach sessions.
        """
        results = tuple(results)
        passed = sum(1 for result in results if result.ok)
        return ProofResult(
            rung=device.proof_rung,
            payload={
                "pieces": ",".join(
                    f"{result.name}={'ok' if result.ok else 'fail'}" for result in results
                ),
                "verified": f"{passed}/{len(results)}",
                "sessions": "",
            },
        )
