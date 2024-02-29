import unittest
import numpy as np
from unittest.mock import MagicMock, patch
from param_est.cost_functions import auxin_peak_at_root_tip, auxin_greater_in_larger_cells 

class TestCostFunctions(unittest.TestCase):
    
    def test_correlation_coefficient(self):
        from param_est.cost_functions import correlation_coefficient
        list_x = [1, 2, 3, 4, 5]
        list_y = [5, 4, 3, 2, 1]
        self.assertEqual(correlation_coefficient(list_x, list_y), -1)
        list_x = [1, 2, 3, 4, 5]
        list_y = [1, 2, 3, 4, 5]
        self.assertEqual(correlation_coefficient(list_x, list_y), 1)
        list_x = [1, 2, 3, 4, 5]
        list_y = [5, 4, 3, 2, 1]
        self.assertEqual(correlation_coefficient(list_x, list_y), -1)

    @patch('param_est.cost_functions.correlation_coefficient')
    def test_auxin_greater_in_larger_cells(self, mock_correlation_coefficient):
        from param_est.cost_functions import auxin_greater_in_larger_cells
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
        sim.cell_list[9].get_dev_zone.return_value = 'transition'
        sim.cell_list[0].get_cell_type.return_value = 'peri'
        sim.cell_list[1].get_cell_type.return_value = 'peri'
        sim.cell_list[2].get_cell_type.return_value = 'peri'
        sim.cell_list[3].get_cell_type.return_value = 'peri'
        sim.cell_list[4].get_cell_type.return_value = 'peri'
        sim.cell_list[5].get_cell_type.return_value = 'peri'
        sim.cell_list[6].get_cell_type.return_value = 'peri'
        sim.cell_list[7].get_cell_type.return_value = 'peri'
        sim.cell_list[8].get_cell_type.return_value = 'peri'
        sim.cell_list[9].get_cell_type.return_value = 'peri'
        sim.cell_list[0].get_quad_perimeter().get_area.return_value = 1
        sim.cell_list[1].get_quad_perimeter().get_area.return_value = 2
        sim.cell_list[2].get_quad_perimeter().get_area.return_value = 3
        sim.cell_list[3].get_quad_perimeter().get_area.return_value = 4
        sim.cell_list[4].get_quad_perimeter().get_area.return_value = 5
        sim.cell_list[5].get_quad_perimeter().get_area.return_value = 6
        sim.cell_list[6].get_quad_perimeter().get_area.return_value = 7
        sim.cell_list[7].get_quad_perimeter().get_area.return_value = 8
        sim.cell_list[8].get_quad_perimeter().get_area.return_value = 9
        sim.cell_list[9].get_quad_perimeter().get_area.return_value = 10
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
        mock_correlation_coefficient.return_value = 0.5
        self.assertEqual(auxin_greater_in_larger_cells(sim), 0.5)
        mock_correlation_coefficient.return_value = -0.5
        self.assertEqual(auxin_greater_in_larger_cells(sim), np.inf)
        mock_correlation_coefficient.return_value = 0
        self.assertEqual(auxin_greater_in_larger_cells(sim), 0)
        mock_correlation_coefficient.return_value = 1
        self.assertEqual(auxin_greater_in_larger_cells(sim), 1)
        mock_correlation_coefficient.return_value = -1
        self.assertEqual(auxin_greater_in_larger_cells(sim), np.inf)

    def test_auxin_peak_at_root_tip(self):
        from param_est.cost_functions import auxin_peak_at_root_tip
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
        result = auxin_peak_at_root_tip(sim)
        self.assertEqual(result, (avg_non_root_tip_auxins/avg_root_tip_auxins))