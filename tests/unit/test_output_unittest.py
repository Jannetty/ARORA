import os
import platform

if platform.system() == "Linux":
    os.environ["ARCADE_HEADLESS"] = "True"
import unittest
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


class TestOutput(unittest.TestCase):

    # def test_get_auxin(self):
    #     output = Output(sim, "ouput.csv")
    #     expected = 2
    #     found = output.get_auxin(cell0)
    #     self.assertEqual(expected, found)

    # def test_get_location(self):
    #     output = Output(sim, "ouput.csv")
    #     expected = [[30.0, 10.0], [10.0, 10.0], [10.0, 30.0], [30.0, 30.0]]
    #     found = output.get_location(cell0)
    #     self.assertEqual(expected, found)

    def test_get_circ_contents(self):

        sim = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, 1, False)
        cell0 = Cell(
            sim,
            [Vertex(10.0, 10.0), Vertex(10.0, 30.0), Vertex(30.0, 30.0), Vertex(30.0, 10.0)],
            init_vals,
            sim.get_next_cell_id(),
        )
        cell1 = Cell(
            sim,
            [Vertex(50.0, 10.0), Vertex(50.0, 30.0), Vertex(30.0, 30.0), Vertex(30.0, 10.0)],
            init_vals2,
            sim.get_next_cell_id(),
        )
        sim.setup()
        CELL_LIST = sim.get_cell_list()

        output = Output(sim, "ouput.csv")
        summary = {"cell": cell0}
        expected = {
            "cell": cell0,
            "ARR": 3,
            "AUX/LAX": 3,
            "PIN_unlocalized": 1,
            "PIN_apical": 0.5,
            "PIN_basal": 0.7,
            "PIN_left": 0.4,
            "PIN_right": 0.2,
            "arr_hist": [0.1, 0.2, 0.3],
            "auxin_w": 1,
        }
        found = output.get_circ_contents(summary, cell0)

        for key in expected:
            print(f"key: {key}")
            print(f"expected: {expected[key]}")
            print(f"found: {found[key]}")
            self.assertEqual(expected[key], found[key])

        self.assertEqual(expected, found)
        # # test cell1
        # summary1 = {"cell": cell1}
        # expected1 = {
        #     "cell": cell1,
        #     "ARR": 3,
        #     "AUX/LAX": 3,
        #     "PIN_unlocalized": 1,
        #     "PIN_apical": 0.5,
        #     "PIN_basal": 0.7,
        #     "PIN_left": 0.4,
        #     "PIN_right": 0.2,
        #     "arr_hist": '[0.1, 0.2, 0.3, 0.4]',
        #     "auxin_w": 1,
        # }
        # found1 = output.get_circ_contents(summary1, cell1)

        # self.assertEqual(expected1, found1)

    def test_get_division_number(self):
        pass

    def test_output_cells(self):
        # output = Output(sim, "ouput.csv")
        # output.output_cells()
        pass
