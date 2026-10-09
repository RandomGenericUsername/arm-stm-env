"""Canonical certified device model (req-003, group 1).

All structs are frozen dataclasses: construction validates field shapes,
mutation raises :class:`dataclasses.FrozenInstanceError`. ``origin_hex``
accepts ``"0x..."`` strings or ints and normalises to int.

Reader views (``DeviceView``, ``CoreView``, ``MemoryRegionView``) are the
only adapter-facing access: read-only facts, no pack paths, no raw YAML,
no loader reference.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator, Sequence, Tuple

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


def _coerce_origin(value: str | int) -> int:
    if isinstance(value, int):
        if value < 0:
            raise ValueError(f"origin must be non-negative, got {value}")
        return value
    if isinstance(value, str):
        try:
            parsed = int(value, 16 if value.lower().startswith("0x") else 10)
        except ValueError:
            raise ValueError(f"origin_hex must be a hex/int literal, got {value!r}")
        if parsed < 0:
            raise ValueError(f"origin must be non-negative, got {value!r}")
        return parsed
    raise TypeError(f"origin_hex must be str or int, got {type(value).__name__}")


@dataclass(frozen=True)
class Core:
    """One CPU core on the device."""

    name: str
    arch: str

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Core.name must be non-empty")
        if not self.arch:
            raise ValueError("Core.arch must be non-empty")


@dataclass(frozen=True)
class MemoryRegion:
    """One addressable memory region; origin normalised to int."""

    name: str
    origin_hex: str | int
    size: int
    origin: int = field(init=False)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("MemoryRegion.name must be non-empty")
        if not isinstance(self.size, int) or isinstance(self.size, bool) or self.size <= 0:
            raise ValueError(f"MemoryRegion.size must be a positive int, got {self.size!r}")
        object.__setattr__(self, "origin", _coerce_origin(self.origin_hex))


@dataclass(frozen=True)
class Endpoint:
    """Probe endpoint vocabulary: transport + address (core-owned, adapters fill)."""

    transport: str
    address: str

    def __post_init__(self) -> None:
        if not self.transport:
            raise ValueError("Endpoint.transport must be non-empty")
        if not self.address:
            raise ValueError("Endpoint.address must be non-empty")


@dataclass(frozen=True)
class ProofResult:
    """Proof verdict for one rung: rung name + comparable evidence payload."""

    rung: str
    payload: Tuple[Tuple[str, str], ...]

    def __init__(self, rung: str, payload: dict[str, str] | Sequence[tuple[str, str] | list[str]]) -> None:
        if not rung:
            raise ValueError("ProofResult.rung must be non-empty")
        if isinstance(payload, dict):
            items = tuple(sorted(payload.items()))
        else:
            items = tuple(sorted((str(k), str(v)) for k, v in payload))
        object.__setattr__(self, "rung", rung)
        object.__setattr__(self, "payload", items)

    def as_dict(self) -> dict[str, str]:
        return dict(self.payload)


@dataclass(frozen=True)
class Device:
    """Certified device: immutable facts + provenance (pack id + version + source hash)."""

    id: str
    version: str
    source_hash: str
    cores: Tuple[Core, ...]
    memory: Tuple[MemoryRegion, ...]
    probe_ref: Endpoint
    proof_rung: str
    provenance: Tuple[Tuple[str, str], ...] = ()

    def __init__(
        self,
        id: str,
        version: str,
        source_hash: str,
        cores: Sequence[Core],
        memory: Sequence[MemoryRegion],
        probe_ref: Endpoint,
        proof_rung: str,
        provenance: dict[str, str] | Sequence[tuple[str, str] | list[str]] = (),
    ) -> None:
        if not id:
            raise ValueError("Device.id must be non-empty")
        if not version:
            raise ValueError("Device.version must be non-empty")
        if not source_hash:
            raise ValueError("Device.source_hash must be non-empty")
        core_t = tuple(cores)
        mem_t = tuple(memory)
        if not core_t:
            raise ValueError("Device.cores must be non-empty")
        if not mem_t:
            raise ValueError("Device.memory must be non-empty")
        if not all(isinstance(c, Core) for c in core_t):
            raise TypeError("Device.cores must all be Core")
        if not all(isinstance(m, MemoryRegion) for m in mem_t):
            raise TypeError("Device.memory must all be MemoryRegion")
        if not isinstance(probe_ref, Endpoint):
            raise TypeError("Device.probe_ref must be an Endpoint")
        if not proof_rung:
            raise ValueError("Device.proof_rung must be non-empty")
        prov = tuple(sorted(provenance.items())) if isinstance(provenance, dict) else tuple(sorted((str(k), str(v)) for k, v in provenance))
        # Provenance always traces to inputs: pack id + version are mandatory facts.
        base = {"pack_id": id, "pack_version": version}
        base.update(dict(prov))
        object.__setattr__(self, "id", id)
        object.__setattr__(self, "version", version)
        object.__setattr__(self, "source_hash", source_hash)
        object.__setattr__(self, "cores", core_t)
        object.__setattr__(self, "memory", mem_t)
        object.__setattr__(self, "probe_ref", probe_ref)
        object.__setattr__(self, "proof_rung", proof_rung)
        object.__setattr__(self, "provenance", tuple(sorted(base.items())))


# --- Adapter-facing reader views (facts only, no loader/pack-path access) ---


@dataclass(frozen=True)
class CoreView:
    name: str
    arch: str

    @classmethod
    def of(cls, core: Core) -> CoreView:
        return cls(name=core.name, arch=core.arch)


@dataclass(frozen=True)
class MemoryRegionView:
    name: str
    origin: int
    size: int

    @classmethod
    def of(cls, region: MemoryRegion) -> MemoryRegionView:
        return cls(name=region.name, origin=region.origin, size=region.size)


@dataclass(frozen=True)
class DeviceView:
    """Read-only adapter view of a Device. No loader, no paths, no raw YAML."""

    id: str
    version: str
    source_hash: str
    cores: Tuple[CoreView, ...]
    memory: Tuple[MemoryRegionView, ...]
    probe_transport: str
    probe_address: str
    proof_rung: str

    @classmethod
    def of(cls, device: Device) -> DeviceView:
        return cls(
            id=device.id,
            version=device.version,
            source_hash=device.source_hash,
            cores=tuple(CoreView.of(c) for c in device.cores),
            memory=tuple(MemoryRegionView.of(m) for m in device.memory),
            probe_transport=device.probe_ref.transport,
            probe_address=device.probe_ref.address,
            proof_rung=device.proof_rung,
        )

    def __iter__(self) -> Iterator[str]:
        yield from ("id", "version", "cores", "memory", "probe", "proof_rung")
