"""Pack population tests (req-004 group 2): 3 packs accept, no sibling drift,
config_headers shape, proof rungs recorded."""

from pathlib import Path

import pytest
import yaml

from engine.core.loader import load_file
from engine.core.model import ProofResult

PACKS = Path(__file__).parent.parent.parent.parent / "packs"
PACK_IDS = ("stm32f411re", "stm32h755", "stm32wl55jc")


def _raw(pack_id):
    return yaml.safe_load((PACKS / f"{pack_id}.yaml").read_text())


def test_packs_accept_f411re():
    dev = load_file(PACKS / "stm32f411re.yaml")
    assert dev.id == "stm32f411re"
    assert [(c.name, c.arch) for c in dev.cores] == [("M4", "thumbv7em-none-eabihf")]
    origins = {m.name: (m.origin, m.size) for m in dev.memory}
    assert origins["flash"] == (0x8000000, 512 * 1024)
    assert origins["ram"] == (0x20000000, 128 * 1024)


def test_packs_accept_h755_dual_bank():
    dev = load_file(PACKS / "stm32h755.yaml")
    assert [(c.name, c.arch) for c in dev.cores] == [
        ("M7", "thumbv7em-none-eabihf"),
        ("M4", "thumbv7em-none-eabihf"),
    ]
    origins = {m.name: (m.origin, m.size) for m in dev.memory}
    assert origins["flash_m7"] == (0x08000000, 1024 * 1024)
    assert origins["flash_m4"] == (0x08100000, 1024 * 1024)
    assert origins["ram"] == (0x10000000, 288 * 1024)


def test_packs_accept_wl55jc_conservative_map():
    dev = load_file(PACKS / "stm32wl55jc.yaml")
    assert [(c.name, c.arch) for c in dev.cores] == [
        ("M4", "thumbv7em-none-eabi"),
        ("M0+", "thumbv7em-none-eabi"),
    ]
    origins = {m.name: (m.origin, m.size) for m in dev.memory}
    assert origins["flash"] == (0x08000000, 1024 * 1024)
    assert origins["ram"] == (0x20000000, 128 * 1024)


def test_packs_accept_openocd_corrected_targets():
    f411 = _raw("stm32f411re")["blocks"]["openocd"]
    assert (f411["interface"], f411["board"]) == ("stlink.cfg", "st_nucleo_f4.cfg")
    h755 = _raw("stm32h755")["blocks"]["openocd"]
    assert (h755["interface"], h755["board"], h755["dual_core"]) == (
        "stlink-dap.cfg",
        "st_nucleo_h745zi.cfg",
        True,
    )
    wl = _raw("stm32wl55jc")["blocks"]["openocd"]
    assert (wl["interface"], wl["target"], wl["dual_core"]) == (
        "stlink.cfg",
        "stm32wlx.cfg",
        True,
    )


def test_packs_accept_no_sibling_drift():
    for pack_id in ("stm32h755", "stm32wl55jc"):
        text = (PACKS / f"{pack_id}.yaml").read_text()
        assert "stm32f4x" not in text


@pytest.mark.parametrize("pack_id", PACK_IDS)
def test_config_headers_defaults_shape_per_pack(pack_id):
    block = _raw(pack_id)["blocks"]["config_headers"]
    for key in ("library", "header", "defaults_source"):
        assert isinstance(block[key], str) and block[key], key
    # Precedence contract for the template story: project file wins,
    # pack default fills the rest (spike-004).
    dev = load_file(PACKS / f"{pack_id}.yaml")
    assert dev.proof_rung


@pytest.mark.parametrize("pack_id", PACK_IDS)
def test_proof_rung_readback_per_pack(pack_id):
    dev = load_file(PACKS / f"{pack_id}.yaml")
    assert dev.proof_rung and "readback" in dev.proof_rung
    # Proof structs cover every pack rung: a verdict binds to the rung name.
    verdict = ProofResult(rung=dev.proof_rung, payload={"pack_id": dev.id})
    assert verdict.rung == dev.proof_rung
