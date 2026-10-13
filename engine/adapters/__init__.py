"""Adapter ports (req-005, group 1): device-agnostic contracts only.

``ProbeAdapter`` exposes ``flash``/``debug`` with multi-piece results; the
image-lookup port maps language -> container image. Real implementations
arrive later; stubs live in :mod:`engine.cli.tests.stubs`. Core types are
read-only views — ports never touch packs, paths, or raw YAML.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Sequence

from engine.core.model import DeviceView, Endpoint, ProofResult

__all__ = [
    "DebugHandle",
    "DefaultImageLookup",
    "ImageLookup",
    "PieceResult",
    "ProbeAdapter",
    "default_backend_name",
    "get_adapter",
    "register_backend",
]


@dataclass(frozen=True)
class PieceResult:
    """Outcome for one programmed piece: piece name + pass/fail + detail."""

    name: str
    ok: bool
    detail: str = ""

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("PieceResult.name must be non-empty")


@dataclass(frozen=True)
class DebugHandle:
    """Handle for an attached debug session: id + prepared endpoint."""

    session_id: str
    endpoint: Endpoint

    def __post_init__(self) -> None:
        if not self.session_id:
            raise ValueError("DebugHandle.session_id must be non-empty")
        if not isinstance(self.endpoint, Endpoint):
            raise TypeError("DebugHandle.endpoint must be an Endpoint")


class ProbeAdapter(ABC):
    """Port for probe operations. Multi-piece flash; proof stays in core types."""

    @abstractmethod
    def flash(
        self,
        device: DeviceView,
        endpoint: Endpoint,
        pieces: Sequence[str],
    ) -> Sequence[PieceResult]:
        """Program each named piece; return one result per piece, in order."""

    @abstractmethod
    def debug(self, device: DeviceView, endpoint: Endpoint) -> DebugHandle:
        """Attach a debug session; return its handle."""


_BACKEND_FACTORIES: dict[str, Callable[[], ProbeAdapter]] = {}


def register_backend(name: str, factory: Callable[[], ProbeAdapter]) -> None:
    """Register a probe backend factory (adapters own backend vocabulary)."""
    _BACKEND_FACTORIES[name] = factory


def default_backend_name() -> str:
    """Backend used when the invocation names none."""
    return "openocd"


def _ensure_builtin_backends() -> None:
    # Deferred imports: backend modules import the ABCs above, so importing
    # them at package top would be circular.
    if "openocd" not in _BACKEND_FACTORIES:
        from engine.adapters.openocd import OpenOCDAdapter

        _BACKEND_FACTORIES["openocd"] = OpenOCDAdapter
    if "probe-rs" not in _BACKEND_FACTORIES:
        from engine.adapters.probe_rs import ProbeRsAdapter

        _BACKEND_FACTORIES["probe-rs"] = ProbeRsAdapter


def get_adapter(name: str | None = None) -> ProbeAdapter:
    """Instantiate a registered probe backend (default when unnamed).

    Callers never name backend modules — adding a backend touches this
    registry only, never CLI code.
    """
    _ensure_builtin_backends()
    key = name or default_backend_name()
    try:
        return _BACKEND_FACTORIES[key]()
    except KeyError:
        raise ValueError(
            f"unknown probe backend {key!r}; registered: {sorted(_BACKEND_FACTORIES)}"
        ) from None


class ImageLookup(ABC):
    """Port mapping source language -> container image reference."""

    @abstractmethod
    def image_for(self, lang: str) -> str:
        """Return the image reference for ``lang``; unknown lang raises."""

    @abstractmethod
    def supported_langs(self) -> tuple[str, ...]:
        """Languages with a known image."""


class DefaultImageLookup(ImageLookup):
    """Core-owned default table (stdlib mapping, no device knowledge)."""

    TABLE: dict[str, str] = {
        # Pinned refs (req-007). c shares the cpp image: one ARM GCC
        # toolchain compiles both; a separate lang-c image would duplicate it.
        "c": "ghcr.io/arm-stm-env/lang-cpp:15.3.rel2",
        "cpp": "ghcr.io/arm-stm-env/lang-cpp:15.3.rel2",
        "rust": "ghcr.io/arm-stm-env/lang-rust:1.99.0",
    }

    def image_for(self, lang: str) -> str:
        try:
            return self.TABLE[lang]
        except KeyError:
            raise ValueError(
                f"unknown language {lang!r}; supported: {sorted(self.TABLE)}"
            ) from None

    def supported_langs(self) -> tuple[str, ...]:
        return tuple(sorted(self.TABLE))
