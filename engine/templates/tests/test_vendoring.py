"""Vendoring unit tests (req-011, group 1): pins, mechanism, loud errors, wiring.

All git interaction is faked (monkeypatched ``_run_git`` / ``shutil.which``)
— no network, no repo required. ops-014 mechanism: each pin is a partial
(blob-filtered) + sparse shallow clone at the tag, registered in
``.gitmodules`` + the index, then made a native submodule via
``submodule absorbgitdirs``/``init`` — CMSIS core first.
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
EXPECTED_FAMILY = {"stm32f411re": "stm32f4", "stm32h755": "stm32h7", "stm32wl55jc": "stm32wl"}


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


def _clones(fake: "FakeGit") -> list[list[str]]:
    return [c for c in fake.calls if c[:2] == ["git", "clone"]]


def test_vendor_relative_project_dir_uses_absolute_paths(monkeypatch, tmp_path) -> None:
    """bug-005: default `--path .` passes a relative dir; `git -C <out>` with
    cwd=<out> must not double it into <out>/<out> — vendor resolves to absolute."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "proj").mkdir()
    fake = FakeGit(monkeypatch)
    vendor("stm32f411re", "stm32f4", "proj")
    cfg = next(c for c in fake.calls if "config" in c)
    assert cfg[cfg.index("-C") + 1] == str(tmp_path / "proj")
    assert str(tmp_path / "proj" / ".gitmodules") in cfg
    assert len(_clones(fake)) == 2


def test_pins_match_verified_upstream_tags() -> None:
    assert PINS["CMSIS_5"] == ("https://github.com/ARM-software/CMSIS_5.git", "5.9.0")
    assert FAMILY_REPOS["stm32f4"][1] == "v2.6.9"
    assert FAMILY_REPOS["stm32h7"][1] == "v1.9.0"
    assert FAMILY_REPOS["stm32wl"][1] == "v1.4.0"
    for fam, (url, _tag) in FAMILY_REPOS.items():
        assert url == f"https://github.com/STMicroelectronics/cmsis_device_{fam.removeprefix('stm32')}.git"


@pytest.mark.parametrize("pack_id", PACK_IDS)
def test_family_repo_from_declared_family(pack_id: str) -> None:
    url, tag, dest = family_repo(pack_id, EXPECTED_FAMILY[pack_id])
    fam = EXPECTED_FAMILY[pack_id]
    assert (url, tag) == FAMILY_REPOS[fam]
    assert dest == f"vendor/cmsis-device-{pack_id}"


def test_family_repo_unknown_family_names_it() -> None:
    with pytest.raises(VendorError, match="nope-family"):
        family_repo("synthetic", "nope-family")


@pytest.mark.parametrize("pack_id", PACK_IDS)
def test_vendor_partial_sparse_clone_per_pin(pack_id: str, tmp_path: Path, monkeypatch) -> None:
    """ops-014: each pin is a partial + sparse shallow clone, then a native submodule."""
    fake = FakeGit(monkeypatch)
    got = vendor(pack_id, EXPECTED_FAMILY[pack_id], tmp_path)
    url, tag, dest = family_repo(pack_id, EXPECTED_FAMILY[pack_id])
    clones = _clones(fake)
    assert len(clones) == 2
    cmsis, family = clones
    for call, (u, t, d) in (
        (cmsis, ("https://github.com/ARM-software/CMSIS_5.git", "5.9.0", VENDOR_CORE_PATH)),
        (family, (url, tag, dest)),
    ):
        assert "--filter=blob:none" in call and "--sparse" in call
        assert call[call.index("--depth") + 1] == "1"
        assert call[call.index("--branch") + 1] == t
        assert call[-2] == u and call[-1] == d
    # Only the referenced subtrees are selected ...
    assert any(c[:3] == ["git", "-C", VENDOR_CORE_PATH] and "CMSIS/Core" in c for c in fake.calls)
    assert any(c[:3] == ["git", "-C", dest] and "Include" in c and "Source" in c for c in fake.calls)
    # ... and each becomes a native submodule (absorb + init), never a full clone.
    assert any(c[-2:] == ["absorbgitdirs", dest] for c in fake.calls)
    assert any(c[-2:] == ["init", dest] for c in fake.calls)
    assert got == [tmp_path / VENDOR_CORE_PATH, tmp_path / dest]


def test_vendor_offline_unreachable_remote_fails_loud(tmp_path: Path, monkeypatch) -> None:
    """Offline simulation: clone fails → non-zero naming the URL."""
    fake = FakeGit(
        monkeypatch,
        fail={("git", "clone"): (128, "", "fatal: unable to connect to github.com")},
    )
    with pytest.raises(VendorError, match="github.com/STMicroelectronics|github.com/ARM-software"):
        vendor("stm32f411re", "stm32f4", tmp_path)
    assert fake.calls[1][:2] == ["git", "clone"]


def test_vendor_sparse_checkout_failure_names_subtree(tmp_path: Path, monkeypatch) -> None:
    FakeGit(
        monkeypatch,
        fail={("git", "-C", VENDOR_CORE_PATH, "sparse-checkout"): (128, "", "error: pathspec did not match")},
    )
    with pytest.raises(VendorError, match="subtree"):
        vendor("stm32f411re", "stm32f4", tmp_path)


def test_vendor_missing_git_names_git(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda _cmd: None)
    with pytest.raises(VendorError, match="git"):
        vendor("stm32f411re", "stm32f4", tmp_path)


def test_vendor_non_repo_out_dir_runs_git_init(tmp_path: Path, monkeypatch) -> None:
    """Fresh dir: vendor git-inits the project, then adds the pins."""
    out = tmp_path / "proj"
    out.mkdir()
    fake = FakeGit(monkeypatch, inside=False)
    vendor("stm32f411re", "stm32f4", out)
    assert ["git", "init"] in fake.calls
    assert len(_clones(fake)) == 2


def test_vendor_init_failure_names_path(tmp_path: Path, monkeypatch) -> None:
    out = tmp_path / "proj"
    out.mkdir()
    FakeGit(monkeypatch, inside=False, fail={("git", "init"): (128, "", "fatal: cannot init")})
    with pytest.raises(VendorError, match="git init"):
        vendor("stm32f411re", "stm32f4", out)


def test_vendor_missing_out_dir_names_path(tmp_path: Path, monkeypatch) -> None:
    FakeGit(monkeypatch)
    with pytest.raises(VendorError, match="does not exist"):
        vendor("stm32f411re", "stm32f4", tmp_path / "nope")


@pytest.mark.parametrize("pack_id", PACK_IDS)
@pytest.mark.parametrize("lang", ("c", "cpp"))
def test_render_vendors_c_cpp(pack_id: str, lang: str, tmp_path: Path, monkeypatch) -> None:
    """Wiring 1.2: render() ends in vendor() for C/C++ (faked git, no network)."""
    fake = FakeGit(monkeypatch)
    device = load_file(PACKS_DIR / f"{pack_id}.yaml")
    render(device, lang, tmp_path)
    clones = _clones(fake)
    assert len(clones) == 2
    assert clones[0][-2] == "https://github.com/ARM-software/CMSIS_5.git"
    assert clones[0][-1] == VENDOR_CORE_PATH
    assert clones[1][-2] == FAMILY_REPOS[EXPECTED_FAMILY[pack_id]][0]
    assert clones[1][-1] == f"vendor/cmsis-device-{pack_id}"


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
        fail={("git", "clone"): (128, "", "fatal: unable to connect to github.com")},
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
