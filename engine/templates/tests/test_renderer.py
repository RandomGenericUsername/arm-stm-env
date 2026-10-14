"""Renderer unit tests (req-008): API shape, per-core contexts, model-only facets."""

from __future__ import annotations

import pytest

from engine.core.loader import load_file
from engine.core.model import Core, Device, DeviceFacets, Endpoint, MemoryRegion, OpenocdConfig
from engine.templates.renderer import SUPPORTED_LANGS, core_context, render
from engine.templates.renderer import fetch_svds as _real_fetch_svds

from .test_cells import PACK_IDS, PACKS_DIR


@pytest.fixture(autouse=True)
def _stub_vendoring(monkeypatch) -> None:
    """req-011/017: render() vendors C/C++ via git and fetches SVDs; unit
    renders stub both (tmp dirs are non-repos, no network)."""
    monkeypatch.setattr("engine.templates.renderer.vendor", lambda _pack_id, _out: [])
    monkeypatch.setattr(
        "engine.templates.renderer.fetch_svds", lambda _device, _out, **k: []
    )


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


def test_renderer_dual_bank_cores_link_own_flash(tmp_path) -> None:
    """H755 M7 -> FLASH_M7, M4 -> FLASH_M4 (per-core region, not first-bank)."""
    device = load_file(PACKS_DIR / "stm32h755.yaml")
    render(device, "c", tmp_path)
    m7 = (tmp_path / f"linker/{device.facets.linker_for('M7', device.id)}").read_text()
    m4 = (tmp_path / f"linker/{device.facets.linker_for('M4', device.id)}").read_text()
    assert ">FLASH_M7" in m7 and ">FLASH_M4" not in m7
    assert ">FLASH_M4" in m4 and ">FLASH_M7" not in m4


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
            startup=(("M4", "startup_synth.s"),),
            system=(("M4", "system_synth.c"),),
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
        assert "board/synth.cfg" in (tmp_path / "probe" / "openocd.cfg").read_text()
        assert (tmp_path / "config/synth_config.h").is_file()
    else:
        assert "0x08000000" in (tmp_path / "memory.x").read_text()
        assert 'name = "synthetic"' in (tmp_path / "Cargo.toml").read_text()


def test_render_vscode_generates_valid_configs(tmp_path) -> None:
    import json

    device = load_file(PACKS_DIR / "stm32f411re.yaml")
    render(device, "c", tmp_path, vscode=True)
    cfg = json.loads((tmp_path / ".vscode/launch.json").read_text())["configurations"][0]
    assert cfg["type"] == "cortex-debug"
    assert cfg["executable"].endswith("build/M4/stm32f411re-M4.elf")
    assert cfg["configFiles"] == [
        "interface/stlink.cfg",
        "board/st_nucleo_f4.cfg",
        "probe/resume-on-detach.cfg",
    ]
    # bug-011: mask interrupts during single-step so stepping advances (H7/M7).
    assert cfg["postLaunchCommands"] == ["monitor cortex_m maskisr steponly"]
    # bug-013: single-core configs need no processor targeting.
    assert "numberOfProcessors" not in cfg and "targetProcessor" not in cfg
    assert (tmp_path / "probe/resume-on-detach.cfg").is_file()
    resume = (tmp_path / "probe/resume-on-detach.cfg").read_text()
    assert "gdb-detach" in resume and "info exists _TARGETNAME" in resume
    assert cfg["gdbPath"].startswith("/opt/arm-gnu-toolchain")
    assert cfg["svdFile"].endswith("probe/STM32F411.svd")
    ext = json.loads((tmp_path / ".vscode/extensions.json").read_text())
    assert "marus25.cortex-debug" in ext["recommendations"]
    tasks = json.loads((tmp_path / ".vscode/tasks.json").read_text())
    assert {"Build", "Clean", "Flash"} <= {t["label"] for t in tasks["tasks"]}


def test_render_vscode_per_core_dual(tmp_path) -> None:
    import json

    device = load_file(PACKS_DIR / "stm32h755.yaml")
    render(device, "c", tmp_path, vscode=True)
    launch = json.loads((tmp_path / ".vscode/launch.json").read_text())
    cfgs = launch["configurations"]
    assert [c["name"] for c in cfgs] == [
        "Debug M7 (OpenOCD)",
        "Debug M4 (OpenOCD)",
        "Debug M7+M4 (OpenOCD)",
    ]
    resume = (tmp_path / "probe/resume-on-detach.cfg").read_text()
    assert "stm32h7x.cpu0 configure -event gdb-detach" in resume
    assert "stm32h7x.cpu1 configure -event gdb-detach" in resume
    # bug-011: every per-core config gets the single-step workaround.
    assert all(
        c["postLaunchCommands"] == ["monitor cortex_m maskisr steponly"]
        for c in cfgs
    )
    # bug-013: each per-core config targets its own OpenOCD processor (cpu0/cpu1)
    m7, m4 = cfgs[0], cfgs[1]
    assert (m7["numberOfProcessors"], m7["targetProcessor"]) == (2, 0)  # M7 -> cpu0
    assert (m4["numberOfProcessors"], m4["targetProcessor"]) == (2, 1)  # M4 -> cpu1
    # ...and a compound config chains the second core off the boot core.
    compound = cfgs[2]
    assert compound["targetProcessor"] == 0
    assert compound["executable"].endswith("build/M7/stm32h755-M7.elf")
    chained = compound["chainedConfigurations"]
    assert chained["detached"] is False
    assert chained["launches"] == [{"name": "Debug M4 (OpenOCD)"}]


def test_vscode_maskisr_gated_to_cortex_m() -> None:
    """bug-012: the `cortex_m` workaround is only emitted for Cortex-M cores."""
    import json
    from dataclasses import replace

    from engine.templates.renderer import _vscode_files

    cm = _vscode_files(_synthetic_device())  # thumbv7em-none-eabihf
    cfgs = json.loads(cm[".vscode/launch.json"])["configurations"]
    assert all(
        c.get("postLaunchCommands") == ["monitor cortex_m maskisr steponly"]
        for c in cfgs
    )

    riscv = replace(
        _synthetic_device(),
        cores=[Core(name="M4", arch="riscv32imac-unknown-none-elf")],
    )
    rv = json.loads(_vscode_files(riscv)[".vscode/launch.json"])["configurations"]
    assert all("postLaunchCommands" not in c for c in rv)


def test_render_vscode_off_by_default(tmp_path) -> None:
    render(load_file(PACKS_DIR / "stm32f411re.yaml"), "c", tmp_path)
    assert not (tmp_path / ".vscode").exists()


def test_fetch_svds_uses_pinned_url(tmp_path) -> None:
    from engine.templates import renderer

    device = load_file(PACKS_DIR / "stm32f411re.yaml")
    seen: dict = {}

    class _Resp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return b"<device/>"

    def opener(url):
        seen["url"] = url
        return _Resp()

    paths = _real_fetch_svds(device, tmp_path, opener=opener)
    assert paths == [tmp_path / "probe" / "STM32F411.svd"]
    assert "modm-io/cmsis-svd-stm32" in seen["url"] and renderer.SVD_SHA in seen["url"]
    assert (tmp_path / "probe" / "STM32F411.svd").read_bytes() == b"<device/>"
