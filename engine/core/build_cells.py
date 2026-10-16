"""Build-cell registry *mechanism* (task-011, AD-15).

The verify harness enumerates cells and builds each in its stack's image. The
mechanism — *which* builder serves which template family — belongs to core; the
builders themselves live with the harness. Registering a builder is how a third
build system joins without editing the harness dispatch (AD-1, AD-15).

Evidence comes back in a shared, stack-neutral envelope
(:class:`BuildEvidence`), kept distinct from the AD-10 flash-proof keys
(``pieces`` / ``verified``), which describe *programming*, not building.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

__all__ = [
    "BuildEvidence",
    "Builder",
    "UnknownBuildCellError",
    "build_cell_for",
    "clear",
    "register_build_cell",
    "registered_build_cells",
]

#: A builder: ``(device, out_dir, image)`` -> a harness result object.
Builder = Callable[..., Any]

_REGISTRY: dict[str, Builder] = {}


class UnknownBuildCellError(ValueError):
    """Raised when no builder is registered for a stack's template family."""


@dataclass(frozen=True)
class BuildEvidence:
    """Shared, stack-neutral build evidence (AD-15).

    ``commands``/``exits`` are the build invocations and their codes;
    ``artifacts`` maps each produced path to its byte size; ``fits`` maps a
    memory region to its ``used/avail`` verdict.
    """

    stack: str
    template_family: str
    commands: tuple[str, ...] = ()
    exits: tuple[int, ...] = ()
    artifacts: tuple[tuple[str, int], ...] = ()
    fits: tuple[tuple[str, str], ...] = ()

    def as_dict(self) -> dict[str, str]:
        return {
            "stack": self.stack,
            "template_family": self.template_family,
            "commands": " | ".join(self.commands),
            "exits": ",".join(str(exit_code) for exit_code in self.exits),
            "artifacts": ",".join(f"{path}={size}" for path, size in self.artifacts),
            "fits": ",".join(f"{region}={verdict}" for region, verdict in self.fits),
        }


def register_build_cell(template_family: str, builder: Builder) -> None:
    """Register the builder serving ``template_family`` (idempotent)."""
    if not template_family:
        raise ValueError("template_family must be non-empty")
    if not callable(builder):
        raise TypeError("builder must be callable")
    existing = _REGISTRY.get(template_family)
    if existing is not None and existing is not builder:
        raise ValueError(f"build cell for {template_family!r} already registered")
    _REGISTRY[template_family] = builder


def build_cell_for(template_family: str) -> Builder:
    try:
        return _REGISTRY[template_family]
    except KeyError:
        raise UnknownBuildCellError(
            f"no build cell registered for template family {template_family!r}; "
            f"registered: {sorted(_REGISTRY)}"
        ) from None


def registered_build_cells() -> tuple[str, ...]:
    return tuple(sorted(_REGISTRY))


def clear() -> None:
    """Reset the registry (tests only)."""
    _REGISTRY.clear()
