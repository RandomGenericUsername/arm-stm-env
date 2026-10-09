"""Cache keys owned by core (req-003, group 2.3).

Key = ``arm-stm-env:v1:<image_digest>:<project_hash>``. Digest change flips
the key so stale entries are never reused. Adapters request keys, never
invent them.
"""

from __future__ import annotations

__all__ = ["KEY_VERSION", "cache_key"]

KEY_VERSION = "v1"


def cache_key(*, image_digest: str, project_hash: str) -> str:
    if not image_digest:
        raise ValueError("image_digest must be non-empty")
    if not project_hash:
        raise ValueError("project_hash must be non-empty")
    return f"arm-stm-env:{KEY_VERSION}:{image_digest}:{project_hash}"
