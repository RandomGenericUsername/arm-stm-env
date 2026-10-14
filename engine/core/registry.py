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


def _validate_startup(payload: Any) -> None:
    if not isinstance(payload, dict) or not payload:
        raise ValueError("startup block must be a non-empty mapping of core name -> vendor file")
    for core, script in payload.items():
        if not isinstance(core, str) or not core:
            raise ValueError(f"startup block core name must be a non-empty string, got {core!r}")
        if not isinstance(script, str) or not script:
            raise ValueError(f"startup block file for core {core!r} must be a non-empty string")


register("startup", _validate_startup, families=_STM32_FAMILIES)


def _validate_system(payload: Any) -> None:
    if not isinstance(payload, dict) or not payload:
        raise ValueError("system block must be a non-empty mapping of core name -> vendor file")
    for core, script in payload.items():
        if not isinstance(core, str) or not core:
            raise ValueError(f"system block core name must be a non-empty string, got {core!r}")
        if not isinstance(script, str) or not script:
            raise ValueError(f"system block file for core {core!r} must be a non-empty string")


register("system", _validate_system, families=_STM32_FAMILIES)


def _validate_defines(payload: Any) -> None:
    if not isinstance(payload, dict) or not payload:
        raise ValueError("defines block must be a non-empty mapping of core name -> device macro")
    for core, macro in payload.items():
        if not isinstance(core, str) or not core:
            raise ValueError(f"defines block core name must be a non-empty string, got {core!r}")
        if not isinstance(macro, str) or not macro:
            raise ValueError(f"defines block macro for core {core!r} must be a non-empty string")


register("defines", _validate_defines, families=_STM32_FAMILIES)

_CONFIG_HEADER_KEYS = ("library", "header", "defaults_source")


def _validate_config_headers(payload: Any) -> None:
    if not isinstance(payload, dict) or not payload:
        raise ValueError("config_headers block must be a non-empty mapping")
    for key in _CONFIG_HEADER_KEYS:
        value = payload.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError(f"config_headers block must declare non-empty {key!r}")


register("config_headers", _validate_config_headers, families=_STM32_FAMILIES)


def _validate_probe_settings(payload: Any) -> None:
    if not isinstance(payload, dict) or not payload:
        raise ValueError("probe_settings block must be a non-empty mapping of backend -> settings")
    for backend, settings in payload.items():
        if not isinstance(backend, str) or not backend:
            raise ValueError(f"probe_settings backend name must be a non-empty string, got {backend!r}")
        if not isinstance(settings, dict) or not settings:
            raise ValueError(f"probe_settings for backend {backend!r} must be a non-empty mapping")
        for key, value in settings.items():
            if not isinstance(key, str) or not key:
                raise ValueError(f"probe_settings key for backend {backend!r} must be a non-empty string")
            if not isinstance(value, str) or not value:
                raise ValueError(f"probe_settings[{backend}][{key}] must be a non-empty string")


register("probe_settings", _validate_probe_settings, families=_STM32_FAMILIES)


_EXAMPLE_ACTIVE = ("high", "low")


def _is_addr(value: Any) -> bool:
    if isinstance(value, int) and not isinstance(value, bool):
        return value > 0
    if isinstance(value, str):
        try:
            return int(value, 0) > 0
        except ValueError:
            return False
    return False


def _validate_example(payload: Any) -> None:
    """On-board LED example fact (req-014/req-015): ``{led: {port,pin,active,
    gpio_base,rcc_en_addr,rcc_en_bit}}``."""
    if not isinstance(payload, dict) or not payload:
        raise ValueError("example block must be a non-empty mapping")
    led = payload.get("led")
    if not isinstance(led, dict):
        raise ValueError("example block must declare a 'led' mapping")
    port = led.get("port")
    if not isinstance(port, str) or len(port) != 1 or not port.isalpha():
        raise ValueError("example.led.port must be a single letter A-Z")
    pin = led.get("pin")
    if not isinstance(pin, int) or isinstance(pin, bool) or not 0 <= pin <= 15:
        raise ValueError("example.led.pin must be an int 0..15")
    active = led.get("active", "high")
    if active not in _EXAMPLE_ACTIVE:
        raise ValueError(
            f"example.led.active must be one of {_EXAMPLE_ACTIVE}, got {active!r}"
        )
    for key in ("gpio_base", "rcc_en_addr"):
        if not _is_addr(led.get(key)):
            raise ValueError(f"example.led.{key} must be a positive int address")
    if not _is_addr(led.get("clock_hz")):
        raise ValueError("example.led.clock_hz must be a positive int (Hz)")
    bit = led.get("rcc_en_bit")
    if not isinstance(bit, int) or isinstance(bit, bool) or not 0 <= bit <= 31:
        raise ValueError("example.led.rcc_en_bit must be an int 0..31")


register("example", _validate_example, families=_STM32_FAMILIES)
