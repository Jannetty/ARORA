# Design Plan 1 — Adjust LRC Behavior to Match VDB 2018

**Date:** 2026-05-20
**Author:** drafted by Claude under direction of skjannetty
**Scope:** ARORA simplified `AUX_SYN_DEG_EXP` circulation module + default geometry
**Status:** draft, ready for implementation

---

## 1. Goal

Bring ARORA's lateral root cap (LRC) cell behavior in line with the van
den Berg & ten Tusscher 2018 model so that the LRC is a *dynamic*
participant in the reflux loop rather than a static atlas of 14
cells. Specifically, after this change ARORA must:

1. Let LRC cells **grow** at zone-appropriate rates (currently they
   are forced to `dev_zone = "roottip"` and have growth rate 0).
2. Let LRC cells **divide**, in the meristematic part of their
   trajectory only (currently division is gated to dev_zone ==
   `"meristematic"` but LRC cells are never in that zone).
3. Let LRC cells **circulate auxin** via the imposed-PIN reflux
   loop (apical PIN2 to push auxin shootward; lateral PIN2 to
   deliver auxin inward to vasculature/pericycle at the TZ–EZ
   boundary). The most-simple circulation module
   (`AUX_SYN_DEG_EXP`, i.e. `CircModEnum.AUX_SYN_DEG_EXP`) must be
   the supported path.
4. Have **LRC daughter cells inherit** the right `auxin_w`,
   `ks_aux`, `kd_aux`, and PIN-distribution behavior (currently the
   atlas-keyed-by-ID approach silently breaks on division because
   daughter IDs are not in `ROOTCAP_CELL_IDs`).
5. **Remove LRC cells** when the basal membrane of the top LRC cell
   passes the TZ–EZ boundary of the epidermis — matching VDB's
   "apoptosis and shed off" rule (§2.5.5, lines 535–544 of the
   paper).

Out of scope:
- Modeling cytoplasmic vs. vacuolar growth modes.
- Modeling pH-dependent influx.
- Modeling LRC cytokinin or peptide signaling.
- Modeling sloughed-off LRC cells as detached agents.
- Other circulation modules (`UNIVERSAL_SYN_DEG`, `INDEP_SYN_DEG`,
  `AUX_SYN_DEG_ONLY`, `IMPOSED_PIN_ARR_ACTIVITY`) are not required
  to support the new LRC behavior in this iteration.

---

## 2. Current state inventory (what an implementer needs to know first)

### 2.1 Static LRC ID list

`src/agent/default_geo_neighbor_helpers.py:14` defines
`NeighborHelpers.ROOTCAP_CELL_IDs = [60, 90, 120, 136, 166, 210, 296,
75, 105, 135, 151, 181, 225, 311]`. The same list is duplicated
inline in `src/agent/cell.py:734-749` inside `calculate_dev_zone()`.
This list is the *only* way a cell is recognized as LRC. It is
hard-coded to the 14 initial IDs and never updated. As a
consequence:

- The list is consulted in 6 places: `cell.py` (dev_zone), `default_geo_neighbor_helpers.py` (×5 — neighbor direction, dynamic LRC search, fix-up, removal), `divider.py` (lines 228–230).
- Cell IDs are assigned monotonically (`sim.get_next_cell_id`) and never recycled. Any LRC daughter created by division gets a fresh ID > 829 and is *not* in `ROOTCAP_CELL_IDs`.

### 2.2 Dev zone and cell type assignment

`Cell.calculate_dev_zone()` returns `"roottip"` if `self.c_id in
root_cap_cells`, regardless of position. `Cell.calculate_cell_type()`
in turn returns `"roottip"` whenever `self.dev_zone == "roottip"`,
so LRC cells have `cell_type = "roottip"` for the entire simulation.

`Cell.get_growth_rate()` returns 0 for `dev_zone == "roottip"`. So
LRC cells never grow.

`Divider.update()` filters `cells_to_divide` to keep only those with
`dev_zone == "meristematic"`. LRC cells are never in that zone, so
they are never divided even if their height grew past
`division_height`.

### 2.3 Imposed PIN atlas

`Cell.get_imposed_pin_distribution()` short-circuits with `return
self.circ_mod.get_pin_weights()` whenever `dev_zone == "roottip" or
cell_type == "roottip"`. So LRC cells use the PIN weights baked into
their init JSON entry and never participate in the zone-banded
imposed atlas. The atlas branches on `cell_type` (`vasc`, `peri`,
`endo`, `cortex`, `epidermis`) — there is currently **no** `lrc`
branch.

