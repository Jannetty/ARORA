import unittest

from src.plantem.loc.vertex.vertex import Vertex
from src.plantem.agent.circ_module_cont import BaseCirculateModuleCont
from src.plantem.agent.cell import GrowingCell
from src.plantem.sim.simulation.sim import GrowingSim

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Starting Template"


class BaseCirculateModuleDiscTests(unittest.TestCase):
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
    }

    def test_calculate_auxin(self):
        sim = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, 1, 400, False)
        cell = GrowingCell(
            sim,
            [
                Vertex(100.0, 100.0),
                Vertex(100.0, 300.0),
                Vertex(300.0, 300.0),
                Vertex(300.0, 100.0),
            ],
            self.init_vals,
        )
        circ_module_cont = BaseCirculateModuleCont(cell, self.init_vals)
        area = cell.quad_perimeter.get_area()
        expected_auxin = -119.995
        found_auxin = circ_module_cont.calculate_auxin(2, area)
        self.assertAlmostEqual(expected_auxin, found_auxin, places=5)
