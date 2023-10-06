import unittest

from src.plantem.sim.output.output import Output
from src.plantem.loc.vertex.vertex import Vertex
from src.plantem.agent.cell import GrowingCell
from src.plantem.sim.simulation.sim import GrowingSim

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Starting Template"
init_vals = {
    "auxin": 2,
    "arr": 3,
    "al": 3,
    "pina": 0.5,
    "pinb": 0.7,
    "pinl": 0.4,
    "pinm": 0.2,
    "k1": 1,
    "k2": 1,
    "k3": 1,
    "k4": 1,
    "k5": 1,
    "k6": 1,
    "ks": 0.005,
    "kd": 0.0015,
    "arr_hist": [0.1, 0.2, 0.3],
    "growing": False,
    "circ_mod": 'cont',
}
init_vals2 = {
    "auxin": 2,
    "arr": 3,
    "al": 3,
    "pina": 0.5,
    "pinb": 0.7,
    "pinl": 0.4,
    "pinm": 0.2,
    "k1": 1,
    "k2": 1,
    "k3": 1,
    "k4": 1,
    "k5": 1,
    "k6": 1,
    "ks": 0.005,
    "kd": 0.0015,
    "arr_hist": [0.1, 0.2, 0.3, 0.4],
    "growing": False,
    "circ_mod": 'cont',
}
sim = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, 1, 400, False)
cell0 = GrowingCell(
    sim,
    [Vertex(100.0, 100.0), Vertex(100.0, 300.0), Vertex(300.0, 300.0), Vertex(300.0, 100.0)],
    init_vals,
    sim.get_next_cell_id(),
)
cell1 = GrowingCell(
    sim,
    [Vertex(100.0, 100.0), Vertex(100.0, 300.0), Vertex(300.0, 300.0), Vertex(300.0, 100.0)],
    init_vals2,
    sim.get_next_cell_id(),
)
sim.setup()
CELL_LIST = [cell0, cell1]


class OutputTests(unittest.TestCase):
    def test_get_auxin(self):
        output = Output(sim, "ouput.csv")
        expected = 2
        found = output.get_auxin(cell0)
        self.assertEqual(expected, found)

    def test_get_location(self):
        output = Output(sim, "ouput.csv")
        expected = [[300.0, 100.0], [100.0, 100.0], [100.0, 300.0], [300.0, 300.0]]
        found = output.get_location(cell0)
        self.assertEqual(expected, found)

    def test_get_circ_contents(self):
        output = Output(sim, "ouput.csv")
        summary = {"cell": cell0}
        expected = {
            "cell": cell0,
            "ARR": 3,
            "AUX/LAX": 3,
            "PIN_apical": 0.5,
            "PIN_basal": 0.7,
            "PIN_left": 0.4,
            "PIN_right": 0.2,
            "arr_hist": [0.1, 0.2, 0.3]
        }
        found = output.get_circ_contents(summary, cell0)
        self.assertEqual(expected, found)
        # test cell1
        summary1 = {"cell": cell1}
        expected1 = {
            "cell": cell1,
            "ARR": 3,
            "AUX/LAX": 3,
            "PIN_apical": 0.5,
            "PIN_basal": 0.7,
            "PIN_left": 0.4,
            "PIN_right": 0.2,
            "arr_hist": [0.1, 0.2, 0.3, 0.4]
        }
        found1 = output.get_circ_contents(summary1, cell1)
        self.assertEqual(expected1, found1)

    def test_get_division_number(self):
        pass

    def test_output_cells(self):
        # output = Output(sim, "ouput.csv")
        # output.output_cells()
        pass