### 2.4 Neighbor topology

`VertexMover.update()` calls
`NeighborHelpers.fix_lrc_neighbors_after_growth(sim)` unconditionally
every tick under default geometry. This iterates non-roottip cells
whose `l_neighbors` already contain an LRC cell and (a) tries to
attach any newly-adjacent LRC cells via
`check_if_neighbors_with_new_root_cap_cell`, and (b) tries to detach
LRC cells whose y-range no longer overlaps via
`check_if_no_longer_neighbors_with_root_cap_cell`. Both helpers
match LRC cells by membership in `ROOTCAP_CELL_IDs`.

`Cell.find_new_neighbor_relative_location()` returns the magic
string `"cell no longer root cap cell neighbor"` when an LRC pair
should be detached — `add_neighbor()` then silently passes. This is
the "funky workaround" the user referred to.

`Divider.set_one_side_neighbors()` (lines 225–233) handles the
LRC-neighbor case during division by *removing* the LRC from the
mother's neighbor list and asking
`check_if_neighbors_with_new_root_cap_cell` to find LRC neighbors
for each daughter from scratch. This works today because LRC cells
themselves never divide.

### 2.5 Cell removal

`GrowingSim.remove_from_cell_list(cell)` exists at `sim.py:252` and
removes a cell from `cell_list`. It does **not** touch
`vertex_list`, neighbor lists of remaining cells, or the divider
queue. There is currently no caller; cell removal is presently only
used by the divider (mother is replaced by two daughters).

### 2.6 Circulation module

`CircModEnum.AUX_SYN_DEG_EXP`
(`circ_module_aux_syn_deg_export.py`) is the simplest mode that
still includes transport. It only supports
`PinLocalizationRulesetEnum.IMPOSED`. It carries `ks_aux`, `kd_aux`,
`auxin_w` per cell. AUX/LAX is hard-pinned to 1. ARR and PIN
abundance ODEs are no-ops. Initial values come from the init JSON
(`default_init_vals.json`); the LRC entries have `auxin_w = 10`.

---

## 3. Target VDB-aligned behavior

| Aspect | VDB 2018 spec | ARORA target (after this plan) |
|---|---|---|
| LRC growth in MZ | `rgrowthMZ` (cytoplasmic), divisions allowed | `MERISTEMATIC_GROWTH_RATE`, divisions allowed |
| LRC growth in TZ | LRC "lacks a TZ" — collapses MZ → EZ | LRC transitions directly from `meristematic` to `elongation` (skip `transition`); use `MERISTEMATIC_GROWTH_RATE` until that point |
| LRC growth in EZ | `rgrowthEZ` (vacuolar expansion), no division | `ELONGATION_GROWTH_RATE`, no division |
| LRC PIN polarity | apical PIN2 dominant; lateral PIN2 in RC and epidermis-side LRC in TZ and EZ to push auxin inward | new `_pin_*` branches keyed on `cell_type == "lrc"`: apical-dominant in MZ/EZ, with `m`-membrane weight rising near the TZ–EZ boundary to deliver auxin inward |
| LRC auxin source | elevated `pA` in LRC throughout | `auxin_w = 10` inherited by daughters; do not reset to 1 |
| LRC apoptosis | when basal membrane of top LRC cell passes start of EZ of epidermis (distance `ELONGATION_MAX_DIST_FROM_TIP_LRC` — same as epidermis EZ boundary) | new `Sloughing` pass each tick: any LRC cell whose `min_y` (basal vertex) crosses the elongation threshold is removed |
| Detachment from sim | sloughed off | `sim.remove_from_cell_list` + clean up neighbor refs + drop vertices that are no longer used by any cell |
| Daughter inheritance | transporters + concentrations from mother | already done by `Divider` via `cell.get_circ_mod().get_state()`; verify `auxin_w` is in the state dict (it is, in `CirculateModuleAuxinSynDegExport.get_state`) |

---

## 4. Implementation phases

The plan is decomposed so that each phase is independently
shippable, testable, and rollback-able.

### Phase A — Replace static LRC ID list with a dynamic cell-type predicate

**Why first:** every other phase needs this. Daughters need to be
recognizable as LRC; the divider needs to assign daughters as LRC;
neighbor logic needs to follow LRC cells through division.

**Tasks:**

