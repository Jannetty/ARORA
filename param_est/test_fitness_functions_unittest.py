import os
import platform
if platform.system() == 'Linux':
    os.environ["ARCADE_HEADLESS"] = "True"
import unittest
import numpy as np
from unittest.mock import MagicMock, patch
from param_est.fitness_functions import auxin_peak_at_root_tip, auxin_greater_in_larger_cells_at_trans_elon_interface

class TestFitnessFunctions(unittest.TestCase):

    def setUp(self):
        self.sim = MagicMock()
        self.sim.cell_list = [MagicMock() for _ in range(10)]
        for cell in self.sim.cell_list:
            cell.get_dev_zone.return_value = 'transition'
            cell.get_cell_type.return_value = 'peri'
            cell.get_quad_perimeter().get_area.return_value = 1.0
            cell.get_circ_mod().get_auxin.return_value = 1.0
        self.chromosome = {}

    @patch('param_est.fitness_functions.spearmanr')
    def test_auxin_greater_in_larger_cells_at_trans_elon_interface(self, mock_spearmanr):
        # Arrange
        mock_spearmanr.return_value = 0.5  # Set a mock correlation coefficient

        # Act
        result = auxin_greater_in_larger_cells_at_trans_elon_interface(self.sim, self.chromosome)

        # Assert
        self.assertEqual(result, 0.5)
        self.assertNotIn("notes", self.chromosome)

    @patch('param_est.fitness_functions.spearmanr')
    def test_auxin_greater_in_larger_cells_at_trans_elon_interface_inverse_correlation(self, mock_spearmanr):
        # Arrange
        mock_spearmanr.return_value = -0.5  # Set a mock inverse correlation coefficient

        # Act
        result = auxin_greater_in_larger_cells_at_trans_elon_interface(self.sim, self.chromosome)

        # Assert
        self.assertEqual(result, 0.5)
        self.assertIn("notes", self.chromosome)
        self.assertIn("Inverse correlation between xpp cell size and auxin concentration", self.chromosome["notes"])


    def test_auxin_peak_at_root_tip(self):
        from param_est.fitness_functions import auxin_peak_at_root_tip
        sim = MagicMock()
        sim.cell_list = [MagicMock() for _ in range(10)]
        sim.cell_list[0].get_dev_zone.return_value = 'meristematic'
        sim.cell_list[1].get_dev_zone.return_value = 'transition'
        sim.cell_list[2].get_dev_zone.return_value = 'meristematic'
        sim.cell_list[3].get_dev_zone.return_value = 'transition'
        sim.cell_list[4].get_dev_zone.return_value = 'meristematic'
        sim.cell_list[5].get_dev_zone.return_value = 'transition'
        sim.cell_list[6].get_dev_zone.return_value = 'meristematic'
        sim.cell_list[7].get_dev_zone.return_value = 'transition'
        sim.cell_list[8].get_dev_zone.return_value = 'meristematic'
        sim.cell_list[9].get_dev_zone.return_value = 'roottip'
        sim.cell_list[0].get_circ_mod().get_auxin.return_value = 1
        sim.cell_list[1].get_circ_mod().get_auxin.return_value = 2
        sim.cell_list[2].get_circ_mod().get_auxin.return_value = 3
        sim.cell_list[3].get_circ_mod().get_auxin.return_value = 4
        sim.cell_list[4].get_circ_mod().get_auxin.return_value = 5
        sim.cell_list[5].get_circ_mod().get_auxin.return_value = 6
        sim.cell_list[6].get_circ_mod().get_auxin.return_value = 7
        sim.cell_list[7].get_circ_mod().get_auxin.return_value = 8
        sim.cell_list[8].get_circ_mod().get_auxin.return_value = 9
        sim.cell_list[9].get_circ_mod().get_auxin.return_value = 10
        avg_non_root_tip_auxins = sum([1, 2, 3, 4, 5, 6, 7, 8, 9])/9
        avg_root_tip_auxins = 10
        chromosome = {}
        result = auxin_peak_at_root_tip(sim, chromosome)
        self.assertEqual(result, (avg_root_tip_auxins/avg_non_root_tip_auxins))

    # def test_auxin_oscillation_across_XPP_cells_in_Oz(self):
    #     from PythonRootDevModel.param_est.fitness_functions import auxin_oscillation_across_XPP_cells_in_OZ
    #     sim = MagicMock()
    #     sim.cell_list = [MagicMock() for _ in range(10)]
    #     sim.cell_list[0].get_dev_zone.return_value = 'meristematic'
    #     sim.cell_list[1].get_dev_zone.return_value = 'transition'
    #     sim.cell_list[2].get_dev_zone.return_value = 'meristematic'
    #     sim.cell_list[3].get_dev_zone.return_value = 'transition'
    #     sim.cell_list[4].get_dev_zone.return_value = 'meristematic'
    #     sim.cell_list[5].get_dev_zone.return_value = 'transition'
    #     sim.cell_list[6].get_dev_zone.return_value = 'meristematic'
    #     sim.cell_list[7].get_dev_zone.return_value = 'transition'
    #     sim.cell_list[8].get_dev_zone.return_value = 'meristematic'
    #     sim.cell_list[9].get_dev_zone.return_value = 'transition'
    #     sim.cell_list[0].get_cell_type.return_value = 'peri'
    #     sim.cell_list[1].get_cell_type.return_value = 'peri'
    #     sim.cell_list[2].get_cell_type.return_value = 'peri'
    #     sim.cell_list[3].get_cell_type.return_value = 'peri'
    #     sim.cell_list[4].get_cell_type.return_value = 'peri'
    #     sim.cell_list[5].get_cell_type.return_value = 'peri'
    #     sim.cell_list[6].get_cell_type.return_value = 'peri'
    #     sim.cell_list[7].get_cell_type.return_value = 'peri'
    #     sim.cell_list[8].get_cell_type.return_value = 'peri'
    #     sim.cell_list[9].get_cell_type.return_value = 'peri'
    #     sim.cell_list[0].get_quad_perimeter().get_area.return_value = 1
    #     sim.cell_list[1].get_quad_perimeter().get_area.return_value = 2
    #     sim.cell_list[2].get_quad_perimeter().get_area.return_value = 3
    #     sim.cell_list[3].get_quad_perimeter().get_area.return_value = 4
    #     sim.cell_list[4].get_quad_perimeter().get_area.return_value = 5
    #     sim.cell_list[5].get_quad_perimeter().get_area.return_value = 6
        

    #def test_auxin_oscillation_across_XPP_cells_in_Oz(self):