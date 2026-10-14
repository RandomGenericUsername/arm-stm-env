"""Vendoring unit tests (req-011, group 1): pins, mechanism, loud errors, wiring.

All git interaction is faked (monkeypatched ``_run_git`` / ``shutil.which``)
— no network, no repo required. Command sequences are asserted exactly:
``git submodule add <url> <path>`` then detached ``git -C <path> checkout
<tag>`` per pin, CMSIS core first.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from engine.core.loader import load_file
from engine.templates import vendoring
from engine.templates.renderer import render
from engine.templates.vendoring import (
    FAMILY_REPOS,
    PINS,
    VENDOR_CORE_PATH,
    VendorError,
    family_repo,
    vendor,
)

from .test_cells import PACKS_DIR

PACK_IDS = ("stm32f411re", "stm32h755", "stm32wl55jc")
EXPECTED_FAMILY = {"stm32f411re": "f4", "stm32h755": "h7", "stm32wl55jc": "wl"}


def _ok(args, cwd):
    return subprocess.CompletedProcess(args, 0, stdout="true\n", stderr="")


class FakeGit:
    """Records argv; per-command (returncode, stdout, stderr) overrides.

    ``inside`` feeds the ``rev-parse --is-inside-work-tree`` probe: True (a
    repo) or False (fresh dir → vendor should ``git init``).
    """

    def __init__(self, monkeypatch, fail: dict | None = None, inside: bool = True):
        self.calls: list[list[str]] = []
        self.fail = fail or {}
        self.inside = inside
        monkeypatch.setattr(vendoring, "_run_git", self)

    def __call__(self, args, cwd):
        self.calls.append(list(args))
        key = tuple(args)
        for pattern, result in self.fail.items():
            if list(pattern) == list(args[: len(pattern)]):
                return subprocess.CompletedProcess(args, *result)
        if args[:2] == ["git", "-C"] and args[3:5] == ["rev-parse", "--is-inside-work-tree"]:
            return subprocess.CompletedProcess(
                args, 0, stdout=("true\n" if self.inside else "false\n"), stderr=""
            )
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")


def test_pins_match_verified_upstream_tags() -> None:
    assert PINS["CMSIS_5"] == ("https://github.com/ARM-software/CMSIS_5.git", "5.9.0")
    assert FAMILY_REPOS["f4"][1] == "v2.6.9"
    assert FAMILY_REPOS["h7"][1] == "v1.9.0"
    assert FAMILY_REPOS["wl"][1] == "v1.4.0"
    for fam, (url, _tag) in FAMILY_REPOS.items():
        assert url == f"https://github.com/STMicroelectronics/cmsis_device_{fam}.git"


@pytest.mark.parametrize("pack_id", PACK_IDS)
def test_family_repo_from_pack_prefix(pack_id: str) -> None:
    url, tag, dest = family_repo(pack_id)
    fam = EXPECTED_FAMILY[pack_id]
    assert (url, tag) == FAMILY_REPOS[fam]
    assert dest == f"vendor/cmsis-device-{pack_id}"


def test_family_repo_unknown_pack_names_pack_id() -> None:
    with pytest.raises(VendorError, match="synthetic"):
        family_repo("synthetic")


@pytest.mark.parametrize("pack_id", PACK_IDS)
def test_vendor_add_then_detached_checkout_per_pin(pack_id: str, tmp_path: Path, monkeypatch) -> None:
    fake = FakeGit(monkeypatch)
    got = vendor(pack_id, tmp_path)
    url, tag, dest = family_repo(pack_id)
    assert fake.calls == [
        ["git", "-C", str(tmp_path), "rev-parse", "--is-inside-work-tree"],
        ["git", "submodule", "add", "https://github.com/ARM-software/CMSIS_5.git", VENDOR_CORE_PATH],
        ["git", "-C", VENDOR_CORE_PATH, "checkout", "5.9.0"],
        ["git", "-C", str(tmp_path), "add", VENDOR_CORE_PATH],
        ["git", "submodule", "add", url, dest],
        ["git", "-C", dest, "checkout", tag],
        ["git", "-C", str(tmp_path), "add", dest],
    ]
    assert got == [tmp_path / VENDOR_CORE_PATH, tmp_path / dest]


def test_vendor_offline_unreachable_remote_fails_loud(tmp_path: Path, monkeypatch) -> None:
    """Offline simulation: submodule add fails → non-zero naming the URL."""
    fake = FakeGit(
        monkeypatch,
        fail={("git", "submodule", "add"): (128, "", "fatal: unable to connect to github.com")},
    )
    with pytest.raises(VendorError, match="github.com/STMicroelectronics|github.com/ARM-software"):
        vendor("stm32f411re", tmp_path)
    assert fake.calls[1][:3] == ["git", "submodule", "add"]


def test_vendor_checkout_failure_names_tag(tmp_path: Path, monkeypatch) -> None:
    fake = FakeGit(
        monkeypatch,
        fail={("git", "-C", VENDOR_CORE_PATH, "checkout"): (128, "", "error: pathspec '5.9.0' did not match")},
    )
    with pytest.raises(VendorError, match="5.9.0"):
        vendor("stm32f411re", tmp_path)
    assert any(c[:3] == ["git", "-C", VENDOR_CORE_PATH] for c in fake.calls)


def test_vendor_missing_git_names_git(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda _cmd: None)
    with pytest.raises(VendorError, match="git"):
        vendor("stm32f411re", tmp_path)


def test_vendor_non_repo_out_dir_runs_git_init(tmp_path: Path, monkeypatch) -> None:
    """Fresh dir: vendor git-inits the project, then adds the pins."""
    out = tmp_path / "proj"
    out.mkdir()
    fake = FakeGit(monkeypatch, inside=False)
    vendor("stm32f411re", out)
    assert ["git", "init"] in fake.calls
    adds = [c for c in fake.calls if c[:3] == ["git", "submodule", "add"]]
    assert len(adds) == 2


def test_vendor_init_failure_names_path(tmp_path: Path, monkeypatch) -> None:
    out = tmp_path / "proj"
    out.mkdir()
    FakeGit(monkeypatch, inside=False, fail={("git", "init"): (128, "", "fatal: cannot init")})
    with pytest.raises(VendorError, match="git init"):
        vendor("stm32f411re", out)


def test_vendor_missing_out_dir_names_path(tmp_path: Path, monkeypatch) -> None:
    FakeGit(monkeypatch)
    with pytest.raises(VendorError, match="does not exist"):
        vendor("stm32f411re", tmp_path / "nope")


@pytest.mark.parametrize("pack_id", PACK_IDS)
@pytest.mark.parametrize("lang", ("c", "cpp"))
def test_render_vendors_c_cpp(pack_id: str, lang: str, tmp_path: Path, monkeypatch) -> None:
    """Wiring 1.2: render() ends in vendor() for C/C++ (faked git, no network)."""
    fake = FakeGit(monkeypatch)
    device = load_file(PACKS_DIR / f"{pack_id}.yaml")
    render(device, lang, tmp_path)
    adds = [c for c in fake.calls if c[:3] == ["git", "submodule", "add"]]
    assert len(adds) == 2
    assert adds[0][3] == "https://github.com/ARM-software/CMSIS_5.git"
    assert adds[1][3] == FAMILY_REPOS[EXPECTED_FAMILY[pack_id]][0]
    assert adds[1][4] == f"vendor/cmsis-device-{pack_id}"


@pytest.mark.parametrize("pack_id", PACK_IDS)
def test_render_rust_has_no_vendor_tree(pack_id: str, tmp_path: Path, monkeypatch) -> None:
    """Wiring 1.2: Rust renders vendor nothing — git must never be invoked."""
    def _boom(args, cwd):
        raise AssertionError(f"git must not run for rust: {args}")

    monkeypatch.setattr(vendoring, "_run_git", _boom)
    device = load_file(PACKS_DIR / f"{pack_id}.yaml")
    render(device, "rust", tmp_path)
    assert not (tmp_path / "vendor").exists()


def test_render_vendor_failure_propagates_loud(tmp_path: Path, monkeypatch, capsys) -> None:
    """Strictness: vendor failure breaks render (create exits non-zero, never silent)."""
    from engine.cli.main import main

    FakeGit(
        monkeypatch,
        fail={("git", "submodule", "add"): (128, "", "fatal: unable to connect to github.com")},
    )
    device = load_file(PACKS_DIR / "stm32f411re.yaml")
    with pytest.raises(VendorError, match="github.com"):
        render(device, "c", tmp_path)
    code = main(
        ["create", "--mcu-config", "stm32f411re", "--lang", "c",
         "--name", "demo", "--path", str(tmp_path)]
    )
    assert code != 0
    assert "github.com" in capsys.readouterr().err


def test_create_missing_git_exits_nonzero_naming_git(tmp_path: Path, monkeypatch, capsys) -> None:
    from engine.cli.main import main

    monkeypatch.setattr(shutil, "which", lambda _cmd: None)
    code = main(
        ["create", "--mcu-config", "stm32f411re", "--lang", "c",
         "--name", "demo", "--path", str(tmp_path)]
    )
    assert code != 0
    assert "git" in capsys.readouterr().err
