# Design Plan 2 — Extend LRC Geometry to Reach the Oscillation Zone

**Date:** 2026-05-20 (revised twice on 2026-05-20; final form)
**Author:** drafted by Claude under direction of skjannetty
**Scope:** ARORA `AUX_SYN_DEG_EXP` circulation module + default geometry
**Status:** draft, ready for implementation
**Branch:** `lrc-geometry-extension`
**Companion plan:** `1_2026-05-20_adjust_LRC_behavior.md` (full
LRC-behavior overhaul; this is the diagnostic predecessor)

---

## 0. Authorship and git policy

Claude's contributions to this work are documented in this plan and
in any implementation logs Sophia maintains. **No git commits,
tags, branch names, PR descriptions, or commit-message trailers
should include AI co-author attribution** (no
`Co-Authored-By: Claude`, no `🤖 Generated with Claude Code`, no
"with assistance from" footer, etc.). Implementation activity that
produces commits must reflect Sophia's authorship only.

This applies to:
- Commit author / committer fields
- Commit message bodies and trailers
- PR descriptions
- Tag annotations
- Branch names

---

## 1. Goal

A surgical, data-only change to ARORA's default geometry: **add new
lateral root cap (LRC) cells stacked above the existing top LRC
cells** so the LRC file reaches the oscillation zone (OZ) on tick
0 of the simulation. LRC cells remain non-growing, non-dividing,
non-dying.

The new cells are sized to match their inner-file (epidermis)
neighbors, so cell dimensions remain biologically reasonable. The
PIN distribution is rearranged so the topmost LRC cell becomes the
"terminal dumper" that delivers auxin laterally inward at the new
shootward end of the chain, near or within the OZ.

The diagnostic question:

> Is the absence of LRC contact at the OZ level sufficient on its
> own to explain ARORA's failure to oscillate?

If yes → this minimal geometric fix produces oscillation, and the
larger Plan 1 (full LRC behavior) is unnecessary for the chapter's
core claim. If no → geometric extension alone is insufficient and
Plan 1 (or a deeper structural change) is required.

Out of scope:
- Any LRC behavioral change (growth, division, apoptosis).
- Re-tuning circulation parameters beyond what is needed to make
  the new cells consistent with the existing LRC cells.
- Modifying any other tissue file.
- Any circulation module other than `AUX_SYN_DEG_EXP`.

---

## 2. Current state inventory

### 2.1 LRC geometry and PIN distribution today

The 14 LRC cells form two vertical files at `x = [21, 26]` (left)
and `x = [116, 121]` (right). The top cell on each side already
spans 24 inner-file epidermis cells.

| ID (left / right) | y-range | dist-from-tip | `pina` | `pinm` |
|---|---|---|---|---|
| 60 / 75 | [84, 94] | 73–83 | **1.0** | 0.1 |
| 90 / 105 | [94, 104] | 83–93 | **1.0** | 0.1 |
| 120 / 135 | [104, 109] | 93–98 | **1.0** | 0.1 |
| 136 / 151 | [109, 119] | 98–108 | **1.0** | 0.1 |
| 166 / 181 | [119, 134] | 108–123 | **1.0** | 0.1 |
| 210 / 225 | [134, 164] | 123–153 | **1.0** | 0.1 |
| **296 / 311** | **[164, 284]** | **153–273** | **0.0** | **1.0** |

The pattern: all LRC cells *except the top* are apical-dominant
(push auxin shootward up the chain with a 10% medial leak). The
top cell is all-medial — the "terminal dumper" that empties the
chain laterally into the epidermis. Under the current geometry
that dump happens at the meristem level (y ≈ 284), far below the
OZ XPP target (y ≈ 357.5).

**This plan moves the terminal dumper to the new top of the
extended chain.** Cell 296/311 become apical-dominant like the
others; whichever new cell sits at the topmost position takes
over the all-medial role.

### 2.2 y-range to cover

Above y = 284, the inner-file epidermis cells we want LRC contact
with are listed below. The plan supports three coverage options;
the recommended default is **Option γ (full elongation)**.

