import unittest

from src.plantem.loc.vertex.vertex import Vertex
from src.plantem.agent.circ_module_cont import BaseCirculateModuleCont
from src.plantem.agent.cell import GrowingCell
from src.plantem.sim.simulation.sim import GrowingSim

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Starting Template"

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
        "k_arr_arr": 1,
        "k_auxin_auxlax": 1,
        "k_auxin_pin": 1,
        "k_arr_pin": 1,
        "ks": 0.005,
        "kd": 0.0015,
        "arr_hist": [0.1, 0.2, 0.3],
        "growing": True,
        "circ_mod": 'cont'
    }
    return init_vals

delta = 5

class CirculatorTests(unittest.TestCase):
    """
    Test Circulator Class
    """


    def test_add_delta(self):
        sim = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, 1, 400, False)
        cell = GrowingCell(
            sim,
            [
                Vertex(100.0, 100.0),
                Vertex(100.0, 300.0),
                Vertex(300.0, 300.0),
                Vertex(300.0, 100.0),
            ],
            make_init_vals(),
            sim.get_next_cell_id(),
        )
        sim.add_to_cell_list(cell)
        sim.get_circulator().add_delta(cell, delta)
        self.assertEqual(sim.get_circulator().get_delta_auxins()[cell], delta)

    def test_update(self):
        sim = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, 1, 400, False)
        cell = GrowingCell(
            sim,
            [
                Vertex(100.0, 100.0),
                Vertex(100.0, 300.0),
                Vertex(300.0, 300.0),
                Vertex(300.0, 100.0),
            ],
            make_init_vals(),
            sim.get_next_cell_id(),
        )
        sim.add_to_cell_list(cell)
        sim.get_circulator().add_delta(cell, delta)
        sim.get_circulator().update()
        self.assertEqual(cell.get_circ_mod().get_auxin(), delta + make_init_vals()['auxin'])
    