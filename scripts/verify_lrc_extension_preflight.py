"""Pre-flight verification for Plan 2 (extend LRC geometry).

Implements Phase A.1 of
docs/plans/design_plans/2_2026-05-20_extend_LRC_geometry.md.

Asserts:
  (1) Vertices 689, 690 are referenced only by cell 296.
  (2) Vertices 706, 707 are referenced only by cell 311.
  (3) The 14 matched epidermis cell pairs that the extension will
      connect to exist at the expected y-ranges and x-centroids.

Exits 0 iff all checks pass; prints a per-check pass/fail line and a
summary. Safe to re-run; reads only, does not modify anything.

Run:
    poetry run python3 scripts/verify_lrc_extension_preflight.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VS_PATH = REPO / "src" / "sim" / "input" / "default_vs.json"
INIT_PATH = REPO / "src" / "sim" / "input" / "default_init_vals.json"


# (left_epi_id, right_epi_id, y_min, y_max) for the 14 rows that
# option γ (full elongation) will match. Options α and β use the
# first 7 and 10 rows respectively.
EXPECTED_EPI_ROWS = [
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
    (816, 829, 747, 1179),  # topmost — LRC will custom-stop at y=1025
]

# Vertices expected to be owned by a single LRC cell (the top vertices
# of cells 296 and 311 — the ones the extension stacks above).
VERTEX_OWNERSHIP = {
    689: 296,
    690: 296,
    706: 311,
    707: 311,
}

LEFT_X_CENTROID = 31.0
RIGHT_X_CENTROID = 111.0
CENTROID_TOL = 1.0   # µm
Y_TOL = 0.5          # µm


def y_range(vids, vs):
    ys = [vs[str(v)]["y"] for v in vids]
    return min(ys), max(ys)


def x_centroid(vids, vs):
    xs = [vs[str(v)]["x"] for v in vids]
    return sum(xs) / len(xs)


def main() -> int:
    vs = json.loads(VS_PATH.read_text())
    init = json.loads(INIT_PATH.read_text())

    n_pass = 0
    n_fail = 0

    print(f"# verify_lrc_extension_preflight.py")
    print(f"# vs   = {VS_PATH}")
    print(f"# init = {INIT_PATH}")
    print(f"# cells={len(init)}, vertices={len(vs)}")
    print()

    # --- Check group 1: vertex ownership ----------------------------
    print("Check group 1 — vertex ownership")
    for vid, expected_cell in VERTEX_OWNERSHIP.items():
        refs = [i for i, c in enumerate(init) if vid in c["vertices"]]
        if refs == [expected_cell]:
            print(f"  PASS  vertex {vid:>3} is owned only by cell {expected_cell}")
            n_pass += 1
        else:
            print(f"  FAIL  vertex {vid:>3} expected only in cell {expected_cell}, found in {refs}")
            n_fail += 1
    print()

    # --- Check group 2: matched epidermis cells exist ---------------
    print("Check group 2 — matched epidermis pairs (14 rows for option γ)")
    print(f"  {'#':>2}  {'L_id':>5} {'L_x':>6} {'L_ymin':>8} {'L_ymax':>8}   "
          f"{'R_id':>5} {'R_x':>6} {'R_ymin':>8} {'R_ymax':>8}   verdict")
    for i, (left_id, right_id, ymin_expected, ymax_expected) in enumerate(EXPECTED_EPI_ROWS, 1):
        l_ymin, l_ymax = y_range(init[left_id]["vertices"], vs)
        l_x = x_centroid(init[left_id]["vertices"], vs)
        r_ymin, r_ymax = y_range(init[right_id]["vertices"], vs)
        r_x = x_centroid(init[right_id]["vertices"], vs)

        ok = (
            abs(l_x - LEFT_X_CENTROID) < CENTROID_TOL
            and abs(l_ymin - ymin_expected) < Y_TOL
            and abs(l_ymax - ymax_expected) < Y_TOL
            and abs(r_x - RIGHT_X_CENTROID) < CENTROID_TOL
            and abs(r_ymin - ymin_expected) < Y_TOL
            and abs(r_ymax - ymax_expected) < Y_TOL
        )
        verdict = "PASS" if ok else "FAIL"
        if ok:
            n_pass += 1
        else:
            n_fail += 1
        print(
            f"  {i:>2}  {left_id:>5} {l_x:>6.1f} {l_ymin:>8.1f} {l_ymax:>8.1f}   "
            f"{right_id:>5} {r_x:>6.1f} {r_ymin:>8.1f} {r_ymax:>8.1f}   {verdict}"
        )
    print()

    # --- Summary ----------------------------------------------------
    total = n_pass + n_fail
    print(f"Summary: {n_pass}/{total} checks passed, {n_fail} failed.")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
