"""ESP32 family block validators (task-013, E1; AD-13, AD-14).

Device truth for the ESP32 family lives here — outside ``core/`` — so the family
is added with a pack and adapters and **no core diff** (AD-1).

The block names are the family's own (``esptool``, ``partitions``, ``sdkconfig``,
``example_led``). They deliberately do not reuse the STM32 ``example`` block:
``core/`` still builds its typed LED facet from that one shape, so a shared name
would be read as STM32 facts. Generalising that extraction is recorded as a
follow-up rather than forced into the ESP32 slice.
"""

from __future__ import annotations

from typing import Any

from engine.core.probe_ids import register_probe_vids
from engine.core.registry import register

__all__ = ["ESP32_FAMILIES", "ESP32_PROBE_VIDS", "register_esp32_families"]

#: Family ids this module owns (the ``family`` an ESP32 pack declares).
ESP32_FAMILIES = ("esp32",)

#: USB-UART bridges an ESP32 board presents — CP210x, CH340 (AD-14). Verified
#: on the owner's bench: a CH340-class dongle enumerated and flashed.
ESP32_PROBE_VIDS = ("10c4", "1a86")

_ESPTOOL_FLASH_MODES = ("qio", "qout", "dio", "dout")
_HEX_DIGITS = "0123456789abcdef"


def _validate_esptool(payload: Any) -> None:
    if not isinstance(payload, dict) or not payload:
        raise ValueError("esptool block must be a non-empty mapping")
    mode = payload.get("flash_mode")
    if mode not in _ESPTOOL_FLASH_MODES:
        raise ValueError(
            f"esptool block 'flash_mode' must be one of {_ESPTOOL_FLASH_MODES}, got {mode!r}"
        )
    size = payload.get("flash_size")
    if not isinstance(size, str) or not size:
        raise ValueError("esptool block must declare a non-empty 'flash_size'")
    for key in ("flash_freq", "baud"):
        if key in payload and (not isinstance(payload[key], str) or not payload[key]):
            raise ValueError(f"esptool block {key!r} must be a non-empty string")


def _is_offset(value: Any) -> bool:
    if isinstance(value, int) and not isinstance(value, bool):
        return value > 0
    if isinstance(value, str):
        try:
            return int(value, 0) > 0
        except ValueError:
            return False
    return False


def _validate_partitions(payload: Any) -> None:
    """Flash layout: the offsets the bootloader/table/app are written to."""
    if not isinstance(payload, dict) or not payload:
        raise ValueError("partitions block must be a non-empty mapping")
    for key in ("bootloader", "partition_table", "app"):
        if not _is_offset(payload.get(key)):
            raise ValueError(
                f"partitions block must declare a positive offset for {key!r} "
                "(hex or int, e.g. '0x1000')"
            )


def _validate_sdkconfig(payload: Any) -> None:
    if not isinstance(payload, dict) or not payload:
        raise ValueError("sdkconfig block must be a non-empty mapping")
    if not isinstance(payload.get("target"), str) or not payload["target"]:
        raise ValueError("sdkconfig block must declare a non-empty 'target'")
    for key, value in payload.items():
        if not isinstance(value, str) or not value:
            raise ValueError(f"sdkconfig block {key!r} must be a non-empty string")


def _validate_example_led(payload: Any) -> None:
    """ESP32 stock example: a plain GPIO pin + active level (no RCC clock gate)."""
    if not isinstance(payload, dict) or not payload:
        raise ValueError("example_led block must be a non-empty mapping")
    gpio = payload.get("gpio")
    if not isinstance(gpio, int) or isinstance(gpio, bool) or gpio < 0:
        raise ValueError("example_led.gpio must be a non-negative int")
    active = payload.get("active", "high")
    if active not in ("high", "low"):
        raise ValueError(f"example_led.active must be 'high' or 'low', got {active!r}")


_ESP32_BLOCKS = {
    "esptool": _validate_esptool,
    "partitions": _validate_partitions,
    "sdkconfig": _validate_sdkconfig,
    "example_led": _validate_example_led,
}


def register_esp32_families() -> None:
    """Register every ESP32 block against every ESP32 family (idempotent)."""
    for block_name, validator in _ESP32_BLOCKS.items():
        register(block_name, validator, families=ESP32_FAMILIES)
    for family in ESP32_FAMILIES:
        register_probe_vids(family, ESP32_PROBE_VIDS)
