import unittest

import numpy as np
from src.plantem.loc.vertex.vertex import Vertex
from src.plantem.agent.circ_module_cont import BaseCirculateModuleCont
from src.plantem.agent.cell import GrowingCell
from src.plantem.sim.simulation.sim import GrowingSim

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Starting Template"


class BaseCirculateModuleDiscTests(unittest.TestCase):

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
            make_init_vals(),
        )
        circ_module_cont = BaseCirculateModuleCont(cell, make_init_vals())
        area = cell.quad_perimeter.get_area()
        expected_auxin = 0.004999925
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
            make_init_vals(),
        )
        circ_module_cont = BaseCirculateModuleCont(cell, make_init_vals())
        sim.setup()
        area = cell.quad_perimeter.get_area()
        expected_arr = 0.004545342045
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
            make_init_vals(),
        )
        circ_module_cont = BaseCirculateModuleCont(cell, make_init_vals())
        sim.setup()
        area = cell.quad_perimeter.get_area()
        expected_al = 0.003333220833
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
            make_init_vals(),
        )
        circ_module_cont = BaseCirculateModuleCont(cell, make_init_vals())
        sim.setup()
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
            make_init_vals(),
        )
        circ_module_cont = BaseCirculateModuleCont(cell, make_init_vals())
        sim.setup()
        area = cell.quad_perimeter.get_area()
        # test apical neighbor
        expected_pin = 0.2499999813
        found_pin = circ_module_cont.calculate_neighbor_pin(1, 0.5, area)
        self.assertAlmostEqual(expected_pin, found_pin, places=5)

    def test_calculate_memfrac(self):
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
        )
        neighbora = GrowingCell(
            sim,
            [
                Vertex(100.0, 300.0),
                Vertex(100.0, 600.0),
                Vertex(300.0, 600.0),
                Vertex(300.0, 300.0),
            ],
            make_init_vals(),
        )
        circ_module_cont = BaseCirculateModuleCont(cell, make_init_vals())
        sim.setup()
        # test apical neighbor
        expected_f = 0.25
        found_f = circ_module_cont.calculate_memfrac(neighbora, "a")
        self.assertAlmostEqual(expected_f, found_f, places=5)

    def test_get_solution(self):
        pass
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
        )
        circ_module_cont = cell.get_circ_mod()
        sim.setup()
        found_soln = circ_module_cont.get_solution()
        print(f"found solution for pina = {found_soln[1, 4]}")
        expected_soln = np.array([[2, 3, 3, 1, 0.5, 0.7, 0.4, 0.2],
                                 [2+0.004999925, 3+0.004545342045,
                                  3+0.003333220833, 1+8.33333333 * 0.0001,
                                  0.5+0.2499999813, 0.7+0.2499999737,
                                  0.4+0.249999985, 0.2+0.2499999925]])
        for i in range(8):
            self.assertAlmostEqual(expected_soln[1, i], found_soln[1, i], places=5)

    def test_get_neighbor_auxin(self):
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
        )
        circ_module = BaseCirculateModuleCont(cell, make_init_vals())
        # test apical neighbor
        neighbora = GrowingCell(
            sim,
            [
                Vertex(100.0, 300.0),
                Vertex(100.0, 600.0),
                Vertex(300.0, 600.0),
                Vertex(300.0, 300.0),
            ],
            make_init_vals(),
        )
        sim.setup()
        area = cell.quad_perimeter.get_area()
        neighbor_list = [neighbora]
        expected_neighbor_auxin = circ_module.get_neighbor_auxin(
            3, 1, neighbor_list, "a", area
        )
        found_neighbor_auxin = {neighbora: 0.0037499625}
        for neighbor in neighbor_list:
            expected = expected_neighbor_auxin[neighbor]
            found = found_neighbor_auxin[neighbor]
            self.assertAlmostEqual(expected, found, places=5)

    def test_calculate_delta_auxin(self):
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
        )
        circ_module = BaseCirculateModuleCont(cell, make_init_vals())
        neighbora = GrowingCell(
            sim,
            [
                Vertex(100.0, 300.0),
                Vertex(100.0, 600.0),
                Vertex(300.0, 600.0),
                Vertex(300.0, 300.0),
            ],
            make_init_vals(),
        )
        sim.setup()
        neighbors_auxin = [{neighbora: 0.0037499625}]
        expected_delta_auxin = 2 + (0.0037499625)
        found_delta_auxin = circ_module.calculate_delta_auxin(2, neighbors_auxin)
        self.assertAlmostEqual(expected_delta_auxin, found_delta_auxin, places=5)

    def test_update_circ_contents(self):
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
        )
        circ_module = BaseCirculateModuleCont(cell, make_init_vals())
        sim.setup()
        soln = circ_module.get_solution()
        circ_module.update_circ_contents(soln)
        # test arr
        expected_arr = 3 + 0.004545342045
        found_arr = circ_module.arr
        self.assertAlmostEqual(expected_arr, found_arr, places=5)
        # test al
        expected_al = 3 + 0.003333220833
        found_al = circ_module.al
        self.assertAlmostEqual(expected_al, found_al, places=5)
        # test pina
        expected_pina = 0.5+0.2499999813
        found_pina = circ_module.pina
        self.assertAlmostEqual(expected_pina, found_pina, places=5)

    def test_update_neighbor_auxin(self):
        sim = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, 1, 400, False)
        curr_cell = GrowingCell(
            sim,
            [
                Vertex(100.0, 100.0),
                Vertex(100.0, 300.0),
                Vertex(300.0, 300.0),
                Vertex(300.0, 100.0),
            ],
            make_init_vals(),
        )
        circ_module = BaseCirculateModuleCont(curr_cell, make_init_vals())
        neighbora = GrowingCell(
            sim,
            [
                Vertex(100.0, 300.0),
                Vertex(100.0, 600.0),
                Vertex(300.0, 600.0),
                Vertex(300.0, 300.0),
            ],
            make_init_vals(),
        )
        neighborm = GrowingCell(
            sim,
            [
                Vertex(300.0, 100.0),
                Vertex(300.0, 300.0),
                Vertex(600.0, 300.0),
                Vertex(600.0, 100.0),
            ],
            make_init_vals(),
        )
        sim.setup()
        neighbors_auxin = [{neighbora: -47997/800}, {neighborm: -47997/800}]
        sim_circ = curr_cell.get_sim().get_circulator()
        circ_module.update_neighbor_auxin(sim_circ, neighbors_auxin)
        expected = curr_cell.get_sim().get_circulator().delta_auxins
        found = {neighbora: 47997/800, neighborm: 47997/800}
        self.assertEqual(expected, found)

    # def test_update_auxin(self):
    #     sim = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, 1, 400, False)
    #     curr_cell = GrowingCell(
    #         sim,
    #         [
    #             Vertex(100.0, 100.0),
    #             Vertex(100.0, 300.0),
    #             Vertex(300.0, 300.0),
    #             Vertex(300.0, 100.0),
    #         ],
    #         make_init_vals(),
    #     )
    #     circ_module = BaseCirculateModuleCont(curr_cell, make_init_vals())
    #     neighbora = GrowingCell(
    #         sim,
    #         [
    #             Vertex(100.0, 300.0),
    #             Vertex(100.0, 600.0),
    #             Vertex(300.0, 600.0),
    #             Vertex(300.0, 300.0),
    #         ],
    #         make_init_vals(),
    #     )
    #     neighborm = GrowingCell(
    #         sim,
    #         [
    #             Vertex(300.0, 100.0),
    #             Vertex(300.0, 300.0),
    #             Vertex(600.0, 300.0),
    #             Vertex(600.0, 100.0),
    #         ],
    #         make_init_vals(),
    #     )
    #     sim.setup()
    #     neighbors_auxin = [{neighbora: -47997/800}, {neighborm: -47997/800}]
    #     sim_circ = curr_cell.get_sim().get_circulator()
    #     circ_module.update_auxin(sim_circ, neighbors_auxin)
    #     expected = curr_cell.get_sim().get_circulator().delta_auxins
    #     found = {curr_cell: -47997/800, neighbora: 47997/800, neighborm: 47997/800}
    #     self.assertEqual(expected, found)

    def test_update_arr_hist(self):
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
        )
        circ_module_cont = BaseCirculateModuleCont(cell, make_init_vals())
        sim.setup()
        expected_arr_hist = [0.2, 0.3, 3]
        circ_module_cont.update_arr_hist()
        found_arr_hist = circ_module_cont.arr_hist
        self.assertEqual(expected_arr_hist, found_arr_hist)

    def test_get_auxin(self):
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
        )
        circ_module = BaseCirculateModuleCont(cell, make_init_vals())
        sim.setup()
        found = circ_module.get_auxin()
        expected = 2
        self.assertEqual(expected, found)


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
        "arr_hist": [0.1, 0.2, 0.3]
    }
    return init_vals
