"""Build-cell registry + build-evidence envelope tests (task-011, AD-15)."""

import pytest

from engine.core import build_cells
from engine.core.build_cells import (
    BuildEvidence,
    UnknownBuildCellError,
    build_cell_for,
    register_build_cell,
    registered_build_cells,
)


def _third_builder(device, out, image):  # pragma: no cover - never executed here
    return None


def test_a_third_stack_registers_its_builder():
    """AD-15: a third build system registers a builder; dispatch follows."""
    register_build_cell("third-family", _third_builder)
    assert build_cell_for("third-family") is _third_builder
    assert "third-family" in registered_build_cells()


def test_unknown_template_family_names_it():
    with pytest.raises(UnknownBuildCellError, match="nope-family"):
        build_cell_for("nope-family")


def test_register_rejects_empty_family_and_non_callable():
    with pytest.raises(ValueError):
        register_build_cell("", _third_builder)
    with pytest.raises(TypeError):
        register_build_cell("some-family", "not-a-builder")


def test_conflicting_registration_for_one_family_raises():
    register_build_cell("dup-family", _third_builder)
    with pytest.raises(ValueError, match="already registered"):
        register_build_cell("dup-family", lambda *a: None)


def test_build_evidence_envelope_is_stack_neutral():
    evidence = BuildEvidence(
        stack="make-cmsis",
        template_family="c-cmsis",
        commands=("make build",),
        exits=(0,),
        artifacts=(("build/M4/x.elf", 123),),
        fits=(("flash", "10/20"),),
    )
    payload = evidence.as_dict()
    assert payload["stack"] == "make-cmsis"
    assert payload["template_family"] == "c-cmsis"
    assert payload["artifacts"] == "build/M4/x.elf=123"
    assert payload["fits"] == "flash=10/20"
    # Distinct from the AD-10 flash-proof keys: build evidence has no
    # pieces/verified.
    assert "pieces" not in payload and "verified" not in payload
