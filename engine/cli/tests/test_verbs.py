"""Verb tests (req-005, group 1.2): argparse wiring + dry-run without runtime."""

import pytest

from engine.cli.main import VERBS, build_parser, main


def _project(tmp_path, stack="make-cmsis"):
    """A minimal mu project: the persisted build stack (AD-11)."""
    (tmp_path / ".mu").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".mu" / "stack").write_text(stack + "\n")
    return tmp_path


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
def test_verbs_dry_run_prints_container_argv_without_runtime(capsys, monkeypatch, tmp_path, verb):
    monkeypatch.setattr("shutil.which", lambda _: None)  # no runtime present
    proj = _project(tmp_path)
    code = main([verb, "--dry-run", "--project-dir", str(proj)])
    assert code == 0
    out = capsys.readouterr().out
    assert "docker" in out and "run" in out
    # `dev` runs an interactive shell, not an engine verb word.
    assert ("/bin/bash" if verb == "dev" else verb) in out


def test_verbs_create_dry_run_renders_locally_without_runtime(capsys, monkeypatch, tmp_path):
    from pathlib import Path

    from engine.cli.main import PACKS_DIR

    pack = sorted(Path(PACKS_DIR).glob("*.yaml"))[0]
    monkeypatch.setattr("shutil.which", lambda _: None)
    assert (
        main(["create", "--name", "demo", "--mcu-config", str(pack), "--path", str(tmp_path), "--dry-run"])
        == 0
    )
    out = capsys.readouterr().out
    assert "demo" in out and pack.stem in out
    assert not (tmp_path / "demo").exists()


def test_verbs_local_mode_dry_run_has_no_runtime_wrap(capsys, tmp_path):
    proj = _project(tmp_path)
    assert main(["build", "--mode", "local", "--dry-run", "--project-dir", str(proj)]) == 0
    out = capsys.readouterr().out.strip()
    assert out == f"cd {proj} && make build" and "docker" not in out


def test_verbs_local_build_runs_toolchain(monkeypatch, tmp_path):
    calls: list = []

    class _Done:
        returncode = 0

    monkeypatch.setattr(
        "subprocess.run",
        lambda cmd, **kw: calls.append((cmd, kw)) or _Done(),
    )
    _project(tmp_path)
    assert main(["build", "--mode", "local", "--project-dir", str(tmp_path)]) == 0
    assert calls == [(["make", "build"], {"cwd": str(tmp_path)})]


def test_verbs_local_build_rust_runs_cargo(monkeypatch, tmp_path):
    calls: list = []

    class _Done:
        returncode = 0

    monkeypatch.setattr(
        "subprocess.run",
        lambda cmd, **kw: calls.append((cmd, kw)) or _Done(),
    )
    _project(tmp_path, stack="cargo-cortex")
    assert main(["build", "--lang", "rust", "--mode", "local",
                  "--project-dir", str(tmp_path)]) == 0
    assert calls == [(["cargo", "build"], {"cwd": str(tmp_path)})]


def test_verbs_mcu_config_outside_project_rejected(capsys, tmp_path):
    outside = tmp_path / "elsewhere.yaml"
    outside.write_text("target: x\n")
    assert main(["flash", "--mcu-config", str(outside),
                  "--project-dir", str(tmp_path / "proj"),
                  "--files", "a.elf"]) == 2
    assert "outside --project-dir" in capsys.readouterr().err


def test_verbs_flash_missing_config_is_usage_error(capsys):
    assert main(["flash", "--mode", "local", "--files", "a.elf"]) == 2
    assert "--mcu-config" in capsys.readouterr().err


def test_verbs_flash_files_forwarded_into_container(capsys, tmp_path):
    from pathlib import Path

    from engine.cli.main import PACKS_DIR

    pack = sorted(Path(PACKS_DIR).glob("*.yaml"))[0].stem
    proj = tmp_path / "proj"
    proj.mkdir()
    assert main(["flash", "--mcu-config", pack,
                  "--project-dir", str(proj),
                  "--files", "a.elf", "b.elf", "--dry-run"]) == 0
    out = capsys.readouterr().out
    assert "--files a.elf b.elf" in out and "docker" in out


def test_verbs_unknown_language_is_usage_error(capsys):
    assert main(["build", "--dry-run", "--lang", "nope"]) == 2
    assert "unknown language" in capsys.readouterr().err


def test_verbs_missing_runtime_fails_fast_with_hint(capsys, monkeypatch, tmp_path):
    monkeypatch.setattr("shutil.which", lambda _: None)
    proj = _project(tmp_path)
    assert main(["build", "--project-dir", str(proj)]) == 1
    assert "not found" in capsys.readouterr().err


def test_verbs_probe_unknown_backend_is_usage_error(capsys, tmp_path):
    from pathlib import Path

    from engine.cli.main import PACKS_DIR

    pack = sorted(Path(PACKS_DIR).glob("*.yaml"))[0]
    code = main(["flash", "--mcu-config", str(pack), "--probe", "nope",
                 "--device", "/dev/x", "--files", "a.elf",
                 "--mode", "local", "--project-dir", str(tmp_path)])
    assert code == 2
    assert "unknown probe backend" in capsys.readouterr().err


