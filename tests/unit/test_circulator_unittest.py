import os
import platform

if platform.system() == "Linux":
    os.environ["ARCADE_HEADLESS"] = "True"
import unittest
from src.loc.vertex.vertex import Vertex
from src.agent.circ_module_cont import BaseCirculateModuleCont
from src.agent.cell import Cell
from src.sim.simulation.sim import GrowingSim

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
        "k1": 1,
        "k2": 1,
        "k3": 1,
        "k4": 1,
        "k5": 1,
        "k6": 1,
        "k_s": 0.005,
        "k_d": 0.0015,
        "auxin_w": 1,
        "arr_hist": [0.1, 0.2, 0.3],
        "growing": False,
        "circ_mod": "cont",
    }
    return init_vals


delta = 5


class TestCirculator(unittest.TestCase):
    """
    Test Circulator Class
    """

    def test_add_delta(self):
        sim = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, 1, False)
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
        sim.get_circulator().add_delta(cell, delta)
        self.assertEqual(sim.get_circulator().get_delta_auxins()[cell], delta)

    def test_update(self):
        sim = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, 1, False)
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
        sim.get_circulator().add_delta(cell, delta)
        sim.get_circulator().update()
        self.assertEqual(cell.get_circ_mod().get_auxin(), delta + make_init_vals()["auxin"])
