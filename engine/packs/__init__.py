"""Family pack validators (task-008, AD-13): device truth lives here, not in core.

Core owns the frame and the registry *mechanism*; each family ships its block
validators alongside the packs it describes. Importing this package registers
the shipped families. A new brand adds a module here plus packs and adapters and
requires **no ``engine/core`` diff** — the AD-1 acceptance test.
"""

from __future__ import annotations

__all__ = ["ensure_registered"]


def ensure_registered() -> None:
    """Register every shipped family (idempotent; safe after ``registry.clear``)."""
    from engine.packs.esp32 import register_esp32_families
    from engine.packs.stm32 import register_stm32_families

    register_stm32_families()
    register_esp32_families()
