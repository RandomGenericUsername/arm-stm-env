"""probe-rs adapter tests (req-006, group 2.1).

Subprocess is always faked: no ``probe-rs`` binary required. Fixture
transcripts come from :mod:`engine.adapters.probe_rs` (marked FIXTURE,
never live runs). Pack vectors load the repo's corrected packs.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Sequence

from engine.adapters import PieceResult, ProbeAdapter
from engine.adapters.probe_rs import (
    DUAL_CORE_FIXTURE,
    PROBE_RS_VERSION,
    VERIFY_OK_FIXTURE,
    ProbeRsAdapter,
    Transcript,
    parse_output,
    session_names,
)
from engine.core.loader import load_file
from engine.core.model import (
    Core,
    Device,
    DeviceView,
    Endpoint,
    MemoryRegion,
    OpenocdConfig,
)

PACKS = Path(__file__).resolve().parents[3] / "packs"


def _device_view(**kw) -> DeviceView:
    base = dict(
        id="generic-board",
        version="1.0.0",
        source_hash="sha256:test",
        cores=[Core(name="core0", arch="generic-arch")],
        memory=[MemoryRegion(name="prog", origin_hex="0x0", size=64 * 1024)],
        probe_ref=Endpoint(transport="generic-probe", address="usb:0"),
        proof_rung="frame",
        openocd=OpenocdConfig(interface="iface.cfg", target="board.cfg"),
    )
    base.update(kw)
    return DeviceView.of(Device(**base))


def _endpoint(address: str = "/dev/node-0") -> Endpoint:
    return Endpoint(transport="generic-probe", address=address)


def _fake_runner(text: str, rc: int = 0, calls: list | None = None):
    def run(argv: Sequence[str]) -> Transcript:
        if calls is not None:
            calls.append(list(argv))
        return Transcript(argv=tuple(argv), returncode=rc, stdout=text)

    return run


def test_probe_rs_adapter_satisfies_probe_port():
    assert isinstance(ProbeRsAdapter(runner=_fake_runner("")), ProbeAdapter)


def test_probe_rs_parser_targets_pinned_version():
    assert PROBE_RS_VERSION == "0.32.0"


def test_probe_rs_argv_renders_chip_from_model_id_only():
    adapter = ProbeRsAdapter(runner=_fake_runner(""))
    argv = adapter.render_argv(_device_view(), _endpoint(), ["alpha", "beta"])
    assert argv[:6] == [
        "probe-rs",
        "download",
        "--chip",
        "generic-board",
        "--probe",
        "/dev/node-0",
    ]
    assert argv[6:] == ["alpha", "beta"]


def test_probe_rs_argv_chip_tracks_pack_id():
    view = DeviceView.of(load_file(PACKS / "stm32h755.yaml"))
    argv = ProbeRsAdapter(runner=_fake_runner("")).render_argv(view, _endpoint(), [])
    assert "--chip" in argv and "stm32h755" in argv


def test_probe_rs_argv_missing_pack_id_raises():
    view = DeviceView(
        id="",
        version="1.0.0",
        source_hash="sha256:test",
        cores=(),
        memory=(),
        probe_transport="generic-probe",
        probe_address="usb:0",
        proof_rung="frame",
    )
    import pytest

    with pytest.raises(ValueError, match="--chip"):
        ProbeRsAdapter(runner=_fake_runner("")).render_argv(view, _endpoint(), ["p"])


def test_probe_rs_flash_verify_ok_fixture_per_piece():
    calls: list = []
    adapter = ProbeRsAdapter(runner=_fake_runner(VERIFY_OK_FIXTURE, calls=calls))
    results = adapter.flash(_device_view(), _endpoint(), ["app"])
    assert [r.name for r in results] == ["app"]
    assert all(isinstance(r, PieceResult) and r.ok for r in results)
    sent = calls[0]
    assert sent[:4] == ["probe-rs", "download", "--chip", "generic-board"]


def test_probe_rs_flash_partial_and_failed_outputs():
    adapter = ProbeRsAdapter(runner=_fake_runner(VERIFY_OK_FIXTURE))
    partial = adapter.flash(_device_view(), _endpoint(), ["a", "b", "c"])
    assert [r.ok for r in partial] == [True, False, False]
    failed = ProbeRsAdapter(runner=_fake_runner("boom", rc=1)).flash(
        _device_view(), _endpoint(), ["a"]
    )
    assert failed[0].ok is False and "rc=1" in failed[0].detail


def test_probe_rs_flash_empty_pieces_runs_nothing():
    calls: list = []
    adapter = ProbeRsAdapter(runner=_fake_runner(VERIFY_OK_FIXTURE, calls=calls))
    assert adapter.flash(_device_view(), _endpoint(), []) == ()
    assert calls == []


def test_probe_rs_debug_binds_shim_endpoint_no_live_claim():
    endpoint = _endpoint()
    handle = ProbeRsAdapter(runner=_fake_runner("")).debug(_device_view(), endpoint)
    assert handle.endpoint == endpoint
    assert handle.session_id.startswith("probe-rs:")


def test_probe_rs_source_carries_no_board_names():
    src = (Path(__file__).resolve().parent.parent / "probe_rs.py").read_text()
    hits = re.findall(r"nucleo|f411|h755|wl55", src, re.IGNORECASE)
    assert hits == [], f"board/chip names leaked into adapter: {hits}"


def test_probe_rs_parse_output_counts_finished_lines():
    tx = Transcript(argv=("probe-rs",), returncode=0, stdout=VERIFY_OK_FIXTURE)
    (only,) = parse_output(["solo"], tx)
    assert only.ok and only.detail == "download-finished"
    assert session_names(tx) == ()


def test_probe_rs_dual_core_fixture_session_lines():
    tx = Transcript(argv=("probe-rs",), returncode=0, stdout=DUAL_CORE_FIXTURE)
    assert session_names(tx) == ("core-0", "core-1")
    results = parse_output(["first", "second"], tx)
    assert [r.ok for r in results] == [True, True]


def test_proof_single_core_payload_fills_core_struct():
    from engine.core.model import ProofResult

    view = _device_view()
    tx = Transcript(argv=("probe-rs",), returncode=0, stdout=VERIFY_OK_FIXTURE)
    results = parse_output(["solo"], tx)
    proof = ProbeRsAdapter(runner=_fake_runner("")).proof_for(view, results, tx)
    assert isinstance(proof, ProofResult)
    assert proof.rung == "frame"
    assert proof.as_dict() == {
        "pieces": "solo=ok",
        "verified": "1/1",
        "sessions": "",
    }


def test_proof_dual_session_vectors_fill_per_core_pieces():
    view = DeviceView.of(load_file(PACKS / "stm32h755.yaml"))
    assert view.proof_rung == "readback-m7-m4"
    endpoint = Endpoint(transport=view.probe_transport, address="/dev/node-0")
    adapter = ProbeRsAdapter(runner=_fake_runner(DUAL_CORE_FIXTURE))
    results = adapter.flash(view, endpoint, ["flash_m7", "flash_m4"])
    assert [r.ok for r in results] == [True, True]
    proof = adapter.proof_for(
        view, results, Transcript(("probe-rs",), 0, DUAL_CORE_FIXTURE)
    )
    assert proof.rung == "readback-m7-m4"
    assert proof.as_dict() == {
        "pieces": "flash_m7=ok,flash_m4=ok",
        "verified": "2/2",
        "sessions": "core-0,core-1",
    }
