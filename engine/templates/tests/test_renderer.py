"""Renderer unit tests (req-008): API shape, per-core contexts, model-only facets."""

from __future__ import annotations

import pytest

from engine.core.loader import load_file
from engine.core.model import Core, Device, DeviceFacets, Endpoint, MemoryRegion, OpenocdConfig
from engine.templates.renderer import SUPPORTED_LANGS, core_context, render

from .test_cells import PACK_IDS, PACKS_DIR


def test_renderer_bad_lang(tmp_path) -> None:
    device = load_file(PACKS_DIR / "stm32f411re.yaml")
    with pytest.raises(ValueError, match="unsupported lang"):
        render(device, "zig", tmp_path)


def test_renderer_returns_sorted_written_list(tmp_path) -> None:
    device = load_file(PACKS_DIR / "stm32f411re.yaml")
    written = render(device, "c", tmp_path)
    assert written == sorted(written)
    assert all(p.is_file() for p in written)


@pytest.mark.parametrize("pack_id", PACK_IDS)
def test_renderer_per_core_contexts_cover_every_core(pack_id: str) -> None:
    device = load_file(PACKS_DIR / f"{pack_id}.yaml")
    assert {c.name for c in device.cores} <= {name for name, _ in device.facets.linker}
    for core in device.cores:
        ctx = core_context(device, core, "c")
        assert ctx["arch"] == core.arch
        assert ctx["cpu_flags"].startswith("-mcpu=") and "-mthumb" in ctx["cpu_flags"]
        assert ctx["linker_script"] == device.facets.linker_for(core.name, device.id)


def test_renderer_supported_langs() -> None:
    assert SUPPORTED_LANGS == ("c", "cpp", "rust")


def test_loader_attaches_facets_to_model() -> None:
    device = load_file(PACKS_DIR / "stm32f411re.yaml")
    assert isinstance(device.facets, DeviceFacets)
    assert (device.facets.fpu_mode, device.facets.fpu_variant) == ("hard", "fpv4-sp-d16")
    assert device.facets.linker_for("M4", device.id) == "STM32F411RETx_FLASH.ld"
    assert device.facets.config_header == "stm32_config.h"
    assert device.facets.config_library == "stm32hal"
    assert device.openocd is not None and device.openocd.board == "st_nucleo_f4.cfg"
    wl = load_file(PACKS_DIR / "stm32wl55jc.yaml")
    assert wl.openocd is not None and wl.openocd.board is None
    assert wl.openocd.target == "stm32wlx.cfg"
    assert (wl.facets.fpu_mode, wl.facets.fpu_variant) == ("soft", "none")


def _synthetic_device() -> Device:
    """Hand-built model (no pack YAML): proves the renderer is model-only."""
    return Device(
        id="synthetic",
        version="9.9.9",
        source_hash="sha256:synthetic",
        cores=[Core(name="M4", arch="thumbv7em-none-eabihf")],
        memory=[
            MemoryRegion(name="flash", origin_hex="0x08000000", size=262144),
            MemoryRegion(name="ram", origin_hex="0x20000000", size=65536),
        ],
        probe_ref=Endpoint(transport="stlink", address="openocd:stlink"),
        proof_rung="readback",
        openocd=OpenocdConfig(interface="stlink.cfg", target="board.cfg", board="synth.cfg"),
        facets=DeviceFacets(
            fpu_mode="hard",
            fpu_variant="fpv4-sp-d16",
            linker=(("M4", "SYNTH_FLASH.ld"),),
            config_library="synthlib",
            config_header="synth_config.h",
            config_defaults_source="pack/synth.h",
        ),
    )


@pytest.mark.parametrize("lang", SUPPORTED_LANGS)
def test_renderer_consumes_model_only(lang: str, tmp_path) -> None:
    written = render(_synthetic_device(), lang, tmp_path)
    assert written, "expected files for synthetic model"
    if lang in ("c", "cpp"):
        text = (tmp_path / "Makefile").read_text()
        assert "-mfpu=fpv4-sp-d16 -mfloat-abi=hard" in text
        assert "linker/SYNTH_FLASH.ld" in text
        assert "board/synth.cfg" in (tmp_path / "openocd.cfg").read_text()
        assert (tmp_path / "config/synth_config.h").is_file()
    else:
        assert "0x08000000" in (tmp_path / "memory.x").read_text()
        assert 'name = "synthetic"' in (tmp_path / "Cargo.toml").read_text()
