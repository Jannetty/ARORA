import os
import platform

if platform.system() == "Linux":
    os.environ["ARCADE_HEADLESS"] = "True"

import unittest
from unittest.mock import MagicMock, patch
from src.agent.default_geo_neighbor_helpers import NeighborHelpers
from src.agent.cell import Cell


class TestNeighborHelpers(unittest.TestCase):

    def test_neighbor_direction_one_v_a(self):
        # Mocking Cell instances
        cell = MagicMock()
        neighbor = MagicMock()
        
        cell_id_vals = [10,11,16,19,20,25,54,54,57,57]
        neighbor_id_vals = [20,25,36,37,36,37,65,66,69,70]
        
        # Expected outcome
        expected_direction = "a"
        
        # Run the function and assert the outcome for each pair
        for idx, cell_id_val in enumerate(cell_id_vals):
            cell.get_c_id.return_value = cell_id_val
            neighbor.get_c_id.return_value = neighbor_id_vals[idx]
            direction = NeighborHelpers.get_neighbor_dir_neighbor_shares_one_v_default_geo(cell, neighbor)
            # Assert the outcome
            self.assertEqual(direction, expected_direction)

    def test_neighbor_direction_one_v_b(self):
        # Mocking Cell instances
        cell = MagicMock()
        neighbor = MagicMock()
        
        cell_id_vals = [20,25,36,37,36,37,65,66,69,70]
        neighbor_id_vals = [10,11,16,19,20,25,54,54,57,57]
        
        # Expected outcome
        expected_direction = "b"
        
        # Run the function and assert the outcome for each pair
        for idx, cell_id_val in enumerate(cell_id_vals):
            cell.get_c_id.return_value = cell_id_val
            neighbor.get_c_id.return_value = neighbor_id_vals[idx]
            direction = NeighborHelpers.get_neighbor_dir_neighbor_shares_one_v_default_geo(cell, neighbor)
            self.assertEqual(direction, expected_direction)

    def test_neighbor_direction_one_v_l(self):
        # Mocking Cell instances
        cell = MagicMock()
        neighbor = MagicMock()
        
        cell_id_vals = [26, 27, 39, 39, 42, 42, 50, 51, 50, 51]
        neighbor_id_vals = [20, 25, 38, 46, 43, 47, 44, 45, 52, 59]
        
        # Expected outcome
        expected_direction = "l"
        
        # Run the function and assert the outcome for each pair
        for idx, cell_id_val in enumerate(cell_id_vals):
            cell.get_c_id.return_value = cell_id_val
            neighbor.get_c_id.return_value = neighbor_id_vals[idx]
            direction = NeighborHelpers.get_neighbor_dir_neighbor_shares_one_v_default_geo(cell, neighbor)
            self.assertEqual(direction, expected_direction)

        # Check case that neighbor is rootcap cell
        neighbor_id_vals = NeighborHelpers.ROOTCAP_CELL_IDs
        cell_id_vals = [-1] * len(cell_id_vals)

        # Run the function and assert the outcome for each pair
        for idx, cell_id_val in enumerate(cell_id_vals):
            cell.get_c_id.return_value = cell_id_val
            neighbor.get_c_id.return_value = neighbor_id_vals[idx]
            direction = NeighborHelpers.get_neighbor_dir_neighbor_shares_one_v_default_geo(cell, neighbor)
            self.assertEqual(direction, expected_direction)

    def test_neighbor_direction_one_v_m(self):
        # Mocking Cell instances
        cell = MagicMock()
        neighbor = MagicMock()
        
        cell_id_vals = [38, 46, 43, 47, 44, 45, 52, 59]
        neighbor_id_vals = [39, 39, 42, 42, 50, 51, 50, 51]
        
        # Expected outcome
        expected_direction = "m"
        
        # Run the function and assert the outcome for each pair
        for idx, cell_id_val in enumerate(cell_id_vals):
            cell.get_c_id.return_value = cell_id_val
            neighbor.get_c_id.return_value = neighbor_id_vals[idx]
            direction = NeighborHelpers.get_neighbor_dir_neighbor_shares_one_v_default_geo(cell, neighbor)
            self.assertEqual(direction, expected_direction)

        # Check case that cell is rootcap cell
        cell_id_vals = NeighborHelpers.ROOTCAP_CELL_IDs
        neighbor_id_vals = [-1] * len(cell_id_vals)

        # Run the function and assert the outcome for each pair
        for idx, cell_id_val in enumerate(cell_id_vals):
            cell.get_c_id.return_value = cell_id_val
            neighbor.get_c_id.return_value = neighbor_id_vals[idx]
            direction = NeighborHelpers.get_neighbor_dir_neighbor_shares_one_v_default_geo(cell, neighbor)
            self.assertEqual(direction, expected_direction)

    def test_check_if_neighbors_with_root_cap_cell_adds_new_root_cap_neighbors_correctly(self):
        # Mocking Cell instances and sim
        mock_cell = MagicMock()
        mock_sim = MagicMock()
        
        root_cap_cell_ids = NeighborHelpers.ROOTCAP_CELL_IDs
        mock_root_cap_cells = [MagicMock() for _ in root_cap_cell_ids]
        for cell, cell_id in zip(mock_root_cap_cells, root_cap_cell_ids):
            cell.get_c_id.return_value = cell_id

        # Setup the simulation's cell list to root cap cells
        mock_sim.get_cell_list.return_value = mock_root_cap_cells

        # Assume the cell initially has no left neighbors
        mock_cell.get_l_neighbors.return_value = []

        # Assume NeighborHelpers.cell_and_lrc_cell_are_neighbors would return True in this scenario
        with patch('src.agent.default_geo_neighbor_helpers.NeighborHelpers.cell_and_lrc_cell_are_neighbors', return_value=True):
            # Execute the function under test
            NeighborHelpers.check_if_neighbors_with_new_root_cap_cell(mock_cell, mock_sim)

            # Verify new neighbors are added correctly
            self.assertEqual(mock_cell.add_l_neighbor.call_count, len(root_cap_cell_ids))
            for cell in mock_root_cap_cells:
                cell.add_m_neighbor.assert_called_once_with(mock_cell)

    def test_check_if_neighbors_with_root_cap_cell_does_not_add_new_root_cap_neighbors_when_already_added(self):
        # Mocking Cell instances and sim
        mock_cell = MagicMock()
        mock_sim = MagicMock()
        
        root_cap_cell_ids = NeighborHelpers.ROOTCAP_CELL_IDs
        mock_root_cap_cells = [MagicMock() for _ in root_cap_cell_ids]
        for cell, cell_id in zip(mock_root_cap_cells, root_cap_cell_ids):
            cell.get_c_id.return_value = cell_id

        # Setup the simulation's cell list to root cap cells
        mock_sim.get_cell_list.return_value = mock_root_cap_cells

        # Assume the cell initially has all root cap cells as left neighbors
        mock_cell.get_l_neighbors.return_value = mock_root_cap_cells

        # Assume NeighborHelpers.cell_and_lrc_cell_are_neighbors would return True in this scenario
        with patch('src.agent.default_geo_neighbor_helpers.NeighborHelpers.cell_and_lrc_cell_are_neighbors', return_value=True):
            # Execute the function under test
            NeighborHelpers.check_if_neighbors_with_new_root_cap_cell(mock_cell, mock_sim)

            # Verify no new neighbors are added
            mock_cell.add_l_neighbor.assert_not_called()
            for cell in mock_root_cap_cells:
                cell.add_m_neighbor.assert_not_called()
    
    def test_check_if_neighbors_with_root_cap_cell_does_not_add_new_root_cap_neighbors_when_not_neighbors(self):
        # Mocking Cell instances and sim
        mock_cell = MagicMock()
        mock_sim = MagicMock()
        
        root_cap_cell_ids = NeighborHelpers.ROOTCAP_CELL_IDs
        mock_root_cap_cells = [MagicMock() for _ in root_cap_cell_ids]
        for cell, cell_id in zip(mock_root_cap_cells, root_cap_cell_ids):
            cell.get_c_id.return_value = cell_id

        # Setup the simulation's cell list to root cap cells
        mock_sim.get_cell_list.return_value = mock_root_cap_cells

        # Assume the cell initially has no left neighbors
        mock_cell.get_l_neighbors.return_value = []

        # Assume NeighborHelpers.cell_and_lrc_cell_are_neighbors would return False in this scenario
        with patch('src.agent.default_geo_neighbor_helpers.NeighborHelpers.cell_and_lrc_cell_are_neighbors', return_value=False):
            # Execute the function under test
            NeighborHelpers.check_if_neighbors_with_new_root_cap_cell(mock_cell, mock_sim)

            # Verify no new neighbors are added
            mock_cell.add_l_neighbor.assert_not_called()
            for cell in mock_root_cap_cells:
                cell.add_m_neighbor.assert_not_called()

    def test_no_vs_by_cell_id(self):
        # Mocking Cell instances
        cell = MagicMock()
        neighbor = MagicMock()
        
        cell_id_vals = [17,20,18,25]
        neighbor_id_vals = [20,17,25,18]
        
        # Expected outcome
        expected_direction = ["l", "b", "l", "b"]
        
        # Run the function and assert the outcome for each pair
        for idx, cell_id_val in enumerate(cell_id_vals):
            cell.get_c_id.return_value = cell_id_val
            neighbor.get_c_id.return_value = neighbor_id_vals[idx]
            direction = NeighborHelpers.get_neighbor_dir_neighbor_shares_no_vs_default_geo(cell, neighbor)
            # Assert the outcome
            self.assertEqual(direction, expected_direction[idx])

    def test_no_vs_root_cap_neighbor_direction_m(self):
        cell = MagicMock()
        neighbor = MagicMock()
        cell.get_c_id.return_value = 60  # this ID is in ROOTCAP_CELL_IDs
        neighbor.get_c_id.return_value = 100  # Arbitrary ID not in ROOTCAP_CELL_IDs
        
        # Mock get_quad_perimeter to simulate geometry
        cell.get_quad_perimeter().get_min_y.return_value = 0
        cell.get_quad_perimeter().get_max_y.return_value = 10
        neighbor.get_quad_perimeter().get_min_y.return_value = 5
        
        direction = NeighborHelpers.get_neighbor_dir_neighbor_shares_no_vs_default_geo(cell, neighbor)
        self.assertEqual(direction, "m")

    def test_no_vs_root_cap_neighbor_direction_l(self):
        cell = MagicMock()
        neighbor = MagicMock()
        cell.get_c_id.return_value = 100  # Arbitrary ID not in ROOTCAP_CELL_IDs
        neighbor.get_c_id.return_value = 60  # this ID is in ROOTCAP_CELL_IDs
        
        # Mock get_quad_perimeter to simulate geometry
        neighbor.get_quad_perimeter().get_min_y.return_value = 0
        neighbor.get_quad_perimeter().get_max_y.return_value = 10
        cell.get_quad_perimeter().get_min_y.return_value = 5
        
        direction = NeighborHelpers.get_neighbor_dir_neighbor_shares_no_vs_default_geo(cell, neighbor)
        self.assertEqual(direction, "l")

    def test_no_vs_root_cap_neighbor_no_longer_neighbor(self):
        cell = MagicMock()
        neighbor = MagicMock()
        neighbor.get_c_id.return_value = 60  # this ID is in ROOTCAP_CELL_IDs
        cell.get_c_id.return_value = 100  # Arbitrary ID not in ROOTCAP_CELL_IDs
        
        # Mock get_quad_perimeter to simulate geometry where they are no longer neighbors
        cell.get_quad_perimeter().get_min_y.return_value = 0
        cell.get_quad_perimeter().get_max_y.return_value = 10
        neighbor.get_quad_perimeter().get_min_y.return_value = 11  # Outside cell's y-range
        
        direction = NeighborHelpers.get_neighbor_dir_neighbor_shares_no_vs_default_geo(cell, neighbor)
        self.assertEqual(direction, "cell no longer root cap cell neighbor")

    @patch('src.agent.default_geo_neighbor_helpers.NeighborHelpers.check_if_no_longer_neighbors_with_root_cap_cell')
    @patch('src.agent.default_geo_neighbor_helpers.NeighborHelpers.check_if_neighbors_with_new_root_cap_cell')
    def test_fix_lrc_neighbors_after_growth(self, mock_check_new_neighbors, mock_check_no_longer_neighbors):
        # Mocking GrowingSim
        sim = MagicMock()
        # Mock cells with different types
        non_root_tip_cell = MagicMock()
        l_neighbor_root_cap_cell = MagicMock()
        l_neighbor_non_root_cap_cell = MagicMock()

        non_root_tip_cell.get_cell_type.return_value = 'vasc'
        l_neighbor_root_cap_cell.get_cell_type.return_value = 'roottip'
        l_neighbor_non_root_cap_cell.get_cell_type.return_value = 'vasc'

        # Set cell IDs for root cap and non-root cap mock cells
        l_neighbor_root_cap_cell.get_c_id.return_value = NeighborHelpers.ROOTCAP_CELL_IDs[0]
        l_neighbor_non_root_cap_cell.get_c_id.return_value = 100

        # Setup cell relationships
        non_root_tip_cell.get_l_neighbors.return_value = [l_neighbor_root_cap_cell, l_neighbor_non_root_cap_cell]

        # Setup the sim to return non-root tip cells
        sim.get_cell_list.return_value = [non_root_tip_cell]

        # Execute the method under test
        NeighborHelpers.fix_lrc_neighbors_after_growth(sim)

        # Assertions to ensure the appropriate methods were called
        mock_check_new_neighbors.assert_called_with(non_root_tip_cell, sim)
        mock_check_new_neighbors.assert_called_once()
        mock_check_no_longer_neighbors.assert_called_with(non_root_tip_cell, l_neighbor_root_cap_cell)
        mock_check_no_longer_neighbors.assert_called_once()

    def test_check_if_no_longer_neighbors_with_root_cap_cell(self):
        # Mocking Cell instances
        cell = MagicMock()
        neighbor = MagicMock()
        with patch('src.agent.default_geo_neighbor_helpers.NeighborHelpers.cell_and_lrc_cell_are_neighbors', return_value=False):
            NeighborHelpers.check_if_no_longer_neighbors_with_root_cap_cell(cell, neighbor)
            cell.remove_l_neighbor.assert_called_once_with(neighbor)
            neighbor.remove_m_neighbor.assert_called_once_with(cell)

        cell = MagicMock()
        neighbor = MagicMock()
        with patch('src.agent.default_geo_neighbor_helpers.NeighborHelpers.cell_and_lrc_cell_are_neighbors', return_value=True):
            NeighborHelpers.check_if_no_longer_neighbors_with_root_cap_cell(cell, neighbor)
            cell.remove_l_neighbor.assert_not_called()
            neighbor.remove_m_neighbor.assert_not_called()

    def test_cell_and_lrc_cell_are_neighbors_cells_on_opposite_sides(self):
        sim = MagicMock()
        sim.get_root_midpointx.return_value = 50
        # Mocking Cell instances
        cell = MagicMock()
        cell.get_sim.return_value = sim
        lrc_cell = MagicMock()
        lrc_cell.get_sim.return_value = sim
        cell.get_c_id.return_value = 100
        lrc_cell.get_c_id.return_value = NeighborHelpers.ROOTCAP_CELL_IDs[0]

        cell.get_quad_perimeter().get_left_lateral_or_medial.return_value = 'lateral'
        lrc_cell.get_quad_perimeter().get_left_lateral_or_medial.return_value = 'medial'

        #Call function under test
        are_neighbors = NeighborHelpers.cell_and_lrc_cell_are_neighbors(cell, lrc_cell)
        self.assertFalse(are_neighbors)

    def test_cell_and_lrc_cell_are_neighbors_cells_on_same_side_are_neighbors(self):
        # Test Laterally adjacent cells
        sim = MagicMock()
        sim.get_root_midpointx.return_value = 50
        # Mocking Cell instances
        cell = MagicMock()
        cell.get_sim.return_value = sim
        lrc_cell = MagicMock()
        lrc_cell.get_sim.return_value = sim
        cell.get_c_id.return_value = 100
        lrc_cell.get_c_id.return_value = NeighborHelpers.ROOTCAP_CELL_IDs[0]

        # Configure cells to be on the same side and share lateral membrane
        cell.get_quad_perimeter().get_left_lateral_or_medial.return_value = 'lateral'
        lrc_cell.get_quad_perimeter().get_left_lateral_or_medial.return_value = 'lateral'
        cell.get_quad_perimeter().get_min_x.return_value = 20
        cell.get_quad_perimeter().get_max_x.return_value = 30
        lrc_cell.get_quad_perimeter().get_min_x.return_value = 10  # Adjacent to cell
        lrc_cell.get_quad_perimeter().get_max_x.return_value = 20

         # Mock Y-coordinate logic
        cell.get_quad_perimeter().get_min_y.return_value = 10
        cell.get_quad_perimeter().get_max_y.return_value = 20
        lrc_cell.get_quad_perimeter().get_min_y.return_value = 15
        lrc_cell.get_quad_perimeter().get_max_y.return_value = 25

        # Call function under test
        are_neighbors = NeighborHelpers.cell_and_lrc_cell_are_neighbors(cell, lrc_cell)
        self.assertTrue(are_neighbors)

        # Test Medially adjacent cells
        sim = MagicMock()
        sim.get_root_midpointx.return_value = 50
        # Mocking Cell instances
        cell = MagicMock()
        cell.get_sim.return_value = sim
        lrc_cell = MagicMock()
        lrc_cell.get_sim.return_value = sim
        cell.get_c_id.return_value = 100
        lrc_cell.get_c_id.return_value = NeighborHelpers.ROOTCAP_CELL_IDs[0]

        # Configure cells to be on the same side and share medial membrane
        cell.get_quad_perimeter().get_left_lateral_or_medial.return_value = 'medial'
        lrc_cell.get_quad_perimeter().get_left_lateral_or_medial.return_value = 'medial'
        cell.get_quad_perimeter().get_min_x.return_value = 10
        cell.get_quad_perimeter().get_max_x.return_value = 20
        lrc_cell.get_quad_perimeter().get_min_x.return_value = 20  # Adjacent to cell
        lrc_cell.get_quad_perimeter().get_max_x.return_value = 30

         # Mock Y-coordinate logic
        cell.get_quad_perimeter().get_min_y.return_value = 10
        cell.get_quad_perimeter().get_max_y.return_value = 20
        lrc_cell.get_quad_perimeter().get_min_y.return_value = 15
        lrc_cell.get_quad_perimeter().get_max_y.return_value = 25

        # Call function under test
        are_neighbors = NeighborHelpers.cell_and_lrc_cell_are_neighbors(cell, lrc_cell)
        self.assertTrue(are_neighbors)