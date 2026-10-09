"""Model tests: construction, frozen-mutation, endpoint/proof struct coverage."""

import dataclasses

import pytest

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


def _device(**kw) -> Device:
    base = dict(
        id="stm32f411re",
        version="1.0.0",
        source_hash="sha256:abc",
        cores=[Core(name="cortex-m4", arch="armv7e-m")],
        memory=[MemoryRegion(name="flash", origin_hex="0x08000000", size=512 * 1024)],
        probe_ref=Endpoint(transport="stlink", address="usb:0"),
        proof_rung="frame",
    )
    base.update(kw)
    return Device(**base)


def test_constructs_device_with_provenance():
    d = _device()
    assert d.id == "stm32f411re"
    assert ("pack_id", "stm32f411re") in d.provenance
    assert ("pack_version", "1.0.0") in d.provenance
    assert d.memory[0].origin == 0x08000000
    assert isinstance(d.cores, tuple) and isinstance(d.memory, tuple)


def test_origin_accepts_int_and_hex_string():
    assert MemoryRegion(name="a", origin_hex=0x20000000, size=1).origin == 0x20000000
    assert MemoryRegion(name="a", origin_hex="0x20000000", size=1).origin == 0x20000000


def test_rejects_empty_and_bad_fields():
    with pytest.raises(ValueError):
        Core(name="", arch="armv7e-m")
    with pytest.raises(ValueError):
        MemoryRegion(name="x", origin_hex="0x0", size=0)
    with pytest.raises(ValueError):
        MemoryRegion(name="x", origin_hex="not-hex", size=8)
    with pytest.raises(ValueError):
        Endpoint(transport="", address="usb:0")
    with pytest.raises(ValueError):
        Device(**{**_device().__dict__, "cores": []})
    with pytest.raises(ValueError):
        ProofResult(rung="", payload={})


@pytest.mark.parametrize("obj", [
    Core(name="c", arch="a"),
    MemoryRegion(name="m", origin_hex="0x0", size=1),
    Endpoint(transport="t", address="a"),
])
def test_frozen_mutation_raises(obj):
    with pytest.raises(dataclasses.FrozenInstanceError):
        object.__getattribute__(obj, "__dataclass_params__")  # sanity: is a dataclass
        obj_name = next(iter(dataclasses.asdict(obj)))
        setattr(obj, obj_name, "mutated")


def test_device_frozen_mutation_raises():
    d = _device()
    with pytest.raises(dataclasses.FrozenInstanceError):
        d.id = "other"  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        d.proof_rung = "other"  # type: ignore[misc]


def test_endpoint_and_proof_structs_comparable():
    e1 = Endpoint(transport="stlink", address="usb:0")
    e2 = Endpoint(transport="stlink", address="usb:0")
    assert e1 == e2
    p1 = ProofResult(rung="frame", payload={"digest": "d1", "target": "stm32f4x"})
    p2 = ProofResult(rung="frame", payload=[("target", "stm32f4x"), ("digest", "d1")])
    assert p1 == p2  # order-insensitive, field-for-field
    assert p1.as_dict() == {"digest": "d1", "target": "stm32f4x"}
    p3 = ProofResult(rung="frame", payload={"digest": "other"})
    assert p1 != p3


def test_reader_views_expose_facts_only():
    d = _device()
    v = DeviceView.of(d)
    assert v.id == d.id and v.probe_transport == "stlink"
    assert isinstance(v.cores[0], CoreView) and isinstance(v.memory[0], MemoryRegionView)
    for attr in ("loader", "pack_path", "raw_yaml", "yaml", "probe_ref"):
        assert not hasattr(v, attr), attr
    with pytest.raises(dataclasses.FrozenInstanceError):
        v.id = "mut"  # type: ignore[misc]


def test_no_loader_exposed_from_core():
    import pathlib

    import engine.core as core_pkg

    # NOTE (req-003 group 2): engine/core/loader.py now exists as a submodule,
    # so `hasattr(pkg, "loader")` is True once any test imports it (Python sets
    # submodule attrs on the parent package). The enforceable boundary is that
    # the package __init__ never re-exports it: adapters doing
    # `from engine.core import X` get no loader.
    init_src = pathlib.Path(core_pkg.__file__).read_text()
    assert "loader" not in init_src, "core __init__ must not re-export a loader"
    assert not hasattr(core_pkg, "load_pack"), "core package must not expose load_pack"
