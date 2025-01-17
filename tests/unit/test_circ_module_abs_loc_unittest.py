import unittest
import pandas as pd
from src.agent.cell import Cell
from src.sim.simulation.sim import GrowingSim
from src.loc.vertex.vertex import Vertex

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Abs Loc Circ Module Test"


class AbsLocCircModTests(unittest.TestCase):
    def testInit_called_correctlyAssignsPinRefs(self):
        sim = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, 1, 40, False)
        cell = Cell(
            sim,
            [
                Vertex(10.0, 10.0),
                Vertex(10.0, 30.0),
                Vertex(30.0, 30.0),
                Vertex(30.0, 10.0),
            ],
            make_init_vals(),
            sim.get_next_cell_id(),
        )
        circ_mod = cell.get_circ_mod()
        pin_refs = circ_mod.pin_refs
        for col in pin_refs.columns:
            if col != "centroid":  # Assuming other columns should be floats/ints
                self.assertTrue(
                    pd.api.types.is_numeric_dtype(pin_refs[col]),
                    f"Expected numeric dtype in column {col} but got {pin_refs[col].dtype}",
                )
        for centroid in pin_refs["centroid"]:
            self.assertIsInstance(
                centroid, tuple, f"Expected tuple in 'centroid' column but got {type(centroid)}"
            )


def make_init_vals():
    init_vals = {
        "auxin": 2,
        "arr": 3,
        "al": 3,
        "pin": 1,
        "pina": 0.5,
        "pinb": 0.7,
        "pinl": 0.4,
        "pinm": 0.2,
        "w_pina": 1,
        "w_pinb": 1,
        "w_pinl": 1,
        "w_pinm": 1,
        "k1": 1,
        "k2": 1,
        "k3": 1,
        "k4": 1,
        "k5": 1,
        "k6": 1,
        "k_s": 0.005,
        "k_d": 0.0015,
        "k_al": 1,
        "k_pin": 1,
        "auxin_w": 1,
        "arr_hist": [0.1, 0.2, 0.3],
        "growing": True,
        "circ_mod": "abs_loc",
    }
    return init_vals
