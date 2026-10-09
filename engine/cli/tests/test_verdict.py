"""Flash verdict tests (req-005, group 2.3): multi-piece stub -> one verdict."""

from engine.adapters import PieceResult
from engine.cli.tests.stubs import StubProbeAdapter, make_device_view, make_endpoint
from engine.cli.verdict import render_flash_verdict
from engine.core.model import ProofResult


def test_verdict_three_piece_ok_plus_rung():
    stub = StubProbeAdapter()
    pieces = list(
        stub.flash(make_device_view(), make_endpoint(), ["boot", "part", "app"])
    )
    assert all(isinstance(p, PieceResult) for p in pieces)
    proof = ProofResult("frame", {"ok": "true"})
    line = render_flash_verdict(pieces, proof)
    assert "3/3 OK" in line
    assert "frame" in line


def test_verdict_partial_failure_names_piece_no_proof_claim():
    stub = StubProbeAdapter(outcomes={"app": False})
    pieces = list(
        stub.flash(make_device_view(), make_endpoint(), ["boot", "part", "app"])
    )
    proof = ProofResult("frame", {"ok": "false"})
    line = render_flash_verdict(pieces, proof)  # proof given but must not be claimed
    assert "FAILED" in line and "2/3" in line
    assert "app" in line
    assert "proof" not in line.lower()


def test_verdict_failure_without_proof_also_clean():
    pieces = [
        PieceResult(name="boot", ok=True),
        PieceResult(name="part", ok=True),
        PieceResult(name="app", ok=False, detail="stub"),
    ]
    line = render_flash_verdict(pieces)
    assert "FAILED" in line and "app" in line
    assert "proof" not in line.lower()
