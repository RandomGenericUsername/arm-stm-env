"""esptool backend tests (task-014, E2; AD-12, AD-14).

Everything is rendered from the pack's certified blocks — the offsets in
:data:`ROLE_ORDER`, the flash parameters, the chip target. The transcript
fixture mirrors the live spike-007 run (``Hash of data verified`` per image).
"""

from pathlib import Path
from typing import Sequence

from engine.adapters import DebugPort, FlashPort, ProbeAdapter
from engine.adapters.esptool import (
    ROLE_ORDER,
    VERIFY_FIXTURE,
    EsptoolAdapter,
    Transcript,
)
from engine.core.loader import load_file
from engine.core.model import DeviceView, Endpoint

PACKS = Path(__file__).resolve().parents[3] / "packs"


def _view() -> DeviceView:
    return DeviceView.of(load_file(PACKS / "esp32cam.yaml"))


def _endpoint() -> Endpoint:
    return Endpoint(transport="probe", address="/dev/ttyUSB0")


def _fake_runner(text: str, rc: int = 0):
    def run(argv: Sequence[str]) -> Transcript:
        return Transcript(argv=tuple(argv), returncode=rc, stdout=text)

    return run


def _adapter(text: str = "", rc: int = 0) -> EsptoolAdapter:
    return EsptoolAdapter(runner=_fake_runner(text, rc))


def test_esptool_is_flash_port_only():
    """AD-12: UART bring-up has no attach, so no DebugPort and no composite."""
    adapter = _adapter()
    assert isinstance(adapter, FlashPort)
    assert not isinstance(adapter, DebugPort)
    assert not isinstance(adapter, ProbeAdapter)


def test_registry_resolves_the_esptool_backend():
    from engine.adapters import get_adapter

    assert isinstance(get_adapter("esptool"), EsptoolAdapter)


def test_render_argv_from_pack_facts():
    argv = _adapter().render_argv(
        _view(), _endpoint(), ["bootloader.bin", "partition-table.bin", "app.bin"]
    )
    assert argv[0] == "esptool"
    assert argv[1:3] == ["--chip", "esp32"]  # from the sdkconfig block
    assert argv[3:5] == ["--port", "/dev/ttyUSB0"]
    assert argv[5:7] == ["--baud", "460800"]  # from the esptool block
    assert argv[7] == "write-flash"
    assert argv[8:10] == ["--flash-mode", "dio"]
    # offsets come from the pack's partitions block, in ROLE_ORDER
    for role, piece in zip(ROLE_ORDER, ["bootloader.bin", "partition-table.bin", "app.bin"]):
        offset = _view().block_for("partitions")[role]
        assert piece in argv and offset in argv
        assert argv[argv.index(offset) + 1] == piece
    assert ROLE_ORDER == ("bootloader", "partition_table", "app")


def test_render_argv_refuses_without_the_partitions_block():
    from engine.core.model import DeviceFacets

    from dataclasses import replace

    view = replace(_view(), blocks=())
    try:
        _adapter().render_argv(view, _endpoint(), ["a.bin"])
    except ValueError as exc:
        assert "partitions" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("expected a loud error without the partitions fact")
    assert DeviceFacets is not None  # imported for clarity of intent


def test_flash_verifies_every_image_from_the_transcript():
    results = _adapter(VERIFY_FIXTURE).flash(
        _view(), _endpoint(), ["bootloader.bin", "partition-table.bin", "app.bin"]
    )
    assert [r.ok for r in results] == [True, True, True]
    assert all(r.detail == "hash-verified" for r in results)


def test_flash_empty_pieces_runs_nothing():
    assert _adapter(VERIFY_FIXTURE).flash(_view(), _endpoint(), []) == ()


def test_flash_fails_loud_on_nonzero_exit():
    results = _adapter("A fatal error occurred\n", rc=2).flash(_view(), _endpoint(), ["a.bin"])
    assert results[0].ok is False
    assert "rc=2" in results[0].detail


def test_partial_verification_leaves_later_pieces_unproven():
    results = _adapter("Hash of data verified.\n").flash(
        _view(), _endpoint(), ["a.bin", "b.bin"]
    )
    assert [r.ok for r in results] == [True, False]
    assert "Hash of data verified" in results[1].detail


def test_proof_payload_uses_the_shared_backend_comparable_keys():
    adapter = _adapter(VERIFY_FIXTURE)
    results = adapter.flash(_view(), _endpoint(), ["a.bin", "b.bin"])
    proof = adapter.proof_for(_view(), results, adapter.last_transcript)
    assert proof.rung == "uart-boot-log"  # the pack's declared rung
    payload = proof.as_dict()
    assert set(payload) == {"pieces", "verified", "sessions"}
    assert payload["verified"] == "2/2"
    assert payload["pieces"] == "a.bin=ok,b.bin=ok"
    assert payload["sessions"] == ""  # no attach sessions for esptool


def test_last_transcript_is_kept_for_proof():
    adapter = _adapter(VERIFY_FIXTURE)
    assert adapter.last_transcript is None
    adapter.flash(_view(), _endpoint(), ["a.bin"])
    assert adapter.last_transcript is not None