| # | Left epi | Right epi | y-range | h (µm) | dist-from-tip | Dev zone | α | β | γ |
|---|---|---|---|---|---|---|:-:|:-:|:-:|
| 1 | 634 | 647 | [284, 297] | 13 | 273–286 | transition | ✓ | ✓ | ✓ |
| 2 | 648 | 661 | [297, 311] | 14 | 286–300 | transition | ✓ | ✓ | ✓ |
| 3 | 662 | 675 | [311, 327] | 16 | 300–316 | transition | ✓ | ✓ | ✓ |
| 4 | 676 | 689 | [327, 346] | 19 | 316–335 | transition | ✓ | ✓ | ✓ |
| 5 | **690** | **703** | [346, 369] | 23 | 335–358 | transition (OZ XPP target row) | ✓ | ✓ | ✓ |
| 6 | 704 | 717 | [369, 397] | 28 | 358–386 | transition | ✓ | ✓ | ✓ |
| 7 | 718 | 731 | [397, 431] | 34 | 386–420 | T→E crossover | ✓ | ✓ | ✓ |
| 8 | 732 | 745 | [431, 472] | 41 | 420–461 | elongation |  | ✓ | ✓ |
| 9 | 746 | 759 | [472, 527] | 55 | 461–516 | elongation |  | ✓ | ✓ |
| 10 | 760 | 773 | [527, 582] | 55 | 516–571 | elongation |  | ✓ | ✓ |
| 11 | 774 | 787 | [582, 637] | 55 | 571–626 | elongation |  |  | ✓ |
| 12 | 788 | 801 | [637, 692] | 55 | 626–681 | elongation |  |  | ✓ |
| 13 | 802 | 815 | [692, 747] | 55 | 681–736 | elongation |  |  | ✓ |
| 14 | 816 | 829 | [747, 1179] | 432 | 736–1168 | elongation→differentiation | | | ✓* |

*Row 14 uses a custom-sized LRC cell at y = [747, 1025] (height
278 µm) which matches the lower part of the giant epi cells
816/829 (whose own y-range crosses into the differentiation zone).
The new LRC stops at y = 1025 so it does not extend into DZ.

### 2.3 Three extent options

| Option | Cells/side | Total new cells | New vertex count | Top LRC y | Distance covered (µm) |
|---|---|---|---|---|---|
| **α (TZ–EZ boundary)** | 7 | 14 | 28 | 431 | 273–420 |
| **β (mid-elongation)** | 10 | 20 | 40 | 582 | 273–571 |
| **γ (full elongation, recommended)** | 14 | 28 | 56 | 1025 | 273–1014 |

All three options share the same lowest 7 cells. β extends β
beyond α; γ extends γ beyond β. The Phase B script (§4) is
parameterized by a single `EXTENT` flag.

### 2.4 Neighbor reciprocity

The init JSON stores neighbors bidirectionally as `c<id>` strings.
When we add a new LRC cell, both the new cell's neighbor list and
the inner-file neighbor's list must reference each other. The
runtime fix-up (`fix_lrc_neighbors_after_growth`) only updates
adjacencies for inner-file cells that already had at least one
LRC neighbor — so initial neighbor lists must be complete at tick
0.

### 2.5 LRC cells are inert under `AUX_SYN_DEG_EXP`

LRC cells stay in `dev_zone = "roottip"`, do not grow or divide,
and use their init-JSON PIN distribution (the imposed atlas
short-circuits for roottip-type cells). They are auxin sources
(`auxin_w = 10`). All this remains true for new LRC cells: as
long as their IDs are in `NeighborHelpers.ROOTCAP_CELL_IDs` and
the duplicate list in `cell.py`, they behave like the existing
ones.

### 2.6 Vertex / cell ID allocation

- Current max vertex ID in `default_vs.json`: **917**
- Current max cell ID in `default_init_vals.json`: **829**
- New IDs are assigned starting at 830 (cells) and 918 (vertices),
  interleaved left-then-right (830 left, 831 right, 832 left, …).
  Specific ID ranges per option:

| Option | New cell IDs | New vertex IDs |
|---|---|---|
| α | 830–843 | 918–945 |
| β | 830–849 | 918–957 |
| γ | 830–857 | 918–973 |

---

## 3. Target geometry — Option γ (recommended default)

Add 28 new LRC cells (14 per side) stacked above cells 296/311,
each matching the y-range of one of the inner-file epidermis cells
in §2.2 (with the 14th cell custom-sized to stop at the
elongation–differentiation boundary).

### 3.1 ID and vertex allocation — left side (γ)

