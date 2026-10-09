"""No-hardware-knowledge gate (req-005, group 1.3).

Scans every file under ``engine/cli/`` for family/chip/backend names;
any hit fails. Backend vocabulary belongs in packs/adapters, never here.
"""

import re
from pathlib import Path

FORBIDDEN_PARTS = (
    "stm" + "32",
    "esp" + "32",
    "av" + "r",
    "open" + "ocd",
    "esp" + "tool",
    "av" + "rdude",
)
FORBIDDEN = re.compile("|".join(FORBIDDEN_PARTS), re.IGNORECASE)


def test_cli_carries_no_hardware_knowledge():
    root = Path(__file__).resolve().parent.parent
    hits = []
    for path in sorted(root.rglob("*")):
        if path.is_dir() or path.suffix not in {".py", ".toml", ".md", ".txt"}:
            continue
        for lineno, line in enumerate(path.read_text().splitlines(), 1):
            if FORBIDDEN.search(line):
                hits.append(f"{path.relative_to(root)}:{lineno}:{line.strip()}")
    assert hits == [], "hardware knowledge leaked into engine/cli/:\n" + "\n".join(hits)
