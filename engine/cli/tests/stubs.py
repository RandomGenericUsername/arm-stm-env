"""Stub port implementations for CLI tests (req-005, group 1.1).

Generic fixtures only — no family/chip/backend names anywhere in this
package (see ``test_no_hardware_knowledge`` gate).
"""

from __future__ import annotations

from typing import Sequence

from engine.adapters import DebugHandle, PieceResult, ProbeAdapter
from engine.core.model import (
    Core,
    Device,
    DeviceView,
    Endpoint,
    MemoryRegion,
)

__all__ = ["StubProbeAdapter", "make_device_view", "make_endpoint"]


def make_endpoint() -> Endpoint:
    return Endpoint(transport="generic-probe", address="usb:0")


def make_device_view(device_id: str = "generic-board") -> DeviceView:
    device = Device(
        id=device_id,
        version="0.1.0",
        source_hash="sha256:test",
        cores=[Core(name="core0", arch="generic-arch")],
        memory=[MemoryRegion(name="prog", origin_hex="0x0", size=64 * 1024)],
        probe_ref=make_endpoint(),
        proof_rung="frame",
    )
    return DeviceView.of(device)


class StubProbeAdapter(ProbeAdapter):
    """In-memory port stub: preloaded per-piece outcomes + canned session."""

    def __init__(
        self,
        outcomes: dict[str, bool] | None = None,
        session_id: str = "session-1",
    ) -> None:
        self._outcomes = dict(outcomes or {})
        self._session_id = session_id
        self.flashed: list[tuple[str, ...]] = []
        self.debugged: int = 0

    def flash(
        self,
        device: DeviceView,
        endpoint: Endpoint,
        pieces: Sequence[str],
    ) -> Sequence[PieceResult]:
        self.flashed.append(tuple(pieces))
        return tuple(
            PieceResult(
                name=name,
                ok=self._outcomes.get(name, True),
                detail="stub",
            )
            for name in pieces
        )

    def debug(self, device: DeviceView, endpoint: Endpoint) -> DebugHandle:
        self.debugged += 1
        return DebugHandle(session_id=self._session_id, endpoint=endpoint)