| New cell ID | y-range | h (µm) | Bottom-left v | Bottom-right v | Top-left v | Top-right v | Matched epi |
|---|---|---|---|---|---|---|---|
| 830 | [284, 297] | 13 | 689 (exist) | 690 (exist) | **918** | **919** | 634 |
| 832 | [297, 311] | 14 | 918 | 919 | **920** | **921** | 648 |
| 834 | [311, 327] | 16 | 920 | 921 | **922** | **923** | 662 |
| 836 | [327, 346] | 19 | 922 | 923 | **924** | **925** | 676 |
| 838 | [346, 369] | 23 | 924 | 925 | **926** | **927** | 690 ← OZ XPP target row |
| 840 | [369, 397] | 28 | 926 | 927 | **928** | **929** | 704 |
| 842 | [397, 431] | 34 | 928 | 929 | **930** | **931** | 718 |
| 844 | [431, 472] | 41 | 930 | 931 | **932** | **933** | 732 |
| 846 | [472, 527] | 55 | 932 | 933 | **934** | **935** | 746 |
| 848 | [527, 582] | 55 | 934 | 935 | **936** | **937** | 760 |
| 850 | [582, 637] | 55 | 936 | 937 | **938** | **939** | 774 |
| 852 | [637, 692] | 55 | 938 | 939 | **940** | **941** | 788 |
| 854 | [692, 747] | 55 | 940 | 941 | **942** | **943** | 802 |
| **856** | **[747, 1025]** | **278** | 942 | 943 | **944** | **945** | 816 ← topmost, terminal dumper |

All new left-side top vertices have `x = 21` (lateral) or
`x = 26` (medial), matching cell 296.

### 3.2 ID and vertex allocation — right side (γ)

| New cell ID | y-range | h (µm) | Bottom-left v | Bottom-right v | Top-left v | Top-right v | Matched epi |
|---|---|---|---|---|---|---|---|
| 831 | [284, 297] | 13 | 706 (exist) | 707 (exist) | **946** | **947** | 647 |
| 833 | [297, 311] | 14 | 946 | 947 | **948** | **949** | 661 |
| 835 | [311, 327] | 16 | 948 | 949 | **950** | **951** | 675 |
| 837 | [327, 346] | 19 | 950 | 951 | **952** | **953** | 689 |
| 839 | [346, 369] | 23 | 952 | 953 | **954** | **955** | 703 ← OZ XPP mirror |
| 841 | [369, 397] | 28 | 954 | 955 | **956** | **957** | 717 |
| 843 | [397, 431] | 34 | 956 | 957 | **958** | **959** | 731 |
| 845 | [431, 472] | 41 | 958 | 959 | **960** | **961** | 745 |
| 847 | [472, 527] | 55 | 960 | 961 | **962** | **963** | 759 |
| 849 | [527, 582] | 55 | 962 | 963 | **964** | **965** | 773 |
| 851 | [582, 637] | 55 | 964 | 965 | **966** | **967** | 787 |
| 853 | [637, 692] | 55 | 966 | 967 | **968** | **969** | 801 |
| 855 | [692, 747] | 55 | 968 | 969 | **970** | **971** | 815 |
| **857** | **[747, 1025]** | **278** | 970 | 971 | **972** | **973** | 829 ← topmost, terminal dumper |

All new right-side top vertices have `x = 116` (medial) or
`x = 121` (lateral), matching cell 311.

For options α and β, truncate after row 7 or row 10 respectively
and adjust the topmost-cell PIN assignment accordingly (§3.3).

### 3.3 PIN distribution — terminal-dumper-at-top

This plan implements what was previously called "Variant 2" —
the user has confirmed it as the only configuration.

**All existing LRC cells become apical-dominant.** This requires
modifying cells 296 and 311 in `default_init_vals.json`:

| Cell | Before | After |
|---|---|---|
| 296 | `pina=0.0, pinb=0.0, pinl=0.0, pinm=1.0` | `pina=1.0, pinb=0.0, pinl=0.0, pinm=0.1` |
| 311 | `pina=0.0, pinb=0.0, pinl=0.0, pinm=1.0` | `pina=1.0, pinb=0.0, pinl=0.0, pinm=0.1` |

**All new LRC cells *except the topmost on each side* are
apical-dominant** with the canonical pattern from cells 60–225:
`pina=1.0, pinb=0.0, pinl=0.0, pinm=0.1`.

**The topmost new LRC cell on each side is the terminal
dumper** with the (previously cell-296) pattern:
`pina=0.0, pinb=0.0, pinl=0.0, pinm=1.0`.

By option:

| Option | Left-side terminal dumper | Right-side terminal dumper |
|---|---|---|
| α | 842 (top y = 431, at TZ–EZ boundary) | 843 (mirror) |
| β | 848 (top y = 582, mid-EZ) | 849 (mirror) |
| **γ (default)** | **856 (top y = 1025, end of EZ)** | **857 (mirror)** |

Under option γ, auxin flows shootward through the entire LRC
chain — cell 60 (y=89) → … → 296 (y=284) → 830 (y=297) → … → 854
(y=747) — and is dumped laterally into the epidermis at the top
LRC cell (856/857), which spans y=[747, 1025], well into the EZ.
The 10 % medial leak at every intermediate cell still delivers
some auxin to each epidermis cell along the chain (including
cell 690 at the OZ XPP target row).

