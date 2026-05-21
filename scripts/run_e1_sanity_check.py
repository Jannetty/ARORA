"""Plan 2 §8 E1 — sanity-check the LRC-geometry extension at runtime.

Runs a short (5-tick) simulation with the extended geometry and the
osc_search_03 best parameters, then verifies the 7 invariants listed
in `docs/plans/design_plans/2_2026-05-20_extend_LRC_geometry.md` §8 E1.

Circulation module: `IMPOSED_PIN_ARR_ACTIVITY` with `IMPOSED` PIN rules.
This deviates from the plan's literal `AUX_SYN_DEG_EXP` specification
but matches CLAUDE.md and what the GA runner (`ARORA_genetic_alg_imposed_auxsyndegexport.py`)
actually executes after the circuit fix described in CLAUDE.md.

Parameters: osc_search_03 best chromosome (8 params).

Run:
    uv run python3 scripts/run_e1_sanity_check.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

# Allow `import src.…` when run as a standalone script.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.sim.simulation.sim import GrowingSim
from src.arora_enums import CircModEnum, PinLocalizationRulesetEnum

# IMPOSED_PIN_ARR_ACTIVITY parameter order (must match
# IMPOSED_PIN_ARR_ACTIVITY_PARAM_NAMES in the GA runner):
#   ks_aux, kd_aux, ks_arr, kd_arr, k1, k5, k6, tau
PARAM_NAMES = ["ks_aux", "kd_aux", "ks_arr", "kd_arr", "k1", "k5", "k6", "tau"]
BEST_PARAMS = pd.Series(
    [
        0.10974987654930562,   # ks_aux
        0.16372745814388645,   # kd_aux
        0.23644894126454083,   # ks_arr
        0.43287612810830595,   # kd_arr
        5.347786360722666,     # k1
        0.023203197888695095,  # k5
        0.02,                  # k6
        8,                     # tau (int)
    ],
    index=PARAM_NAMES,
)

N_TICKS = 5


def build_sim() -> GrowingSim:
    return GrowingSim(
        800, 600, "E1",
        timestep=1/9,   # 1/9 h (≈ 6.6 min) matches the §8 plan and GA
        vis=False,
        pin_loc_rules=PinLocalizationRulesetEnum.IMPOSED,
        circ_mod=CircModEnum.IMPOSED_PIN_ARR_ACTIVITY,
        cell_val_file="src/sim/input/indep_syndeg_init_vals.json",
        v_file="src/sim/input/default_vs.json",
        gparam_series=BEST_PARAMS,
        geometry="default",
        output_file="param_est/e1_sanity_output",
        # max_hours is checked as `tick < max_hours/dt`; using N_TICKS+1
        # ensures the loop will do at least N_TICKS worth of actual work.
        max_hours=(N_TICKS + 1) * (1/9),
        output_frequency=N_TICKS,   # write one snapshot, not 5
    )


def tick_once(sim: GrowingSim) -> None:
    """Drive the simulator forward by one tick.

    ``on_update`` is the arcade game-loop entry point but in headless
    mode (vis=False) it skips the draw call, so it's safe to call
    directly. ``delta_time`` is unused by the body of on_update — it
    pulls timestep from ``self.get_timestep_hours()`` internally."""
    sim.on_update(1/9)


def neighbors_of(cell):
    """Return the IDs of the cell's neighbors regardless of which neighbor
    accessor the codebase exposes here."""
    for accessor in ("get_all_neighbors", "get_neighbors"):
        if hasattr(cell, accessor):
            ns = getattr(cell, accessor)()
            return [n.get_c_id() for n in ns]
    raise RuntimeError("Cell has no neighbor accessor")


def main() -> int:
    print(f"# E1 sanity check — IMPOSED_PIN_ARR_ACTIVITY, {N_TICKS} ticks at dt=1/9 h")
    sim = build_sim()
    by_id = {c.get_c_id(): c for c in sim.cell_list}

    # Pre-tick: capture initial auxin so we can compare at tick N
    initial_auxin_856 = by_id[856].get_circ_mod().get_state()["auxin"]

    for t in range(N_TICKS):
        tick_once(sim)

    print(f"# completed {N_TICKS} ticks; final tick = {sim.get_tick()}")
    print()

    # =====================================================================
    # 7 invariants from plan §8 E1
    # =====================================================================
    results = []

    # 1. len(sim.cell_list) == 858 (γ extent)
    n = len(sim.cell_list)
    results.append(("1. cell count == 858", n == 858, f"got {n}"))

    # Cells we'll inspect
    c838 = by_id.get(838)  # OZ-row LRC, left side (rows 4-counted from 0 in option γ)
    c690 = by_id.get(690)  # matched epidermis at OZ row
    c693 = by_id.get(693)  # OZ XPP target
    c856 = by_id.get(856)  # topmost LRC, left
    c857 = by_id.get(857)  # topmost LRC, right
    c296 = by_id.get(296)  # PIN-flipped
    c311 = by_id.get(311)  # PIN-flipped

    # 2. c838 has c690 in its m-neighbors AND auxin > 0
    n838 = neighbors_of(c838) if c838 else []
    aux838 = c838.get_circ_mod().get_state()["auxin"] if c838 else float("nan")
    ok2 = (690 in n838) and (aux838 > 0)
    results.append(
        ("2. c838 neighbors c690 & auxin > 0", ok2,
         f"690 in c838.neighbors? {690 in n838}; c838.auxin={aux838:.3f}")
    )

    # 3. c690 has c838 in its neighbors
    n690 = neighbors_of(c690) if c690 else []
    ok3 = 838 in n690
    results.append(("3. c690 neighbors c838", ok3, f"c690.neighbors includes 838? {ok3}"))

    # 4. c693 reachable from new LRC via the known reflux path
    #    c693 -> c692 -> c691 -> c690 -> c838.
    #    (Plan §8 E1 step 4 mis-states that c693 has c690 as a direct
    #    l-neighbor; it doesn't — they're 4 file-positions apart.
    #    During Phase D the corresponding test was renamed from
    #    test_oz_xpp_target_two_hops_from_lrc to
    #    test_oz_xpp_target_reachable_from_lrc for the same reason.)
    path_n693 = neighbors_of(c693) if c693 else []
    n692 = neighbors_of(by_id.get(692)) if 692 in by_id else []
    n691 = neighbors_of(by_id.get(691)) if 691 in by_id else []
    n690 = neighbors_of(by_id.get(690)) if 690 in by_id else []
    ok4 = (
        692 in path_n693
        and 691 in n692
        and 690 in n691
        and 838 in n690
    )
    results.append(
        ("4. c693 -> c692 -> c691 -> c690 -> c838 path", ok4,
         f"each hop present? {ok4}")
    )

    # 5. Auxin chain visible — OZ-level LRC has nontrivial auxin
    #    (Skip the full kymograph in this scripted run; just check
    #    that the LRC chain has substantial auxin at the OZ-row level.)
    aux838 = c838.get_circ_mod().get_state()["auxin"] if c838 else 0.0
    aux856 = c856.get_circ_mod().get_state()["auxin"] if c856 else 0.0
    aux690 = c690.get_circ_mod().get_state()["auxin"] if c690 else 0.0
    ok5 = aux838 > 0 and aux856 > 0 and aux690 > 0
    results.append(
        ("5. LRC + OZ-epi auxin all > 0", ok5,
         f"c838.aux={aux838:.3f}, c856.aux={aux856:.3f}, c690.aux={aux690:.3f}")
    )

    # 6. Topmost LRC on each side has pinm == 1.0 (terminal dumper)
    st856 = c856.get_circ_mod().get_state() if c856 else {}
    st857 = c857.get_circ_mod().get_state() if c857 else {}
    ok6 = (st856.get("pinm") == 1.0) and (st857.get("pinm") == 1.0)
    results.append(
        ("6. c856.pinm == c857.pinm == 1.0", ok6,
         f"c856.pinm={st856.get('pinm')}, c857.pinm={st857.get('pinm')}")
    )

    # 7. c296 and c311 are apical-dominant.
    #    NOTE: get_state() returns the *normalized* pin_weights
    #    (Cell.calculate_pin_weights divides by sum). Raw init was
    #    pina=1.0, pinm=0.1 (sum 1.1) -> pina=10/11, pinm=1/11. The
    #    plan §8 E1 step 7 phrases this as "pina == 1.0" but really
    #    means "post-flip apical-dominant"; the right check is the
    #    relative magnitude of pina vs pinm.
    st296 = c296.get_circ_mod().get_state() if c296 else {}
    st311 = c311.get_circ_mod().get_state() if c311 else {}
    ok7 = (
        st296.get("pina", 0) > st296.get("pinm", 0)
        and st311.get("pina", 0) > st311.get("pinm", 0)
        and st296.get("pina", 0) > 0.5
        and st311.get("pina", 0) > 0.5
    )
    results.append(
        ("7. c296 & c311 are apical-dominant", ok7,
         f"c296: pina={st296.get('pina'):.3f} pinm={st296.get('pinm'):.3f}; "
         f"c311: pina={st311.get('pina'):.3f} pinm={st311.get('pinm'):.3f}")
    )

    # =====================================================================
    # Report
    # =====================================================================
    print(f"{'check':<40s} {'pass':>6s}  detail")
    print("-" * 90)
    all_pass = True
    for label, ok, detail in results:
        all_pass = all_pass and ok
        print(f"{label:<40s} {'OK' if ok else 'FAIL':>6s}  {detail}")
    print()

    # Additional informational dump for the log
    print("# auxin snapshot at tick", sim.get_tick())
    for cid in (60, 296, 311, 634, 690, 693, 830, 838, 856, 857):
        c = by_id.get(cid)
        if c is None:
            continue
        st = c.get_circ_mod().get_state()
        print(f"  c{cid:3d}  dev_zone={c.get_dev_zone():<14s} type={c.get_cell_type():<10s} "
              f"auxin={st['auxin']:>10.3f}  arr={st['arr']:>8.3f}  pina={st['pina']:.2f} pinm={st['pinm']:.2f}")

    print()
    print("OVERALL:", "PASS" if all_pass else "FAIL")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
