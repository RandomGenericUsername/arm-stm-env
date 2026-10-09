"""Adapter conformance + cross-adapter comparability (req-006, group 2.2).

Conformance: both backends satisfy the core-owned ``ProbeAdapter`` ABC
with identical call semantics (per-piece ordered results, empty pieces
run nothing, debug binds the shim endpoint with no live claim).

Comparability decision (KNOWN ISSUE from group 1, decided here):
SUBSET equality, not full equality. ``pieces`` and ``verified`` are
backend-comparable keys and SHALL be field-equal for the same rung;
``sessions`` is backend-native (OpenOCD ``Info : <t> examined`` vs
probe-rs ``Core <n>:`` spellings) and is explicitly exempt until HW
smoke unifies it against a physical probe. Forcing full equality now
would fake a comparability the real tools do not have.
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import pytest

from engine.adapters import PieceResult, ProbeAdapter
from engine.adapters.openocd import (
    DUAL_CORE_FIXTURE as OCD_DUAL,
)
from engine.adapters.openocd import (
    VERIFY_OK_FIXTURE as OCD_SINGLE,
)
from engine.adapters.openocd import OpenOCDAdapter
from engine.adapters.openocd import Transcript as OcdTranscript
from engine.adapters.openocd import parse_transcript
from engine.adapters.probe_rs import DUAL_CORE_FIXTURE as PRS_DUAL
from engine.adapters.probe_rs import VERIFY_OK_FIXTURE as PRS_SINGLE
from engine.adapters.probe_rs import ProbeRsAdapter
from engine.adapters.probe_rs import Transcript as PrsTranscript
from engine.adapters.probe_rs import parse_output
from engine.core.loader import load_file
from engine.core.model import DeviceView, Endpoint

PACKS = Path(__file__).resolve().parents[3] / "packs"


def _fake_ocd(text: str, rc: int = 0):
    def run(argv: Sequence[str]) -> OcdTranscript:
        return OcdTranscript(argv=tuple(argv), returncode=rc, stdout=text)

    return run


def _fake_prs(text: str, rc: int = 0):
    def run(argv: Sequence[str]) -> PrsTranscript:
        return PrsTranscript(argv=tuple(argv), returncode=rc, stdout=text)

    return run


@pytest.fixture(params=["openocd", "probe-rs"])
def adapter(request) -> ProbeAdapter:
    if request.param == "openocd":
        return OpenOCDAdapter(runner=_fake_ocd(OCD_SINGLE))
    return ProbeRsAdapter(runner=_fake_prs(PRS_SINGLE))


@pytest.fixture(params=["openocd", "probe-rs"])
def view_and_endpoint(request) -> tuple[DeviceView, Endpoint]:
    pack = "stm32f411re.yaml" if request.param == "openocd" else "stm32h755.yaml"
    view = DeviceView.of(load_file(PACKS / pack))
    return view, Endpoint(transport=view.probe_transport, address="/dev/node-0")


def test_conformance_both_adapters_satisfy_probe_adapter_abc():
    assert isinstance(OpenOCDAdapter(runner=_fake_ocd("")), ProbeAdapter)
    assert isinstance(ProbeRsAdapter(runner=_fake_prs("")), ProbeAdapter)
    assert set(ProbeAdapter.__abstractmethods__) == {"flash", "debug"}


def test_conformance_flash_contract_single_piece(adapter, view_and_endpoint):
    view, endpoint = view_and_endpoint
    results = adapter.flash(view, endpoint, ["app"])
    assert len(results) == 1
    assert all(isinstance(r, PieceResult) for r in results)
    assert [r.name for r in results] == ["app"]
    assert all(r.ok for r in results)


def test_conformance_flash_empty_pieces_runs_nothing(adapter, view_and_endpoint):
    view, endpoint = view_and_endpoint
    assert adapter.flash(view, endpoint, []) == ()


def test_conformance_debug_binds_shim_endpoint_no_live_claim(
    adapter, view_and_endpoint
):
    view, endpoint = view_and_endpoint
    handle = adapter.debug(view, endpoint)
    assert handle.endpoint == endpoint
    assert handle.session_id  # deterministic, backend-prefixed; no live attach


def test_cross_adapter_comparability_subset_shared_keys_equal_sessions_backend_specific():
    # Same rung (H755 dual readback), each backend with its own fixture.
    # SUBSET decision: pieces + verified field-equal; sessions exempt
    # (backend-native spellings: "core0,core1" vs "core-0,core-1").
    view = DeviceView.of(load_file(PACKS / "stm32h755.yaml"))
    endpoint = Endpoint(transport=view.probe_transport, address="/dev/node-0")

    ocd = OpenOCDAdapter(runner=_fake_ocd(OCD_DUAL))
    ocd_results = ocd.flash(view, endpoint, ["flash_m7", "flash_m4"])
    ocd_proof = ocd.proof_for(
        view, ocd_results, OcdTranscript(("openocd",), 0, OCD_DUAL)
    )

    prs = ProbeRsAdapter(runner=_fake_prs(PRS_DUAL))
    prs_results = prs.flash(view, endpoint, ["flash_m7", "flash_m4"])
    prs_proof = prs.proof_for(
        view, prs_results, PrsTranscript(("probe-rs",), 0, PRS_DUAL)
    )

    assert ocd_proof.rung == prs_proof.rung == "readback-m7-m4"
    ocd_payload, prs_payload = ocd_proof.as_dict(), prs_proof.as_dict()
    assert set(ocd_payload) == set(prs_payload) == {"pieces", "verified", "sessions"}
    for key in ("pieces", "verified"):  # shared backend-comparable keys
        assert ocd_payload[key] == prs_payload[key], key
    # sessions diverges by backend spelling — pinned, not unified, until HW smoke.
    assert ocd_payload["sessions"] == "core0,core1"
    assert prs_payload["sessions"] == "core-0,core-1"


def test_cross_adapter_single_core_sessions_agree_empty():
    # Single-core rungs have no session lines on either backend: full
    # equality holds there; the subset exemption only bites on dual-core.
    view = DeviceView.of(load_file(PACKS / "stm32f411re.yaml"))
    ocd_proof = OpenOCDAdapter(runner=_fake_ocd("")).proof_for(
        view,
        parse_transcript(["solo"], OcdTranscript(("openocd",), 0, OCD_SINGLE)),
        OcdTranscript(("openocd",), 0, OCD_SINGLE),
    )
    prs_proof = ProbeRsAdapter(runner=_fake_prs("")).proof_for(
        view,
        parse_output(["solo"], PrsTranscript(("probe-rs",), 0, PRS_SINGLE)),
        PrsTranscript(("probe-rs",), 0, PRS_SINGLE),
    )
    assert ocd_proof.as_dict() == prs_proof.as_dict()
