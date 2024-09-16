import os
import platform
import ast

if platform.system() == "Linux":
    os.environ["ARCADE_HEADLESS"] = "True"
import unittest
import numpy as np
import pandas as pd
from unittest.mock import MagicMock, patch
from param_est.fitness_functions import (
    avg_auxin_root_tip_greater_than_elsewhere,
    auxin_greater_in_larger_cells_at_trans_elon_interface,
    parity_of_mz_auxin_concentrations_with_VDB_data,
    collect_auxin_data_by_tick,
    calculate_auxin_summary,
    find_closest_ARORA_pericycle_cell,
    find_ARORA_cell_closest_to_centroid,
    preprocess_ARORA_sim_output,
    get_min_y,
    parity_of_auxin_c_for_xpp_boundary_cell_at_each_time_point,
)


class TestFitnessFunctions(unittest.TestCase):

    def setUp(self):
        self.sim = MagicMock()
        self.sim.cell_list = [MagicMock() for _ in range(10)]
        for cell in self.sim.cell_list:
            cell.get_dev_zone.return_value = "transition"
            cell.get_cell_type.return_value = "peri"
            cell.get_quad_perimeter().get_area.return_value = 1.0
            cell.get_circ_mod().get_auxin.return_value = 1.0
        self.chromosome = {}

        self.arora_df_ONLY_PERICYCLE = pd.DataFrame(
            {
                "adj_centroid_y": [50, 100, 150, 200, 250],
                "auxin": [10, 20, 30, 40, 50],  # Mock auxin concentration
                "cell": [1, 2, 3, 4, 5],
            }
        )

        self.centroid_y_locations = np.array([80, 185])

        self.mock_sim_output = pd.DataFrame(
            {
                "tick": [1, 1, 2, 2],
                "dev_zone": [
                    "meristematic",
                    "meristematic",
                    "meristematic",
                    "meristematic",
                ],
                "cell_type": ["peri", "peri", "peri", "peri"],
                "auxin": [10, 20, 15, 25],
                "adj_centroid_y": [75, 80, 120, 125],
                "centroid_y": [75, 80, 120, 125],
            }
        )

        self.mock_vdb_summary = pd.DataFrame({"auxin_mean": [12, 22, 30, 40]})

        # Additional setup for find_ARORA_cell_closest_to_centroid tests
        self.arora_df_with_strings = pd.DataFrame(
            {
                "cell": [1, 2, 3],
                "adj_centroid": [
                    "[50, 50]",
                    "[100, 100]",
                    "[150, 150]",
                ],  # Centroids as strings
                "auxin": [10, 20, 30],
                "tick": [1, 1, 1],
            }
        )

        self.arora_df_with_tuples = pd.DataFrame(
            {
                "cell": [1, 2, 3],
                "adj_centroid": [
                    (50, 50),
                    (100, 100),
                    (150, 150),
                ],  # Centroids as tuples
                "auxin": [10, 20, 30],
                "tick": [1, 1, 1],
            }
        )

        self.target_centroid = [75, 75]

        # Mock data for sim_output_df
        self.sim_output_df = pd.DataFrame({
            'location': ['[[71, 11], [54, 13], [58, 34], [71, 33]]', '[[58, 12], [60, 14], [68, 20], [80, 25]]'],
            'tick': [1, 2]
        })

        # Expected parsed locations (as lists of tuples)
        self.parsed_locations = [
            [[71, 11], [54, 13], [58, 34], [71, 33]],
            [[58, 12], [60, 14], [68, 20], [80, 25]]
        ]

    @patch("param_est.fitness_functions.spearmanr")
    def test_auxin_greater_in_larger_cells_at_trans_elon_interface(
        self, mock_spearmanr
    ):
        # Arrange
        mock_spearmanr.return_value = MagicMock(
            statistic=0.5
        )  # Set a mock correlation coefficient

        # Act
        result = auxin_greater_in_larger_cells_at_trans_elon_interface(
            self.sim, self.chromosome
        )

        # Assert
        self.assertEqual(result, 0.5)
        self.assertNotIn("notes", self.chromosome)

    @patch("param_est.fitness_functions.spearmanr")
    def test_auxin_greater_in_larger_cells_at_trans_elon_interface_inverse_correlation(
        self, mock_spearmanr
    ):
        # Arrange
        mock_spearmanr.return_value = MagicMock(
            statistic=-0.5
        )  # Set a mock inverse correlation coefficient

        # Act
        result = auxin_greater_in_larger_cells_at_trans_elon_interface(
            self.sim, self.chromosome
        )

        # Assert
        self.assertEqual(result, 0.5)
        self.assertIn("notes", self.chromosome)
        self.assertIn(
            "Inverse correlation between xpp cell size and auxin concentration",
            self.chromosome["notes"],
        )

    def test_auxin_peak_at_root_tip(self):
        sim = MagicMock()
        sim.cell_list = [MagicMock() for _ in range(10)]
        sim.cell_list[0].get_dev_zone.return_value = "meristematic"
        sim.cell_list[1].get_dev_zone.return_value = "transition"
        sim.cell_list[2].get_dev_zone.return_value = "meristematic"
        sim.cell_list[3].get_dev_zone.return_value = "transition"
        sim.cell_list[4].get_dev_zone.return_value = "meristematic"
        sim.cell_list[5].get_dev_zone.return_value = "transition"
        sim.cell_list[6].get_dev_zone.return_value = "meristematic"
        sim.cell_list[7].get_dev_zone.return_value = "transition"
        sim.cell_list[8].get_dev_zone.return_value = "meristematic"
        sim.cell_list[9].get_dev_zone.return_value = "roottip"
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
        avg_non_root_tip_auxins = sum([1, 2, 3, 4, 5, 6, 7, 8, 9]) / 9
        avg_root_tip_auxins = 10
        chromosome = {}
        result = avg_auxin_root_tip_greater_than_elsewhere(sim, chromosome)
        self.assertEqual(result, (avg_root_tip_auxins / avg_non_root_tip_auxins))

    def test_collect_auxin_data_by_tick(self):
        this_centroid_y_locations = np.linspace(75, 178, 7)
        collected_data = collect_auxin_data_by_tick(
            self.mock_sim_output, this_centroid_y_locations
        )
        # Check that collected_data has the expected number of rows
        self.assertEqual(len(collected_data), 14)  # expect 7 points per tick, 2 ticks
        # Check that collected_data contains the necessary columns
        self.assertTrue("auxin" in collected_data.columns)

    def test_calculate_auxin_summary(self):
        summary_df = calculate_auxin_summary(self.mock_sim_output)
        # Check if summary DataFrame contains expected statistics
        self.assertEqual(len(summary_df), 2)  # Expect 2 ranks based on mock data
        self.assertTrue("auxin_mean" in summary_df.columns)
        self.assertTrue("auxin_range" in summary_df.columns)

    def test_find_closest_ARORA_pericycle_cell(self):
        # Call the function
        closest_cells = find_closest_ARORA_pericycle_cell(
            self.centroid_y_locations, self.arora_df_ONLY_PERICYCLE
        )

        # Check that the number of returned closest cells is the same as centroid_y_locations
        self.assertEqual(len(closest_cells), len(self.centroid_y_locations))

        # Check that the correct closest cells are returned
        self.assertEqual(closest_cells[0]["adjusted_centroid_y"], 100)
        self.assertEqual(closest_cells[1]["adjusted_centroid_y"], 200)

        # Optionally, check auxin values for additional confirmation
        self.assertEqual(closest_cells[0]["cell"], 2)
        self.assertEqual(closest_cells[1]["cell"], 4)

    @patch("pandas.read_csv")
    @patch("param_est.fitness_functions.preprocess_ARORA_sim_output")
    @patch("param_est.fitness_functions.collect_auxin_data_by_tick")
    @patch("param_est.fitness_functions.calculate_auxin_summary")
    def test_parity_of_mz_auxin_concentrations_with_VDB_data(
        self,
        mock_calculate_auxin_summary,
        mock_collect_auxin_data_by_tick,
        mock_preprocess_ARORA_sim_output,
        mock_read_csv,
    ):
        # Set up the mock simulation data
        sim_mock = MagicMock()
        sim_mock.output.filename_csv = "mock_sim_output.csv"

        chromosome_mock = {}

        # Step 1: Mock reading the VDB and ARORA CSVs
        # Adjusted the mock VDB data to have 3 elements (to match ARORA summary data)
        mock_read_csv.side_effect = [
            pd.DataFrame({"auxin_mean": [10, 20, 30]}),  # Mock VDB data with 3 elements
            pd.DataFrame(
                {"tick": [1, 2, 3], "auxin": [10, 15, 20]}
            ),  # Mock simulation output data
        ]

        # Step 2: Mock preprocessing ARORA simulation output
        mock_preprocess_ARORA_sim_output.return_value = pd.DataFrame(
            {"tick": [1, 2, 3], "auxin": [10, 15, 20]}
        )

        # Step 3: Mock the auxin concentration collection
        mock_collect_auxin_data_by_tick.return_value = pd.DataFrame(
            {"auxin": [10, 20, 30], "tick": [1, 2, 3]}
        )

        # Step 4: Mock the auxin summary statistics
        mock_calculate_auxin_summary.return_value = pd.DataFrame(
            {"auxin_mean": [10, 20, 30]}
        )

        # Step 5: Call the function and assert the result
        result = parity_of_mz_auxin_concentrations_with_VDB_data(
            sim_mock, chromosome_mock
        )

        # Step 6: Assert that the Pearson correlation coefficient is as expected
        expected_correlation = np.corrcoef([10, 20, 30], [10, 20, 30])[
            0, 1
        ]  # Perfect correlation
        self.assertAlmostEqual(result, expected_correlation)

        # Optionally, verify the mocks were called correctly
        mock_read_csv.assert_called()
        mock_preprocess_ARORA_sim_output.assert_called()
        mock_collect_auxin_data_by_tick.assert_called()
        mock_calculate_auxin_summary.assert_called()

    def test_find_ARORA_cell_closest_to_centroid_with_strings(self):
        # Test when centroids are in string format
        result = find_ARORA_cell_closest_to_centroid(
            self.target_centroid, self.arora_df_with_strings
        )

        # Expected result (cell 1 is the closest to centroid [75, 75])
        expected_result = {
            "Closest_Cell": 1,
            "Closest_Adj_Centroid": [50, 50],
            "Distance": np.linalg.norm(np.array([50, 50]) - np.array([75, 75])),
            "Auxin": 10,
            "Tick": 1,
        }

        self.assertEqual(result["Closest_Cell"], expected_result["Closest_Cell"])
        self.assertEqual(
            result["Closest_Adj_Centroid"], expected_result["Closest_Adj_Centroid"]
        )
        self.assertAlmostEqual(result["Distance"], expected_result["Distance"])
        self.assertEqual(result["Auxin"], expected_result["Auxin"])
        self.assertEqual(result["Tick"], expected_result["Tick"])

    def test_find_ARORA_cell_closest_to_centroid_with_tuples(self):
        # Test when centroids are in tuple/list format
        result = find_ARORA_cell_closest_to_centroid(
            self.target_centroid, self.arora_df_with_tuples
        )

        # Expected result (cell 1 is the closest to centroid [75, 75])
        expected_result = {
            "Closest_Cell": 1,
            "Closest_Adj_Centroid": (50, 50),
            "Distance": np.linalg.norm(np.array([50, 50]) - np.array([75, 75])),
            "Auxin": 10,
            "Tick": 1,
        }

        self.assertEqual(result["Closest_Cell"], expected_result["Closest_Cell"])
        self.assertEqual(
            result["Closest_Adj_Centroid"], expected_result["Closest_Adj_Centroid"]
        )
        self.assertAlmostEqual(result["Distance"], expected_result["Distance"])
        self.assertEqual(result["Auxin"], expected_result["Auxin"])
        self.assertEqual(result["Tick"], expected_result["Tick"])

    @patch('param_est.fitness_functions.get_min_y')
    def test_preprocess_ARORA_sim_output(self, mock_get_min_y):
        # Prepare a copy of the simulated output DataFrame
        sim_output_df_copy = self.sim_output_df.copy()

        # Mock get_min_y to return the minimum 'y' for each tick
        mock_get_min_y.side_effect = [11, 12]  # These are mock minimum y-values for the two rows

        # Call the function
        processed_df = preprocess_ARORA_sim_output(sim_output_df_copy)

        # Assert that 'location' column is correctly evaluated into lists of tuples
        self.assertEqual(processed_df['location'].tolist(), self.parsed_locations)

        # Assert that 'centroid' column is added correctly
        expected_centroids = [[63.5, 22.75], [66.5, 17.75]]
        self.assertEqual(processed_df['centroid'].tolist(), expected_centroids)

        # Assert that 'centroid_x' and 'centroid_y' columns are correctly created
        self.assertEqual(processed_df['centroid_x'].tolist(), [63.5, 66.5])
        self.assertEqual(processed_df['centroid_y'].tolist(), [22.75, 17.75])

        # Assert that 'min_y' column is correctly populated
        self.assertEqual(processed_df['min_y'].tolist(), [11, 12])

        # Assert that 'adj_centroid_y' is correctly calculated
        VDB_Y_min = 11
        expected_adj_centroid_y = [22.75 - (11 + VDB_Y_min), 17.75 - (12 + VDB_Y_min)]
        self.assertTrue(np.allclose(processed_df['adj_centroid_y'].tolist(), expected_adj_centroid_y))

        # Assert that 'adj_centroid' column is correctly created
        expected_adj_centroids = [[63.5, 22.75 - (11 + VDB_Y_min)], [66.5, 17.75 - (12 + VDB_Y_min)]]
        self.assertEqual(processed_df['adj_centroid'].tolist(), expected_adj_centroids)

    @patch('param_est.fitness_functions.find_ARORA_cell_closest_to_centroid')
    @patch('param_est.fitness_functions.preprocess_ARORA_sim_output')
    @patch('pandas.read_csv')
    def test_parity_of_auxin_c_for_xpp_boundary_cell_at_each_time_point(self, mock_read_csv, mock_preprocess_ARORA_sim_output, mock_find_closest_cell):
        # Step 1: Mock the VDB auxin data (what you expect from 'vdb_auxins_at_56pt5_336pt5')
        mock_vdb_auxins = pd.DataFrame({
            'auxin': [10, 15, 20]  # Mock auxin values from VDB
        })

        # Step 2: Mock the simulation output CSV data
        mock_sim_output_df = pd.DataFrame({
            'tick': [1, 1, 2, 2, 3, 3],  # Mock simulation ticks
            'location': ['[[56.5, 336.5]]', '[[58.5, 338.5]]', '[[56.5, 336.5]]', '[[58.5, 338.5]]', '[[56.5, 336.5]]', '[[58.5, 338.5]]'],
            'auxin': [12, 13, 18, 19, 25, 26],  # Mock auxin values for cells
        })

        # Mock read_csv to return VDB auxin data first, then the simulation output CSV
        mock_read_csv.side_effect = [mock_vdb_auxins, mock_sim_output_df]

        # Step 3: Mock the preprocessed simulation data
        mock_preprocess_ARORA_sim_output.return_value = mock_sim_output_df

        # Step 4: Mock the closest cell finder for each tick
        mock_find_closest_cell.side_effect = [
            {'Auxin': 12},  # Closest cell at tick 1
            {'Auxin': 18},  # Closest cell at tick 2
            {'Auxin': 25},  # Closest cell at tick 3
        ]

        # Step 5: Mock simulation object
        mock_sim = MagicMock()
        mock_sim.output.filename_csv = 'mock_sim_output.csv'

        # Step 6: Call the function and compute the expected Pearson correlation
        result = parity_of_auxin_c_for_xpp_boundary_cell_at_each_time_point(mock_sim, {})
        
        # Step 7: Calculate the expected correlation coefficient using mock data
        expected_corr = np.corrcoef([10, 15, 20], [12, 18, 25])[0, 1]  # Comparing VDB auxin with simulated auxin
        
        # Step 8: Assert the result is correct
        self.assertAlmostEqual(result, expected_corr, places=5)

        # Verify that the functions were called as expected
        mock_read_csv.assert_called()
        mock_preprocess_ARORA_sim_output.assert_called()
        mock_find_closest_cell.assert_called()