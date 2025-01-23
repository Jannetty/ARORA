import os
import platform

if platform.system() == "Linux":
    os.environ["ARCADE_HEADLESS"] = "True"

import numpy as np
from scipy.integrate import odeint
import unittest
from unittest.mock import MagicMock, patch
from src.sim.util.math_helpers import round_to_sf
from src.agent.circ_module_indep_syn_deg import CirculateModuleIndSynDeg
from typing import cast


class TestCirculateModuleIndSynDeg(unittest.TestCase):
    def setUp(self):
        self.cell_mock = MagicMock()
        self.cell_mock.get_quad_perimeter.return_value.get_left_lateral_or_medial.return_value = (
            "lateral"
        )
        self.cell_mock.get_quad_perimeter.return_value.get_right_lateral_or_medial.return_value = (
            "medial"
        )
        self.cell_mock.get_sim.return_value.get_root_midpointx.return_value = 0.5
        self.cell_mock.get_c_id.return_value = 1
        self.cell_mock.get_quad_perimeter.return_value.get_perimeter_len.return_value = 100.0

        self.init_vals = {
            "auxin": 0.1,
            "arr": 0.2,
            "al": 0.3,
            "pin": 0.4,
            "pina": 0.5,
            "pinb": 0.6,
            "pinl": 0.7,
            "pinm": 0.8,
            "growing": True,
            "k1": 1.1,
            "k2": 1.2,
            "k3": 1.3,
            "k4": 1.4,
            "k5": 1.5,
            "k6": 1.6,
            "ks_aux": 2.1,
            "kd_aux": 2.2,
            "ks_arr": 2.3,
            "kd_arr": 2.4,
            "ks_pinu": 2.5,
            "kd_pinu": 2.6,
            "kd_pinloc": 2.7,
            "ks_auxlax": 2.8,
            "kd_auxlax": 2.9,
            "auxin_w": 3.0,
            "arr_hist": [0.1, 0.2, 0.3],
        }
        self.circ_mod = CirculateModuleIndSynDeg(self.cell_mock, self.init_vals)
        self.circulator_mock = MagicMock()
        self.cell_mock.get_sim.return_value.get_circulator.return_value = self.circulator_mock

        self.neighbors_a = [MagicMock(), MagicMock()]
        self.neighbors_b = [MagicMock(), MagicMock()]
        self.neighbors_l = [MagicMock(), MagicMock()]
        self.neighbors_m = [MagicMock(), MagicMock()]

        self.cell_mock.get_a_neighbors.return_value = self.neighbors_a
        self.cell_mock.get_b_neighbors.return_value = self.neighbors_b
        self.cell_mock.get_l_neighbors.return_value = self.neighbors_l
        self.cell_mock.get_m_neighbors.return_value = self.neighbors_m

        self.neighbor_mock = MagicMock()
        self.neighbor_mock.get_c_id.return_value = 2
        self.neighbor_circ_mod_mock = MagicMock()
        self.neighbor_circ_mod_mock.calculate_neighbor_memfrac.return_value = 0.2
        self.neighbor_circ_mod_mock.get_auxin.return_value = 0.5
        self.neighbor_mock.get_circ_mod.return_value = self.neighbor_circ_mod_mock

    def test_initialization(self):
        module = CirculateModuleIndSynDeg(self.cell_mock, self.init_vals)
        self.assertEqual(module.auxin, 0.1)
        self.assertEqual(module.arr, 0.2)
        self.assertEqual(module.auxlax, 0.3)
        self.assertEqual(module.pin, 0.4)
        self.assertEqual(module.pina, 0.5)
        self.assertEqual(module.pinb, 0.6)
        self.assertEqual(module.pinl, 0.7)
        self.assertEqual(module.pinm, 0.8)
        self.assertEqual(module.k_arr_arr, 1.1)
        self.assertEqual(module.k_auxin_auxlax, 1.2)
        self.assertEqual(module.k_auxin_pin, 1.3)
        self.assertEqual(module.k_arr_pin, 1.4)
        self.assertEqual(module.k_al, 1.5)
        self.assertEqual(module.k_pin, 1.6)
        self.assertEqual(module.ks_aux, 2.1)
        self.assertEqual(module.kd_aux, 2.2)
        self.assertEqual(module.ks_arr, 2.3)
        self.assertEqual(module.kd_arr, 2.4)
        self.assertEqual(module.ks_pinu, 2.5)
        self.assertEqual(module.kd_pinu, 2.6)
        self.assertEqual(module.kd_pinloc, 2.7)
        self.assertEqual(module.ks_auxlax, 2.8)
        self.assertEqual(module.kd_auxlax, 2.9)
        self.assertEqual(module.auxin_w, 3.0)
        self.assertEqual(module.arr_hist, [0.1, 0.2, 0.3])
        self.assertEqual(module.left, "lateral")
        self.assertEqual(module.right, "medial")

    def test_initialize_pin_weights(self):
        self.circ_mod.get_apical_pin = MagicMock(return_value=1.0)
        self.circ_mod.get_basal_pin = MagicMock(return_value=2.0)
        self.circ_mod.get_lateral_pin = MagicMock(return_value=3.0)
        self.circ_mod.get_medial_pin = MagicMock(return_value=4.0)
        total_pin = 1.0 + 2.0 + 3.0 + 4.0
        expected_weights = {
            "a": 1.0 / total_pin,
            "b": 2.0 / total_pin,
            "l": 3.0 / total_pin,
            "m": 4.0 / total_pin,
        }
        pin_weights = self.circ_mod.initialize_pin_weights()
        self.assertDictEqual(pin_weights, expected_weights)

    def test_calculate_auxin(self):
        auxin_initial = 0.1
        expected_auxin = (self.circ_mod.ks_aux * self.circ_mod.auxin_w) - (
            self.circ_mod.kd_aux * auxin_initial
        )
        calculated_auxin = self.circ_mod.calculate_auxin(auxin_initial)
        self.assertAlmostEqual(calculated_auxin, expected_auxin, places=5)

    def test_calculate_arr(self):
        arr_initial = 0.1
        expected_arr = (
            self.circ_mod.ks_arr
            * (self.circ_mod.k_arr_arr / (self.circ_mod.arr_hist[0] + self.circ_mod.k_arr_arr))
        ) - (self.circ_mod.kd_arr * arr_initial)
        calculated_arr = self.circ_mod.calculate_arr(arr_initial)
        self.assertAlmostEqual(calculated_arr, expected_arr, places=5)

    def test_calculate_auxlax(self):
        auxin_initial = 0.1
        auxlax_initial = 0.2
        expected_auxlax = (self.circ_mod.ks_auxlax) * (
            auxin_initial / (auxin_initial + self.circ_mod.k_auxin_auxlax)
        ) - (self.circ_mod.kd_auxlax * auxlax_initial)
        calculated_auxlax = self.circ_mod.calculate_auxlax(auxin_initial, auxlax_initial)
        self.assertAlmostEqual(calculated_auxlax, expected_auxlax, places=5)

    def test_calculate_pin(self):
        auxin_initial = 0.2
        arr_initial = 0.1
        expected_pin = self.circ_mod.ks_pinu * (
            self.circ_mod.k_arr_pin / (arr_initial + self.circ_mod.k_arr_pin)
        ) * (auxin_initial / (auxin_initial + self.circ_mod.k_auxin_pin)) - (
            self.circ_mod.kd_pinu * self.circ_mod.pin
        )
        calculated_pin = self.circ_mod.calculate_pin(auxin_initial, arr_initial)
        self.assertAlmostEqual(calculated_pin, expected_pin, places=5)

    def test_calculate_membrane_pin(self):
        pin_initial = 0.1
        pind_initial = 0.2
        direction = "lateral"
        pin_weight = 0.3
        memfrac = 0.4
        expected_membrane_pin = pin_weight * pin_initial - (self.circ_mod.kd_pinloc * pind_initial)
        calculated_membrane_pin = self.circ_mod.calculate_membrane_pin(
            pin_initial, pind_initial, direction, pin_weight
        )
        self.assertAlmostEqual(calculated_membrane_pin, expected_membrane_pin, places=5)

    def test_calculate_neighbor_memfrac(self):
        neighbor_mock = MagicMock()
        neighbor_mock.get_c_id.return_value = 2
        self.circ_mod.cell.quad_perimeter.get_perimeter_len.return_value = 100.0
        with unittest.mock.patch(
            "src.agent.circ_module.get_len_perimeter_in_common", return_value=25.0
        ) as mock_get_len_perimeter_in_common:
            memfrac = self.circ_mod.calculate_neighbor_memfrac(neighbor_mock)
            mock_get_len_perimeter_in_common.assert_called_once_with(
                self.circ_mod.cell, neighbor_mock
            )
            expected_memfrac = 25.0 / 100.0
            self.assertAlmostEqual(memfrac, expected_memfrac, places=6)

    def test_get_aux_exchange_across_membrane(self):
        auxlax = 0.3
        pindi = 0.4
        neighbors = [self.neighbor_mock]

        with unittest.mock.patch.object(
            self.circ_mod, "calculate_neighbor_memfrac", return_value=0.2
        ):
            expected_auxin_influx = (0.5 * 0.2) * (auxlax * 0.2) * self.circ_mod.k_al
            expected_pin_activity = pindi * self.circ_mod.k_pin
            expected_accessible_auxin = self.circ_mod.auxin * 0.2
            expected_auxin_efflux = expected_accessible_auxin * expected_pin_activity
            expected_neighbor_aux_exchange = round_to_sf(
                expected_auxin_influx - expected_auxin_efflux, 5
            )
            aux_exchange = self.circ_mod.get_aux_exchange_across_membrane(auxlax, pindi, neighbors)
            self.assertIn(self.neighbor_mock, aux_exchange)
            self.assertAlmostEqual(
                aux_exchange[self.neighbor_mock], expected_neighbor_aux_exchange, places=5
            )

    def test_calculate_delta_auxin(self):
        syn_deg_auxin = 0.5
        neighbors_auxin = [{self.neighbor_mock: 0.1}, {self.neighbor_mock: -0.05}]
        expected_total_auxin = syn_deg_auxin + 0.1 + (-0.05)
        calculated_total_auxin = self.circ_mod.calculate_delta_auxin(syn_deg_auxin, neighbors_auxin)
        self.assertAlmostEqual(calculated_total_auxin, expected_total_auxin, places=5)

    def test_update_arr_hist(self):
        initial_arr_hist = [0.1, 0.2, 0.3]
        self.circ_mod.arr = 0.4
        self.circ_mod.arr_hist = initial_arr_hist.copy()
        self.circ_mod.update_arr_hist()
        expected_arr_hist = [0.2, 0.3, 0.4]
        self.assertEqual(self.circ_mod.arr_hist, expected_arr_hist)

    def test_update_circ_contents(self):
        soln = np.array(
            [
                [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
                [0.1, 0.21, 0.31, 0.41, 0.51, 0.61, 0.71, 0.81],
            ]
        )
        self.circ_mod.arr_hist = [0.1, 0.2, 0.3]
        self.circ_mod.arr = 0.15  # Current arr value to be updated to the history
        self.circ_mod.update_circ_contents(soln)
        self.assertAlmostEqual(self.circ_mod.arr, round_to_sf(0.21, 5))
        self.assertAlmostEqual(self.circ_mod.auxlax, round_to_sf(0.31, 5))
        self.assertAlmostEqual(self.circ_mod.pin, round_to_sf(0.41, 5) - 0.4)
        self.assertAlmostEqual(self.circ_mod.pina, round_to_sf(0.51, 5))
        self.assertAlmostEqual(self.circ_mod.pinb, round_to_sf(0.61, 5))
        self.assertAlmostEqual(self.circ_mod.pinl, round_to_sf(0.71, 5))
        self.assertAlmostEqual(self.circ_mod.pinm, round_to_sf(0.81, 5))
        expected_arr_hist = [0.2, 0.3, 0.21]  # Shift left and append the current arr value
        self.assertEqual(self.circ_mod.arr_hist, expected_arr_hist)

    def test_update_neighbor_auxin(self):
        neighbor_mock_1 = MagicMock()
        neighbor_mock_2 = MagicMock()
        neighbors_auxin = [{neighbor_mock_1: 0.1}, {neighbor_mock_2: -0.05}]
        self.circ_mod.update_neighbor_auxin(neighbors_auxin)
        self.circulator_mock.add_delta.assert_any_call(neighbor_mock_1, -0.1)
        self.circulator_mock.add_delta.assert_any_call(neighbor_mock_2, 0.05)

    def test_get_neighbors(self):
        neighbors = self.circ_mod.get_neighbors()

        self.assertEqual(neighbors[0], self.neighbors_a)
        self.assertEqual(neighbors[1], self.neighbors_b)
        self.assertEqual(neighbors[2], self.neighbors_l)
        self.assertEqual(neighbors[3], self.neighbors_m)
        self.cell_mock.get_a_neighbors.assert_called_once()
        self.cell_mock.get_b_neighbors.assert_called_once()
        self.cell_mock.get_l_neighbors.assert_called_once()
        self.cell_mock.get_m_neighbors.assert_called_once()

    def test_update_auxin(self):
        soln = np.array(
            [
                [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
                [0.1, 0.21, 0.31, 0.41, 0.51, 0.61, 0.71, 0.81],
            ]
        )
        self.circ_mod.auxin = 0.1
        self.circ_mod.auxlax = 0.3
        self.circ_mod.pina = 0.4
        self.circ_mod.pinb = 0.6
        self.circ_mod.pinl = 0.7
        self.circ_mod.pinm = 0.8

        # Mocking methods to return known values
        auxina_exchange = {self.neighbors_a[0]: 0.05}
        auxinb_exchange = {self.neighbors_b[0]: 0.1}
        auxinl_exchange = {self.neighbors_l[0]: -0.05}
        auxinm_exchange = {self.neighbors_m[0]: -0.1}

        self.circ_mod.get_aux_exchange_across_membrane = MagicMock(
            side_effect=[auxina_exchange, auxinb_exchange, auxinl_exchange, auxinm_exchange]
        )
        self.circ_mod.calculate_delta_auxin = MagicMock(return_value=0.2)
        self.circ_mod.update_neighbor_auxin = MagicMock()

        self.circ_mod.update_auxin(soln)

        # Verify that get_aux_exchange_across_membrane was called with correct parameters
        self.circ_mod.get_aux_exchange_across_membrane.assert_any_call(
            self.circ_mod.auxlax, self.circ_mod.pina, self.neighbors_a
        )
        self.circ_mod.get_aux_exchange_across_membrane.assert_any_call(
            self.circ_mod.auxlax, self.circ_mod.pinb, self.neighbors_b
        )
        self.circ_mod.get_aux_exchange_across_membrane.assert_any_call(
            self.circ_mod.auxlax, self.circ_mod.pinl, self.neighbors_l
        )
        self.circ_mod.get_aux_exchange_across_membrane.assert_any_call(
            self.circ_mod.auxlax, self.circ_mod.pinm, self.neighbors_m
        )

        # Verify calculate_delta_auxin was called with correct parameters
        auxin_synthesized_and_degraded_this_timestep = soln[1, 0] - self.circ_mod.auxin
        self.circ_mod.calculate_delta_auxin.assert_called_once_with(
            auxin_synthesized_and_degraded_this_timestep,
            [auxina_exchange, auxinb_exchange, auxinl_exchange, auxinm_exchange],
        )

        # Verify add_delta was called correctly for the current cell
        self.circulator_mock.add_delta.assert_any_call(self.cell_mock, round_to_sf(0.2, 5))

        # Verify update_neighbor_auxin was called with correct parameters
        self.circ_mod.update_neighbor_auxin.assert_called_once_with(
            [auxina_exchange, auxinb_exchange, auxinl_exchange, auxinm_exchange]
        )

    def test_get_auxin(self):
        self.assertEqual(self.circ_mod.get_auxin(), self.init_vals["auxin"])

    def test_get_arr(self):
        self.assertEqual(self.circ_mod.get_arr(), self.init_vals["arr"])

    def test_get_auxlax(self):
        self.assertEqual(self.circ_mod.get_auxlax(), self.init_vals["al"])

    def test_get_arr_hist(self):
        self.assertEqual(self.circ_mod.get_arr_hist(), self.init_vals["arr_hist"])

    def test_get_auxin_w(self):
        self.assertEqual(self.circ_mod.get_auxin_w(), self.init_vals["auxin_w"])

    def test_get_pin(self):
        self.assertEqual(self.circ_mod.get_pin(), self.init_vals["pin"])

    def test_get_apical_pin(self):
        self.assertEqual(self.circ_mod.get_apical_pin(), self.init_vals["pina"])

    def test_get_basal_pin(self):
        self.assertEqual(self.circ_mod.get_basal_pin(), self.init_vals["pinb"])

    def test_get_lateral_pin(self):
        self.assertEqual(self.circ_mod.get_lateral_pin(), self.init_vals["pinl"])

    def test_get_medial_pin(self):
        self.assertEqual(self.circ_mod.get_medial_pin(), self.init_vals["pinm"])

    def test_get_left_pin(self):
        if self.circ_mod.left == "medial":
            self.assertEqual(self.circ_mod.get_left_pin(), self.init_vals["pinm"])
        else:
            self.assertEqual(self.circ_mod.get_left_pin(), self.init_vals["pinl"])

    def test_get_right_pin(self):
        if self.circ_mod.right == "medial":
            self.assertEqual(self.circ_mod.get_right_pin(), self.init_vals["pinm"])
        else:
            self.assertEqual(self.circ_mod.get_right_pin(), self.init_vals["pinl"])

    def test_get_state(self):
        expected_state = {
            "auxin": self.init_vals["auxin"],
            "arr": self.init_vals["arr"],
            "al": self.init_vals["al"],
            "pin": self.init_vals["pin"],
            "pina": self.init_vals["pina"],
            "pinb": self.init_vals["pinb"],
            "pinl": self.init_vals["pinl"],
            "pinm": self.init_vals["pinm"],
            "k1": self.init_vals["k1"],
            "k2": self.init_vals["k2"],
            "k3": self.init_vals["k3"],
            "k4": self.init_vals["k4"],
            "k5": self.init_vals["k5"],
            "k6": self.init_vals["k6"],
            "ks_aux": self.init_vals["ks_aux"],
            "kd_aux": self.init_vals["kd_aux"],
            "ks_arr": self.init_vals["ks_arr"],
            "kd_arr": self.init_vals["kd_arr"],
            "ks_pinu": self.init_vals["ks_pinu"],
            "kd_pinu": self.init_vals["kd_pinu"],
            "kd_pinloc": self.init_vals["kd_pinloc"],
            "ks_auxlax": self.init_vals["ks_auxlax"],
            "kd_auxlax": self.init_vals["kd_auxlax"],
            "auxin_w": self.init_vals["auxin_w"],
            "arr_hist": self.init_vals["arr_hist"],
            "circ_mod": "indep_syn_deg",
        }
        self.assertEqual(self.circ_mod.get_state(), expected_state)

    def test_set_auxin(self):
        new_auxin = 0.5
        self.circ_mod.set_auxin(new_auxin)
        self.assertEqual(self.circ_mod.get_auxin(), new_auxin)

    def test_f(self):
        # Mock the methods that are called within `f`
        self.circ_mod.calculate_auxin = MagicMock(return_value=0.1)
        self.circ_mod.calculate_arr = MagicMock(return_value=0.2)
        self.circ_mod.calculate_auxlax = MagicMock(return_value=0.3)
        self.circ_mod.calculate_pin = MagicMock(return_value=0.4)
        self.circ_mod.calculate_membrane_pin = MagicMock(side_effect=[0.5, 0.6, 0.7, 0.8])

        # Test input values
        y = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
        t = 0.0

        # Call the `f` function
        result = self.circ_mod.f(y, t)

        # Expected values based on the mocks
        expected_result = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

        # Verify the results
        self.assertEqual(result, expected_result)

        # Verify that the dependent methods were called with correct arguments
        self.circ_mod.calculate_auxin.assert_called_once_with(0.1)
        self.circ_mod.calculate_arr.assert_called_once_with(0.2)
        self.circ_mod.calculate_auxlax.assert_called_once_with(0.1, 0.3)
        self.circ_mod.calculate_pin.assert_called_once_with(0.1, 0.2)
        self.circ_mod.calculate_membrane_pin.assert_any_call(
            0.4, 0.5, "a", cast(float, self.circ_mod.pin_weights.get("a"))
        )
        self.circ_mod.calculate_membrane_pin.assert_any_call(
            0.4, 0.6, "b", cast(float, self.circ_mod.pin_weights.get("b"))
        )
        self.circ_mod.calculate_membrane_pin.assert_any_call(
            0.4, 0.7, "l", cast(float, self.circ_mod.pin_weights.get("l"))
        )
        self.circ_mod.calculate_membrane_pin.assert_any_call(
            0.4, 0.8, "m", cast(float, self.circ_mod.pin_weights.get("m"))
        )

    @patch("src.agent.circ_module.odeint")
    def test_solve_equations(self, mock_odeint):
        # Mock the return value of odeint
        mock_solution = np.array(
            [
                [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
                [0.11, 0.21, 0.31, 0.41, 0.51, 0.61, 0.71, 0.81],
            ]
        )
        mock_odeint.return_value = mock_solution

        # Expected initial conditions and time array
        expected_y0 = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
        expected_t = np.linspace(0, 1.0, int(1.0 / 0.001) + 1)

        # Call the function
        result = self.circ_mod.solve_equations()

        # Verify the correct calls to odeint
        args, kwargs = mock_odeint.call_args

        # Check the function f and initial conditions
        self.assertEqual(args[0], self.circ_mod.f)
        np.testing.assert_array_equal(args[1], expected_y0)

        # Check the time array
        np.testing.assert_array_equal(args[2], expected_t)

        # Verify the result
        np.testing.assert_array_equal(result, mock_solution)

    @patch("src.agent.circ_module_indep_syn_deg.CirculateModuleIndSynDeg.update_auxin")
    @patch("src.agent.circ_module_indep_syn_deg.CirculateModuleIndSynDeg.solve_equations")
    @patch("src.agent.circ_module_indep_syn_deg.CirculateModuleIndSynDeg.update_circ_contents")
    def test_update(self, mock_update_circ_contents, mock_solve_equations, mock_update_auxin):
        # Mocking solve_equations to return a known solution
        mock_soln = np.array(
            [
                [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
                [0.11, 0.21, 0.31, 0.41, 0.51, 0.61, 0.71, 0.81],
            ]
        )
        mock_solve_equations.return_value = mock_soln

        # Mocking get_pin_weights to return a dictionary with weights summing to 1
        pin_weights_mock = {"a": 0.25, "b": 0.25, "l": 0.25, "m": 0.25}
        self.cell_mock.get_pin_weights.return_value = pin_weights_mock

        # Call the update method
        self.circ_mod.update()

        # Verify that get_pin_weights is called
        self.cell_mock.get_pin_weights.assert_called_once()

        # Verify that the pin weights sum to 1
        self.assertEqual(round_to_sf(sum(pin_weights_mock.values()), 2), 1.0)

        # Verify that solve_equations is called
        mock_solve_equations.assert_called_once()

        # Verify that update_auxin and update_circ_contents are called with the solution
        mock_update_auxin.assert_called_once_with(mock_soln)
        mock_update_circ_contents.assert_called_once_with(mock_soln)
