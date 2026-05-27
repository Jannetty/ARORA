# Design Plan 3 — ARR-free (VDB-aligned) Model and LRC Geometry Re-evaluation

**Date:** 2026-05-27
**Author:** drafted by Claude under direction of skjannetty
**Scope:** new circulation module, GA runner extension, evaluation scripts
**Status:** draft, ready for implementation
**Branch:** `lrc-geometry-extension` (extends the existing branch)
**Predecessor plan:** `2_2026-05-20_extend_LRC_geometry.md` (Plan 2 confirmed
the LRC geometry extension does not produce oscillation under the
ARR-coupled `IMPOSED_PIN_ARR_ACTIVITY` model; this plan re-runs the
same diagnostic under a model without ARR)

---

## 0. Authorship and git policy

Claude's contributions are documented here and in the implementation log.
**No git commits, tags, branch names, PR descriptions, or commit-message
trailers should include AI co-author attribution** (no `Co-Authored-By:
Claude`, no `🤖 Generated with Claude Code`, no "with assistance from"
footer, etc.). Commits must reflect Sophia's authorship only.

---

## 1. Goal

Plan 2 evaluated whether extending the LRC geometry to reach the OZ was
sufficient to produce oscillations in ARORA. It used
`CircModEnum.IMPOSED_PIN_ARR_ACTIVITY`, a module in which ARR responds to
auxin and feeds back on PIN transport (a Goodwin-type delayed oscillator).
The result was a null: 0/10 chromosomes showed temporal oscillation.

However, the VDB 2021 paper's model has **no ARR-PIN feedback loop at
all**. Oscillations in VDB arise purely from:

1. The auxin reflux loop (PIN-mediated polar transport + AUX/LAX import).
2. Growth-driven cell-size alternations in the transition zone (large cells
   from meristematic clones arrive in the TZ followed by smaller cells,
   periodically varying the surface-to-volume ratio and hence auxin loading).

To structurally align ARORA with VDB and make the Plan 2 diagnostic
meaningful as a comparison, we need to re-run it with ARR **clamped to
zero**: `dARR/dt ≡ 0`, PIN regulation factor ≡ 1.0 (no transport
inhibition by ARR).

The diagnostic question is the same as Plan 2:

> With the Plan 2 LRC geometry extension in place, does the pure
> reflux-and-growth mechanism (no ARR feedback) produce temporal
> oscillations in OZ XPP cells?

Out of scope:
- Changes to the LRC geometry (already done in Plan 2).
- Any modification to PIN spatial patterns, cell growth, division, or
  zone-transition logic.
- Other circulation modules (`UNIVERSAL_SYN_DEG`, etc.).
- Any production-code change other than the new module, enum entry,
  and factory wiring.

---

## 2. Current state inventory

### 2.1 Existing circulation module

`src/agent/circ_module_imposed_pin_arr_activity.py` — class
`CirculateModuleImposedPinArrActivity`. Key methods relevant to this plan:

| Method | Current behavior |
|--------|-----------------|
| `calculate_arr(arri)` | ARR synthesis driven by auxin (Hill function) with delayed self-repression; degrades at rate `kd_arr` |
| `get_pin_reg_factor()` | Returns `k_half / (ARR + k_half)` ∈ [0,1]; k_half ≈ ARR steady-state; reg=1 when ARR=0 |
| `calculate_auxin(auxini)` | `ks_aux * auxin_w - kd_aux * auxin` (unchanged) |

### 2.2 Enum and factory

- `src/arora_enums.py`: `CircModEnum.IMPOSED_PIN_ARR_ACTIVITY = 5`
- Factory: `src/agent/cell.py` lines ~169–180, match statement:
  `case CircModEnum.IMPOSED_PIN_ARR_ACTIVITY:
      self.circ_mod = CirculateModuleImposedPinArrActivity(self, init_vals)`

### 2.3 GA runner

`param_est/ARORA_genetic_alg_imposed_auxsyndegexport.py`:

