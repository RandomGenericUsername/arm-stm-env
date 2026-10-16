"""Build-stack registry tests (task-009, AD-11, AD-8): mechanism + shipped stacks."""

import pytest

from engine.core import stacks
from engine.core.stacks import (
    StackSpec,
    UnknownStackError,
    register_stack,
    registered_stacks,
    stack_spec,
)


def _spec(stack_id="t-stack", family="t-family", argv=("build",), image="img:1"):
    return StackSpec(stack_id=stack_id, template_family=family, build_argv=argv, image=image)


def test_register_and_lookup_roundtrip():
    register_stack(_spec("t-roundtrip"))
    assert stack_spec("t-roundtrip").image == "img:1"
    assert "t-roundtrip" in registered_stacks()


def test_unknown_stack_names_it():
    with pytest.raises(UnknownStackError, match="nope-stack"):
        stack_spec("nope-stack")


def test_re_register_same_spec_is_idempotent_conflict_raises():
    spec = _spec("t-dup")
    register_stack(spec)
    register_stack(spec)  # identical: no-op
    with pytest.raises(ValueError, match="already registered"):
        register_stack(_spec("t-dup", image="other:2"))


def test_spec_rejects_empty_fields():
    with pytest.raises(ValueError):
        _spec(stack_id="")
    with pytest.raises(ValueError):
        _spec(family="")
    with pytest.raises(ValueError):
        _spec(argv=())
    with pytest.raises(ValueError):
        _spec(image="")


def test_shipped_stacks_are_registered_by_the_toolchain_adapter():
    from engine.adapters.toolchain import ensure_registered

    ensure_registered()
    assert {"make-cmsis", "cargo-cortex"} <= set(registered_stacks())
    assert stack_spec("make-cmsis").build_argv == ("make", "build")
    assert stack_spec("cargo-cortex").build_argv == ("cargo", "build")
