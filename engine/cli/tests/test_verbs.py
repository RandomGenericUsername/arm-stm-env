"""Verb tests (req-005, group 1.2): argparse wiring + dry-run without runtime."""

import pytest

from engine.cli.main import VERBS, build_parser, main


def test_verbs_all_five_registered():
    assert tuple(VERBS) == ("create", "dev", "build", "flash", "debug")


def test_verbs_each_has_help(capsys):
    for verb in VERBS:
        with pytest.raises(SystemExit) as exc:
            build_parser().parse_args([verb, "--help"])
        assert exc.value.code == 0
        out = capsys.readouterr().out
        assert "--dry-run" in out and "--lang" in out and "--mode" in out


@pytest.mark.parametrize("verb", ["dev", "build", "flash", "debug"])
def test_verbs_dry_run_prints_container_argv_without_runtime(capsys, monkeypatch, verb):
    monkeypatch.setattr("shutil.which", lambda _: None)  # no runtime present
    code = main([verb, "--dry-run"])
    assert code == 0
    out = capsys.readouterr().out
    assert "docker" in out and "run" in out and verb in out


def test_verbs_create_dry_run_carries_name(capsys, monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: None)
    assert main(["create", "--name", "demo", "--dry-run"]) == 0
    out = capsys.readouterr().out
    assert "docker" in out and "demo" in out


def test_verbs_local_mode_dry_run_has_no_runtime_wrap(capsys):
    assert main(["build", "--mode", "local", "--dry-run"]) == 0
    out = capsys.readouterr().out.strip()
    assert out.startswith("stm build") and "docker" not in out


def test_verbs_unknown_language_is_usage_error(capsys):
    assert main(["build", "--dry-run", "--lang", "nope"]) == 2
    assert "unknown language" in capsys.readouterr().err


def test_verbs_missing_runtime_fails_fast_with_hint(capsys, monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: None)
    assert main(["build"]) == 1
    assert "not found" in capsys.readouterr().err
