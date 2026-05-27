"""Unit and integration tests for CirculateModuleImposedPinNoArr.

Reference:
    docs/plans/design_plans/3_2026-05-27_noARR_model.md  §4 Phase D.1

Four tests:
  - calculate_arr always returns 0.0 for any inputs
  - get_pin_reg_factor always returns 1.0 for any state
  - arr stays exactly 0.0 for all cells throughout a 5-tick GrowingSim run
  - get_state circ_mod key is 'imposed_pin_no_arr'
"""

import os
import platform

if platform.system() == "Linux":
    os.environ["ARCADE_HEADLESS"] = "True"

import unittest
import pandas as pd

from src.arora_enums import CircModEnum, PinLocalizationRulesetEnum
from src.sim.simulation.sim import GrowingSim

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "test_no_arr"

CIRC_MOD = CircModEnum.IMPOSED_PIN_NO_ARR
PIN_LOC_RULES = PinLocalizationRulesetEnum.IMPOSED
CELL_VAL_FILE = "src/sim/input/indep_syndeg_init_vals.json"
V_FILE = "src/sim/input/default_vs.json"

# osc_search_03 best params trimmed to the 4 relevant ones
GPARAM_SERIES = pd.Series(
    {
        "ks_aux": 0.10974987654930562,
        "kd_aux": 0.16372745814388645,
        "k5": 0.023203197888695095,
        "k6": 0.02,
    }
)


def _make_sim() -> GrowingSim:
    return GrowingSim(
        width=SCREEN_WIDTH,
        height=SCREEN_HEIGHT,
        title=SCREEN_TITLE,
        timestep=1.0 / 9.0,
        vis=False,
        circ_mod=CIRC_MOD,
        pin_loc_rules=PIN_LOC_RULES,
        cell_val_file=CELL_VAL_FILE,
        v_file=V_FILE,
        gparam_series=GPARAM_SERIES,
        geometry="default",
    )


class TestCirculateModuleImposedPinNoArr(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.sim = _make_sim()
        # Pick one non-LRC cell for state manipulation tests
        cls.sample_cell = next(
            c for c in cls.sim.cell_list
            if c.get_dev_zone() in ("transition", "elongation")
            and c.get_cell_type() == "peri"
        )
        cls.circ = cls.sample_cell.get_circ_mod()

    def test_calculate_arr_always_zero(self):
        """calculate_arr returns 0.0 regardless of arri or current auxin."""
        for arri in (0.0, 0.5, 5.0, 100.0):
            for auxin_val in (0.0, 10.0, 200.0):
                self.circ.auxin = auxin_val
                result = self.circ.calculate_arr(arri)
                self.assertEqual(
                    result, 0.0,
                    f"calculate_arr({arri}) with auxin={auxin_val} returned {result}, expected 0.0",
                )

    def test_get_pin_reg_factor_always_one(self):
        """get_pin_reg_factor returns 1.0 regardless of arr, auxin, ks_arr, kd_arr."""
        for arr_val in (0.0, 0.1, 5.0, 100.0):
            for auxin_val in (0.0, 10.0, 200.0):
                self.circ.arr = arr_val
                self.circ.auxin = auxin_val
                result = self.circ.get_pin_reg_factor()
                self.assertEqual(
                    result, 1.0,
                    f"get_pin_reg_factor with arr={arr_val}, auxin={auxin_val} "
                    f"returned {result}, expected 1.0",
                )

    def test_get_state_circ_mod_key(self):
        """get_state returns circ_mod == 'imposed_pin_no_arr'."""
        state = self.circ.get_state()
        self.assertEqual(state["circ_mod"], "imposed_pin_no_arr")

    def test_arr_stays_zero_after_5_ticks(self):
        """arr is 0.0 for every cell in the simulation after 5 ticks."""
        sim = _make_sim()
        dt = 1.0 / 9.0
        for _ in range(5):
            sim.on_update(dt)

        non_zero = [
            (c.id, c.get_circ_mod().arr)
            for c in sim.cell_list
            if c.get_circ_mod().arr != 0.0
        ]
        self.assertEqual(
            non_zero, [],
            f"Expected arr==0 for all cells after 5 ticks; "
            f"found non-zero arr in {len(non_zero)} cell(s): {non_zero[:5]}",
        )


if __name__ == "__main__":
    unittest.main()
