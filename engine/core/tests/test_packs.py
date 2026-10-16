"""Pack loading tests (req-003 group 2.2): 3 accept, 1 rejects naming the block."""

from pathlib import Path

import pytest

from engine.core.loader import FrameError, load_file, load_text
from engine.core import registry
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
    mem = {m.name: (m.origin, m.size) for m in dev.memory}
    # bug-008: real STM32WL55JC = 256K flash, 64K SRAM (SRAM1 32K + SRAM2 32K).
    assert mem["flash"] == (0x08000000, 256 * 1024)
    assert mem["ram"] == (0x20000000, 64 * 1024)


def test_pack_unknown_block_rejects_naming_block():
    with pytest.raises(UnknownBlockError, match="mystery_block"):
        load_file(FIX / "negative_unknown_block.yaml")


def test_pack_missing_frame_key_rejects():
    from engine.core.loader import load_text

    with pytest.raises(FrameError, match="memory|cores|probe|proof_rung|family"):
        load_text("id: x\nversion: '1'\ncores: [{name: A, arch: B}]\n")


def test_loader_attaches_all_family_blocks_generically():
    repo_packs = Path(__file__).resolve().parents[3] / "packs"
    dev = load_file(repo_packs / "stm32f411re.yaml")
    names = {name for name, _payload in dev.facets.blocks}
    # every declared block reaches the model, generically named (task-008)
    assert {
        "openocd", "fpu", "linker", "startup", "system", "defines",
        "config_headers", "probe_settings", "example", "svd",
    } <= names
    assert dev.facets.block_for("svd")
    assert dev.facets.block_for("not_a_block") is None


def test_pack_probe_backend_defaults_from_shipped_packs():
    repo_packs = Path(__file__).resolve().parents[3] / "packs"
    for pack_id in ("stm32f411re", "stm32h755", "stm32wl55jc"):
        dev = load_file(repo_packs / f"{pack_id}.yaml")
        assert dev.probe_backend, f"{pack_id} declares no probe default"


def test_pack_probe_backend_absent_is_none():
    from engine.core.loader import load_text

    dev = load_text(
        "id: x\nversion: '1'\nfamily: stm32f4\nstacks: {c: make-cmsis}\n"
        "cores: [{name: A, arch: B}]\n"
        "memory: [{name: flash, origin_hex: '0x0', size: 1024}]\n"
        "probe: {transport: t, address: a}\n"
        "proof_rung: frame\n"
    )
    assert dev.probe_backend is None


def test_pack_probe_settings_reach_view():
    from engine.core.model import DeviceView

    repo_packs = Path(__file__).resolve().parents[3] / "packs"
    expected = {
        "stm32f411re": "STM32F411RE",
        "stm32h755": "STM32H755ZI",
        "stm32wl55jc": "STM32WL55JC",
    }
    for pack_id, chip in expected.items():
        view = DeviceView.of(load_file(repo_packs / f"{pack_id}.yaml"))
        assert view.probe_setting("probe-rs", "chip") == chip, pack_id
        assert view.probe_setting("probe-rs", "nope") is None


def test_new_family_needs_no_core_change():
    """AD-13 acceptance: a family registered outside ``core/`` loads its own block.

    Nothing in ``engine/core`` names this family or its block; the validator is
    registered from outside (as a shipped family module does) and the pack
    loads purely through the mechanism.
    """

    def _validate_widgets(payload):
        if not isinstance(payload, dict) or "count" not in payload:
            raise ValueError("widgets block must declare 'count'")

    registry.register("widgets", _validate_widgets, families=("acme",))

    dev = load_text(
        "id: acme-1\nversion: '1'\nfamily: acme\nstacks: {c: cargo-cortex}\n"
        "cores: [{name: C0, arch: generic}]\n"
        "memory: [{name: flash, origin_hex: '0x0', size: 1024}]\n"
        "probe: {transport: t, address: a}\n"
        "proof_rung: rung\n"
        "blocks:\n  widgets: {count: 3}\n"
    )
    assert dev.id == "acme-1"
    assert dev.facets.block_for("widgets") == {"count": 3}

    # and the family's blocks do not leak into another family
    with pytest.raises(UnknownBlockError, match="widgets"):
        load_text(
            "id: acme-2\nversion: '1'\nfamily: stm32f4\nstacks: {c: make-cmsis}\n"
            "cores: [{name: C0, arch: generic}]\n"
            "memory: [{name: flash, origin_hex: '0x0', size: 1024}]\n"
            "probe: {transport: t, address: a}\n"
            "proof_rung: rung\n"
            "blocks:\n  widgets: {count: 3}\n"
        )
