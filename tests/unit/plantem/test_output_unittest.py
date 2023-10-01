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
    "k_arr_arr": 1,
    "k_auxin_auxlax": 1,
    "k_auxin_pin": 1,
    "k_arr_pin": 1,
    "ks": 0.005,
    "kd": 0.0015,
    "growing": True,
    "circ_mod": 'disc'
}
sim = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, 1, 400, False)
cell = GrowingCell(
    sim,
    [Vertex(100.0, 100.0), Vertex(100.0, 300.0), Vertex(300.0, 300.0), Vertex(300.0, 100.0)],
    init_vals,
    sim.get_next_cell_id(),
)
sim.setup()
CELL_LIST = [cell]


class OutputTests(unittest.TestCase):
    def test_get_auxin(self):
        output = Output(sim, "ouput.csv")
        expected = 2
        found = output.get_auxin(cell)
        self.assertEqual(expected, found)

    def test_get_location(self):
        output = Output(sim, "ouput.csv")
        expected = [[300.0, 100.0], [100.0, 100.0], [100.0, 300.0], [300.0, 300.0]]
        found = output.get_location(cell)
        self.assertEqual(expected, found)

    def test_get_circ_contents(self):
        output = Output(sim, "ouput.csv")
        summary = {"cell": cell}
        expected = {
            "cell": cell,
            "ARR": 3,
            "AUX/LAX": 3,
            "PIN_apical": 0.5,
            "PIN_basal": 0.7,
            "PIN_left": 0.4,
            "PIN_right": 0.2,
        }
        found = output.get_circ_contents(summary, cell)
        self.assertEqual(expected, found)

    def test_get_division_number(self):
        pass
