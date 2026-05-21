"""Apply Plan 2's LRC geometry extension to `indep_syndeg_init_vals.json`.

Implements follow-up F-005 of
docs/plans/imp_logs/2_2026-05-20_extend_LRC_geometry_log.md.

Reads:  src/sim/input/default_init_vals.json   (already extended in Phase B)
        src/sim/input/indep_syndeg_init_vals.json  (not yet extended)
Writes: src/sim/input/indep_syndeg_init_vals.json (in-place)

What this does
--------------
The original Phase-B script (`scripts/extend_lrc_geometry.py`) edits
`default_init_vals.json` and adds vertices 918-973 to
`default_vs.json`. The vertices file is shared across all circulation
modules, so it does not need to be touched again. But the per-cell
initial-conditions file used by `AUX_SYN_DEG_EXP` is a different
file (`indep_syndeg_init_vals.json`) with a different schema, and
it still has 830 cells.

This script copies the *cell-level* changes from default into indep:

1. PIN flip on cells 296 / 311 (terminal-dumper -> apical-dominant).
2. Append 28 new cells 830-857, schema-translated from default's
   "cont" circ_mod schema into indep_syndeg's schema:
     - drop ``k_s`` / ``k_d``
     - add ``ks_aux, kd_aux, ks_arr, kd_arr, ks_pinu, kd_pinu,
            kd_pinloc, ks_auxlax, kd_auxlax`` (values copied from
            an existing indep_syndeg LRC cell, e.g. c60)
     - set ``circ_mod = "indep_syndeg"``
3. Append the new neighbor entries that the Phase-B script added to
   cells 296, 311, and 634-829 (only ones referring to c830+).

This is robust: it diff's default's neighbor list against indep's
neighbor list and appends just the new c830+ entries. It does not
re-do the geometry math.

Pre-conditions (asserted at startup):
- default has 858 cells, indep has 830 cells
- default cell 296 has pina=1.0 (post-flip)
- indep cell 296 has pina=0.0 (pre-flip; the change this script makes)

Post-conditions (asserted at end):
- indep has 858 cells
- indep cells 296 and 311 have pina=1.0
- indep cell 830 has circ_mod="indep_syndeg" and ks_aux key present

Run:
    uv run python3 scripts/extend_lrc_geometry_indep_syndeg.py

Idempotency: this script is NOT idempotent. It will refuse to run if
indep already has 858 cells (the post-condition state). Re-running on
a fresh checkout reproduces the same patch.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_PATH = REPO / "src" / "sim" / "input" / "default_init_vals.json"
INDEP_PATH = REPO / "src" / "sim" / "input" / "indep_syndeg_init_vals.json"

# IDs from the Phase-B extension
NEW_LRC_IDS = list(range(830, 858))   # 830-857 inclusive
CELLS_TO_FLIP_TO_APICAL = (296, 311)

# Schema keys present in default ("cont") but not in indep
DEFAULT_ONLY_KEYS = ("k_s", "k_d")

# Schema keys present in indep ("indep_syndeg") but not in default —
# template values are copied from an existing indep LRC cell.
INDEP_TEMPLATE_LRC_ID = 60

# Apical-dominant PIN spec (must match the Phase-B script)
APICAL_DOMINANT_PIN = {"pin": 0.275, "pina": 1.0, "pinb": 0.0, "pinl": 0.0, "pinm": 0.1}


def translate_cell_to_indep_schema(default_cell: dict, indep_template: dict) -> dict:
    """Convert a 'cont'-schema cell entry into an 'indep_syndeg' entry."""
    out = {k: v for k, v in default_cell.items() if k not in DEFAULT_ONLY_KEYS}
    out["circ_mod"] = "indep_syndeg"
    # Copy the indep-only rate keys from the template
    for k in ("ks_aux", "kd_aux", "ks_arr", "kd_arr", "ks_pinu",
              "kd_pinu", "kd_pinloc", "ks_auxlax", "kd_auxlax"):
        out[k] = indep_template[k]
    return out


def new_neighbors_to_append(default_neighbors: list[str], indep_neighbors: list[str]) -> list[str]:
    """Return the entries in default's neighbor list that refer to new
    LRC cells (c830+) and are not already in indep's neighbor list.
    Order preserved from default's list."""
    indep_set = set(indep_neighbors)
    new_ids = {f"c{cid}" for cid in NEW_LRC_IDS}
    return [n for n in default_neighbors if n in new_ids and n not in indep_set]


