"""Verdict rendering (req-005, group 1): multi-piece results -> one verdict."""

from __future__ import annotations

from typing import Sequence

from engine.adapters import PieceResult
from engine.core.model import ProofResult

__all__ = ["render_flash_verdict"]


def render_flash_verdict(
    pieces: Sequence[PieceResult], proof: ProofResult | None = None
) -> str:
    """Render a single verdict line from per-piece results + proof payload.

    All pieces OK -> ``"<n>/<n> pieces OK"`` plus the proof rung when given.
    Any failure -> names the failed pieces and carries no proof claim.
    """
    names = [p.name for p in pieces]
    if len(set(names)) != len(names):
        raise ValueError(f"duplicate piece names in flash results: {names}")
    total = len(pieces)
    failed = [p.name for p in pieces if not p.ok]
    done = total - len(failed)
    if failed:
        return (
            f"flash verdict: FAILED {done}/{total} OK; "
            f"failed piece(s): {', '.join(failed)}"
        )
    line = f"flash verdict: {done}/{total} OK ({total} pieces)"
    if proof is not None:
        line += f" + proof rung {proof.rung!r}"
    return line
