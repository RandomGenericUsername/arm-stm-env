"""YAML pack loader + frame validator (req-003, group 2.1).

Frame keys: id, version, cores, memory, probe, proof_rung, optional blocks.
``blocks`` maps block_name -> payload; each name must be registered
(unknown = hard error naming the block). Returns a certified
:class:`engine.core.model.Device` with ``source_hash`` = sha256 of raw bytes.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import yaml

from engine.core.model import Core, Device, Endpoint, MemoryRegion, OpenocdConfig
from engine.core.registry import UnknownBlockError, validate_block

__all__ = ["FRAME_KEYS", "FrameError", "load_file", "load_text", "validate_frame"]

FRAME_KEYS = ("id", "version", "cores", "memory", "probe", "proof_rung")


class FrameError(ValueError):
    """Raised when a pack fails frame validation."""


def _source_hash(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def validate_frame(doc: dict) -> Device:
    if not isinstance(doc, dict):
        raise FrameError(f"pack must be a mapping, got {type(doc).__name__}")
    for key in FRAME_KEYS:
        if key not in doc:
            raise FrameError(f"pack missing required frame key: {key!r}")
    try:
        cores = tuple(Core(name=c["name"], arch=c["arch"]) for c in doc["cores"])
    except (TypeError, KeyError, AttributeError) as exc:
        raise FrameError(f"invalid 'cores' section: {exc}") from exc
    try:
        memory = tuple(
            MemoryRegion(name=m["name"], origin_hex=m.get("origin_hex", m.get("origin")), size=m["size"])
            for m in doc["memory"]
        )
    except (TypeError, KeyError, AttributeError) as exc:
        raise FrameError(f"invalid 'memory' section: {exc}") from exc
    try:
        probe = Endpoint(transport=doc["probe"]["transport"], address=doc["probe"]["address"])
    except (TypeError, KeyError, AttributeError) as exc:
        raise FrameError(f"invalid 'probe' section: {exc}") from exc
    blocks = doc.get("blocks", {})
    if not isinstance(blocks, dict):
        raise FrameError("'blocks' must be a mapping of block_name -> payload")
    for name, payload in blocks.items():
        try:
            validate_block(name, payload)
        except UnknownBlockError:
            raise
        except ValueError as exc:
            raise FrameError(f"family block {name!r} invalid: {exc}") from exc
    openocd: OpenocdConfig | None = None
    if "openocd" in blocks:
        raw_block = blocks["openocd"]
        target = raw_block.get("target", raw_block.get("board"))
        openocd = OpenocdConfig(
            interface=raw_block["interface"],
            target=target,
            dual_core=bool(raw_block.get("dual_core", False)),
        )
    return Device(
        id=doc["id"],
        version=str(doc["version"]),
        source_hash=doc["_source_hash"],
        cores=cores,
        memory=memory,
        probe_ref=probe,
        proof_rung=doc["proof_rung"],
        openocd=openocd,
        provenance={"pack_id": doc["id"], "pack_version": str(doc["version"])},
    )


def load_text(text: str, raw: bytes | None = None) -> Device:
    doc = yaml.safe_load(text)
    if not isinstance(doc, dict):
        raise FrameError(f"pack must be a mapping, got {type(doc).__name__}")
    doc["_source_hash"] = _source_hash(raw if raw is not None else text.encode())
    return validate_frame(doc)


def load_file(path: str | Path) -> Device:
    raw = Path(path).read_bytes()
    return load_text(raw.decode(), raw)
