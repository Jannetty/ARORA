"""Extend ARORA's default LRC geometry shootward to reach the OZ.

Implements Phase B of
docs/plans/design_plans/2_2026-05-20_extend_LRC_geometry.md.

Reads:  src/sim/input/default_vs.json
        src/sim/input/default_init_vals.json
Writes: same paths, in-place

What this does
--------------
1. Adds N new LRC cells per side (left and right), stacked above
   the existing top LRC cells (296 left, 311 right). Each new LRC
   cell shares its bottom vertices with the cell below it.
2. Allocates new vertex IDs starting at 918 and new cell IDs
   starting at 830, interleaved (830=left, 831=right, 832=left, …).
3. Flips cells 296 and 311 to apical-dominant PIN
   (pina=1.0, pinm=0.1) — they were previously all-medial
   terminal dumpers.
4. Makes the topmost new LRC cell on each side the new terminal
   dumper (pina=0.0, pinm=1.0).
5. Wires bidirectional neighbor entries between each new LRC cell
   and its matched epidermis cell.

Run:
    uv run python3 scripts/extend_lrc_geometry.py
    # or, in this sandbox:
    uv run --no-project python3 scripts/extend_lrc_geometry.py

The script is idempotent against itself only in the sense that
re-running on already-extended data will keep adding cells. It is
intended to run exactly once per fresh checkout.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

EXTENT = "gamma"   # "alpha" | "beta" | "gamma"

# (left_epi, right_epi, y_min, y_max) for the 14 rows that option γ
# (full elongation) will match. Options α and β use the first 7 / 10
# rows respectively. The 14th row's y_max is custom (1025) so the LRC
# stops at the elongation–differentiation boundary; the matched
# epidermis cells 816 / 829 extend further (y up to 1179) into DZ.
LRC_EXTENSION_ROWS_FULL = [
    (634, 647, 284, 297),
    (648, 661, 297, 311),
    (662, 675, 311, 327),
    (676, 689, 327, 346),
    (690, 703, 346, 369),   # OZ XPP target row
    (704, 717, 369, 397),
    (718, 731, 397, 431),   # T-E boundary
    (732, 745, 431, 472),
    (746, 759, 472, 527),
    (760, 773, 527, 582),
    (774, 787, 582, 637),
    (788, 801, 637, 692),
    (802, 815, 692, 747),
    (816, 829, 747, 1025),  # topmost; y_max custom (EZ end)
]

ROW_COUNT_BY_EXTENT = {"alpha": 7, "beta": 10, "gamma": 14}

# LRC x-coordinates (unchanged from cell 296 / 311)
LEFT_X_OUTER, LEFT_X_INNER = 21, 26    # x_outer = lateral, x_inner = medial
RIGHT_X_INNER, RIGHT_X_OUTER = 116, 121

# Template cell IDs to inherit init values from
TEMPLATE_APICAL_DOMINANT_ID = 60   # for non-terminal new cells
TEMPLATE_TERMINAL_DUMPER_ID = 296  # for terminal (topmost) new cells

# Cells flipped from terminal-dumper PIN to apical-dominant PIN
# (their old all-medial role is taken over by the new topmost cells).
CELLS_TO_FLIP_TO_APICAL = (296, 311)

# Starting vertices of each LRC chain (top corners of cells 296 / 311)
LEFT_CHAIN_START_BOTTOM = (689, 690)    # bottom-left, bottom-right (in cell coord convention)
RIGHT_CHAIN_START_BOTTOM = (706, 707)

# Bottom-of-chain anchor cells (the new lowest cell on each side
# uses these as its b-neighbor)
LEFT_CHAIN_BELOW_FIRST = "c296"
RIGHT_CHAIN_BELOW_FIRST = "c311"

# Vertex-ordering convention used by existing cells (verified in
# Phase B.3 on 2026-05-20 against cells 60, 296, 311, 297):
#     vertices = [bl, br, tl, tr]
# (Plan §4 Phase B.1 pseudocode incorrectly said [bl, br, tr, tl];
# see implementation log D-004.)

REPO = Path(__file__).resolve().parent.parent
VS_PATH = REPO / "src" / "sim" / "input" / "default_vs.json"
INIT_PATH = REPO / "src" / "sim" / "input" / "default_init_vals.json"


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def apical_dominant_pin():
    return {"pin": 0.275, "pina": 1.0, "pinb": 0.0, "pinl": 0.0, "pinm": 0.1}


def terminal_dumper_pin():
    return {"pin": 0.275, "pina": 0.0, "pinb": 0.0, "pinl": 0.0, "pinm": 1.0}


def base_template(init_data, is_terminal):
    src = init_data[TEMPLATE_TERMINAL_DUMPER_ID if is_terminal else TEMPLATE_APICAL_DOMINANT_ID]
    out = {k: v for k, v in src.items() if k not in ("vertices", "neighbors", "auxin")}
    out["auxin"] = 49.24   # same as cell 296 / cell 311 — a calmer starting value than 1725
    # Overwrite PIN explicitly to be belt-and-suspenders regardless of template
    out.update(terminal_dumper_pin() if is_terminal else apical_dominant_pin())
    return out


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

def main() -> int:
    rows = LRC_EXTENSION_ROWS_FULL[: ROW_COUNT_BY_EXTENT[EXTENT]]
    n_rows = len(rows)

    vs   = json.loads(VS_PATH.read_text())
    init = json.loads(INIT_PATH.read_text())

    cells_before = len(init)
    verts_before = len(vs)
    print(f"# extend_lrc_geometry.py")
    print(f"# extent = {EXTENT}, rows = {n_rows}")
    print(f"# before: cells = {cells_before}, vertices = {verts_before}")

    # ---- (1) Flip cells 296 / 311 to apical-dominant -----------------
    for cid in CELLS_TO_FLIP_TO_APICAL:
        old = (init[cid]["pina"], init[cid]["pinb"], init[cid]["pinl"], init[cid]["pinm"])
        init[cid].update(apical_dominant_pin())
        new = (init[cid]["pina"], init[cid]["pinb"], init[cid]["pinl"], init[cid]["pinm"])
        print(f"# flipped cell {cid} PIN: pina/pinb/pinl/pinm  {old} → {new}")

    # ---- (2) Allocate new cells / vertices ---------------------------
    next_v = max(int(k) for k in vs.keys()) + 1   # 918
    next_c = len(init)                             # 830

    new_cells = {}              # cell_id -> entry
    new_lrc_ids_left, new_lrc_ids_right = [], []

    left_bottom = LEFT_CHAIN_START_BOTTOM
    right_bottom = RIGHT_CHAIN_START_BOTTOM

    for i, (left_epi, right_epi, ymin, ymax) in enumerate(rows):
        is_terminal = (i == n_rows - 1)

        # ---- left side ----
        bl, br = left_bottom
        tl, tr = next_v, next_v + 1
        vs[str(tl)] = {"x": LEFT_X_OUTER, "y": ymax}
        vs[str(tr)] = {"x": LEFT_X_INNER, "y": ymax}
        next_v += 2

        cid_left = next_c
        next_c += 1

        # ---- right side ----
        bl_r, br_r = right_bottom
        tl_r, tr_r = next_v, next_v + 1
        vs[str(tl_r)] = {"x": RIGHT_X_INNER, "y": ymax}
        vs[str(tr_r)] = {"x": RIGHT_X_OUTER, "y": ymax}
        next_v += 2

        cid_right = next_c
        next_c += 1

        # ---- build cell entries (a-neighbor filled in below) ----
        cell_l = base_template(init, is_terminal)
        cell_l["vertices"] = [bl, br, tl, tr]      # [bl, br, tl, tr] convention
        cell_l["neighbors"] = [
            LEFT_CHAIN_BELOW_FIRST if i == 0 else f"c{cid_left - 2}",  # b-neighbor
            f"c{left_epi}",                                              # m-neighbor (epi)
        ]
        new_cells[cid_left] = cell_l
        new_lrc_ids_left.append(cid_left)

        cell_r = base_template(init, is_terminal)
        cell_r["vertices"] = [bl_r, br_r, tl_r, tr_r]
        cell_r["neighbors"] = [
            RIGHT_CHAIN_BELOW_FIRST if i == 0 else f"c{cid_right - 2}",
            f"c{right_epi}",
        ]
        new_cells[cid_right] = cell_r
        new_lrc_ids_right.append(cid_right)

        # advance the chain bottoms for the next iteration
        left_bottom = (tl, tr)
        right_bottom = (tl_r, tr_r)

    # ---- (3) Fill in a-neighbors (above) for each new cell -----------
    for j in range(n_rows - 1):
        new_cells[new_lrc_ids_left[j]]["neighbors"].append(f"c{new_lrc_ids_left[j+1]}")
        new_cells[new_lrc_ids_right[j]]["neighbors"].append(f"c{new_lrc_ids_right[j+1]}")

    # ---- (4) Append new cells to init in ID order --------------------
    for cid in sorted(new_cells.keys()):
        init.append(new_cells[cid])

    # ---- (5) Cell 296 / 311 get their new a-neighbor -----------------
    init[296]["neighbors"].append(f"c{new_lrc_ids_left[0]}")
    init[311]["neighbors"].append(f"c{new_lrc_ids_right[0]}")

    # ---- (6) Each matched epidermis cell gets its new LRC l-neighbor -
    for (le, re_, _, _), cl, cr in zip(rows, new_lrc_ids_left, new_lrc_ids_right):
        init[le]["neighbors"].append(f"c{cl}")
        init[re_]["neighbors"].append(f"c{cr}")

    # ---- (7) Write back ----------------------------------------------
    VS_PATH.write_text(json.dumps(vs, indent=2))
    INIT_PATH.write_text(json.dumps(init, indent=2))

    cells_after = len(init)
    verts_after = len(vs)
    print(f"# after:  cells = {cells_after}, vertices = {verts_after}")
    print(f"# new cells: {cells_after - cells_before}, new vertices: {verts_after - verts_before}")
    print(f"# left-side LRC IDs:  {new_lrc_ids_left}")
    print(f"# right-side LRC IDs: {new_lrc_ids_right}")
    print(f"# terminal dumpers (topmost): left={new_lrc_ids_left[-1]}, right={new_lrc_ids_right[-1]}")
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