- `IMPOSED_PIN_ARR_ACTIVITY_PARAM_NAMES = ["ks_aux","kd_aux","ks_arr","kd_arr","k1","k5","k6","tau"]` (8 params)
- `make_paramspace_imposed_pin_arr_activity()` — 8-dimensional gene space
- `_run_ARORA()` — instantiates `GrowingSim` with `circ_mod=CircModEnum.IMPOSED_PIN_ARR_ACTIVITY`
- `fitness_mode`: `"oscillation"` or `"vdb_ssd"`

### 2.4 Init file

`src/sim/input/indep_syndeg_init_vals.json` — 858 cells (Plan 2 extended
from 830). Contains all ARR-related fields per cell: `arr`, `arr_hist`,
`ks_arr`, `kd_arr`, `k1`, `k3`, `k4`. These will be read by the new
module's `__init__` (inherited) but never mutated dynamically because
`calculate_arr` will always return 0.0.

### 2.5 Existing evaluation outputs (Plan 2, ARR-coupled)

For reference when interpreting Plan 3 results:

| File | Contents |
|------|----------|
| `evaluation/intervention_c693_auxin.png` | E3: auxin at c693 over 26 h, monotonic decay |
| `evaluation/intervention_run.csv` | E3 per-tick aggregate |
| `evaluation/intervention_summary.txt` | E3 oscillation_score = 0.184, legacy FFT = 85.5 |
| `evaluation/e4_sensitivity.csv` | E4: 10 chromosomes, 0/10 oscillation_score ≥ 0.3 |
| `evaluation/e4_scatter.png` | E4 scatter plot |

---

## 3. Design

### 3.1 New circulation module

**File:** `src/agent/circ_module_imposed_pin_no_arr.py`

**Class:** `CirculateModuleImposedPinNoArr`
inherits from `CirculateModuleImposedPinArrActivity`

Override exactly two methods:

```python
def calculate_arr(self, arri: float) -> float:
    # ARR is structurally absent (VDB-aligned model).
    # dARR/dt ≡ 0; since arr initialises to 0, arr stays 0 for all time.
    return 0.0

def get_pin_reg_factor(self) -> float:
    # ARR = 0 always → no PIN inhibition → unrestricted transport.
    return 1.0
```

Override `get_state()` to return `circ_mod: "imposed_pin_no_arr"` so CSV
output is identifiable.

**Invariants:**
- `arr` stays at its initial value (0.0) for the entire simulation.
- `get_pin_reg_factor()` always returns exactly 1.0, never computed from
  ARR or auxin.
- `ks_arr`, `kd_arr`, `k1`, `tau`, `arr_hist` are loaded from the init
  file (required by inherited `__init__`) but play no role in dynamics.

### 3.2 Enum and factory

Add to `src/arora_enums.py`:
```python
IMPOSED_PIN_NO_ARR = 6
```

Add to the match block in `src/agent/cell.py` (after case 5):
```python
from src.agent.circ_module_imposed_pin_no_arr import CirculateModuleImposedPinNoArr
...
case CircModEnum.IMPOSED_PIN_NO_ARR:
    self.circ_mod = CirculateModuleImposedPinNoArr(self, init_vals)
```

### 3.3 GA runner changes

**New constant:**
```python
IMPOSED_PIN_NO_ARR_PARAM_NAMES = ["ks_aux", "kd_aux", "k5", "k6"]
```

**New method `make_paramspace_imposed_pin_no_arr()`:**
```python
def make_paramspace_imposed_pin_no_arr(self):
    ks_aux_range = np.geomspace(0.1, 10.0, 100).astype(float)
    kd_aux_range = np.geomspace(0.05, 0.5, 100).astype(float)
    k5_range     = np.geomspace(0.02, 1.0, 80).astype(float)
    k_pin_range  = np.geomspace(0.02, 1.0, 80).astype(float)
    return [ks_aux_range, kd_aux_range, k5_range, k_pin_range]
```

Ranges identical to the ARR-coupled module for the shared parameters
(`ks_aux`, `kd_aux`, `k5`, `k6`), so GA searches are directly comparable.

