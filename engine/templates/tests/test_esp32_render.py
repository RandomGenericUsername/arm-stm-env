"""ESP-IDF template-family render tests (task-015, E3; AD-11, AD-14)."""

import json
from pathlib import Path

from engine.core.loader import load_file
from engine.templates.renderer import render

PACKS_DIR = Path(__file__).resolve().parents[3] / "packs"


def _render(tmp_path) -> set[str]:
    device = load_file(PACKS_DIR / "esp32cam.yaml")
    written = render(device, "c", tmp_path)
    return {path.relative_to(tmp_path).as_posix() for path in written}


def test_idf_tree_has_the_cmake_app_shape(tmp_path) -> None:
    names = _render(tmp_path)
    assert {
        "CMakeLists.txt",
        "main/CMakeLists.txt",
        "main/main.c",
        "sdkconfig.defaults",
        ".gitignore",
        ".mu/stack",
        "README.md",
    } <= names
    assert (tmp_path / ".mu" / "stack").read_text().strip() == "idf-cmake"


def test_idf_tree_carries_no_stm32_artifacts(tmp_path) -> None:
    """AD-14: no OpenOCD, CMSIS config headers, vendor tree, or make/cargo files."""
    names = _render(tmp_path)
    assert not {n for n in names if n.startswith("probe/")}
    assert not {n for n in names if n.startswith("config/")}
    assert not {n for n in names if n.startswith("linker/")}
    assert "Makefile" not in names and "Cargo.toml" not in names
    assert not (tmp_path / "vendor").exists()


def test_idf_example_uses_the_pack_led_fact(tmp_path) -> None:
    _render(tmp_path)
    main_c = (tmp_path / "main" / "main.c").read_text()
    assert "#define LED_GPIO 33" in main_c           # from the example_led block
    assert "gpio_set_level(LED_GPIO, 0)" in main_c   # active-low: 0 is ON
    assert "gpio_set_level(LED_GPIO, 1)" in main_c


def test_idf_sdkconfig_comes_from_the_pack(tmp_path) -> None:
    _render(tmp_path)
    sdk = (tmp_path / "sdkconfig.defaults").read_text()
    assert 'CONFIG_IDF_TARGET="esp32"' in sdk
    assert "CONFIG_ESPTOOLPY_FLASHSIZE_4MB=y" in sdk


def test_idf_readme_documents_uart_not_openocd(tmp_path) -> None:
    _render(tmp_path)
    readme = (tmp_path / "README.md").read_text()
    assert "GPIO0" in readme and "download mode" in readme
    assert "OpenOCD" not in readme and "VS Code" not in readme


def test_idf_root_cmake_names_the_project(tmp_path) -> None:
    _render(tmp_path)
    root = (tmp_path / "CMakeLists.txt").read_text()
    assert "project(esp32cam)" in root
    assert "$ENV{IDF_PATH}/tools/cmake/project.cmake" in root


def test_idf_vscode_flow_has_build_flash_monitor(tmp_path) -> None:
    device = load_file(PACKS_DIR / "esp32cam.yaml")
    render(device, "c", tmp_path, vscode=True)
    tasks = json.loads((tmp_path / ".vscode" / "tasks.json").read_text())
    labels = [t["label"] for t in tasks["tasks"]]
    assert labels == ["Build", "Flash", "Monitor", "Build + Flash + Monitor"]
    commands = {t["label"]: t["command"] for t in tasks["tasks"]}
    assert commands["Build"] == "idf.py build"
    assert commands["Flash"] == "idf.py flash"
    assert commands["Monitor"] == "idf.py monitor"
    assert (tmp_path / ".vscode" / "extensions.json").is_file()


def test_idf_vscode_flow_has_no_cortex_debug_or_launch(tmp_path) -> None:
    """No attach without external JTAG (req-022 non-goals) — log-based only."""
    device = load_file(PACKS_DIR / "esp32cam.yaml")
    render(device, "c", tmp_path, vscode=True)
    assert not (tmp_path / ".vscode" / "launch.json").exists()
    vscode = tmp_path / ".vscode"
    blob = "".join(p.read_text() for p in vscode.iterdir())
    assert "cortex-debug" not in blob and "openocd" not in blob.lower()
    assert not (tmp_path / "probe").exists()
