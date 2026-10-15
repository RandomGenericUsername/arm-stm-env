"""Mount-preflight tests (bug-022): probe argv, failure parsing, verb wiring."""

import subprocess

from engine.cli.main import main
from engine.cli.shim import (
    ShimRequest,
    build_container_argv,
    build_probe_argv,
    parse_mount_failure,
)

import pytest

MACOS_DAEMON_STDERR = (
    "docker: Error response from daemon: error while creating mount source path "
    "'/host_mnt/Users/juan.david/Desktop/personal/test-project': "
    "mkdir /host_mnt/Users/juan.david/Desktop: operation not permitted\n"
    "\n"
    "Run 'docker run --help' for more information\n"
)

LINUX_DAEMON_STDERR = (
    "docker: Error response from daemon: error while creating mount source path "
    "'/root/owned-proj': mkdir /root/owned-proj: permission denied\n"
)


def test_probe_argv_mirrors_run_mounts_and_runs_true():
    request = ShimRequest(verb="build", lang="c", project_dir=".")
    run = build_container_argv(request)
    probe = build_probe_argv(request)
    image = run[run.index("-w") + 2]
    assert probe[: probe.index(image) + 1] == run[: run.index(image) + 1]
    assert probe[probe.index(image) + 1 :] == ["true"]
    assert "-it" not in probe


def test_probe_argv_dev_request_is_not_interactive():
    request = ShimRequest(verb="dev", lang="c", project_dir=".", interactive=True)
    assert "-it" in build_container_argv(request)
    probe = build_probe_argv(request)
    assert "-it" not in probe and probe[-1] == "true"


def test_probe_argv_local_mode_raises():
    with pytest.raises(ValueError):
        build_probe_argv(ShimRequest(verb="build", mode="local"))


def test_parse_mount_failure_macos_host_mnt():
    assert parse_mount_failure(MACOS_DAEMON_STDERR) == (
        "/Users/juan.david/Desktop/personal/test-project"
    )


def test_parse_mount_failure_plain_path_verbatim():
    assert parse_mount_failure(LINUX_DAEMON_STDERR) == "/root/owned-proj"


def test_parse_mount_failure_unrelated_is_none():
    assert parse_mount_failure("Error: No such image: foo:latest\n") is None
    assert parse_mount_failure("") is None


class _Proc:
    def __init__(self, rc=0, stderr=""):
        self.returncode = rc
        self.stderr = stderr


class _FakeProc:
    """Minimal Popen double: iterable stderr + wait()."""

    def __init__(self, rc, lines):
        self._rc = rc
        self.stderr = iter(lines)

    def wait(self):
        return self._rc


def _auto_mocks(monkeypatch, probe, run_rc=0, run_lines=()):
    """Mock docker-present, image-present, scripted probe; fail if real run used."""
    monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/docker")

    def _fake_run(cmd, **kw):
        if cmd[:3] == ["docker", "image", "inspect"]:
            return _Proc(0)
        assert cmd[-1] == "true", f"expected probe argv, got: {cmd}"
        return probe

    monkeypatch.setattr(subprocess, "run", _fake_run)
    calls: list = []

    def _no_exec(*args, **kwargs):
        calls.append((args, kwargs))
        raise AssertionError(f"real run must not execute: {args[0]}")

    monkeypatch.setattr(subprocess, "Popen", _no_exec)
    return calls


def test_main_probe_mount_failure_hint_and_no_exec(monkeypatch, tmp_path, capsys):
    _auto_mocks(monkeypatch, _Proc(1, MACOS_DAEMON_STDERR))
    assert main(["build", "--project-dir", str(tmp_path)]) == 1
    err = capsys.readouterr().err
    assert "cannot mount '/Users/juan.david/Desktop/personal/test-project'" in err
    assert "File Sharing" in err


def test_main_probe_non_mount_failure_relayed(monkeypatch, tmp_path, capsys):
    _auto_mocks(monkeypatch, _Proc(125, "docker: daemon explosion\n"))
    assert main(["build", "--project-dir", str(tmp_path)]) == 1
    err = capsys.readouterr().err
    assert "daemon explosion" in err and "cannot mount" not in err


def test_main_probe_ok_executes_and_passes_code(monkeypatch, tmp_path):
    _auto_mocks(monkeypatch, _Proc(0))
    seen: list = []

    def _fake_popen(argv, **kw):
        seen.append(argv)
        return _FakeProc(3, [])

    monkeypatch.setattr(subprocess, "Popen", _fake_popen)
    assert main(["build", "--project-dir", str(tmp_path)]) == 3
    assert seen and seen[0][:3] == ["docker", "run", "--rm"]


def test_main_late_mount_failure_hint_with_daemon_code(monkeypatch, tmp_path, capsys):
    _auto_mocks(monkeypatch, _Proc(0))

    def _fake_popen(argv, **kw):
        return _FakeProc(1, MACOS_DAEMON_STDERR.splitlines(keepends=True))

    monkeypatch.setattr(subprocess, "Popen", _fake_popen)
    assert main(["build", "--project-dir", str(tmp_path)]) == 1
    err = capsys.readouterr().err
    assert "operation not permitted" in err  # streamed live
    assert "cannot mount '/Users/juan.david/Desktop/personal/test-project'" in err
