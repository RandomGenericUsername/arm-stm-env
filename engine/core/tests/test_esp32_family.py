"""ESP32 family + pack tests (task-013, E1; AD-13, AD-14)."""

from pathlib import Path

import pytest

from engine.core.loader import load_file, load_text
from engine.core.probe_ids import known_probe_vids
from engine.core.registry import UnknownBlockError, registered_blocks, validate_block

REPO_PACKS = Path(__file__).resolve().parents[3] / "packs"


def test_esp32_pack_loads_with_its_family_blocks():
    device = load_file(REPO_PACKS / "esp32cam.yaml")
    assert device.family == "esp32"
    assert device.stack_for("c") == "idf-cmake"
    assert [core.arch for core in device.cores] == ["xtensa-lx6", "xtensa-lx6"]
    assert device.probe_ref.transport == "uart-serial"
    assert device.probe_backend == "esptool"
    assert device.facets.block_for("esptool")["flash_size"] == "4MB"
    assert device.facets.block_for("partitions")["app"] == "0x10000"
    assert device.facets.block_for("sdkconfig")["target"] == "esp32"
    assert device.facets.block_for("example_led") == {"gpio": 33, "active": "low"}


def test_esp32_blocks_are_family_qualified():
    for block in ("esptool", "partitions", "sdkconfig", "example_led"):
        assert block in registered_blocks(family="esp32")
        assert block not in registered_blocks(family="stm32f4")


def test_esp32_block_in_an_stm32_pack_is_rejected():
    with pytest.raises(UnknownBlockError, match="sdkconfig"):
        load_text(
            "id: x\nversion: '1'\nfamily: stm32f4\nstacks: {c: make-cmsis}\n"
            "cores: [{name: A, arch: B}]\n"
            "memory: [{name: flash, origin_hex: '0x0', size: 1024}]\n"
            "probe: {transport: t, address: a}\n"
            "proof_rung: r\n"
            "blocks:\n  sdkconfig: {target: esp32}\n"
        )


def test_esp32_uart_bridge_vids_are_registered():
    vids = known_probe_vids()
    assert "10c4" in vids and "1a86" in vids  # CP210x, CH340


@pytest.mark.parametrize(
    "payload",
    [
        {"flash_size": "4MB"},                      # missing flash_mode
        {"flash_mode": "turbo", "flash_size": "4MB"},  # bad mode
        {"flash_mode": "dio"},                      # missing flash_size
    ],
)
def test_esptool_block_rejects_bad_shapes(payload):
    with pytest.raises(ValueError, match="esptool|flash_mode|flash_size"):
        validate_block("esptool", payload, family="esp32")


def test_partitions_block_requires_the_three_offsets():
    with pytest.raises(ValueError, match="partitions"):
        validate_block(
            "partitions", {"bootloader": "0x1000", "partition_table": "0x8000"},
            family="esp32",
        )


def test_sdkconfig_block_requires_a_target():
    with pytest.raises(ValueError, match="target"):
        validate_block("sdkconfig", {"flash_size": "4MB"}, family="esp32")


def test_example_led_block_is_a_plain_gpio_fact():
    validate_block("example_led", {"gpio": 33, "active": "low"}, family="esp32")
    with pytest.raises(ValueError, match="gpio"):
        validate_block("example_led", {"active": "low"}, family="esp32")
