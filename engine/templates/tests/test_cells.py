"""Structural render harness (req-008): 9 cells, 3 packs x c/cpp/rust.

Each cell asserts the expected file list, zero unrendered placeholders
(``string.Template`` ``$``-leftovers, ``{{``, ``@@``), pack-derived greps
(flags/linker/CMSIS for c/cpp; pins + memory.x origins for rust), and
group-2 full-content greps (build/clean/flash targets, linker sections,
startup note, Cargo pins, build.rs link glue, corrected openocd paths,
config/ wiring).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from engine.core.loader import load_file
from engine.templates.renderer import RUST_PINS, render

PACKS_DIR = Path(__file__).resolve().parents[3] / "packs"
PACK_IDS = ("stm32f411re", "stm32h755", "stm32wl55jc")
LANGS = ("c", "cpp", "rust")

# Placeholder leak: $IDENT / ${IDENT} leftovers (make `$(...)` is legal and
# excluded), plus {{ and @@ syntaxes.
PLACEHOLDER_RE = re.compile(r"\$\{[A-Za-z_]|\$[A-Za-z_]|{{|@@")

SRC_EXT = {"c": "c", "cpp": "c", "rust": "rs"}

# Corrected openocd config paths per spike-001 (board/ vs target/ split).
EXPECTED_OC = {
    "stm32f411re": ("interface/stlink.cfg", "board/st_nucleo_f4.cfg", False),
    "stm32h755": ("interface/stlink-dap.cfg", "board/st_nucleo_h745zi.cfg", True),
    "stm32wl55jc": ("interface/stlink.cfg", "target/stm32wlx.cfg", True),
}


def _pack_doc(pack_id: str) -> dict:
    return yaml.safe_load((PACKS_DIR / f"{pack_id}.yaml").read_text())


def expected_files(pack_id: str, lang: str) -> list[str]:
    """Checklist-encoded file list per cell (literals, not renderer-derived)."""
    doc = _pack_doc(pack_id)
    linker = doc["blocks"]["linker"]
    header = doc["blocks"]["config_headers"]["header"]
    base = ["Makefile" if lang in ("c", "cpp") else "Cargo.toml"]
    if lang in ("c", "cpp"):
        files = list(base)
        for core in doc["cores"]:
            files.append(f"src/main-{core['name']}.c")
            files.append(f"linker/{linker[core['name']]}")
        files.append("Startup/NOTE.md")
    else:
        files = [*base, "memory.x", "build.rs", "src/main.rs"]
    files += ["openocd.cfg", f"config/{header}", "config/OVERRIDES.md"]
    return sorted(files)


def _render_cell(pack_id: str, lang: str, tmp_path: Path) -> Path:
    device = load_file(PACKS_DIR / f"{pack_id}.yaml")
    out = tmp_path / pack_id / lang
    written = render(device, lang, out)
    assert [p.relative_to(out).as_posix() for p in written] == expected_files(pack_id, lang)
    return out


def _assert_no_placeholders(root: Path) -> None:
    for path in sorted(root.rglob("*")):
        if path.is_file():
            hit = PLACEHOLDER_RE.search(path.read_text())
            assert hit is None, f"{path.relative_to(root)}: unrendered placeholder {hit.group()!r}"


@pytest.mark.parametrize("pack_id", PACK_IDS)
@pytest.mark.parametrize("lang", LANGS)
def test_cells(pack_id: str, lang: str, tmp_path: Path) -> None:
    out = _render_cell(pack_id, lang, tmp_path)
    _assert_no_placeholders(out)
    doc = _pack_doc(pack_id)
    header = doc["blocks"]["config_headers"]["header"]
    if lang in ("c", "cpp"):
        text = (out / "Makefile").read_text()
        for core in doc["cores"]:
            assert core["arch"] in text, f"arch {core['arch']} missing"
            assert doc["blocks"]["linker"][core["name"]] in text, "linker ref missing"
            assert f"build-{core['name']}" in text, "build target missing"
            assert f"clean-{core['name']}" in text, "clean target missing"
            assert f"flash-{core['name']}" in text, "flash-helper target missing"
            main = (out / f"src/main-{core['name']}.c").read_text()
            assert "wfi" in main and header in main, "bring-up source incomplete"
            linker = (out / f"linker/{doc['blocks']['linker'][core['name']]}").read_text()
            assert "ENTRY(Reset_Handler)" in linker and "MEMORY" in linker
        fpu = doc["blocks"]["fpu"]
        assert ("-mfloat-abi=soft" if fpu["mode"] == "soft" else fpu["variant"]) in text
        assert "vendor/CMSIS/Include" in text and "-Iconfig" in text
        assert "verify reset exit" in text, "flash helper must verify+reset"
        assert "Reset_Handler" in (out / "Startup/NOTE.md").read_text()
        if lang == "cpp":
            assert "-std=c++17" in text
    else:
        cargo = (out / "Cargo.toml").read_text()
        for crate, pin in RUST_PINS.items():
            assert f'{crate} = "{pin}"' in cargo, f"pin {crate} missing"
        assert 'flip-link = "0.1.12"' in cargo
        memx = (out / "memory.x").read_text()
        for region in doc["memory"]:
            origin = int(region["origin_hex"], 16)
            assert f"0x{origin:08X}" in memx, f"region {region['name']} origin missing"
            assert str(region["size"]) in memx, f"region {region['name']} size missing"
        assert "_stack_start" in memx
        build_rs = (out / "build.rs").read_text()
        assert "-Tlink.x" in build_rs and "rerun-if-changed" in build_rs
        main_rs = (out / "src/main.rs").read_text()
        assert "#[entry]" in main_rs and "wfi" in main_rs
    oc_text = (out / "openocd.cfg").read_text()
    iface, cfg_path, dual = EXPECTED_OC[pack_id]
    assert iface in oc_text and cfg_path in oc_text, "corrected openocd path missing"
    if dual and cfg_path.startswith("target/"):
        assert "set DUAL_CORE 1" in oc_text
    overrides = (out / "config/OVERRIDES.md").read_text()
    assert "project" in overrides and "-Iconfig" in overrides, "override doc incomplete"
    assert doc["blocks"]["config_headers"]["library"] in overrides
