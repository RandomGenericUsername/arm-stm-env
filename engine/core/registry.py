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
    iface = payload.get("interface")
    if not isinstance(iface, str) or not iface:
        raise ValueError("openocd block must declare non-empty 'interface'")
    boardish = ("board", "target")
    if not any(k in payload for k in boardish):
        raise ValueError("openocd block must declare one of 'board'/'target'")
    for key in boardish:
        if key in payload and (not isinstance(payload[key], str) or not payload[key]):
            raise ValueError(f"openocd block {key!r} must be a non-empty string")
    if "dual_core" in payload and not isinstance(payload["dual_core"], bool):
        raise ValueError("openocd block 'dual_core' flag must be a bool")


register("openocd", _validate_openocd, families=("stm32f4", "stm32h7", "stm32wl"))

_STM32_FAMILIES = ("stm32f4", "stm32h7", "stm32wl")

_FPU_MODES = ("soft", "softfp", "hard")


def _validate_fpu(payload: Any) -> None:
    if not isinstance(payload, dict) or not payload:
        raise ValueError("fpu block must be a non-empty mapping")
    mode = payload.get("mode")
    if not isinstance(mode, str) or not mode:
        raise ValueError("fpu block must declare non-empty 'mode'")
    if mode not in _FPU_MODES:
        raise ValueError(f"fpu block 'mode' must be one of {_FPU_MODES}, got {mode!r}")
    variant = payload.get("variant")
    if not isinstance(variant, str) or not variant:
        raise ValueError("fpu block must declare non-empty 'variant'")


register("fpu", _validate_fpu, families=_STM32_FAMILIES)


def _validate_linker(payload: Any) -> None:
    if not isinstance(payload, dict) or not payload:
        raise ValueError("linker block must be a non-empty mapping of core name -> script")
    for core, script in payload.items():
        if not isinstance(core, str) or not core:
            raise ValueError(f"linker block core name must be a non-empty string, got {core!r}")
        if not isinstance(script, str) or not script:
            raise ValueError(f"linker block script for core {core!r} must be a non-empty string")


register("linker", _validate_linker, families=_STM32_FAMILIES)

_CONFIG_HEADER_KEYS = ("library", "header", "defaults_source")


def _validate_config_headers(payload: Any) -> None:
    if not isinstance(payload, dict) or not payload:
        raise ValueError("config_headers block must be a non-empty mapping")
    for key in _CONFIG_HEADER_KEYS:
        value = payload.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError(f"config_headers block must declare non-empty {key!r}")


register("config_headers", _validate_config_headers, families=_STM32_FAMILIES)
