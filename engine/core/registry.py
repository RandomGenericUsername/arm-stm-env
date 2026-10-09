"""Explicit family-block registry (req-003, group 2.1).

``block_name -> validator fn``. Unknown block = hard error naming the block
(fail-closed). Family membership recorded in ``FAMILY_BLOCKS``.
"""

from __future__ import annotations

from typing import Any, Callable

__all__ = [
    "FAMILY_BLOCKS",
    "UnknownBlockError",
    "clear",
    "get",
    "register",
    "registered_blocks",
    "validate_block",
]

Validator = Callable[[Any], None]

_REGISTRY: dict[str, Validator] = {}
FAMILY_BLOCKS: dict[str, tuple[str, ...]] = {}


class UnknownBlockError(ValueError):
    """Raised when a pack declares a family block with no registered validator."""


def register(block_name: str, validator: Validator, *, families: tuple[str, ...] = ()) -> None:
    if not block_name:
        raise ValueError("block_name must be non-empty")
    if not callable(validator):
        raise TypeError("validator must be callable")
    _REGISTRY[block_name] = validator
    for family in families:
        members = tuple(FAMILY_BLOCKS.get(family, ()))
        if block_name not in members:
            FAMILY_BLOCKS[family] = members + (block_name,)


def get(block_name: str) -> Validator:
    try:
        return _REGISTRY[block_name]
    except KeyError:
        raise UnknownBlockError(f"unknown family block: {block_name!r}") from None


def registered_blocks() -> tuple[str, ...]:
    return tuple(sorted(_REGISTRY))


def validate_block(block_name: str, payload: Any) -> None:
    """Run the registered validator; unknown block names raise naming the block."""
    get(block_name)(payload)


def clear() -> None:
    """Reset registry (tests only)."""
    _REGISTRY.clear()
    FAMILY_BLOCKS.clear()


def _validate_openocd(payload: Any) -> None:
    if not isinstance(payload, dict) or not payload:
        raise ValueError("openocd block must be a non-empty mapping")
    if "interface" not in payload:
        raise ValueError("openocd block must declare 'interface'")
    boardish = ("board", "target")
    if not any(k in payload for k in boardish):
        raise ValueError("openocd block must declare one of 'board'/'target'")


register("openocd", _validate_openocd, families=("stm32f4", "stm32h7", "stm32wl"))
