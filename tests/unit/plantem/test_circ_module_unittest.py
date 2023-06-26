import unittest

from src.plantem.loc.vertex.vertex import Vertex
from src.plantem.agent.circ_module_disc import BaseCirculateModuleDisc
from src.plantem.agent.cell import GrowingCell
from src.plantem.sim.simulation.sim import GrowingSim

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Starting Template"


class BaseCirculateModuleTests(unittest.TestCase):
    # def test_update(self):
    #     cell1 = GrowingCell(self, [Vertex(100.0,100.0), Vertex(100.0,300.0), Vertex(300.0,300.0), Vertex(300.0,100.0)], {})

    #     test_dict = {cell1: 1}

    #     for cell in test_dict:
    #         with self.subTest(cell=cell):
    #             circ_module = BaseCirculateModule(cell,{})
    #             found_delta = circ_module.update()[cell]
    #             expected_delta = test_dict[cell]

    #             self.assertEqual(found_delta, expected_delta)

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
    }

    def test_determine_left_right(self):
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
        circ_module = BaseCirculateModuleDisc(cell, self.init_vals)
        sim.setup()
        found_left, found_right = circ_module.determine_left_right()
        expected_left = "lateral"
        expected_right = "medial"
        self.assertEqual(expected_left, found_left)
        self.assertEqual(expected_right, found_right)

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
        circ_module = BaseCirculateModuleDisc(cell, self.init_vals)
        sim.setup()
        timestep = 1
        area = 100
        expected_auxin = -0.295
        found_auxin = circ_module.calculate_auxin(timestep, area)
        self.assertEqual(expected_auxin, found_auxin)

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
        circ_module = BaseCirculateModuleDisc(cell, self.init_vals)
        sim.setup()
        timestep = 1
        area = 100
        expected_arr = -359 / 800
        found_arr = circ_module.calculate_arr(timestep, area)
        self.assertAlmostEqual(expected_arr, found_arr, places=5)

    def test_calculate_aux_lax(self):
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
        circ_module = BaseCirculateModuleDisc(cell, self.init_vals)
        sim.setup()
        timestep = 1
        area = 100
        expected_aux_lax = -0.45209
        found_aux_lax = circ_module.calculate_aux_lax(timestep, area)
        self.assertAlmostEqual(expected_aux_lax, found_aux_lax, places=5)

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
        circ_module = BaseCirculateModuleDisc(cell, self.init_vals)
        sim.setup()
        timestep = 1
        area = 100
        expected_PIN = -0.0037954
        found_PIN = circ_module.calculate_pin(timestep, area)
        self.assertAlmostEqual(expected_PIN, found_PIN, places=5)

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
        circ_module = BaseCirculateModuleDisc(cell, self.init_vals)
        sim.setup()
        timestep = 1
        area = 100
        expected_neighbor_PIN = -0.075949
        found_neighbor_PIN = circ_module.calculate_neighbor_pin(0.5, timestep, area)
        self.assertAlmostEqual(expected_neighbor_PIN, found_neighbor_PIN, places=5)

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
            self.init_vals,
        )
        circ_module = BaseCirculateModuleDisc(cell, self.init_vals)
        # test apical nerighbor
        neighbora = GrowingCell(
            sim,
            [
                Vertex(100.0, 300.0),
                Vertex(100.0, 600.0),
                Vertex(300.0, 600.0),
                Vertex(300.0, 300.0),
            ],
            self.init_vals,
        )
        sim.setup()
        found_memfrac = circ_module.calculate_memfrac(neighbora, "a")
        expected_memfrac = 0.25
        self.assertEqual(expected_memfrac, found_memfrac)

    def test_get_neighbor_auxin(self):
        timestep = 1
        area = 100
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
        circ_module = BaseCirculateModuleDisc(cell, self.init_vals)
        # test apical neighbor
        neighbora = GrowingCell(
            sim,
            [
                Vertex(100.0, 300.0),
                Vertex(100.0, 600.0),
                Vertex(300.0, 600.0),
                Vertex(300.0, 300.0),
            ],
            self.init_vals,
        )
        sim.setup()
        neighbor_list = [neighbora]
        expected_neighbor_auxin = circ_module.get_neighbor_auxin(
            0.5, neighbor_list, "a", timestep, area
        )
        found_neighbor_auxin = {neighbora: 866179 / 80000000}
        for neighbor in neighbor_list:
            expected = expected_neighbor_auxin[neighbor]
            found = found_neighbor_auxin[neighbor]
            self.assertAlmostEqual(expected, found, places=5)

    def test_calcualte_delta_auxin(self):
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
        circ_module = BaseCirculateModuleDisc(cell, self.init_vals)
        neighbora = GrowingCell(
            sim,
            [
                Vertex(100.0, 300.0),
                Vertex(100.0, 600.0),
                Vertex(300.0, 600.0),
                Vertex(300.0, 300.0),
            ],
            self.init_vals,
        )
        sim.setup()
        neighbors_auxin = [{neighbora: 866179 / 80000000}]
        expected_delta_auxin = 2 + 866179 / 80000000
        found_delta_auxin = circ_module.calculate_delta_auxin(neighbors_auxin)
        self.assertAlmostEqual(expected_delta_auxin, found_delta_auxin, places=5)

    def test_update_current_cell(self):
        sim = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, 1, 400, False)
        curr_cell = GrowingCell(
            sim,
            [
                Vertex(100.0, 100.0),
                Vertex(100.0, 300.0),
                Vertex(300.0, 300.0),
                Vertex(300.0, 100.0),
            ],
            self.init_vals,
        )
        circ_module = BaseCirculateModuleDisc(curr_cell, self.init_vals)
        sim.setup()

        cell_dict = {}
        delta_aux = 0.5

        expected_dict = {curr_cell: 0.5}
        found_dict = circ_module.update_current_cell(curr_cell, cell_dict, delta_aux)
        self.assertEqual(expected_dict, found_dict)

    def test_update_neighbor_cell(self):
        # circ_module = BaseCirculateModule(GrowingCell, self.init_vals)

        # curr_cell = GrowingCell
        # sim = None

        # cellA = GrowingCell(sim, [Vertex(100.0,100.0), Vertex(100.0,300.0), Vertex(300.0,300.0), Vertex(300.0,100.0)], self.init_vals)
        # cellB = GrowingCell(sim, [Vertex(101.0,101.0), Vertex(101.0,300.0), Vertex(300.0,300.0), Vertex(300.0,101.0)], self.init_vals)
        # cellL = GrowingCell(sim, [Vertex(100.0,100.0), Vertex(100.0,301.0), Vertex(301.0,301.0), Vertex(301.0,100.0)], self.init_vals)
        # cellM = GrowingCell(sim, [Vertex(200.0,200.0), Vertex(200.0,300.0), Vertex(300.0,300.0), Vertex(300.0,200.0)], self.init_vals)
        # neighbors = [cellA, cellB, cellL, cellM]
        # neighbors_aux = [0.1, -0.4, 0.05, 0]
        # cell_dict = {curr_cell: 0.5, cellA: 1}

        # expected_dict = {curr_cell: 0.5, cellA: 0.9, cellB: 0.4, cellL: -0.05, cellM: 0}
        # found_dict = circ_module.update_neighbor_cell(cell_dict, neighbors, neighbors_aux)
        # self.assertEqual(expected_dict, found_dict)
        sim = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, 1, 400, False)
        curr_cell = GrowingCell(
            sim,
            [
                Vertex(100.0, 100.0),
                Vertex(100.0, 300.0),
                Vertex(300.0, 300.0),
                Vertex(300.0, 100.0),
            ],
            self.init_vals,
        )
        circ_module = BaseCirculateModuleDisc(curr_cell, self.init_vals)
        neighbora = GrowingCell(
            sim,
            [
                Vertex(100.0, 300.0),
                Vertex(100.0, 600.0),
                Vertex(300.0, 600.0),
                Vertex(300.0, 300.0),
            ],
            self.init_vals,
        )
        neighborm = GrowingCell(
            sim,
            [
                Vertex(300.0, 100.0),
                Vertex(300.0, 300.0),
                Vertex(600.0, 300.0),
                Vertex(600.0, 100.0),
            ],
            self.init_vals,
        )
        sim.setup()
        neighbors_auxin = [{neighbora: 866179 / 80000000}, {neighborm: 866179 / 80000000}]
        cell_dict = {curr_cell: 0.5, neighbora: 0.1}
        expected_dict = {
            curr_cell: 0.5,
            neighbora: 0.1 - 866179 / 80000000,
            neighborm: -866179 / 80000000,
        }
        found_dict = circ_module.update_neighbor_cell(cell_dict, neighbors_auxin)
        self.assertEqual(expected_dict, found_dict)

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
            self.init_vals,
        )
        circ_module = BaseCirculateModuleDisc(cell, self.init_vals)
        sim.setup()
        found = circ_module.get_auxin()
        expected = 2
        self.assertEqual(expected, found)