### 3.4 Per-cell init values for the new cells

Each new non-terminal cell inherits all init values from cell 60
(the canonical apical-dominant LRC cell), with one adjustment:
`auxin` starting value of 49.24 (same as cell 296) for a less
abrupt initial gradient than 1725.42 (cell 60's auxin) would
provide that far up the root.

Each new terminal cell (the topmost on each side) inherits all
init values from cell 296 (the canonical terminal dumper), so it
gets `pina=0.0, pinm=1.0` and `auxin=49.24` already.

Specifically for non-terminal new cells: `auxin = 49.24, arr = 0,
al = 1, pin = 0.275, pina = 1.0, pinb = 0.0, pinl = 0.0,
pinm = 0.1, k1 = 85.0, k2 = 75.0, k3 = 42.5, k4 = 200.0,
k5 = 0.07, k6 = 0.2, k_s = 0.3, k_d = 0.03, auxin_w = 10,
arr_hist = [0]*tau, growing = False, circ_mod = "cont"`.

Terminal new cells get the same fields except `pina = 0.0,
pinm = 1.0`.

---

## 4. Implementation phases

### Phase A — Pre-flight verification

A.1 Run a script that asserts:
- Vertices 689, 690 are referenced only by cell 296.
- Vertices 706, 707 are referenced only by cell 311.
- The matched epidermis cells exist with the expected vertex IDs
  and centroids (right-side mirror IDs already pre-verified during
  plan drafting on 2026-05-20).

A.2 Create the feature branch:
```
git checkout -b lrc-geometry-extension
```
No co-author attribution in commits on this branch (§0).

### Phase B — Generate the modified data files

This phase produces edited copies of
`src/sim/input/default_vs.json` and
`src/sim/input/default_init_vals.json`. Implementation is a
script — manual JSON editing of 28 new cells is too error-prone.

B.1 Write `scripts/extend_lrc_geometry.py`. Pseudocode:

```python
"""Extend the LRC geometry shootward to reach the oscillation zone.

Reads:  src/sim/input/default_vs.json, default_init_vals.json
Writes: same paths, in-place

The script implements option γ by default; pass EXTENT="alpha"
or EXTENT="beta" to truncate.
"""
import json
from pathlib import Path

EXTENT = "gamma"   # "alpha" | "beta" | "gamma"

# (matched_left_epi, matched_right_epi, y_min, y_max)
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
    (816, 829, 747, 1025),  # topmost — y_max custom (stops at EZ end)
]

n_rows = {"alpha": 7, "beta": 10, "gamma": 14}[EXTENT]
rows = LRC_EXTENSION_ROWS_FULL[:n_rows]

LEFT_X_OUTER, LEFT_X_INNER = 21, 26
RIGHT_X_INNER, RIGHT_X_OUTER = 116, 121

vs   = json.loads(Path("src/sim/input/default_vs.json").read_text())
init = json.loads(Path("src/sim/input/default_init_vals.json").read_text())

# Source templates
template_apical  = init[60]    # apical-dominant LRC cell
template_terminal = init[296]  # all-medial terminal dumper

def base_template(is_terminal):
    src = template_terminal if is_terminal else template_apical
    out = {k: v for k, v in src.items() if k not in ("vertices", "neighbors", "auxin")}
    out["auxin"] = 49.24
    return out

# (1) Flip cells 296 / 311 to apical-dominant
for cid in (296, 311):
    init[cid]["pina"] = 1.0
    init[cid]["pinb"] = 0.0
    init[cid]["pinl"] = 0.0
    init[cid]["pinm"] = 0.1

next_v = max(int(k) for k in vs.keys()) + 1   # 918
next_c = len(init)                             # 830

# (2) Build left side
left_bottom = (689, 690)
new_cells = {}        # cell_id -> entry, kept here until insertion
new_lrc_ids_left, new_lrc_ids_right = [], []

for i, (left_epi, right_epi, ymin, ymax) in enumerate(rows):
    is_terminal = (i == len(rows) - 1)
    # left-side new cell
    bl, br = left_bottom
    tl, tr = next_v, next_v + 1
    vs[str(tl)] = {"x": LEFT_X_OUTER, "y": ymax}
    vs[str(tr)] = {"x": LEFT_X_INNER, "y": ymax}
    next_v += 2
    cid_left = next_c; next_c += 1

    # right-side new cell, allocated immediately after
    bl_r, br_r = (706, 707) if i == 0 else right_bottom
    tl_r, tr_r = next_v, next_v + 1
    vs[str(tl_r)] = {"x": RIGHT_X_INNER, "y": ymax}
    vs[str(tr_r)] = {"x": RIGHT_X_OUTER, "y": ymax}
    next_v += 2
    cid_right = next_c; next_c += 1

    # Build cell entries (a-neighbor filled in after)
    cell_l = base_template(is_terminal)
    cell_l["vertices"] = [bl, br, tr, tl]
    cell_l["neighbors"] = [
        f"c{cid_left - 2}" if i > 0 else "c296",   # b-neighbor
        f"c{left_epi}",                              # m-neighbor (epi)
    ]
    new_cells[cid_left] = cell_l
    new_lrc_ids_left.append(cid_left)

    cell_r = base_template(is_terminal)
    cell_r["vertices"] = [bl_r, br_r, tr_r, tl_r]
    cell_r["neighbors"] = [
        f"c{cid_right - 2}" if i > 0 else "c311",   # b-neighbor
        f"c{right_epi}",                              # m-neighbor (epi)
    ]
    new_cells[cid_right] = cell_r
    new_lrc_ids_right.append(cid_right)

    left_bottom = (tl, tr)
    right_bottom = (tl_r, tr_r)

# (3) Fill in a-neighbors (above) for each cell
for j in range(len(rows) - 1):
    new_cells[new_lrc_ids_left[j]]["neighbors"].append(f"c{new_lrc_ids_left[j+1]}")
    new_cells[new_lrc_ids_right[j]]["neighbors"].append(f"c{new_lrc_ids_right[j+1]}")

# (4) Append to init in interleaved order (matching ID assignment)
for cid in sorted(new_cells.keys()):
    init.append(new_cells[cid])

# (5) Update cell 296 / 311 to list their new a-neighbor
init[296]["neighbors"].append(f"c{new_lrc_ids_left[0]}")
init[311]["neighbors"].append(f"c{new_lrc_ids_right[0]}")

# (6) Update each matched epidermis cell to list its new LRC l-neighbor
for cid_left, cid_right, (left_epi, right_epi, *_ ) in zip(
        new_lrc_ids_left, new_lrc_ids_right,
        zip(*[iter(rows)]*1)):  # iterate paired
    pass  # the next loop is clearer

for (le, re, _, _), cl, cr in zip(rows, new_lrc_ids_left, new_lrc_ids_right):
    init[le]["neighbors"].append(f"c{cl}")
    init[re]["neighbors"].append(f"c{cr}")

# (7) Write
Path("src/sim/input/default_vs.json").write_text(json.dumps(vs, indent=2))
Path("src/sim/input/default_init_vals.json").write_text(json.dumps(init, indent=2))

print(f"OK: added {2*len(rows)} cells, {4*len(rows)} vertices, extent={EXTENT}")
```

B.2 Run the script with `EXTENT = "gamma"`. Sanity-check the
output: `len(init) == 858`, `len(vs) == 974` for option γ.

B.3 The vertex-ordering convention in cell `vertices` lists
(`[bl, br, tr, tl]`) should match the existing convention. Verify
by inspecting cell 60's existing vertex order against its known
corners. If the existing convention differs (e.g.,
counter-clockwise from top-left), adjust B.1 accordingly.

### Phase C — Update the hardcoded LRC ID lists in Python code

C.1 `src/agent/default_geo_neighbor_helpers.py:14` —
`NeighborHelpers.ROOTCAP_CELL_IDs`: extend with the new IDs (for γ
that's 28 new entries: 830–857).

C.2 `src/agent/cell.py:734-749` — `root_cap_cells` inside
`calculate_dev_zone`: same extension.

C.3 Optional but recommended: refactor so the duplicate list in
`cell.py` is removed and `calculate_dev_zone` reads from
`NeighborHelpers.ROOTCAP_CELL_IDs` only. Not strictly required
for this plan; flagged for follow-up.

### Phase D — Tests

D.1 `tests/functional/test_initialization_symmetry_unittest.py`:
add assertions
- `len(cell_list) == 830 + 2*N` where N is the per-option count
  (14 for γ).
- The new IDs all have `cell_type == "roottip"`.
- The OZ XPP target row LRC cell (838 left, 839 right under γ)
  has its matched epi (690 left, 703 right) in its neighbors.
- The matched epi cells reciprocate.
- Symmetry: for each left-side new cell at y-range Y, the
  corresponding right-side new cell exists at the same y-range.
- Cells 296 and 311 have `pina = 1.0` after the change (the
  PIN flip).
- The topmost new cell on each side has `pinm = 1.0` (terminal
  dumper).

D.2 New: `tests/functional/test_lrc_reaches_oz_functional.py`:

- `test_new_lrc_cells_have_auxin_w_10`
- `test_new_lrc_intermediate_cells_have_apical_dominant_pin`
- `test_new_lrc_topmost_cell_is_terminal_dumper`
- `test_lrc_chain_unbroken` — walk from cell 60 following
  a-neighbors through cell 296 then through all new cells to the
  topmost; assert each step exists.
- `test_oz_xpp_target_two_hops_from_lrc` — cell 693 → its
  l-neighbor cell 690 → its l-neighbor cell 838 (LRC). Two hops.
- `test_no_exceptions_50_ticks` — run a 50-tick simulation with
  `AUX_SYN_DEG_EXP`; assert no exceptions.

D.3 `uv run python3 -m pytest tests/ -x -q` must continue to
pass (modulo the pre-existing `test_calculate_arr` failure noted
in CLAUDE.md §7).

### Phase E — Documentation

E.1 Add a §15 to `ASSUMPTIONS.md` noting that the default geometry
was extended with N×2 new LRC cells (N = 14 under γ) and that
cells 296/311 had their PIN distribution flipped from
terminal-dumper to apical-dominant. Cross-reference this plan.

E.2 Update `CLAUDE.md` §2 with a one-paragraph note on the
geometric extension and the diagnostic that motivates it.

E.3 If the diagnostic in §8 produces a publishable result,
incorporate the finding (positive or negative) into the
dissertation chapter draft.

---

## 5. Neighbor-tracking strategy

Plan 2's neighbor work is *static and one-shot*:

1. All new cells exist at tick 0 with complete neighbor lists.
2. `fix_lrc_neighbors_after_growth` runs every tick but finds no
   geometric changes to react to: LRC y-ranges are fixed.
3. Inner-file cell divisions during a simulation could still create
   new adjacencies with LRC. The existing
   `Divider.set_one_side_neighbors` code path (lines 225–233)
   calls `check_if_neighbors_with_new_root_cap_cell` for daughters
   of any cell with an LRC neighbor — this works unchanged because
   we only extended the ID list.
4. No assumption is added beyond what's already in the codebase.

The "funky workarounds" Sophia previously wrote remain in place
and continue to function as designed. The intervention is
strictly data-side.

---

## 6. File-by-file change manifest

| File | Change |
|---|---|
| `src/sim/input/default_vs.json` | 4N new vertex entries (N = 14 under γ → 56 vertices, IDs 918–973). |
| `src/sim/input/default_init_vals.json` | 2N new cell entries (IDs 830–857 under γ). PIN flip on cells 296 and 311. Neighbor list updates on cells 296, 311, and 2N matched epidermis cells. |
| `src/agent/default_geo_neighbor_helpers.py` | Extend `ROOTCAP_CELL_IDs` by 2N. |
| `src/agent/cell.py` | Extend `root_cap_cells` list in `calculate_dev_zone` by 2N. |
| `scripts/extend_lrc_geometry.py` | New — JSON-generation script (Phase B). |
| `tests/functional/test_initialization_symmetry_unittest.py` | Add 7 assertions (D.1). |
| `tests/functional/test_lrc_reaches_oz_functional.py` | New (D.2). |
| `ASSUMPTIONS.md` | Add §15 note (E.1). |
| `CLAUDE.md` | One-paragraph update (E.2). |

No changes to circulation modules, divider, vertex mover, or any
agent behavior code.

---

## 7. Risks and rollback

| Risk | Likelihood | Mitigation |
|---|---|---|
| Vertex-ordering convention `[bl, br, tr, tl]` doesn't match the existing one | medium | Inspect cell 60's existing vertex list and corner geometry before running B.1. |
| Flipping cell 296/311 to apical-dominant removes the inward auxin dump at the meristem, which the rest of the existing model may have depended on | medium | This is by design of the plan, but worth checking: run E1 (sanity) and inspect epidermis-zone auxin distribution. If the meristem-zone epidermis becomes auxin-starved, consider reducing pinm of cells 296/311 from 0.1 to 0.2–0.3 to retain some leakage. |
| The new LRC cells' init `auxin` value (49.24) creates an unphysical jump at tick 0 | low | After 5–10 ticks of transport, the gradient re-equilibrates. Optionally, in a future revision, set the new cells' initial auxin by linear interpolation from cell 60's auxin (1725.42 at y=89) to a low value at the top. Not necessary for the diagnostic. |
| Adding 2N new cells changes `len(cell_list)` and breaks any test that hardcodes 830 | medium | D.1 explicitly updates the count. Also grep for `830` and `len(.*cell.*list)` in tests. |
| The topmost LRC cell's apical PIN is unused (no apical neighbor) | low | Topmost cell is terminal dumper (`pina = 0.0`); no apical efflux is expected. |
| GA parameter ranges that previously worked may now be suboptimal | medium | E4's sensitivity sweep guards against this. |
| Cached fitness or simulation outputs based on old geometry pollute the diagnostic | medium | Before running §8, delete `param_est/ARORA_output_*.csv`, `verify_osc_test_*`, and any `plots/` from prior runs. |
| The new cells' init `arr_hist` length must match the global `tau` | high | `arr_hist` is built from `tau` in `input.py`; copying from cell 60 should match. Verify in B.1. |
| Option γ's 14th cell is 278 µm tall — three times any other new cell | low | Same height ratio as existing cell 296 (120 µm in a column of 5–30 µm cells). The existing code path handles it. |

**Rollback:** This plan lives entirely on the
`lrc-geometry-extension` branch. To revert, switch back to the base
branch. JSON files and two Python ID-list additions are the only
modifications.

---

## 8. Evaluation — does the geometric extension enable OZ oscillation?

The diagnostic the plan exists to answer. The evaluation has four
mandatory stages (E1–E4) and two optional ones (E5–E6).

### Default baseline parameters

For E2 and E3, use the best-known parameter set from prior GA
search `osc_search_03`, stored at
`param_est/ga_runs/osc_search_03/best_summary.txt`. The relevant
parameters for `AUX_SYN_DEG_EXP` are a subset of the full
`IMPOSED_PIN_ARR_ACTIVITY` parameter space:

```
ks_aux = 0.10974987654930562
kd_aux = 0.16372745814388645
k5     = 0.023203197888695095    # AUX/LAX rate (unused in AUX_SYN_DEG_EXP since auxlax=1)
k6     = 0.02                    # PIN export rate
```

(`ks_arr`, `kd_arr`, `k1`, `tau` from the best-summary do not
apply because `AUX_SYN_DEG_EXP` forces ARR = 0.)

If those values lead to obviously broken behavior (e.g., auxin
explosion / collapse), fall back to the midpoints of the GA's
ranges (`ks_aux = 5.05, kd_aux = 0.275, k5 = 0.51, k6 = 0.51`).

### E1 — Sanity check (~30 min)

Verify the intervention had the intended effect on the model. Run
a 5-tick simulation with the new geometry:

1. Confirm `len(sim.cell_list) == 830 + 2N`.
2. Confirm the OZ-row LRC cell (838 left under γ) has the matched
   epi (690) in its m-neighbors and `auxin > 0`.
3. Confirm cell 690 has 838 in its l-neighbors.
4. Confirm cell 693 has cell 690 in its l-neighbors (this was
   already true pre-fix; verify unchanged).
5. Plot per-cell auxin at tick 5 as a kymograph / heatmap. Confirm
   the LRC chain is visible and that auxin in the OZ-level
   epidermis cells (690, 704, 718, etc.) is higher than it would
   be without the extension.
6. Confirm the topmost LRC cell on each side has `pinm == 1.0`
   (terminal dumper).
7. Confirm cells 296 and 311 now have `pina == 1.0` (PIN flip).

**Pass criterion:** all seven checks succeed.

### E2 — Baseline establishment: pre-fix non-oscillation (~1 hr)

On the branch *before* the geometry change (i.e., on base
branch):

1. Run a single 26-hour simulation (234 ticks at `dt = 1/9 h`)
   with `CircModEnum.AUX_SYN_DEG_EXP`, `PinLocalizationRulesetEnum.IMPOSED`,
   and the default baseline parameters above.
2. Extract auxin time series at cell 693 (the OZ XPP target).
   Also extract the mean auxin time series across all OZ XPP cells
   (transition + elongation zone, `cell_type == "peri"`). The
   existing fitness function
   `auxin_oscillation_across_XPP_cells_in_OZ` in
   `param_est/fitness_functions.py` does this analysis already.
3. Compute the FFT amplitude using that fitness function. Record
   the value `FFT_baseline`.
4. Plot the time series. Visually confirm: no clear periodic peaks.
5. Save both the time series and the FFT amplitude to
   `evaluation/baseline_run.csv`.

**Pass criterion:** `FFT_baseline < 10` (per CLAUDE.md §7 step 2's
threshold for "detectable oscillatory content"). If the baseline
*already* shows oscillation, the diagnostic is invalid — revisit
the parameter set.

### E3 — Intervention run: same parameters, new geometry (~1 hr)

On the `lrc-geometry-extension` branch:

1. Run the identical 26-hour simulation with the identical
   parameter set used in E2.
2. Extract auxin time series at cell 693 and across OZ XPP cells.
3. Compute FFT amplitude → `FFT_intervention`.
4. Plot the time series.
5. Save to `evaluation/intervention_run.csv`.

**Pass criterion (oscillation enabled):**
- `FFT_intervention > 10` (CLAUDE.md threshold), AND
- `FFT_intervention > 3 × FFT_baseline` (substantial improvement),
  AND
- Visually, at least 2 peaks of comparable amplitude appear in
  the second half of the simulation.

**Fail criterion:** any of the above is not met. If E3 fails,
proceed to E4 anyway — the sensitivity sweep often reveals
parameter regimes where the geometry change matters even if the
one baseline point did not.

### E4 — Sensitivity sweep: robustness across parameter sets (~1 day)

A single parameter point is not enough — the diagnostic must
distinguish "the geometry made it possible" from "we got lucky on
one parameter combination."

1. Identify 10 distinct parameter chromosomes:
   - Chromosome 1: the default baseline (from E2).
   - Chromosomes 2–10: 9 samples drawn uniformly at random from
     the relevant GA parameter space (for `AUX_SYN_DEG_EXP`, that's
     `ks_aux ∈ [0.1, 10]`, `kd_aux ∈ [0.05, 0.5]`,
     `k5 ∈ [0.02, 1]`, `k6 ∈ [0.02, 1]`).
2. For each chromosome, run E2 (baseline) and E3 (intervention)
   pairs. Record both FFT amplitudes.
3. Plot the 10 baseline FFTs and 10 intervention FFTs side by
   side (scatter plot, baseline on x-axis, intervention on y-axis,
   with the `y = x` line drawn for reference).
4. Compute aggregate statistics:
   - Number of (baseline, intervention) pairs where
     `FFT_intervention > FFT_baseline`.
   - Mean and median `FFT_intervention - FFT_baseline`.
   - Number of intervention runs with `FFT_intervention > 10`.

**Pass criterion (geometry change is generically helpful):**
- ≥ 8 / 10 pairs have `FFT_intervention > FFT_baseline`, AND
- ≥ 5 / 10 intervention runs have `FFT_intervention > 10`.

**Partial pass:** 5–7 / 10 pairs improved → the intervention helps
under some regimes but not others; still publishable.

**Fail:** ≤ 4 / 10 pairs improved → geometric extension does not
generically enable oscillation; Plan 1 (or another deeper change)
is needed.

### E5 — GA convergence (optional, ~1–2 days)

If E3 + E4 give a positive but ambiguous result, run a GA
optimization on the new geometry to see how good a fit it can
find:

1. On `lrc-geometry-extension`, run a 20-generation GA with
   `AUX_SYN_DEG_EXP` and the existing GA fitness (consider adding
   `auxin_oscillation_across_XPP_cells_in_OZ` as a fitness
   component if it isn't already — CLAUDE.md §7 step 5 has
   instructions).
2. Plot best-fitness-per-generation.
3. Take the best chromosome from the final generation; reproduce
   its E3 metrics.
4. Compare the GA's best-fit FFT amplitude to E4's median
   intervention FFT amplitude.

### E6 — Visual / qualitative confirmation (optional, ~1 hr)

1. Build a kymograph (space-time plot) of pericycle/XPP auxin in
   the OZ for both baseline and intervention runs, using the same
   color scale.
2. Look for the "diagonal stripes" VDB's Fig. 2 / 3 show — the
   spatial manifestation of temporal oscillations.
3. Compare directly to VDB Fig. 2C in the bioRxiv paper.

### Interpreting the four possible outcomes

| E3 | E4 | Conclusion |
|---|---|---|
| Pass | Pass | Geometric gap was the primary cause. Plan 1 unnecessary for the chapter's core claim. |
| Pass | Partial | Geometric extension helps in some parameter regimes. Worth reporting; consider Plan 1 as complement. |
| Pass | Fail | E3 was a parameter-set artifact. Treat E3 as negative for the dissertation; proceed to Plan 1. |
| Fail | Fail | Geometric extension is insufficient. Plan 1 is required. |

Each outcome is publishable. Negative results constrain the set of
plausible mechanism-breaking assumptions.

---

## 9. Open questions for the user before implementation

All previous open questions are resolved:

1. **PIN strategy:** Variant 2 (terminal dumper at top of new chain;
   cells 296/311 flipped to apical-dominant). ✓
2. **Extent:** Three options (α, β, γ) with γ as default. ✓
3. **Cell density:** One LRC cell per inner-file epidermis cell. ✓
4. **Branch name:** `lrc-geometry-extension`. ✓
5. **Baseline parameters:** from `osc_search_03/best_summary.txt`
   (see §8). ✓

No remaining open questions. Implementation can proceed.
