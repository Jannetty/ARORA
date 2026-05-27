"""Plan 3 §5 E1 — sanity check for CirculateModuleImposedPinNoArr.

Runs a 5-tick GrowingSim with IMPOSED_PIN_NO_ARR and verifies four
invariants that confirm ARR is structurally absent and auxin is
circulating:

  1. 858 cells initialised (extended LRC geometry, option γ)
  2. arr == 0.0 for every cell after 5 ticks
  3. get_pin_reg_factor() == 1.0 for a sample OZ XPP cell (no PIN inhibition)
  4. Auxin non-zero and circulating in key LRC / epidermis / XPP cells

Compare to scripts/run_e1_sanity_check.py (Plan 2, IMPOSED_PIN_ARR_ACTIVITY).

Run:
    uv run python3 scripts/run_e1_noARR.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.sim.simulation.sim import GrowingSim
from src.arora_enums import CircModEnum, PinLocalizationRulesetEnum

PARAM_NAMES = ["ks_aux", "kd_aux", "k5", "k6"]
BEST_PARAMS = pd.Series(
    [
        0.10974987654930562,   # ks_aux  (osc_search_03 best, trimmed)
        0.16372745814388645,   # kd_aux
        0.023203197888695095,  # k5
        0.02,                  # k6
    ],
    index=PARAM_NAMES,
)

N_TICKS = 5


def build_sim() -> GrowingSim:
    return GrowingSim(
        800, 600, "E1_noARR",
        timestep=1.0 / 9.0,
        vis=False,
        pin_loc_rules=PinLocalizationRulesetEnum.IMPOSED,
        circ_mod=CircModEnum.IMPOSED_PIN_NO_ARR,
        cell_val_file="src/sim/input/indep_syndeg_init_vals.json",
        v_file="src/sim/input/default_vs.json",
        gparam_series=BEST_PARAMS,
        geometry="default",
        output_file="param_est/e1_noARR_output",
        max_hours=(N_TICKS + 1) * (1.0 / 9.0),
        output_frequency=N_TICKS,
    )


def main() -> int:
    print(f"# E1_noARR — IMPOSED_PIN_NO_ARR, {N_TICKS} ticks at dt=1/9 h")
    print(f"# params: {dict(BEST_PARAMS)}")
    print()

    sim = build_sim()
    by_id = {c.get_c_id(): c for c in sim.cell_list}

    for _ in range(N_TICKS):
        sim.on_update(1.0 / 9.0)

    print(f"# completed {N_TICKS} ticks; final tick = {sim.get_tick()}")
    print()

    results = []

    # 1. Cell count
    n = len(sim.cell_list)
    results.append(("1. cell count == 858", n == 858, f"got {n}"))

    # 2. arr == 0.0 for every cell
    nonzero_arr = [(c.get_c_id(), c.get_circ_mod().arr) for c in sim.cell_list
                   if c.get_circ_mod().arr != 0.0]
    ok2 = len(nonzero_arr) == 0
    detail2 = "all 0.0" if ok2 else f"{len(nonzero_arr)} cells non-zero: {nonzero_arr[:3]}"
    results.append(("2. arr == 0.0 for all cells", ok2, detail2))

    # 3. get_pin_reg_factor() == 1.0 for a sample OZ XPP cell
    oz_xpp = [c for c in sim.cell_list
               if c.get_dev_zone() in ("transition", "elongation")
               and c.get_cell_type() == "peri"]
    if oz_xpp:
        sample = oz_xpp[0]
        reg = sample.get_circ_mod().get_pin_reg_factor()
        ok3 = reg == 1.0
        results.append(
            ("3. OZ XPP reg factor == 1.0", ok3,
             f"c{sample.get_c_id()} get_pin_reg_factor()={reg}")
        )
    else:
        results.append(("3. OZ XPP reg factor == 1.0", False, "no OZ XPP cells found"))

    # 4. Auxin non-zero in key LRC / epidermis / XPP cells
    key_ids = [838, 856, 690, 693]
    aux_vals = {cid: by_id[cid].get_circ_mod().auxin for cid in key_ids if cid in by_id}
    ok4 = all(v > 0 for v in aux_vals.values())
    aux_str = ", ".join(f"c{cid}={v:.3f}" for cid, v in aux_vals.items())
    results.append(("4. key cell auxin all > 0", ok4, aux_str))

    # 5. circ_mod key in get_state()
    if oz_xpp:
        state_key = oz_xpp[0].get_circ_mod().get_state().get("circ_mod", "MISSING")
        ok5 = state_key == "imposed_pin_no_arr"
        results.append(
            ("5. get_state circ_mod == 'imposed_pin_no_arr'", ok5, f"got '{state_key}'")
        )

    # Report
    print(f"{'check':<44s} {'pass':>4s}  detail")
    print("-" * 90)
    all_pass = True
    for label, ok, detail in results:
        all_pass = all_pass and ok
        print(f"{label:<44s} {'OK' if ok else 'FAIL':>4s}  {detail}")

    # Auxin snapshot for the log
    print()
    print(f"# auxin snapshot at tick {sim.get_tick()}")
    for cid in (838, 856, 690, 693):
        c = by_id.get(cid)
        if c is None:
            continue
        st = c.get_circ_mod().get_state()
        print(f"  c{cid:3d}  dev_zone={c.get_dev_zone():<14s} type={c.get_cell_type():<10s} "
              f"auxin={st['auxin']:>10.3f}  arr={st['arr']:>6.3f}")

    print()
    print("OVERALL:", "PASS" if all_pass else "FAIL")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
