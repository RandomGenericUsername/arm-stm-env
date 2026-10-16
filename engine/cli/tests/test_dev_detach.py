"""Detached dev-container tests (task-019).

`dev --detach` starts a long-running, named container an editor can attach to,
instead of an interactive shell (`-it /bin/bash`) that dies with its terminal.
"""

import pytest

from engine.cli.main import _dev_container_name
from engine.cli.shim import (
    ShimRequest,
    build_container_argv,
    build_probe_argv,
    detach_command,
)


def _detached(name="mu-dev-x", env_setup=". /opt/esp/idf/export.sh"):
    return build_container_argv(
        ShimRequest(verb="dev", stack="idf-cmake", detach=True, name=name,
                    env_setup=env_setup, project_dir=".")
    )


def test_detach_argv_runs_detached_and_named():
    argv = _detached()
    assert "-d" in argv
    assert argv[argv.index("--name") + 1] == "mu-dev-x"
    # a detached run has no terminal and must not self-remove on stop
    assert "-it" not in argv
    assert "--rm" not in argv


def test_detach_command_keeps_the_container_up_and_exposes_the_toolchain():
    inner = _detached()[-1]
    assert "exec sleep infinity" in inner          # liveness only
    assert ". /opt/esp/idf/export.sh" in inner      # exec'd shells get idf.py
    assert "zz-mu-env" in inner                     # via the shell profile


def test_detach_command_without_env_setup_is_just_liveness():
    assert detach_command("") == "exec sleep infinity"


def test_interactive_dev_is_unchanged():
    argv = build_container_argv(
        ShimRequest(verb="dev", stack="make-cmsis", interactive=True, project_dir=".")
    )
    assert "-it" in argv and argv[-1] == "/bin/bash"
    assert "-d" not in argv


def test_detach_requires_a_container_name():
    with pytest.raises(ValueError, match="name"):
        build_container_argv(ShimRequest(verb="dev", stack="make-cmsis", detach=True))


def test_mount_preflight_never_detaches_or_claims_the_name():
    probe = build_probe_argv(
        ShimRequest(verb="dev", stack="idf-cmake", detach=True, name="mu-dev-x",
                    project_dir=".")
    )
    assert "-d" not in probe and "--name" not in probe
    assert probe[-1] == "true"


def test_dev_container_name_is_stable_and_sanitised():
    assert _dev_container_name("/home/u/Desktop/my-board") == "mu-dev-my-board"
    assert _dev_container_name("/tmp/weird name!") == "mu-dev-weird-name-"
