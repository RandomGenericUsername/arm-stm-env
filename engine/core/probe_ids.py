"""Probe autodetect id registry *mechanism* (task-010, AD-14, AD-9).

The host shim owns the per-OS mapping (AD-9), but *which* USB ids are probes is
device truth: each family registers its own. Replaces the hardcoded VID tuple
that lived in ``engine/cli/`` (a core-side brand fact).
"""

from __future__ import annotations

__all__ = ["clear", "known_probe_vids", "register_probe_vids"]

#: family id -> tuple of lowercase hex vendor ids.
_REGISTRY: dict[str, tuple[str, ...]] = {}


def register_probe_vids(family: str, vids: tuple[str, ...]) -> None:
    """Register the vendor ids a family's probes present (idempotent)."""
    if not family:
        raise ValueError("family must be non-empty")
    cleaned = tuple(v.lower() for v in vids)
    if not cleaned or not all(v and all(c in "0123456789abcdef" for c in v) for v in cleaned):
        raise ValueError("probe vids must be non-empty lowercase hex strings")
    existing = _REGISTRY.get(family)
    if existing is not None and existing != cleaned:
        raise ValueError(f"probe vids for family {family!r} already registered differently")
    _REGISTRY[family] = cleaned


def known_probe_vids() -> tuple[str, ...]:
    """Every registered probe vendor id (shipped families auto-registered)."""
    from engine.packs import ensure_registered

    ensure_registered()
    return tuple(sorted({vid for vids in _REGISTRY.values() for vid in vids}))


def clear() -> None:
    """Reset the registry (tests only)."""
    _REGISTRY.clear()
