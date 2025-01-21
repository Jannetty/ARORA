import os
import platform
import unittest
import json
from src.sim.output.output import Output
from src.loc.vertex.vertex import Vertex
from src.agent.cell import Cell
from src.sim.simulation.sim import GrowingSim


# CELL_LIST = sim.get_cell_list()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Starting Template"

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
    "growing": False,
    "circ_mod": "cont",
}

init_vals2 = {
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
    "arr_hist": [0.1, 0.2, 0.3, 0.4],
    "growing": False,
    "circ_mod": "cont",
}

init_vals3 = {
    "auxin": 0.1,
    "arr": 0.2,
    "al": 0.3,
    "pin": 0.4,
    "pina": 0.5,
    "pinb": 0.6,
    "pinl": 0.7,
    "pinm": 0.8,
    "growing": True,
    "k1": 1.1,
    "k2": 1.2,
    "k3": 1.3,
    "k4": 1.4,
    "k5": 1.5,
    "k6": 1.6,
    "ks_aux": 2.1,
    "kd_aux": 2.2,
    "ks_arr": 2.3,
    "kd_arr": 2.4,
    "ks_pinu": 2.5,
    "kd_pinu": 2.6,
    "kd_pinloc": 2.7,
    "ks_auxlax": 2.8,
    "kd_auxlax": 2.9,
    "auxin_w": 3.0,
    "arr_hist": [0.1, 0.2, 0.3],
    "circ_mod": "indep_syn_deg",
}
sim = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, 1, 40, False)
cell0 = Cell(
    sim,
    [Vertex(10.0, 10.0), Vertex(10.0, 30.0), Vertex(30.0, 30.0), Vertex(30.0, 10.0)],
    init_vals,
    sim.get_next_cell_id(),
)
cell1 = Cell(
    sim,
    [Vertex(10.0, 10.0), Vertex(10.0, 30.0), Vertex(30.0, 30.0), Vertex(30.0, 10.0)],
    init_vals2,
    sim.get_next_cell_id(),
)


class TestOutput(unittest.TestCase):

    def setUp(self):
        """Set up common test variables."""
        self.output_csv = "output.csv"
        self.output_json = "output.json"
        CELL_LIST = [cell0, cell1]
        self.output = Output(sim, self.output_csv, self.output_json)
        sim.setup()
        sim.add_to_cell_list(cell0)
        sim.add_to_cell_list(cell1)

    def tearDown(self):
        """Clean up test files."""
        if os.path.isfile(self.output_csv):
            os.remove(self.output_csv)
        if os.path.isfile(self.output_json):
            os.remove(self.output_json)

    def test_get_circ_contents(self):
        summary = {"cell": cell0}
        expected = cell0.get_circ_mod().get_state()
        found = self.output.get_circ_contents(summary, cell0)
        self.assertEqual(expected, found)

        # test cell1
        summary1 = {"cell": cell1}
        expected1 = cell1.get_circ_mod().get_state()
        found1 = self.output.get_circ_contents(summary1, cell1)
        self.assertEqual(expected1, found1)

        # test cell2 (with circ_mod: indep_syn_deg)
        cell2 = Cell(
            sim,
            [Vertex(10.0, 10.0), Vertex(10.0, 30.0), Vertex(30.0, 30.0), Vertex(30.0, 10.0)],
            init_vals3,
            sim.get_next_cell_id(),
        )
        summary2 = {"cell": cell2}
        expected2 = cell2.get_circ_mod().get_state()
        found2 = self.output.get_circ_contents(summary2, cell2)

    def test_output_cells(self):
        self.output.output_cells()
        # Check if files are created and not empty
        self.assertTrue(os.path.isfile(self.output_csv))
        self.assertTrue(os.path.isfile(self.output_json))
        self.assertGreater(os.path.getsize(self.output_csv), 0)
        self.assertGreater(os.path.getsize(self.output_json), 0)

    def test_get_division_number(self):
        pass
