"""Toolchain adapters (task-009, AD-8): register build stacks against the core registry.

One stack per toolchain family. Registration — never a core edit — is how a
toolchain joins (AD-1): ``core/`` owns the mechanism (:mod:`engine.core.stacks`),
adapters own the specs (image, build command, template family). A pack's
``stacks`` map selects among them by source language.
"""

from __future__ import annotations

from engine.core.stacks import StackSpec, register_stack

__all__ = ["CARGO_CORTEX", "MAKE_CMSIS", "ensure_registered"]

#: ARM GCC + CMSIS device trees, built with make (C and C++).
MAKE_CMSIS = StackSpec(
    stack_id="make-cmsis",
    template_family="c-cmsis",
    build_argv=("make", "build"),
    image="ghcr.io/randomgenericusername/lang-cpp:15.3.rel2",
)

#: Rust on Cortex-M, built with cargo.
CARGO_CORTEX = StackSpec(
    stack_id="cargo-cortex",
    template_family="rust-cortex",
    build_argv=("cargo", "build"),
    image="ghcr.io/randomgenericusername/lang-rust:1.99.0",
)

_SHIPPED = (MAKE_CMSIS, CARGO_CORTEX)


def ensure_registered() -> None:
    """Register every shipped stack (idempotent; safe after ``stacks.clear``)."""
    for spec in _SHIPPED:
        register_stack(spec)
