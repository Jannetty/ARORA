import unittest

from src.plantem.loc.vertex.vertex import Vertex
from src.plantem.agent.circ_module import BaseCirculateModule

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

    init_vals = {"auxin": 2, "arr": 3, "aux_lax": 3, "pina": 0.5, "pinb": 0.7,
                 "pinl": 0.4, "pinm": 0.2, "k_ARR_ARR": 1, "k_auxin_AUXLAX": 1,
                 "k_auxin_PIN": 1, "k_ARR_PIN": 1, "ks": 0.005, "kd": 0.0015}

    def test_calculate_auxin(self):
        circ_module = BaseCirculateModule(GrowingCell, self.init_vals)
        timestep = 1
        area = 100
        expected_auxin = -0.295
        found_auxin = circ_module.calculate_auxin(timestep, area)
        self.assertAlmostEqual(expected_auxin, found_auxin, places=5)

    def test_calculate_arr(self):
        circ_module = BaseCirculateModule(GrowingCell, self.init_vals)
        timestep = 1
        area = 100
        expected_arr = -0.44875
        found_arr = circ_module.calculate_arr(timestep, area)
        self.assertAlmostEqual(expected_arr, found_arr, places=5)
    
    def test_calculate_aux_lax(self):
        circ_module = BaseCirculateModule(GrowingCell, self.init_vals)
        timestep = 1
        area = 100
        expected_aux_lax = -0.45209
        found_aux_lax = circ_module.calculate_aux_lax(timestep, area)
        self.assertAlmostEqual(expected_aux_lax, found_aux_lax, places=5)
    
    def test_calcualte_pin(self):
        circ_module = BaseCirculateModule(GrowingCell, self.init_vals)
        timestep = 1
        area = 100
        expected_PIN = -0.0037954
        found_PIN = circ_module.calculate_pin(timestep, area)
        self.assertAlmostEqual(expected_PIN, found_PIN, places=5)

    def test_calculate_neighbor_PIN(self):
        circ_module = BaseCirculateModule(GrowingCell, self.init_vals)
        timestep = 1
        area = 100
        expected_neighbor_PIN = -0.075949
        found_neighbor_PIN = circ_module.calculate_neighbor_pin(0.5, timestep, area)
        self.assertAlmostEqual(expected_neighbor_PIN, found_neighbor_PIN, places=5)

    def test_calculate_neighbor_auxin(self):
        circ_module = BaseCirculateModule(GrowingCell, self.init_vals)
        timestep = 1
        area = 100
        expected_neighbor_auxin = 0.01082723
        found_neighbor_auxin = circ_module.calculate_neighbor_auxin(0.5, timestep, area)
        self.assertAlmostEqual(expected_neighbor_auxin, found_neighbor_auxin, places=5)

    def test_update_current_cell(self):
        circ_module = BaseCirculateModule(GrowingCell, self.init_vals)
        cell_dict = {}
        curr_cell = GrowingCell
        delta_aux = 0.5

        expected_dict = {curr_cell: 0.5}
        found_dict = circ_module.update_current_cell(curr_cell, cell_dict, delta_aux)
        self.assertEqual(expected_dict, found_dict)

    def test_update_neighbor_cell(self):
        circ_module = BaseCirculateModule(GrowingCell, self.init_vals)

        curr_cell = GrowingCell
        sim = None

        cellA = GrowingCell(sim, [Vertex(100.0,100.0), Vertex(100.0,300.0), Vertex(300.0,300.0), Vertex(300.0,100.0)], self.init_vals)
        cellB = GrowingCell(sim, [Vertex(101.0,101.0), Vertex(101.0,300.0), Vertex(300.0,300.0), Vertex(300.0,101.0)], self.init_vals)
        cellL = GrowingCell(sim, [Vertex(100.0,100.0), Vertex(100.0,301.0), Vertex(301.0,301.0), Vertex(301.0,100.0)], self.init_vals)
        cellM = GrowingCell(sim, [Vertex(200.0,200.0), Vertex(200.0,300.0), Vertex(300.0,300.0), Vertex(300.0,200.0)], self.init_vals)
        neighbors = [cellA, cellB, cellL, cellM]
        neighbors_aux = [0.1, -0.4, 0.05, 0]
        cell_dict = {curr_cell: 0.5, cellA: 1}

        expected_dict = {curr_cell: 0.5, cellA: 0.9, cellB: 0.4, cellL: -0.05, cellM: 0}
        found_dict = circ_module.update_neighbor_cell(cell_dict, neighbors, neighbors_aux)
        self.assertEqual(expected_dict, found_dict)