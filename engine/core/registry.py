"""Family-block registry *mechanism* (req-003 group 2.1; task-008, AD-13).

Core owns the mechanism only — registration, family-qualified lookup, and
dispatch. Family block validators live in :mod:`engine.packs` (device truth),
so a new brand adds a family module there and requires no ``core/`` diff.

Keys are qualified by ``(family, block_name)``: two families cannot silently
share one block name, and :data:`FAMILY_BLOCKS` is the dispatch source (which
blocks a family may declare). Unknown blocks — or blocks registered for another
family — are a hard, fail-closed error naming the block.
"""

from __future__ import annotations

from typing import Any, Callable

__all__ = [
    "FAMILY_BLOCKS",
    "FamilyCollisionError",
    "UnknownBlockError",
    "clear",
    "get",
    "register",
    "registered_blocks",
    "validate_block",
]

Validator = Callable[[Any], None]

#: (family, block_name) -> validator.
_REGISTRY: dict[tuple[str, str], Validator] = {}

#: family -> (block names it registered), the dispatch source.
FAMILY_BLOCKS: dict[str, tuple[str, ...]] = {}


class UnknownBlockError(ValueError):
    """Raised when a pack declares a block its family did not register."""


class FamilyCollisionError(ValueError):
    """Raised when two validators claim the same ``(family, block)`` key."""


def register(
    block_name: str,
    validator: Validator,
    *,
    families: tuple[str, ...] = (),
) -> None:
    """Register ``validator`` for ``block_name`` under each of ``families``.

    Idempotent: re-registering the *same* validator is a no-op (so
    ``clear()`` + ``ensure_registered()`` works). A *different* validator
    claiming the same ``(family, block)`` raises
    :class:`FamilyCollisionError` rather than silently overwriting.
    """
    if not block_name:
        raise ValueError("block_name must be non-empty")
    if not callable(validator):
        raise TypeError("validator must be callable")
    for family in families:
        if not family:
            raise ValueError("family must be non-empty")
        key = (family, block_name)
        existing = _REGISTRY.get(key)
        if existing is not None and existing is not validator:
            raise FamilyCollisionError(
                f"family block {block_name!r} already registered for family {family!r}"
            )
        _REGISTRY[key] = validator
        members = tuple(FAMILY_BLOCKS.get(family, ()))
        if block_name not in members:
            FAMILY_BLOCKS[family] = members + (block_name,)


def get(family: str, block_name: str) -> Validator:
    try:
        return _REGISTRY[(family, block_name)]
    except KeyError:
        raise UnknownBlockError(
            f"unknown family block: {block_name!r} (family {family!r})"
        ) from None


def registered_blocks(family: str | None = None) -> tuple[str, ...]:
    """Block names for ``family`` (or every registered block when ``None``)."""
    if family is None:
        return tuple(sorted({block for (_family, block) in _REGISTRY}))
    return tuple(sorted(FAMILY_BLOCKS.get(family, ())))


def validate_block(block_name: str, payload: Any, *, family: str) -> None:
    """Run the ``family``'s validator; unknown/foreign blocks raise naming it."""
    get(family, block_name)(payload)


def clear() -> None:
    """Reset the registry (tests only); call ``ensure_registered`` to refill."""
    _REGISTRY.clear()
    FAMILY_BLOCKS.clear()