A.1 Add a new `cell_type = "lrc"` (and parallel `"rc"` if you want
to retain the distinction VDB makes between the curved RC and the
flank LRC — recommended `"lrc"` only for v1, since ARORA's atlas
doesn't currently distinguish them).

A.2 Add `Cell.is_lrc()` returning `True` iff `self.cell_type ==
"lrc"`. Add `set_cell_type(t)` setter for the divider to use.

A.3 At init, mark cells whose ID is in the current
`ROOTCAP_CELL_IDs` as `cell_type = "lrc"` (instead of `"roottip"`).
Do this in `Cell.__init__` *after* dev_zone is computed.

A.4 Decouple LRC from `dev_zone == "roottip"`: in
`Cell.calculate_dev_zone`, *remove* the `if self.c_id in
root_cap_cells: return "roottip"` early return. Let LRC cells get
their dev_zone from y-position like every other cell.

A.5 Rewrite every `c_id in NeighborHelpers.ROOTCAP_CELL_IDs` check
to `cell.is_lrc()`. Locations:
- `src/agent/default_geo_neighbor_helpers.py` lines 156–160,
  179–181, 226–227, 237, 247, 257
- `src/sim/divider/divider.py` lines 228–230
- `src/agent/cell.py` line 750 (remove entirely, see A.4)

A.6 Keep `NeighborHelpers.ROOTCAP_CELL_IDs` as a *seed* list used
only by `input.py` at simulation startup (rename to
`INITIAL_LRC_CELL_IDs` to make the role explicit). The seed list
must not be consulted after `setup()` returns.

A.7 Audit the meaning of `dev_zone == "roottip"` for the genuine
QC / columella / curved-RC cells (`Cell.get_growth_rate()` line 779,
`get_imposed_pin_distribution()` line 860, `VertexMover.execute_vertex_movement()`
line 257). For v1, those stay as-is: only the LRC ID list moves to a
cell_type predicate. The 8 QC/columella cells in the curved region
keep `dev_zone == "roottip"`.

**Acceptance for Phase A:**
- `tests/unit/test_neighbor_helpers_unittest.py` passes with
  `cell.is_lrc()` rewrites.
- A 1-tick simulation starting from default init shows the 14 LRC
  cells now have `cell_type == "lrc"` and `dev_zone == "meristematic"`
  (since their distance-from-tip is 78–213 µm, all in MZ).
- LRC neighbor lists at tick 0 are unchanged from before the change.

### Phase B — Let LRC cells grow and divide

**Tasks:**

B.1 Extend `Cell.get_growth_rate()` so that `cell_type == "lrc"`
returns:
- `MERISTEMATIC_GROWTH_RATE` if `dev_zone == "meristematic"`
- `MERISTEMATIC_GROWTH_RATE` if `dev_zone == "transition"`
  (because VDB says LRC lacks a TZ — treat it as part of MZ for
  growth)
- `ELONGATION_GROWTH_RATE` if `dev_zone == "elongation"`
- 0 if `dev_zone == "differentiation"` (LRC should not reach this
  zone — see Phase D)

The height cap of 250 µm remains.

B.2 At init, set `cell.growing = True` for all LRC cells (currently
their init JSON likely has `growing = True` already; verify by
reading `default_init_vals.json` for IDs 60, 90, …).

B.3 Extend `Divider.update()` so that LRC cells are eligible to
divide. Change the filter from
```python
[cell for cell in self.cells_to_divide if cell.get_dev_zone() == "meristematic"]
```
to
```python
[cell for cell in self.cells_to_divide
 if cell.get_dev_zone() == "meristematic"
    or (cell.is_lrc() and cell.get_dev_zone() in ("meristematic", "transition"))]
```
(Equivalently: LRC cells divide for as long as they would be in MZ
under VDB's collapsed-TZ assumption.)

B.4 In `Divider.update()`, after constructing daughters, propagate
the LRC tag:
```python
if cell.is_lrc():
    new_top_cell.set_cell_type("lrc")
    new_bottom_cell.set_cell_type("lrc")
```
(Place this immediately after the `set_growing` calls.)

B.5 Verify the divider's neighbor-handling for divided LRC cells.
The current code in `set_one_side_neighbors` lines 225–233 detects
LRC neighbors of the dividing cell (mother) and calls
`check_if_neighbors_with_new_root_cap_cell` for each daughter. This
*assumes the dividing cell is not itself LRC*. We are now dividing
LRC cells, so:
- For an LRC mother dividing, its l-neighbors are non-LRC cells
  (inner files) and its m-neighbors are nothing (LRC is the
  outermost layer). The existing inner-file neighbors must be
  carried over correctly.
- Add a unit test (Phase F.3) covering an LRC mother division.

**Acceptance for Phase B:**
- 1-tick smoke test: a run with `AUX_SYN_DEG_EXP` proceeds without
  exceptions when LRC cells are growing.
- Multi-tick test: an LRC cell whose `height >= division_height`
  appears in the divider's queue and is divided into two LRC
  daughters with correct vertex positions, correct `cell_type ==
  "lrc"`, and correct neighbor structure.

### Phase C — LRC-specific PIN distribution in imposed atlas

**Tasks:**

C.1 Remove the early return in
`Cell.get_imposed_pin_distribution()` for LRC cells:
```python
# Before:
if dev_zone == "roottip" or cell_type == "roottip":
    return self.circ_mod.get_pin_weights()
# After:
if dev_zone == "roottip" and cell_type == "roottip":
    # only true RC/QC/columella cells now
    return self.circ_mod.get_pin_weights()
```

C.2 Add an `lrc` branch to `_pin_meristematic` and `_pin_transition`
(treating LRC's "transition" zone as still MZ-style per VDB).
Initial weights, conservative defaults from VDB Fig. 1D:
- MZ + TZ (treated as MZ for LRC): apical-dominant, `{"a": 0.8,
  "b": 0.1, "l": 0.0, "m": 0.1}` (m = inward, l = outward; LRC has
  nothing outside it, so the small "l" leak corresponds to
  apoplast escape)
- EZ: `{"a": 0.5, "b": 0.0, "l": 0.0, "m": 0.5}` — half apical
  (shootward), half medial (inward) — this is the *lateral inward
  delivery* VDB identifies as essential.

C.3 Add an `lrc` branch to `_pin_elongation` and
`_pin_differentiation`. For elongation, see C.2 above. For
differentiation, the LRC should have been sloughed by then (Phase
D) but defensively return apical-dominant.

C.4 (Optional) Make the "m" weight in C.2 EZ phase rise smoothly
with distance from the TZ–EZ boundary, to approximate VDB's "auxin
loading zone" that builds up over the lower EZ. For v1, keep it
flat at 0.5; revisit in a future iteration.

**Acceptance for Phase C:**
- Unit test: an LRC cell at distance 78 µm (MZ) returns the new
  `lrc` MZ weights, not the previous initial-distribution weights.
- An LRC cell artificially placed at distance 450 µm (EZ) returns
  the EZ weights.
- Visual sanity check: in a run, kymograph of auxin in the OZ XPP
  cell shows non-zero contribution from LRC delivery.

### Phase D — LRC apoptosis (cell removal)

**Tasks:**

D.1 Define `LRC_SHEDDING_DIST_FROM_TIP =
ELONGATION_MAX_DIST_FROM_TIP_EPIDERMIS`. For ARORA's current
thresholds, this is `ELONGATION_MAX_DIST_FROM_TIP` = 1014 µm. VDB's
literal rule is "basal membrane of top LRC cell passes border of TZ
and EZ of the epidermis" — which in ARORA's threshold terminology
is **the start** of EZ, not the end. So set
`LRC_SHEDDING_DIST_FROM_TIP = TRANSITION_MAX_DIST_FROM_TIP = 414`
µm. Make this a named constant in `cell.py` (top of file with the
other zone thresholds).

D.2 Implement `Cell.should_slough() -> bool`:
```python
def should_slough(self) -> bool:
    if not self.is_lrc():
        return False
    # basal y of cell = max distance from tip among its vertices
    root_tip_y = self.sim.get_root_tip_y()
    basal_y = self.quad_perimeter.get_max_y()  # cells stacked toward shoot at higher y
    basal_dist = abs(basal_y - root_tip_y)
    return basal_dist >= LRC_SHEDDING_DIST_FROM_TIP
```
(Confirm the y-orientation: ARORA tracks root tip at *minimum* y.
The "basal" — shootward — vertex is at maximum y. The cell sloughs
when its top edge passes the EZ boundary.)

D.3 Implement `GrowingSim.slough_lrc_cells()` (new method in
`sim.py`):
```python
def slough_lrc_cells(self) -> None:
    if self.geometry != "default":
        return
    to_remove = [c for c in self.cell_list if c.should_slough()]
    for cell in to_remove:
        self._remove_cell_completely(cell)
```

D.4 Implement `GrowingSim._remove_cell_completely(cell)` — this is
the core sloughing primitive. It must:
- For every cell `n` in `cell.get_all_neighbors()`: call
  `n.remove_neighbor(cell)` so dangling refs are cleared.
- Call `self.remove_from_cell_list(cell)`.
- For each vertex of `cell`, if it is not used by any other cell in
  `cell_list`, remove it from `self.vertex_list`. Otherwise leave it
  alone (a shared vertex between an LRC cell and an inner-file
  epidermis cell must be preserved while the epidermis cell still
  uses it; ARORA does not currently model the LRC–epidermis wall
  separately, so the vertex stays).
- If `cell` is in `self.divider.cells_to_divide`, remove it.
- If `cell` has a delta registered in
  `self.vertex_mover.cell_deltas`, remove that entry.

D.5 Wire it into the tick loop. Sloughing must run *after*
`VertexMover.update()` (which calls
`fix_lrc_neighbors_after_growth`) so growth-induced positions are
current, but *before* the next tick's `Cell.update()` calls. The
cleanest insertion point is in `GrowingSim.on_update()` (or
equivalent — search for the per-tick loop in `sim.py`). After the
existing `self.vertex_mover.update()`, add `self.slough_lrc_cells()`.

D.6 The order of cells in `to_remove` matters if multiple LRC cells
slough in the same tick. Sort by descending basal_y so the
shootward-most cell is removed first; this keeps the
`get_all_neighbors()` lookups simple.

**Acceptance for Phase D:**
- Unit test: an LRC cell whose top vertex is artificially moved to
  y > start-of-EZ is detected by `should_slough()`.
- Functional test: a multi-tick simulation where the top LRC
  cell reaches the threshold has that cell removed; the
  cell-list count decreases; the surviving LRC cell's `a_neighbors`
  list no longer contains the removed cell; no exception is raised
  on the next tick.

### Phase E — Daughter inheritance + parameter consistency

**Tasks:**

E.1 Confirm `CirculateModuleAuxinSynDegExport.get_state()` includes
`auxin_w`. (Inspected — yes, line 70.)

E.2 Daughters created by `Divider.update()` already use
`cell.get_circ_mod().get_state()`; this includes `auxin_w`,
`ks_aux`, `kd_aux`, etc. So LRC daughters automatically inherit
`auxin_w = 10`. Add an explicit test (Phase F.5) so this can't
regress.

E.3 Ensure `Cell.__init__` recomputes `cell_type` correctly for
daughters. When the divider sets `cell_type = "lrc"` *after*
construction (B.4), the constructor's `calculate_cell_type()` will
have already run with x-position-based assignment. For LRC cells
with `x ≈ 23.5`, `|x - 71| = 47.5 µm`, which falls *outside* the
epidermis threshold (45 µm) — `calculate_cell_type()` will raise
`ValueError: Cell type not recognized`. Two acceptable fixes:
- **(preferred)** Add an explicit `lrc` band at `dist_from_root_midpoint
  ≥ 45` (i.e., everything outside epidermis) in
  `calculate_cell_type()`.
- (alternative) Have the divider construct daughters with a
  modified init dict that includes a hint, and skip the constructor
  type calculation when the hint is present.

Recommend the preferred fix because it removes one more place
where "LRC = ID list" is implicit.

**Acceptance for Phase E:**
- LRC daughter has `auxin_w == 10`, `ks_aux == mother.ks_aux`,
  `kd_aux == mother.kd_aux`, `cell_type == "lrc"`,
  `is_lrc() == True`.
- `Cell` construction with `x = 23.5` no longer raises.

### Phase F — Tests

All under `tests/unit/` and `tests/functional/`. Each test must
run with `uv run python3 -m pytest <path> -v` and pass.

F.1 `tests/unit/test_cell_lrc_unittest.py` (new file)
- `test_lrc_cell_has_lrc_type_after_init` — LRC ID seed list yields
  `cell_type == "lrc"`.
- `test_lrc_cell_dev_zone_follows_position` — moving an LRC cell's
  vertices to distance > 234 changes its dev_zone to "transition".
- `test_lrc_cell_growth_rate_meristematic` — `get_growth_rate()`
  returns `MERISTEMATIC_GROWTH_RATE` for an LRC in MZ.
- `test_lrc_cell_growth_rate_transition` — same growth rate
  in "transition" (since LRC has no TZ).
- `test_lrc_cell_growth_rate_elongation` — `ELONGATION_GROWTH_RATE`
  in EZ.
- `test_lrc_cell_imposed_pin_meristem` — returns expected MZ LRC
  weights.
- `test_lrc_cell_imposed_pin_elongation` — returns EZ LRC weights
  with non-zero "m" component.
- `test_lrc_cell_should_slough_when_past_threshold` — returns True
  when basal_y crosses `LRC_SHEDDING_DIST_FROM_TIP`.

F.2 `tests/unit/test_divider_lrc_unittest.py` (new file)
- `test_lrc_mother_in_mz_is_divided` — queue an LRC cell at MZ
  with `height >= division_height`; after `Divider.update()`, the
  mother is removed and two daughters exist with `cell_type ==
  "lrc"`, `is_lrc() == True`, and inherited `auxin_w`.
- `test_non_meristematic_lrc_not_divided` — an LRC cell in EZ is
  not divided.

F.3 Extend `tests/unit/test_neighbor_helpers_unittest.py`:
- `test_lrc_daughter_recognized_as_lrc_neighbor` — after LRC
  mother divides, the inner-file cell that neighbored the mother
  now lists *both* daughters as l-neighbors (vertical neighbors
  along the LRC file) — well, actually one of them. Match exact
  expected behavior: the daughter whose y-range overlaps the
  inner-file cell.
- Replace all current uses of `ROOTCAP_CELL_IDs` in this test
  file with the new `cell.is_lrc()` predicate.

F.4 `tests/unit/test_sim_slough_unittest.py` (new file)
- `test_slough_lrc_cells_removes_cell_at_threshold` — set up two
  cells; advance the LRC one's basal vertex past the threshold;
  call `sim.slough_lrc_cells()`; assert removal.
- `test_slough_lrc_cells_removes_neighbor_refs` — the surviving
  cells must not retain a reference to the removed LRC.
- `test_slough_lrc_cells_clears_vertex_mover_state` — if the
  removed cell had a delta registered, that delta is dropped.

F.5 `tests/functional/test_lrc_vdb_behavior_functional.py` (new file)
- `test_lrc_grows_over_full_simulation` — run a 50-tick simulation
  with `AUX_SYN_DEG_EXP`; assert that the top LRC cell's vertices
  have moved shootward by at least one growth-step delta.
- `test_lrc_reaches_oz_after_growth` — run long enough that an
  LRC cell crosses the meristem-transition threshold (234 µm); show
  that this LRC cell is at the same y-level as the OZ XPP target
  cell (the cell at ~(56.5, 357.5) in original coords) within ±10
  µm during *some* tick of the simulation. Document the tick.
- `test_lrc_is_sloughed_when_past_ez_boundary` — run long enough
  for an LRC cell to be sloughed; assert cell count of LRC cells
  decreases.
- `test_full_run_no_exceptions_50_ticks` — smoke test, no
  exceptions for 50 ticks with the new LRC code path.

F.6 Regression
- `uv run python3 -m pytest tests/ -x -q` must pass overall
  (excluding the pre-existing `test_calculate_arr` failure noted
  in CLAUDE.md §7).

---

## 5. Neighbor-tracking strategy (the hard part)

The current code has three sources of fragility around LRC
neighbors, all rooted in the static ID list assumption:

1. **Detection** of LRC neighbors uses `c_id in ROOTCAP_CELL_IDs`.
2. **Recovery after growth** assumes only previously LRC-adjacent
   cells will ever be LRC-adjacent
   (`fix_lrc_neighbors_after_growth`).
3. **Decision to forget** an LRC neighbor uses a magic string
   return value (`"cell no longer root cap cell neighbor"`).

The cleanest path through these is:

**Step 1 (Phase A.5)** Replace identity-based detection with
`cell.is_lrc()`. This alone makes most of the code correct for
daughters as long as daughters carry the `lrc` cell_type.

**Step 2 (post-Phase B)** Keep `fix_lrc_neighbors_after_growth`
running every tick, but loosen its guard. The current code only
considers non-roottip cells whose `l_neighbors` already contain an
LRC. After Phase A, an "LRC" is no longer in the `"roottip"` cell
type. The replacement:

```python
@staticmethod
def fix_lrc_neighbors_after_growth(sim: "GrowingSim") -> None:
    non_lrc_cells = [c for c in sim.get_cell_list() if not c.is_lrc()]
    for non_lrc_cell in non_lrc_cells:
        existing_lrc_neighbors = [n for n in non_lrc_cell.get_l_neighbors() if n.is_lrc()]
        if existing_lrc_neighbors:
            NeighborHelpers.check_if_neighbors_with_new_root_cap_cell(non_lrc_cell, sim)
            for n in existing_lrc_neighbors:
                NeighborHelpers.check_if_no_longer_neighbors_with_root_cap_cell(non_lrc_cell, n)
```

This still avoids the full O(N²) sweep across all cells by gating
on existing adjacency. The assumption it embeds — *that an LRC
cell which is not currently adjacent to a given inner-file cell
will never become adjacent to it* — is the same assumption as
before, and it remains correct for ARORA's geometry because growth
only moves things along the y-axis: cells slide past each other
shootward, they do not migrate laterally between files.

**Step 3 (Phase D)** When an LRC cell is sloughed, the inner-file
cell that was its l-neighbor should *not* be left thinking it has
that LRC neighbor. `_remove_cell_completely` handles this
explicitly (see D.4).

**Step 4 (Phase D)** After a new LRC daughter is created,
`fix_lrc_neighbors_after_growth` may not catch it on the same tick
because the daughter is brand new and no inner-file cell yet lists
it as a neighbor. The divider's existing call to
`check_if_neighbors_with_new_root_cap_cell` for each daughter
(lines 231–232) handles this — *as long as* this helper uses
`cell.is_lrc()` (Phase A.5) rather than `ROOTCAP_CELL_IDs`. Verify
this in test F.3.

**Edge cases to test:**
- LRC mother in MZ divides → two LRC daughters. Each daughter
  must have correct `l_neighbors` (inner-file cells) and
  `a/b_neighbors` (the other daughter and any remaining LRC cells
  above/below).
- Two LRC cells are vertically adjacent (`a_neighbors` /
  `b_neighbors` of each other). One is sloughed. The other's
  a_neighbors must not contain the removed cell.
- Inner-file cell migrates shootward (via growth) past an LRC
  cell's y-range. `check_if_no_longer_neighbors_with_root_cap_cell`
  must drop the stale adjacency.

---

## 6. File-by-file change manifest

| File | Change |
|---|---|
| `src/agent/cell.py` | Remove `c_id in root_cap_cells` branch in `calculate_dev_zone` (A.4). Add `lrc` band in `calculate_cell_type` (E.3). Add `is_lrc()`, `set_cell_type()`, `should_slough()`. Extend `get_growth_rate` for LRC (B.1). Remove the LRC short-circuit in `get_imposed_pin_distribution` and add `lrc` branches in `_pin_meristematic`, `_pin_transition`, `_pin_elongation`, `_pin_differentiation` (C.1–C.3). Add `LRC_SHEDDING_DIST_FROM_TIP` constant. |
| `src/agent/default_geo_neighbor_helpers.py` | Rename `ROOTCAP_CELL_IDs` → `INITIAL_LRC_CELL_IDs`. Replace all six lookups with `cell.is_lrc()` (A.5). Rewrite `fix_lrc_neighbors_after_growth` per §5 Step 2. |
| `src/sim/input/input.py` | After `create_cells()`, walk over the new cells and set `cell.cell_type = "lrc"` for IDs in `INITIAL_LRC_CELL_IDs`. (A.3) |
| `src/sim/divider/divider.py` | Extend the meristematic filter in `update()` (B.3). Propagate `cell_type = "lrc"` to daughters (B.4). Replace `ROOTCAP_CELL_IDs` check with `is_lrc()` (A.5). |
| `src/sim/simulation/sim.py` | Add `slough_lrc_cells()` and `_remove_cell_completely()` (D.3, D.4). Insert call in tick loop (D.5). |
| `src/sim/mover/vertex_mover.py` | `execute_vertex_movement` still uses `dev_zone == "roottip"` as the "don't propagate, translate rigidly" gate — this is still correct after Phase A since LRC cells leave the `"roottip"` zone. The remaining `"roottip"` cells (QC, columella, curved RC) keep that behavior. |
| `tests/unit/test_cell_lrc_unittest.py` | New (F.1) |
| `tests/unit/test_divider_lrc_unittest.py` | New (F.2) |
| `tests/unit/test_neighbor_helpers_unittest.py` | Extend (F.3) |
| `tests/unit/test_sim_slough_unittest.py` | New (F.4) |
| `tests/functional/test_lrc_vdb_behavior_functional.py` | New (F.5) |

---

## 7. Risks and rollback

| Risk | Likelihood | Mitigation |
|---|---|---|
| Removing `dev_zone = "roottip"` for LRC cells breaks the `execute_vertex_movement` rigid-translation logic for the genuine QC/columella cells | low | Phase A.7 explicitly leaves the 8 curved-region cells in `"roottip"`. Add a test that checks a non-LRC `"roottip"` cell (e.g., QC) is still treated as rigid. |
| Vertex cleanup in `_remove_cell_completely` removes a vertex that is shared with a non-LRC cell | medium | D.4 only removes vertices not used by any remaining cell. Add an assertion. |
| New PIN weights for LRC don't conserve flux | low | PIN weights normalize to 1 by construction. Unit test: assert `sum(weights.values()) == 1.0`. |
| `fix_lrc_neighbors_after_growth` runs every tick and now has more LRC cells to consider as the population grows | low | Same O(N · k) complexity; the work per tick increases by at most a constant factor as long as LRC count stays bounded by the sloughing rule. |
| Sloughing removes a cell that is still queued for division in the same tick | medium | D.4 also removes the cell from `divider.cells_to_divide`. |
| Daughters fail `calculate_cell_type` because `x = 23.5` is outside epidermis threshold | high | Phase E.3 explicitly addresses this. |
| LRC daughters spawned mid-tick are missed by `fix_lrc_neighbors_after_growth` in the same tick | medium | The divider already calls `check_if_neighbors_with_new_root_cap_cell` for each new daughter. Verify in test F.3. |
| Other circulation modules silently break because they assumed LRC = "roottip" | medium | Run the full test suite at the end of each phase. The non-imposed modules use the base-class `get_pin_reg_factor` with hardcoded denominators (CLAUDE.md, ASSUMPTIONS.md §6.15) — that's already broken and not in scope. |

**Rollback strategy:** Each phase is a single git commit. If Phase
D fails functional tests, revert that commit and continue with A–C
in place (LRC cells will then grow indefinitely, but the rest of
the system continues to work).

---

## 8. Validation against VDB

Once phases A–F land, the following behaviors should be observable
in a `AUX_SYN_DEG_EXP` run from the default init:

1. The LRC cell file now extends shootward over time as cells grow.
   By tick ~50 the topmost LRC cell should have crossed
   distance-from-tip 234 µm (out of MZ).
2. By the tick at which the topmost LRC cell reaches 414 µm (TZ–EZ
   boundary), it is sloughed; a new top LRC cell takes its place.
3. At any tick where the LRC file extends past 234 µm,
   inner-file cells at that y-level (epidermis, then cortex, etc.)
   list an LRC cell in their `l_neighbors`.
4. Auxin in the OZ XPP target cell (id 693 in the default init)
   gains a contribution from LRC delivery whenever the LRC file is
   in contact with that y-level.

These four checks together demonstrate that ARORA's LRC behavior
matches VDB's qualitatively. Quantitative comparison against VDB's
Figure 4 panels (specifically panel D — "LRC does not grow or shed
off" — vs. the new ARORA behavior with LRC dynamics enabled) is a
separate dissertation-chapter exercise and is not blocking for
this plan.

---

## 9. Open questions for the user before implementation

1. **Cell type granularity.** VDB distinguishes RC (curved, pink)
   from LRC (flank, orange). ARORA currently has neither. The plan
   adds only `"lrc"` and keeps the curved cells as `"roottip"`.
   Confirm this is sufficient.
2. **PIN weight values.** The values in C.2 are reasonable defaults
   matched to VDB's Fig. 1D but they are *not* GA-optimized. Should
   they be added to `IMPOSED_PIN_ARR_ACTIVITY_PARAM_NAMES` (or the
   `AUX_SYN_DEG_EXP` parameter space) so the GA can tune them?
3. **Sloughing threshold.** VDB's threshold is "start of EZ of
   epidermis" — in ARORA that's 414 µm. Confirm this is the
   intended threshold; alternatives are the end of TZ (same) or
   the start of DZ (1014 µm, which would extend LRC much
   further).
4. **AUX_SYN_DEG_EXP only.** The plan supports only the simplest
   module. If other modules need LRC support later, Phase A and B
   are reusable, but C (PIN distributions) and D (sloughing)
   should be smoke-tested under each.
