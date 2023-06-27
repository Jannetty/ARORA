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
        "arr_hist": [0.1, 0.2, 0.3]
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
        sim.
        area = cell.quad_perimeter.get_area()
        expected_auxin = -119.995
        found_auxin = circ_module_cont.calculate_auxin(2, area)
        self.assertAlmostEqual(expected_auxin, found_auxin, places=5)

    def test_calculate_arr(self):
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
        expected_arr = -179.9954545
        found_arr = circ_module_cont.calculate_arr(3, area)
        self.assertAlmostEqual(expected_arr, found_arr, places=5)

    def test_calculate_al(self):
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
        expected_al = -179.9966667
        found_al = circ_module_cont.calculate_al(2, 3, area)
        self.assertAlmostEqual(expected_al, found_al, places=5)

    def test_calculate_pin(self):
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
        expected_pin = 8.33333333 * 0.0001
        found_pin = circ_module_cont.calculate_pin(2, 3)
        self.assertAlmostEqual(expected_pin, found_pin, places=5)

    def test_calculate_neighbor_pin(self):
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
        # test apical neighbor
        expected_pin = -119/4
        found_pin = circ_module_cont.calculate_neighbor_pin(1, 0.5, area)
        self.assertAlmostEqual(expected_pin, found_pin, places=5)

    # def test_calculate_memfrac(self):
    #     sim = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, 1, 400, False)
    #     cell = GrowingCell(
    #         sim,
    #         [
    #             Vertex(100.0, 100.0),
    #             Vertex(100.0, 300.0),
    #             Vertex(300.0, 300.0),
    #             Vertex(300.0, 100.0),
    #         ],
    #         self.init_vals,
    #     )
    #     neighbora = GrowingCell(
    #         sim,
    #         [
    #             Vertex(100.0, 300.0),
    #             Vertex(100.0, 600.0),
    #             Vertex(300.0, 600.0),
    #             Vertex(300.0, 300.0),
    #         ],
    #         self.init_vals,
    #     )
    #     circ_module_cont = BaseCirculateModuleCont(cell, self.init_vals)
    #     # test apical neighbor
    #     expected_pin = 0.25
    #     found_pin = circ_module_cont.calculate_memfrac()
    #     self.assertAlmostEqual(expected_pin, found_pin, places=5)