def test_verbs_probe_defaults_to_pack_backend(monkeypatch, tmp_path, capsys):
    from pathlib import Path

    from engine.adapters import PieceResult
    import sys
    from engine.cli.main import PACKS_DIR, load_file, main

    pack = sorted(Path(PACKS_DIR).glob("*.yaml"))[0]
    expected = load_file(pack).probe_backend
    assert expected, "shipped pack must declare a probe default for this test"
    seen: list = []

    class _Fake:
        def flash(self, device, endpoint, pieces):
            return [PieceResult(name=p, ok=True) for p in pieces]

        def debug(self, device, endpoint):
            raise AssertionError("not under test")

        @property
        def last_transcript(self):
            return None

    def _factory(name=None, **kwargs):
        seen.append((name, kwargs))
        return _Fake()

    monkeypatch.setattr(sys.modules["engine.cli.main"], "get_adapter", _factory)
    code = main(["flash", "--mcu-config", str(pack), "--device", "/dev/x",
                 "--files", "a.elf", "--mode", "local",
                 "--project-dir", str(tmp_path)])
    assert code == 0
    assert seen == [(expected, {"stream": True, "log_path": None})]
    assert "2" not in capsys.readouterr().err


def test_verbs_verbose_forwarded_into_container(capsys, tmp_path):
    proj = tmp_path / "proj"
    proj.mkdir()
    _project(proj)
    assert main(
        ["flash", "--project-dir", str(proj), "--files", "a.elf", "--verbose", "--dry-run"]
    ) == 0
    out = capsys.readouterr().out
    assert "--verbose" in out and "--files a.elf" in out


def test_verbs_missing_image_names_make_images(capsys, monkeypatch, tmp_path):
    import subprocess

    class _Proc:
        def __init__(self, rc):
            self.returncode = rc

    def _fake_run(cmd, **kw):
        if cmd[:3] == ["docker", "image", "inspect"]:
            return _Proc(1)
        raise AssertionError(f"should stop before exec: {cmd}")

    monkeypatch.setattr(subprocess, "run", _fake_run)
    proj = _project(tmp_path)
    code = main(["build", "--project-dir", str(proj)])
    assert code == 1
    assert "make images" in capsys.readouterr().err


def test_verbs_verbose_creates_log_dir(monkeypatch, tmp_path, capsys):
    import sys as _sys

    from pathlib import Path

    from engine.adapters import PieceResult
    from engine.cli.main import PACKS_DIR, load_file

    pack = sorted(Path(PACKS_DIR).glob("*.yaml"))[0]
    seen: list = []

    class _Fake:
        def flash(self, device, endpoint, pieces):
            return [PieceResult(name=p, ok=True) for p in pieces]

        def debug(self, device, endpoint):
            raise AssertionError("not under test")

        @property
        def last_transcript(self):
            return None

    def _factory(name=None, **kwargs):
        seen.append(kwargs)
        return _Fake()

    monkeypatch.setattr(_sys.modules["engine.cli.main"], "get_adapter", _factory)
    proj = tmp_path / "proj"
    proj.mkdir()
    code = main(["flash", "--mcu-config", str(pack), "--device", "/dev/x",
                 "--files", "a.elf", "--mode", "local", "--verbose",
                 "--project-dir", str(proj)])
    assert code == 0
    assert (proj / ".mu" / "logs").is_dir()
    assert seen and seen[0].get("stream") is True
    assert str(seen[0].get("log_path", "")).startswith(str(proj / ".mu" / "logs"))


def test_verbs_debug_fails_when_backend_has_no_debug_port(monkeypatch, tmp_path, capsys):
    """AD-12: a programming-only backend fails the debug verb, no fake handle."""
    import sys as _sys
    from pathlib import Path

    from engine.adapters import FlashPort, PieceResult
    from engine.cli.main import PACKS_DIR

    pack = sorted(Path(PACKS_DIR).glob("*.yaml"))[0]

    class _FlashOnly(FlashPort):
        last_transcript = None

        def render_argv(self, device, endpoint, pieces):
            return ["program-only", *pieces]

        def flash(self, device, endpoint, pieces):
            return [PieceResult(name=p, ok=True) for p in pieces]

        def proof_for(self, device, results, transcript):
            from engine.core.model import ProofResult

            return ProofResult(rung=device.proof_rung, payload={})

    monkeypatch.setattr(
        _sys.modules["engine.cli.main"],
        "get_adapter",
        lambda name=None, **kwargs: _FlashOnly(),
    )
    code = main(
        ["debug", "--mcu-config", str(pack), "--device", "/dev/x",
         "--mode", "local", "--project-dir", str(tmp_path)]
    )
    assert code == 2
    assert "no debug port" in capsys.readouterr().err


def test_verbs_build_uses_project_stack_not_language(monkeypatch, tmp_path):
    """AD-11: the persisted stack — not --lang — selects the build command."""
    calls: list = []

    class _Done:
        returncode = 0

    monkeypatch.setattr("subprocess.run", lambda cmd, **kw: calls.append(cmd) or _Done())
    _project(tmp_path, stack="cargo-cortex")
    assert main(["build", "--lang", "c", "--mode", "local", "--project-dir", str(tmp_path)]) == 0
    assert calls == [["cargo", "build"]]


def test_verbs_build_without_a_stack_errors_clearly(capsys, tmp_path):
    assert main(["build", "--mode", "local", "--project-dir", str(tmp_path)]) == 2
    assert "no build stack" in capsys.readouterr().err
