"""Public surface for engine.templates (req-008)."""

from engine.templates.renderer import (
    CPU_BY_CORE,
    RUST_PINS,
    SUPPORTED_LANGS,
    core_context,
    render,
)

__all__ = [
    "CPU_BY_CORE",
    "RUST_PINS",
    "SUPPORTED_LANGS",
    "core_context",
    "render",
]
