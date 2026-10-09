"""Shim lookup tests (req-005, group 2.1): language->image via core interface."""

import pytest

from engine.adapters import DefaultImageLookup, ImageLookup
from engine.cli.main import main
from engine.cli.shim import ShimRequest, build_container_argv


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
    assert lookup.image_for("c") == "ghcr.io/arm-stm-env/lang-c:latest"
    assert lookup.image_for("cpp") == "ghcr.io/arm-stm-env/lang-cpp:latest"
    assert lookup.image_for("rust") == "ghcr.io/arm-stm-env/lang-rust:latest"
    with pytest.raises(ValueError):
        lookup.image_for("nope")


def test_shim_lookup_uses_injected_core_interface():
    rec = _RecordingLookup()
    argv = build_container_argv(ShimRequest(verb="build", lang="c"), lookup=rec)
    assert rec.seen == ["c"]
    assert "img-c:v1" in argv


@pytest.mark.parametrize("lang", ["c", "cpp", "rust"])
def test_shim_lookup_identical_resolution_both_modes(lang):
    lookup = DefaultImageLookup()
    auto = build_container_argv(
        ShimRequest(verb="build", lang=lang, mode="auto"), lookup=lookup
    )
    local = build_container_argv(
        ShimRequest(verb="build", lang=lang, mode="local"), lookup=lookup
    )
    assert lookup.image_for(lang) in auto  # same image host-side ...
    assert local == ["stm", "build", "--lang", lang]  # ... and inside-container
    assert auto[-3:] == ["stm", "build", "--lang"] or "--lang" in auto


def test_shim_lookup_dry_run_equivalence_auto_vs_local(capsys):
    assert main(["build", "--lang", "cpp", "--dry-run"]) == 0
    auto_out = capsys.readouterr().out
    assert DefaultImageLookup().image_for("cpp") in auto_out
    assert main(["build", "--lang", "cpp", "--mode", "local", "--dry-run"]) == 0
    local_out = capsys.readouterr().out.strip()
    assert local_out == "stm build --lang cpp"
    # identical resolution: auto wraps the same lang/image pair
    assert "--lang cpp" in auto_out


def test_shim_lookup_unknown_lang_rejected_both_modes():
    with pytest.raises(ValueError):
        build_container_argv(ShimRequest(verb="build", lang="nope", mode="auto"))
    with pytest.raises(ValueError):
        build_container_argv(ShimRequest(verb="build", lang="nope", mode="local"))
