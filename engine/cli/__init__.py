"""Thin orchestration verbs (req-005, group 1): pure model -> port wiring.

No file in this package branches on device family, chip, or backend name;
all device behavior arrives via the certified model + adapter ports.
"""

from engine.cli.main import build_parser, main

__all__ = ["build_parser", "main"]