**Changes to `_run_ARORA()`:** when `fitness_mode == "oscillation_no_arr"`,
use `circ_mod=CircModEnum.IMPOSED_PIN_NO_ARR`. Everything else (init file,
v_file, timestep, max_hours, output) stays the same.

**Changes to `run_genetic_alg()`:** when `fitness_mode == "oscillation_no_arr"`:
- Use `make_paramspace_imposed_pin_no_arr()` for gene space.
- Set `self.param_names = IMPOSED_PIN_NO_ARR_PARAM_NAMES`.
- Use same GA hyperparameters as `"oscillation"` mode (20 gen, 30 sol,
  20 % mutation, tournament, elitism=3).

**Changes to `__init__`:** set `self.param_names` based on `fitness_mode`
(4 params when mode is `oscillation_no_arr`, 8 otherwise). Also update
the CSV header write to use `self.param_names`.

**`--mode` flag:** extend the `if __name__ == "__main__"` argparse block
to accept `oscillation_no_arr` as a valid `--mode` value.

### 3.4 Evaluation scripts

**`scripts/run_e3_noARR.py`** — mirrors `scripts/run_e3_intervention.py`:
- Uses `CircModEnum.IMPOSED_PIN_NO_ARR`
- Uses osc_search_03 best chromosome trimmed to 4 params:
  `ks_aux=0.10975, kd_aux=0.16373, k5=0.023203, k6=0.02`
- 26 h run (234 ticks), same output paths as E3 but under
  `evaluation/noARR_intervention_*.{csv,png,txt}`

**`scripts/run_e4_noARR.py`** — mirrors `scripts/run_e4_sensitivity.py`:
- 10 chromosomes: #1 = E3 best (as above); #2 = geometric midpoints of
  4-param ranges; #3–10 = log-uniform random samples (seed `20260527`)
- `evaluation/noARR_e4_sensitivity.csv`, `evaluation/noARR_e4_scatter.png`,
  `evaluation/noARR_e4_chrom_<i>_auxin.png`

---

## 4. Implementation phases

### Phase A — New circulation module (≈ 30 min)

**A.1** Create `src/agent/circ_module_imposed_pin_no_arr.py`
with `CirculateModuleImposedPinNoArr` as described in §3.1.

**A.2** Add `IMPOSED_PIN_NO_ARR = 6` to `src/arora_enums.py`.

**A.3** Wire the factory in `src/agent/cell.py`:
add import + match case for `IMPOSED_PIN_NO_ARR`.

**A.4** Smoke test (not committed — just run interactively or via quick script):
instantiate a `GrowingSim` with `IMPOSED_PIN_NO_ARR` for 5 ticks; assert
`all(cell.get_circ_mod().arr == 0 for cell in sim.cell_list)` at tick 5
and `cell.get_circ_mod().get_pin_reg_factor() == 1.0` for a sample cell.

**A.5** Commit Phase A (3 files).

### Phase B — GA runner extension (≈ 45 min)

**B.1** Add `IMPOSED_PIN_NO_ARR_PARAM_NAMES` constant to GA runner.

**B.2** Add `make_paramspace_imposed_pin_no_arr()` method.

**B.3** Update `_run_ARORA()` to branch on `fitness_mode == "oscillation_no_arr"`.

**B.4** Update `run_genetic_alg()` to use the 4-param space and correct
`circ_mod` when mode is `oscillation_no_arr`.

**B.5** Update `__init__` to set `self.param_names` based on mode; update
CSV header write accordingly.

**B.6** Extend `__main__` argparse to accept `"oscillation_no_arr"` as mode.

**B.7** Commit Phase B (1 file).

### Phase C — Evaluation scripts (≈ 30 min)

**C.1** Write `scripts/run_e3_noARR.py`.

**C.2** Write `scripts/run_e4_noARR.py`.

**C.3** Commit Phase C (2 files).

### Phase D — Tests (≈ 45 min)

