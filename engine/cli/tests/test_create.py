"""Create wiring tests (task-002): pack -> render() -> out_dir/name + next steps."""

import re
from pathlib import Path

import yaml

from engine.cli.main import PACKS_DIR, main

PLACEHOLDER = re.compile(r"\$\{|\$[A-Za-z_]")


def _first_pack() -> tuple[str, Path]:
    """A shipped pack (id, yaml path); id is read at runtime so this file
    carries no hardware knowledge (see test_no_hardware_knowledge)."""
    packs = sorted(PACKS_DIR.glob("*.yaml"))
    assert packs, "no shipped packs found"
    doc = yaml.safe_load(packs[0].read_text())
    return doc["id"], packs[0]


def _rendered_texts(root: Path) -> list[str]:
    return [p.read_text() for p in sorted(root.rglob("*")) if p.is_file()]


def test_create_renders_c_project(tmp_path, capsys):
    pack_id, _ = _first_pack()
    code = main(
        ["create", "--mcu-config", pack_id, "--lang", "c", "--name", "demo", "--out-dir", str(tmp_path)]
    )
    assert code == 0
    out = capsys.readouterr().out
    proj = tmp_path / "demo"
    files = [p for p in sorted(proj.rglob("*")) if p.is_file()]
    assert files, "rendered file list must be non-empty"
    assert any(p.name == "Makefile" for p in files)
    for text in _rendered_texts(proj):
        assert not PLACEHOLDER.search(text), f"unsubstituted placeholder in:\n{text[:200]}"
    assert "created" in out and "next steps" in out and "stm build" in out


def test_create_accepts_pack_file_path(tmp_path, capsys):
    _, pack_path = _first_pack()
    assert main(["create", "--mcu-config", str(pack_path), "--name", "bypath", "--out-dir", str(tmp_path)]) == 0
    assert (tmp_path / "bypath" / "Makefile").is_file()
    capsys.readouterr()


def test_create_dry_run_writes_nothing(tmp_path, capsys):
    pack_id, _ = _first_pack()
    code = main(
        ["create", "--mcu-config", pack_id, "--name", "demo", "--out-dir", str(tmp_path), "--dry-run"]
    )
    assert code == 0
    assert not (tmp_path / "demo").exists()
    out = capsys.readouterr().out
    assert "demo" in out and pack_id in out


def test_create_flags_only_invocation_exits_2(tmp_path, capsys):
    pack_id, _ = _first_pack()
    assert main(["create", "--name", "demo", "--mcu", pack_id, "--out-dir", str(tmp_path)]) == 2
    assert "--mcu-config" in capsys.readouterr().err


def test_create_missing_config_exits_2(tmp_path, capsys):
    assert main(["create", "--name", "demo", "--out-dir", str(tmp_path)]) == 2
    assert "--mcu-config" in capsys.readouterr().err


def test_create_invalid_pack_id_names_candidates(tmp_path, capsys):
    pack_id, _ = _first_pack()
    code = main(["create", "--mcu-config", "no-such-pack", "--name", "demo", "--out-dir", str(tmp_path)])
    assert code != 0
    assert pack_id in capsys.readouterr().err
