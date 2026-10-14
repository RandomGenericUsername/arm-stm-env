"""Shim lookup tests (req-005, group 2.1): language->image via core interface."""

import pytest

from engine.adapters import DefaultImageLookup, ImageLookup
from engine.cli.main import main
from engine.cli.shim import ShimRequest, build_container_argv, engine_root, packs_dir


class _RecordingLookup(ImageLookup):
    def __init__(self) -> None:
        self.seen: list[str] = []

    def image_for(self, lang: str) -> str:
        self.seen.append(lang)
        return f"img-{lang}:v1"

    def supported_langs(self) -> tuple[str, ...]:
        return ("c",)


def test_shim_lookup_maps_languages_via_core_interface():
    lookup = DefaultImageLookup()
    assert lookup.image_for("c") == "ghcr.io/randomgenericusername/lang-cpp:15.3.rel2"
    assert lookup.image_for("cpp") == "ghcr.io/randomgenericusername/lang-cpp:15.3.rel2"
    assert lookup.image_for("rust") == "ghcr.io/randomgenericusername/lang-rust:1.99.0"
    with pytest.raises(ValueError):
        lookup.image_for("nope")


def test_shim_lookup_uses_injected_core_interface():
    rec = _RecordingLookup()
    argv = build_container_argv(ShimRequest(verb="build", lang="c"), lookup=rec)
    assert rec.seen == ["c"]
    assert "img-c:v1" in argv


@pytest.mark.parametrize("lang", ["c", "cpp", "rust"])
def test_shim_lookup_identical_resolution_both_modes(lang, tmp_path):
    lookup = DefaultImageLookup()
    auto = build_container_argv(
        ShimRequest(verb="build", lang=lang, mode="auto", project_dir=str(tmp_path)),
        lookup=lookup,
    )
    assert lookup.image_for(lang) in auto  # same image host-side ...
    # ... and the container side runs the engine, never the bare CLI:
    assert "mu" not in auto
    assert "python3" in auto and "-m" in auto and "engine" in auto
    assert "--mode" in auto and "local" in auto
    with pytest.raises(ValueError):
        build_container_argv(
            ShimRequest(verb="build", lang=lang, mode="local"), lookup=lookup
        )  # local executes in-process; no container argv exists


def test_shim_lookup_dry_run_equivalence_auto_vs_local(capsys, tmp_path):
    assert main(["build", "--lang", "cpp", "--dry-run"]) == 0
    auto_out = capsys.readouterr().out
    assert DefaultImageLookup().image_for("cpp") in auto_out
    assert main(["build", "--lang", "cpp", "--mode", "local", "--dry-run"]) == 0
    local_out = capsys.readouterr().out.strip()
    assert local_out == "cd . && make build"
    assert "docker" not in local_out
    # identical resolution: auto wraps the same lang/image pair
    assert "--lang cpp" in auto_out


def test_shim_lookup_unknown_lang_rejected():
    with pytest.raises(ValueError):
        build_container_argv(ShimRequest(verb="build", lang="nope", mode="auto"))


def test_shim_container_argv_mounts_engine_and_project(tmp_path):
    argv = build_container_argv(
        ShimRequest(verb="build", lang="c", project_dir=str(tmp_path))
    )
    assert "-v" in argv
    joined = " ".join(argv)
    assert f"{tmp_path.resolve()}:/project:rw" in joined
    assert f"{engine_root()}:/opt/mu/engine:ro" in argv
    assert f"{packs_dir()}:/opt/mu/packs:ro" in argv
    assert "PYTHONPATH=/opt/mu" in joined
    assert "-w" in argv and "/project" in argv
    assert "--project-dir" in argv and "/project" in argv


def test_shim_dev_argv_is_interactive_shell(tmp_path):
    argv = build_container_argv(
        ShimRequest(verb="dev", lang="c", interactive=True,
                    project_dir=str(tmp_path))
    )
    assert "-it" in argv
    assert argv[-1] == "/bin/bash"
    assert "python3" not in argv