def main() -> int:
    default = json.loads(DEFAULT_PATH.read_text())
    indep = json.loads(INDEP_PATH.read_text())

    # ---- Pre-conditions ----------------------------------------------
    assert len(default) == 858, f"expected 858 cells in default, got {len(default)}"
    if len(indep) == 858:
        print("# indep_syndeg_init_vals.json already has 858 cells; nothing to do.")
        return 0
    assert len(indep) == 830, f"expected 830 cells in indep, got {len(indep)}"
    assert default[296]["pina"] == 1.0, "default cell 296 is not post-flip (pina != 1.0)"
    assert default[311]["pina"] == 1.0, "default cell 311 is not post-flip (pina != 1.0)"
    assert indep[296]["pina"] == 0.0, "indep cell 296 already flipped (pina != 0.0)"
    assert indep[311]["pina"] == 0.0, "indep cell 311 already flipped (pina != 0.0)"

    print(f"# extend_lrc_geometry_indep_syndeg.py")
    print(f"# before: indep cells = {len(indep)}")

    template = indep[INDEP_TEMPLATE_LRC_ID]

    # ---- (1) PIN flip on 296 / 311 in indep --------------------------
    for cid in CELLS_TO_FLIP_TO_APICAL:
        old = (indep[cid]["pina"], indep[cid]["pinb"], indep[cid]["pinl"], indep[cid]["pinm"])
        indep[cid].update(APICAL_DOMINANT_PIN)
        new = (indep[cid]["pina"], indep[cid]["pinb"], indep[cid]["pinl"], indep[cid]["pinm"])
        print(f"# flipped indep cell {cid} PIN: pina/pinb/pinl/pinm {old} -> {new}")

    # ---- (2) Append new a-/l-neighbors to existing cells -------------
    # Any cell whose default-neighbor list contains a c830+ reference
    # that indep's list doesn't already have should get that reference
    # appended.
    cells_to_check = list(CELLS_TO_FLIP_TO_APICAL) + list(range(634, 830))
    appended = 0
    for cid in cells_to_check:
        extra = new_neighbors_to_append(default[cid]["neighbors"], indep[cid]["neighbors"])
        if extra:
            indep[cid]["neighbors"].extend(extra)
            appended += len(extra)
    print(f"# appended {appended} new neighbor references to existing indep cells")

    # ---- (3) Append translated cells 830-857 -------------------------
    for cid in NEW_LRC_IDS:
        translated = translate_cell_to_indep_schema(default[cid], template)
        indep.append(translated)
    print(f"# appended {len(NEW_LRC_IDS)} new LRC cells (IDs 830-857) to indep")

    # ---- Post-conditions ---------------------------------------------
    assert len(indep) == 858, f"expected 858 cells in indep after patch, got {len(indep)}"
    assert indep[296]["pina"] == 1.0
    assert indep[311]["pina"] == 1.0
    assert indep[830]["circ_mod"] == "indep_syndeg"
    assert "ks_aux" in indep[830]
    assert "k_s" not in indep[830]
    assert "k_d" not in indep[830]
    # The first new LRC should reference c296 (its b-neighbor) and the matched epi (c634)
    assert "c296" in indep[830]["neighbors"]
    assert "c634" in indep[830]["neighbors"]
    # The topmost left should reference 854 (its b-neighbor) and the matched epi (816), no a-neighbor
    assert "c854" in indep[856]["neighbors"]
    assert "c816" in indep[856]["neighbors"]
    # 296 should now have c830 added; 311 should now have c831 added
    assert "c830" in indep[296]["neighbors"]
    assert "c831" in indep[311]["neighbors"]

    # ---- Write back --------------------------------------------------
    INDEP_PATH.write_text(json.dumps(indep, indent=2))
    print(f"# after: indep cells = {len(indep)}")
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
