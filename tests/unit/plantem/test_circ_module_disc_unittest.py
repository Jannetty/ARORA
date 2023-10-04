import unittest

from src.plantem.loc.vertex.vertex import Vertex
from src.plantem.agent.circ_module_disc import BaseCirculateModuleDisc
from src.plantem.agent.cell import GrowingCell
from src.plantem.sim.simulation.sim import GrowingSim

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Starting Template"


class BaseCirculateModuleDiscTests(unittest.TestCase):
    """
    Tests BaseCirculateModuleDisc Class
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
        circ_module_disc = BaseCirculateModuleDisc(cell, make_init_vals())
        sim.setup()
        found_left, found_right = circ_module_disc.determine_left_right()
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
        circ_module_disc = cell.get_circ_mod()
        sim.setup()
        timestep = 1
        area = cell.quad_perimeter.get_area()
        expected_auxin = 0.004999925
        found_auxin = circ_module_disc.calculate_auxin(timestep, area)
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
            make_init_vals(),
            sim.get_next_cell_id(),
        )
        circ_module_disc = BaseCirculateModuleDisc(cell, make_init_vals())
        sim.setup()
        timestep = 1
        area = cell.quad_perimeter.get_area()
        expected_arr = 0.004545342045
        found_arr = circ_module_disc.calculate_arr(timestep, area)
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
            make_init_vals(),
            sim.get_next_cell_id(),
        )
        circ_module_disc = BaseCirculateModuleDisc(cell, make_init_vals())
        sim.setup()
        timestep = 1
        area = cell.quad_perimeter.get_area()
        expected_aux_lax = 0.003333220833
        found_aux_lax = circ_module_disc.calculate_aux_lax(timestep, area)
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
            make_init_vals(),
            sim.get_next_cell_id(),
        )
        circ_module_disc = cell.get_circ_mod()
        sim.setup()
        timestep = 1
        area = cell.quad_perimeter.get_area()
        init_vals = make_init_vals()
        expected_PIN = ((init_vals['k_s']
            * (1 / (init_vals['arr'] / init_vals['k4'] + 1))
            * (init_vals['auxin'] / (init_vals['auxin'] + init_vals['k3']))
        ) - init_vals['k_d'] * init_vals['pin'])* timestep
        found_PIN = circ_module_disc.calculate_pin(timestep, area)
        self.assertAlmostEqual(expected_PIN, found_PIN, places=5)

    def test_calculate_membrane_pin(self):
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
        circ_module_disc = BaseCirculateModuleDisc(cell, make_init_vals())
        sim.setup()
        timestep = 1
        area = cell.quad_perimeter.get_area()
        # test apical
        expected_neighbor_PIN = 0.2499999813
        found_neighbor_PIN = circ_module_disc.calculate_membrane_pin(0.5, timestep, area)
        self.assertAlmostEqual(expected_neighbor_PIN, found_neighbor_PIN, places=5)

    def test_calculate_neighbor_memfrac(self):
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
        circ_module_disc = BaseCirculateModuleDisc(cell, make_init_vals())
        # test apical nerighbor
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
        found_memfrac = circ_module_disc.calculate_neighbor_memfrac(neighbora, "a")
        expected_memfrac = 0.25
        self.assertEqual(expected_memfrac, found_memfrac)

    def test_get_neighbors(self):
        sim = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, 1, 400, False)
        v1 = Vertex(100,100)
        v2 = Vertex(100,300)
        v3 = Vertex(300,300)
        v4 = Vertex(300,100)
        v5 = Vertex(100,600)
        v6 = Vertex(300,600)
        v7 = Vertex(600,300)
        v8 = Vertex(600,100)
        curr_cell = GrowingCell(
            sim,
            [v1,v2,v3,v4],
            make_init_vals(),
            sim.get_next_cell_id(),
        )
        circ_module_disc_cont = curr_cell.get_circ_mod()
        neighbora = GrowingCell(
            sim,
            [v2,v5,v6,v3],
            make_init_vals(),
            sim.get_next_cell_id(),
        )
        neighborm = GrowingCell(
            sim,
            [v4,v3,v7,v8],
            make_init_vals(),
            sim.get_next_cell_id(),
        )
        curr_cell.add_neighbor(neighbora)
        curr_cell.add_neighbor(neighborm)
        sim.setup()
        found_neighbors = ([neighbora], [], [], [neighborm])
        expected_neighbors = circ_module_disc_cont.get_neighbors()
        self.assertEqual(expected_neighbors, found_neighbors)

    def test_get_neighbor_auxin(self):
        timestep = 1
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
        circ_module_disc = cell.get_circ_mod()
        area = cell.quad_perimeter.get_area()
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
        neighbor_list = [neighbora]
        pin_dir = .5
        found_neighbor_auxin = circ_module_disc.get_neighbor_auxin_exchange(
            pin_dir, neighbor_list, "a", timestep, area
        )

        memfrac = circ_module_disc.calculate_neighbor_memfrac(neighbora, 'a')
        # TODO: Make k_al and k_pin  parameters from input
        k_al = 1
        k_pin = 1
        neighbor_aux = neighbora.get_circ_mod().get_auxin()
        neighbor_aux = (
            neighbor_aux * memfrac * circ_module_disc.al * k_al - circ_module_disc.auxin * pin_dir * (1 / area) * k_pin
        ) * timestep

        expected_neighbor_auxin = {neighbora: neighbor_aux}
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
            make_init_vals(),
            sim.get_next_cell_id(),
        )
        circ_module_disc = BaseCirculateModuleDisc(cell, make_init_vals())
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
        neighbors_auxin = [{neighbora: 0.00374998125}]
        expected_delta_auxin = 0.00374998125 + 0.00374998125
        found_delta_auxin = circ_module_disc.calculate_delta_auxin(0.00374998125, neighbors_auxin)
        self.assertAlmostEqual(expected_delta_auxin, found_delta_auxin, places=5)

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
        circ_module_disc = BaseCirculateModuleDisc(curr_cell, make_init_vals())
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
        circ_module_disc.update_neighbor_auxin(sim_circ, neighbors_auxin)
        expected = curr_cell.get_sim().get_circulator().delta_auxins
        found = {neighbora: -0.00374998125, neighborm: -0.0037499925}
        self.assertEqual(expected, found)

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
        circ_module_disc_disc = BaseCirculateModuleDisc(cell, make_init_vals())
        sim.setup()
        expected_arr_hist = [0.2, 0.3, 3]
        circ_module_disc_disc.update_arr_hist()
        found_arr_hist = circ_module_disc_disc.arr_hist
        self.assertEqual(expected_arr_hist, found_arr_hist)

    def test_update(self):
        sim = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, 1, 400, False)
        v1 = Vertex(100,100)
        v2 = Vertex(100,300)
        v3 = Vertex(300,300)
        v4 = Vertex(300,100)
        v5 = Vertex(100,600)
        v6 = Vertex(300,600)
        v7 = Vertex(600,300)
        v8 = Vertex(600,100)
        curr_cell = GrowingCell(
            sim,
            [v1,v2,v3,v4],
            make_init_vals(),
            sim.get_next_cell_id(),
        )
        circ_module_disc = curr_cell.get_circ_mod()
        neighbora = GrowingCell(
            sim,
            [v2,v5,v6,v3],
            make_init_vals(),
            sim.get_next_cell_id(),
        )
        neighborm = GrowingCell(
            sim,
            [v4,v3,v7,v8],
            make_init_vals(),
            sim.get_next_cell_id(),
        )
        curr_cell.add_neighbor(neighbora)
        curr_cell.add_neighbor(neighborm)
        sim.setup()
        circ_module_disc.update()
        # test circulator
        found_circulator = curr_cell.get_sim().get_circulator().delta_auxins

        timestep = 1
        area = curr_cell.quad_perimeter.get_area()
        pina = circ_module_disc.calculate_membrane_pin(circ_module_disc.pina, timestep, area)
        pinm = circ_module_disc.calculate_membrane_pin(circ_module_disc.pinm, timestep, area)
        syn_deg_auxin = circ_module_disc.calculate_auxin(timestep, area)

        auxina = circ_module_disc.get_neighbor_auxin_exchange(pina, [neighbora], "a", timestep, area)
        auxinm = circ_module_disc.get_neighbor_auxin_exchange(pinm, [neighborm], "m", timestep, area)

        expected_circulator = {
            curr_cell: syn_deg_auxin + auxina[neighbora] + auxinm[neighborm],
            neighbora: -auxina[neighbora],
            neighborm: -auxinm[neighborm],
        }
        for key in expected_circulator:
            self.assertAlmostEqual(expected_circulator[key], found_circulator[key], places=5)
        # test arr_hist
        found_arr_hist = circ_module_disc.arr_hist
        expected_arr_hist = [0.2, 0.3, circ_module_disc.arr]
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
            sim.get_next_cell_id(),
        )
        circ_module_disc = BaseCirculateModuleDisc(cell, make_init_vals())
        sim.setup()
        found = circ_module_disc.get_auxin()
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
        circ_module_cont = BaseCirculateModuleDisc(cell, make_init_vals())
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
        circ_module_cont = BaseCirculateModuleDisc(cell, make_init_vals())
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
        circ_module_cont = BaseCirculateModuleDisc(cell, make_init_vals())
        sim.setup()
        found = circ_module_cont.get_pin()
        expected = 1
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
        circ_module_disc = BaseCirculateModuleDisc(cell, make_init_vals())
        sim.setup()
        found = circ_module_disc.get_left_pin()
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
        circ_module_disc = BaseCirculateModuleDisc(cell, make_init_vals())
        sim.setup()
        found = circ_module_disc.get_right_pin()
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
        "k1": 1,
        "k2": 1,
        "k3": 1,
        "k4": 1,
        "k_s": 0.005,
        "k_d": 0.0015,
        "arr_hist": [0.1, 0.2, 0.3],
        "growing": True,
        "circ_mod": 'disc'
    }
    return init_vals
