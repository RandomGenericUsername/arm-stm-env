"""Transcript retention for proof wiring (task-005).

``flash()`` keeps its transcript so callers can fill proof structs without
widening the port ABC.
"""

from engine.adapters.openocd import VERIFY_OK_FIXTURE, OpenOCDAdapter
from engine.adapters.probe_rs import ProbeRsAdapter
from engine.adapters.tests.test_openocd import _device_view, _endpoint, _fake_runner
from engine.adapters.tests.test_probe_rs import (
    VERIFY_OK_FIXTURE as RS_VERIFY_OK_FIXTURE,
)
from engine.adapters.tests.test_probe_rs import _fake_runner as _rs_fake_runner


def test_openocd_keeps_last_transcript():
    adapter = OpenOCDAdapter(runner=_fake_runner(VERIFY_OK_FIXTURE))
    assert adapter.last_transcript is None
    results = adapter.flash(_device_view(), _endpoint(), ["fw.elf"])
    assert [r.ok for r in results] == [True]
    assert adapter.last_transcript is not None
    proof = adapter.proof_for(_device_view(), results, adapter.last_transcript)
    assert proof.rung == "frame" and "fw.elf=ok" in dict(proof.payload)["pieces"]


def test_probe_rs_keeps_last_transcript():
    adapter = ProbeRsAdapter(runner=_rs_fake_runner(RS_VERIFY_OK_FIXTURE))
    results = adapter.flash(_device_view(), _endpoint(), ["fw.elf"])
    assert adapter.last_transcript is not None
    proof = adapter.proof_for(_device_view(), results, adapter.last_transcript)
    assert proof.rung == "frame"


def test_streaming_runner_passes_output_live_and_captures(capsys, tmp_path):
    import sys as _sys

    from engine.adapters.openocd import subprocess_runner

    log = tmp_path / "tool.log"
    tool = [_sys.executable, "-c", "print('progress-line')"]
    tx = subprocess_runner(tool, stream=True, log_path=str(log))
    assert tx.returncode == 0
    assert "progress-line" in tx.stdout
    assert "progress-line" in capsys.readouterr().out
    assert "progress-line" in log.read_text()


def test_plain_runner_stays_silent(capsys, tmp_path):
    import sys as _sys

    from engine.adapters.probe_rs import subprocess_runner

    tool = [_sys.executable, "-c", "print('quiet-line')"]
    tx = subprocess_runner(tool)
    assert "quiet-line" in tx.stdout
    assert capsys.readouterr().out == ""
