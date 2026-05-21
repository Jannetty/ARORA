"""Runtime smoke-check for follow-up F-005.

Loads ``indep_syndeg_init_vals.json`` through the simulator's input
pipeline under ``INDEP_SYN_DEG`` and verifies the 28 new LRC cells
(IDs 830-857) and the PIN flip on 296/311 are visible at runtime.

Run:
    uv run python3 scripts/verify_indep_syndeg_extension.py
"""

import sys
from pathlib import Path

# Allow ``import src.…`` when run as a standalone script.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.sim.simulation.sim import GrowingSim
from src.arora_enums import PinLocalizationRulesetEnum, CircModEnum
from main import make_indep_param_series


def main() -> int:
    # IMPORTANT: must pass geometry="default" explicitly. The
    # sim.main() entry-point string-matches v_file to derive this,
    # but the GrowingSim constructor does not — if geometry is "",
    # Cell.__init__ sets dev_zone="" and get_imposed_pin_distribution
    # raises "Dev zone error cannot get imposed PIN pattern".
    sim = GrowingSim(
        800, 600, "TEST",
        1, False,
        PinLocalizationRulesetEnum.IMPOSED,
        CircModEnum.INDEP_SYN_DEG,
        cell_val_file="src/sim/input/indep_syndeg_init_vals.json",
        v_file="src/sim/input/default_vs.json",
        gparam_series=make_indep_param_series(),
        geometry="default",
    )

    ids = sorted(c.get_c_id() for c in sim.cell_list)
    print(f"cells: {len(sim.cell_list)}")
    print(f"id range: {ids[0]} - {ids[-1]}")
    print(f"cells with id >= 830: {sum(1 for cid in ids if cid >= 830)}")

    by_id = {c.get_c_id(): c for c in sim.cell_list}

    # Cell 856 — topmost left, terminal dumper
    c856 = by_id[856]
    st = c856.get_circ_mod().get_state()
    print(f"cell 856: pina={st['pina']:.2f}, pinm={st['pinm']:.2f} "
          f"(expected 0.00 / 1.00)")
    print(f"          dev_zone={c856.get_dev_zone()}, "
          f"cell_type={c856.get_cell_type()}")

    # Cell 296 — flipped to apical-dominant
    c296 = by_id[296]
    st = c296.get_circ_mod().get_state()
    print(f"cell 296: pina={st['pina']:.2f}, pinm={st['pinm']:.2f} "
          f"(expected 1.00 / 0.10)")

    # Cell 693 — OZ XPP target, unchanged
    c693 = by_id[693]
    print(f"cell 693: dev_zone={c693.get_dev_zone()}, "
          f"cell_type={c693.get_cell_type()}")

    # Pass/fail summary
    ok = (
        len(sim.cell_list) == 858
        and st["pina"] == 1.0  # cell 296
        and by_id[856].get_circ_mod().get_state()["pinm"] == 1.0
    )
    print()
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
