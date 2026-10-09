"""Certified device-model core: immutable facts, no pack I/O.

Adapter-facing access goes through reader views in :mod:`engine.core.model`
(:class:`DeviceView`, :class:`CoreView`, ...). The pack loader lives in a
separate module (task 2.x) and is never re-exported here, so adapters cannot
reach pack paths or raw YAML through this package.
"""

from engine.core.model import (
    Core,
    CoreView,
    Device,
    DeviceView,
    Endpoint,
    MemoryRegion,
    MemoryRegionView,
    ProofResult,
)

__all__ = [
    "Core",
    "CoreView",
    "Device",
    "DeviceView",
    "Endpoint",
    "MemoryRegion",
    "MemoryRegionView",
    "ProofResult",
]
