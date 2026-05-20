"""Regression test for F-004: there must be exactly one canonical
seed-style LRC ID list in the codebase.

Background
----------
Before F-004, the canonical LRC seed list (cells 60, 90, 120, 136,
166, 210, 296, 75, 105, 135, 151, 181, 225, 311) was duplicated
across seven hardcoded literals in src/. Each duplication had to
be kept in sync manually; getting it wrong produced runtime
ValueError / AssertionError with no diagnostic connection back to
"the lists drifted." F-004 collapsed all duplicates to read from
``NeighborHelpers.ROOTCAP_CELL_IDs``.

This test guards against the duplication coming back. It does NOT
test that ROOTCAP_CELL_IDs itself contains the right cells — that's
covered by ``test_plan2_lrc_extension_invariants`` in the
initialization symmetry tests.

The check is purely textual (regex over .py files in src/), so it
runs fast and doesn't require building a simulation.
"""

import re
import unittest
from pathlib import Path

# A 14-int sequence that's unique enough to identify a "real" copy
# of the canonical seed list. Matches the original 14 IDs in the
# original order, allowing any whitespace / trailing-commas between
# items. If a future LRC cell is added, append it to
# NeighborHelpers.ROOTCAP_CELL_IDs — NOT to a new inline list.
SEED_IDS = [60, 90, 120, 136, 166, 210, 296, 75, 105, 135, 151, 181, 225, 311]
SEED_PATTERN = re.compile(
    r"\b" + r"\s*,\s*".join(str(i) for i in SEED_IDS) + r"\b",
    re.MULTILINE,
)

# The single canonical location (relative to repo root).
CANONICAL_PATH = "src/agent/default_geo_neighbor_helpers.py"

# Repo root resolved from this test file's location.
REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class TestLRCIDListCanonicity(unittest.TestCase):
    def test_seed_list_appears_in_only_one_place_in_src(self):
        """Walk every .py file under src/ and find seed-list-shaped
        literals. There should be exactly one — the canonical
        ``NeighborHelpers.ROOTCAP_CELL_IDs``."""
        occurrences = []
        for py_path in sorted((REPO_ROOT / "src").rglob("*.py")):
            if "__pycache__" in py_path.parts:
                continue
            text = py_path.read_text()
            for match in SEED_PATTERN.finditer(text):
                line = text[: match.start()].count("\n") + 1
                occurrences.append((py_path.relative_to(REPO_ROOT), line))

        self.assertEqual(
            len(occurrences),
            1,
            "Expected exactly one canonical seed-list literal in src/, found "
            f"{len(occurrences)}: {occurrences}. If you added a new LRC ID, "
            "append it to NeighborHelpers.ROOTCAP_CELL_IDs only, not to a "
            "new inline list. See implementation log F-004.",
        )

        canonical_relative = Path(CANONICAL_PATH)
        self.assertEqual(
            occurrences[0][0],
            canonical_relative,
            f"The one remaining seed-list literal is at "
            f"{occurrences[0][0]}, not the expected canonical location "
            f"{canonical_relative}.",
        )


if __name__ == "__main__":
    unittest.main()