**D.1** Add unit tests for `CirculateModuleImposedPinNoArr`:

- `test_calculate_arr_always_zero`: call `calculate_arr` with various
  `arri` values and various `self.auxin` levels; assert return is 0.0.
- `test_get_pin_reg_factor_always_one`: assert `get_pin_reg_factor()` == 1.0
  regardless of `arr`, `auxin`, `ks_arr`, `kd_arr`.
- `test_arr_stays_zero_after_5_ticks`: 5-tick `GrowingSim` integration
  test; assert `arr == 0` for all cells at all ticks.
- `test_get_state_circ_mod_key`: assert `get_state()["circ_mod"]` ==
  `"imposed_pin_no_arr"`.

Suggested file: `tests/unit/test_circ_module_no_arr_unittest.py`

**D.2** Run regression suite:
```sh
uv run python3 -m pytest tests/ -q \
    --deselect tests/unit/test_circ_module_cont_unittest.py::test_calculate_arr
```
Expected: all pass (same pre-existing failure as documented in CLAUDE.md §7).

**D.3** Commit Phase D (1 new test file).

### Phase E — Evaluation (≈ 1–2 h compute, then optional GA)

**E1 — Quick sanity (5 ticks, ~5 min):**
Confirm the new module instantiates and runs without errors; confirm `arr`
stays 0 and auxin circulates normally. Can be the A.4 smoke test run more
formally.

**E2 — E3_noARR (26 h run, ~30 min):**
```sh
uv run python3 scripts/run_e3_noARR.py
```
Record `oscillation_score_from_csv` and visual inspection of
`evaluation/noARR_intervention_c693_auxin.png`.

Pass criterion: `oscillation_score ≥ 0.3` AND ≥ 2 visible peaks in the
second half of the time-course.

**E3 — E4_noARR sensitivity sweep (10 × 26 h, ~5 h):**
```sh
uv run python3 scripts/run_e4_noARR.py
```
Report: fraction of chromosomes with `oscillation_score ≥ 0.3`.

Pass criterion: ≥ 5/10 chromosomes pass the oscillation threshold.

**E4 — Full GA run (optional, if E2/E3 are inconclusive or promising):**
```sh
uv run python3 -m param_est.ARORA_genetic_alg_imposed_auxsyndegexport \
    --mode oscillation_no_arr --run-name noarr_osc_search_01
```
20 gens × 30 solutions; report best fitness trajectory.

---

## 5. Pass/fail logic and interpretation

| E2 | E3 | Interpretation | Recommended next step |
|----|----|-|-|
| Pass | ≥ 5/10 | Pure reflux-and-growth + extended LRC IS sufficient | Document; run GA to confirm best params |
| Pass | < 5/10 | Weakly oscillatory; parameter-sensitive | Run GA (E4) to find reliable regime |
| Fail | any | Pure reflux-and-growth + extended LRC NOT sufficient even without ARR drag | Revisit growth dynamics (cell-size alternation model, zone-dependent auxin_w) |

Compare to Plan 2 null result: if Plan 3 also fails, the missing mechanism
is not ARR per se but the cell-size alternation mechanism (Mechanism 1 in
CLAUDE.md §1) that ARORA does not yet model explicitly.

---

## 6. Files changed (complete list)

| File | Change |
|------|--------|
| `src/agent/circ_module_imposed_pin_no_arr.py` | **New.** `CirculateModuleImposedPinNoArr` class |
| `src/arora_enums.py` | Add `IMPOSED_PIN_NO_ARR = 6` |
| `src/agent/cell.py` | Add import + match case for new enum |
| `param_est/ARORA_genetic_alg_imposed_auxsyndegexport.py` | New param names, paramspace method, mode wiring |
| `scripts/run_e3_noARR.py` | **New.** 26-h single-run evaluation script |
| `scripts/run_e4_noARR.py` | **New.** 10-chromosome sensitivity sweep |
| `tests/unit/test_circ_module_no_arr_unittest.py` | **New.** Unit + integration tests |
