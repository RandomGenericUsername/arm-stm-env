"""Pack loading tests (req-003 group 2.2): 3 accept, 1 rejects naming the block."""

from pathlib import Path

import pytest

from engine.core.loader import FrameError, load_file
from engine.core.registry import UnknownBlockError

FIX = Path(__file__).parent / "fixtures"


def test_pack_f411re_accepts():
    dev = load_file(FIX / "stm32f411re.yaml")
    assert dev.id == "stm32f411re"
    assert [c.name for c in dev.cores] == ["M4"]
    assert dev.cores[0].arch == "thumbv7em-none-eabihf"
    flash = next(m for m in dev.memory if m.name == "flash")
    assert (flash.origin, flash.size) == (0x8000000, 512 * 1024)
    assert len(dev.source_hash) == 64
    assert dict(dev.provenance)["pack_id"] == "stm32f411re"


def test_pack_h755_accepts_dual_bank():
    dev = load_file(FIX / "stm32h755.yaml")
    assert [c.name for c in dev.cores] == ["M7", "M4"]
    origins = {m.name: (m.origin, m.size) for m in dev.memory}
    assert origins["flash_m7"] == (0x08000000, 1024 * 1024)
    assert origins["flash_m4"] == (0x08100000, 1024 * 1024)
    assert origins["ram"] == (0x10000000, 288 * 1024)


def test_pack_wl55jc_accepts_dual_core():
    dev = load_file(FIX / "stm32wl55jc.yaml")
    assert [c.name for c in dev.cores] == ["M4", "M0+"]
    flash = next(m for m in dev.memory if m.name == "flash")
    assert (flash.origin, flash.size) == (0x08000000, 1024 * 1024)


def test_pack_unknown_block_rejects_naming_block():
    with pytest.raises(UnknownBlockError, match="mystery_block"):
        load_file(FIX / "negative_unknown_block.yaml")


def test_pack_missing_frame_key_rejects():
    from engine.core.loader import load_text

    with pytest.raises(FrameError, match="memory|cores|probe|proof_rung"):
        load_text("id: x\nversion: '1'\ncores: [{name: A, arch: B}]\n")
