import unittest

from scipy.integrate import odeint
import numpy as np
from src.plantem.loc.vertex.vertex import Vertex
from src.plantem.agent.cell import GrowingCell
from src.plantem.sim.simulation.sim import GrowingSim

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Starting Template"

KS = 0.005
KD = 0.0015
K1 = 1  # k_arr_arr
K2 = 1  # k_auxin_auxlax
K3 = 1  # k_arr_pin
K4 = 1  # k_auxin_pin
ARR_HIST = [0.1, 0.2, 0.3]


class BaseCirculateModuleContTests(unittest.TestCase):
    """
    Tests BaseCirculateModuleCont Class
    """

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
            make_init_vals(),
            sim.get_next_cell_id(),
        )
        circ_module = cell.get_circ_mod()
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
            make_init_vals(),
            sim.get_next_cell_id(),
        )
        circ_module_cont = cell.get_circ_mod()
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
            sim.get_next_cell_id(),
        )
        circ_module_cont = cell.get_circ_mod()
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
            sim.get_next_cell_id(),
        )
        circ_module_cont = cell.get_circ_mod()
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
            sim.get_next_cell_id(),
        )
        circ_module_cont = cell.get_circ_mod()
        sim.setup()
        expected_pin = 8.33333333 * 0.0001 - 0.0015 * 1
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
            sim.get_next_cell_id(),
        )
        circ_module_cont = cell.get_circ_mod()
        sim.setup()
        area = cell.quad_perimeter.get_area()
        # test apical neighbor
        expected_pin = 0.2499999813
        found_pin = circ_module_cont.calculate_neighbor_pin(1, 0.5, 1, area)
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
            sim.get_next_cell_id(),
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
            sim.get_next_cell_id(),
        )
        circ_module_cont = cell.get_circ_mod()
        sim.setup()
        # test apical neighbor
        expected_f = 0.25
        found_f = circ_module_cont.calculate_memfrac(neighbora, "a")
        self.assertAlmostEqual(expected_f, found_f, places=5)

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
            sim.get_next_cell_id(),
        )
        circ_module_cont = cell.get_circ_mod()
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
            sim.get_next_cell_id(),
        )
        sim.setup()
        area = cell.quad_perimeter.get_area()
        neighbor_list = [neighbora]
        expected_neighbor_auxin = circ_module_cont.get_neighbor_auxin(
            3, 1, neighbor_list, "a", area
        )
        found_neighbor_auxin = {neighbora: 0.00374998125}
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
            sim.get_next_cell_id(),
        )
        circ_module_cont = cell.get_circ_mod()
        neighbora = GrowingCell(
            sim,
            [
                Vertex(100.0, 300.0),
                Vertex(100.0, 600.0),
                Vertex(300.0, 600.0),
                Vertex(300.0, 300.0),
            ],
            make_init_vals(),
            sim.get_next_cell_id(),
        )
        sim.setup()
        neighbors_auxin = [{neighbora: 0.004999925}]
        expected_delta_auxin = 0.004999925 + 0.004999925
        found_delta_auxin = circ_module_cont.calculate_delta_auxin(0.004999925, neighbors_auxin)
        self.assertAlmostEqual(expected_delta_auxin, found_delta_auxin, places=5)

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
            sim.get_next_cell_id(),
        )
        circ_module_cont = cell.get_circ_mod()
        sim.setup()
        y0 = [
            circ_module_cont.auxin,
            circ_module_cont.arr,
            circ_module_cont.al,
            circ_module_cont.pin,
            circ_module_cont.pina,
            circ_module_cont.pinb,
            circ_module_cont.pinl,
            circ_module_cont.pinm
        ]
        t = np.array([0, 1])
        expected_soln = odeint(f, y0, t)
        found_soln = circ_module_cont.get_solution()
        for i in range(8):
            self.assertAlmostEqual(expected_soln[1, i], found_soln[1, i], places=5)

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
            sim.get_next_cell_id(),
        )
        circ_module_cont = cell.get_circ_mod()
        sim.setup()
        expected_arr_hist = [0.2, 0.3, 3]
        circ_module_cont.update_arr_hist()
        found_arr_hist = circ_module_cont.arr_hist
        self.assertEqual(expected_arr_hist, found_arr_hist)

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
            sim.get_next_cell_id(),
        )
        circ_module_cont = cell.get_circ_mod()
        sim.setup()
        y0 = [
            circ_module_cont.auxin,
            circ_module_cont.arr,
            circ_module_cont.al,
            circ_module_cont.pin,
            circ_module_cont.pina,
            circ_module_cont.pinb,
            circ_module_cont.pinl,
            circ_module_cont.pinm,
        ]
        t = np.array([0, 1])
        soln = odeint(f, y0, t)
        circ_module_cont.update_circ_contents(soln)
        # test arr
        expected_arr = soln[1, 1]
        found_arr = circ_module_cont.arr
        self.assertAlmostEqual(expected_arr, found_arr, places=5)
        # test al
        expected_al = soln[1, 2]
        found_al = circ_module_cont.al
        self.assertAlmostEqual(expected_al, found_al, places=5)
        # test pina
        expected_pina = soln[1, 4]
        found_pina = circ_module_cont.pina
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
            sim.get_next_cell_id(),
        )
        circ_module_cont = curr_cell.get_circ_mod()
        neighbora = GrowingCell(
            sim,
            [
                Vertex(100.0, 300.0),
                Vertex(100.0, 600.0),
                Vertex(300.0, 600.0),
                Vertex(300.0, 300.0),
            ],
            make_init_vals(),
            sim.get_next_cell_id(),
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
            sim.get_next_cell_id(),
        )
        sim.setup()
        neighbors_auxin = [{neighbora: 0.00374998125}, {neighborm: 0.0037499925}]
        sim_circ = curr_cell.get_sim().get_circulator()
        circ_module_cont.update_neighbor_auxin(sim_circ, neighbors_auxin)
        expected = curr_cell.get_sim().get_circulator().delta_auxins
        found = {neighbora: -0.00374998125, neighborm: -0.0037499925}
        self.assertEqual(expected, found)

    def test_get_neighbors(self):
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
            sim.get_next_cell_id(),
        )
        circ_module_cont = curr_cell.get_circ_mod()
        neighbora = GrowingCell(
            sim,
            [
                Vertex(100.0, 300.0),
                Vertex(100.0, 600.0),
                Vertex(300.0, 600.0),
                Vertex(300.0, 300.0),
            ],
            make_init_vals(),
            sim.get_next_cell_id(),
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
            sim.get_next_cell_id(),
        )
        curr_cell.add_neighbor(neighbora)
        curr_cell.add_neighbor(neighborm)
        sim.setup()
        found_neighbors = ([neighbora], [], [], [neighborm])
        expected_neighbors = circ_module_cont.get_neighbors()
        self.assertEqual(expected_neighbors, found_neighbors)

    def test_update_auxin(self):
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
            sim.get_next_cell_id(),
        )
        circ_module_cont = curr_cell.get_circ_mod()
        neighbora = GrowingCell(
            sim,
            [
                Vertex(100.0, 300.0),
                Vertex(100.0, 600.0),
                Vertex(300.0, 600.0),
                Vertex(300.0, 300.0),
            ],
            make_init_vals(),
            sim.get_next_cell_id(),
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
            sim.get_next_cell_id(),
        )
        curr_cell.add_neighbor(neighbora)
        curr_cell.add_neighbor(neighborm)
        sim.setup()
        y0 = [
            circ_module_cont.auxin,
            circ_module_cont.arr,
            circ_module_cont.al,
            circ_module_cont.pin,
            circ_module_cont.pina,
            circ_module_cont.pinb,
            circ_module_cont.pinl,
            circ_module_cont.pinm
        ]
        t = np.array([0, 1])
        soln = odeint(f, y0, t)
        circ_module_cont.update_auxin(soln)
        expected = curr_cell.get_sim().get_circulator().delta_auxins
        found = {
            curr_cell: (soln[1, 0] - 2) + 0.00374998125 + 0.0037499925,
            neighbora: -0.00374998125,
            neighborm: -0.0037499925,
        }
        for key in expected:
            self.assertAlmostEqual(expected[key], found[key], places=15)

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
            sim.get_next_cell_id(),
        )
        circ_module_cont = cell.get_circ_mod()
        sim.setup()
        found = circ_module_cont.get_auxin()
        expected = 2
        self.assertEqual(expected, found)

    def test_get_arr(self):
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
            sim.get_next_cell_id(),
        )
        circ_module_cont = cell.get_circ_mod()
        sim.setup()
        found = circ_module_cont.get_arr()
        expected = 3
        self.assertEqual(expected, found)

    def test_get_al(self):
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
            sim.get_next_cell_id(),
        )
        circ_module_cont = cell.get_circ_mod()
        sim.setup()
        found = circ_module_cont.get_al()
        expected = 3
        self.assertEqual(expected, found)

    def test_get_pin(self):
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
            sim.get_next_cell_id(),
        )
        circ_module_cont = cell.get_circ_mod()
        sim.setup()
        found = circ_module_cont.get_pin()
        expected = 1
        self.assertEqual(expected, found)

    def test_get_apical_pin(self):
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
            sim.get_next_cell_id(),
        )
        circ_module_cont = cell.get_circ_mod()
        sim.setup()
        found = circ_module_cont.get_apical_pin()
        expected = 0.5
        self.assertEqual(expected, found)

    def test_get_left_pin(self):
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
            sim.get_next_cell_id(),
        )
        circ_module_cont = cell.get_circ_mod()
        sim.setup()
        found = circ_module_cont.get_left_pin()
        expected = 0.4
        self.assertEqual(expected, found)

    def test_get_right_pin(self):
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
            sim.get_next_cell_id(),
        )
        circ_module_cont = cell.get_circ_mod()
        sim.setup()
        found = circ_module_cont.get_right_pin()
        expected = 0.2
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
        "w_pina": 1,
        "w_pinb": 1,
        "w_pinl": 1,
        "w_pinm": 1,
        "k1": 1,
        "k2": 1,
        "k3": 1,
        "k4": 1,
        "k_s": 0.005,
        "k_d": 0.0015,
        "k_al": 1,
        "k_pin": 1,
        "arr_hist": [0.1, 0.2, 0.3],
        "growing": 0
    }
    return init_vals


def f(y, t) -> list:
    """
    Setup the model functions
    """
    area = 40000
    w_pina = 1
    w_pinb = 1
    w_pinl = 1
    w_pinm = 1

    # setup species
    auxini = y[0]
    arri = y[1]
    ali = y[2]
    pini = y[3]
    pinai = y[4]
    pinbi = y[5]
    pinli = y[6]
    pinmi = y[7]

    # the model equations
    # auxin
    f0 = KS - KD * auxini * (1 / area)
    # arr
    f1 = KS * 1 / (ARR_HIST[0] / K1 + 1) - KD * arri * (1 / area)
    # al
    f2 = KS * (auxini / (auxini + K2)) - KD * ali * (1 / area)
    # pin
    f3 = KS * (1 / (arri / K3 + 1)) * (auxini / (auxini + K4)) - KD * pini
    # neighbor pin
    f4 = 0.25 * pini - w_pina * KD * pinai * (1 / area)
    f5 = 0.25 * pini - w_pinb * KD * pinbi * (1 / area)
    f6 = 0.25 * pini - w_pinl * KD * pinli * (1 / area)
    f7 = 0.25 * pini - w_pinm * KD * pinmi * (1 / area)

    return [f0, f1, f2, f3, f4, f5, f6, f7]
