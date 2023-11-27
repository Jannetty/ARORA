import unittest
import pandas

from src.plantem.sim.input.input import Input
from src.plantem.sim.simulation.sim import GrowingSim
from src.plantem.agent.cell import GrowingCell
from src.plantem.loc.vertex.vertex import Vertex
from src.plantem.agent.circ_module_cont import BaseCirculateModuleCont
from src.plantem.agent.circ_module_disc import BaseCirculateModuleDisc

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Starting Template"


class TestInput(unittest.TestCase):
    """
    Tests Input Class
    """

    def test_get_vertex(self):
        sim = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, 1, 400, False)
        input = Input(
            "tests/unit/plantem/test_csv/init_vals.csv",
            "tests/unit/plantem/test_csv/vertex.csv",
            sim,
        )
        expected_vertex_list = {
            "0": [10, 300],
            "1": [10, 330],
            "2": [30, 300],
            "3": [30, 330],
            "4": [10, 360],
            "5": [30, 360],
        }
        found_vertex_input = input.get_vertex()
        for each in found_vertex_input:
            found_vertex_list = found_vertex_input[each].get_xy()
            self.assertEqual(expected_vertex_list[each], found_vertex_list)

    def test_get_init_vals(self):
        sim = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, 1, 400, False)
        input = Input(
            "tests/unit/plantem/test_csv/init_vals.csv",
            "tests/unit/plantem/test_csv/vertex.csv",
            sim,
        )
        expected = {
            "c0": {
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
                "k5": 1,
                "k6": 1,
                "k_s": 0.005,
                "k_d": 0.0015,
                "arr_hist": [3, 3, 3],
                "growing": False,
                "circ_mod": "cont",
                "vertices": [0, 1, 2, 3],
                "neighbors": ["c1"],
            },
            "c1": {
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
                "k5": 1,
                "k6": 1,
                "k_s": 0.005,
                "k_d": 0.0015,
                "arr_hist": [3, 3, 3, 3],
                "growing": False,
                "circ_mod": "cont",
                "vertices": [1, 3, 4, 5],
                "neighbors": ["c0"],
            },
        }
        found = input.get_init_vals()
        for cell in expected:
            for val in expected[cell]:
                self.assertEqual(expected[cell][val], found[cell][val])

    def test_set_arr_hist(self):
        sim = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, 1, 400, False)
        input = Input(
            "tests/unit/plantem/test_csv/init_vals.csv",
            "tests/unit/plantem/test_csv/vertex.csv",
            sim,
        )
        dict = {
            "c0": {
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
                "k5": 1,
                "k6": 1,
                "k_s": 0.005,
                "k_d": 0.0015,
                "arr_hist": [3, 3, 3],
                "growing": False,
                "circ_mod": "cont",
                "vertices": [0, 1, 2, 3],
                "neighbors": ["c1"],
            },
            "c1": {
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
                "k5": 1,
                "k6": 1,
                "k_s": 0.005,
                "k_d": 0.0015,
                "arr_hist": [3, 3, 3, 3],
                "growing": False,
                "circ_mod": "cont",
                "vertices": [1, 3, 4, 5],
                "neighbors": ["c0"],
            },
        }
        expected = {
            "c0": {
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
                "k5": 1,
                "k6": 1,
                "k_s": 0.005,
                "k_d": 0.0015,
                "arr_hist": [3, 3, 3],
                "growing": False,
                "circ_mod": "cont",
                "vertices": [0, 1, 2, 3],
                "neighbors": ["c1"],
            },
            "c1": {
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
                "k5": 1,
                "k6": 1,
                "k_s": 0.005,
                "k_d": 0.0015,
                "arr_hist": [3, 3, 3, 3],
                "growing": False,
                "circ_mod": "cont",
                "vertices": [1, 3, 4, 5],
                "neighbors": ["c0"],
            },
        }
        input.set_arr_hist(dict)
        found = dict
        for cell in expected:
            for val in expected[cell]:
                self.assertEqual(expected[cell][val], found[cell][val])

    def test_get_vertex_assignment(self):
        sim = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, 1, 400, False)
        input = Input(
            "tests/unit/plantem/test_csv/init_vals.csv",
            "tests/unit/plantem/test_csv/vertex.csv",
            sim,
        )
        expected = {"c0": ["0", "1", "2", "3"], "c1": ["1", "3", "4", "5"]}
        found = input.get_vertex_assignment()
        for cell in expected:
            for i in range(len(expected[cell])):
                self.assertEqual(expected[cell][i], found[cell][i])

    def test_get_neighbors_assignment(self):
        sim = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, 1, 400, False)
        input = Input(
            "tests/unit/plantem/test_csv/init_vals.csv",
            "tests/unit/plantem/test_csv/vertex.csv",
            sim,
        )
        expected = {"c0": ["c1"], "c1": ["c0"]}
        found = input.get_neighbors_assignment()
        for cell in expected:
            for i in range(len(expected[cell])):
                self.assertEqual(expected[cell][i], found[cell][i])

    def test_group_vertices(self):
        sim = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, 1, 400, False)
        input = Input(
            "tests/unit/plantem/test_csv/init_vals.csv",
            "tests/unit/plantem/test_csv/vertex.csv",
            sim,
        )
        found_vertices = input.get_vertex()
        found_vertex_assignment = input.get_vertex_assignment()
        expected_vertex_cell0 = [[10, 300], [10, 330], [30, 300], [30, 330]]
        expected_vertex_cell1 = [[10, 330], [30, 330], [10, 360], [30, 360]]
        found = input.group_vertices(found_vertices, found_vertex_assignment)
        # test cell0
        for i in range(len(expected_vertex_cell0)):
            self.assertEqual(expected_vertex_cell0[i], found["c0"][i].get_xy())
        # test cell1
        for i in range(len(expected_vertex_cell1)):
            self.assertEqual(expected_vertex_cell1[i], found["c1"][i].get_xy())

    def test_create_cells(self):
        sim = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, 1, 400, False)
        input = Input(
            "tests/unit/plantem/test_csv/init_vals.csv",
            "tests/unit/plantem/test_csv/vertex.csv",
            sim,
        )
        v0 = Vertex(10, 300)
        v1 = Vertex(10, 330)
        v2 = Vertex(30, 300)
        v3 = Vertex(30, 330)
        v4 = Vertex(10, 360)
        v5 = Vertex(30, 360)
        cell_dict = input.create_cells()
        expected_cell0 = GrowingCell(sim, [v0, v1, v2, v3], make_init_vals(), 0)
        expected_cell1 = GrowingCell(sim, [v1, v3, v4, v5], make_init_vals(), 1)
        found_cell0 = cell_dict["c0"]
        # test cell0
        self.assertEqual(expected_cell0.get_id(), found_cell0.get_id())
        self.assertEqual(
            expected_cell0.get_quad_perimeter().get_area(),
            found_cell0.get_quad_perimeter().get_area(),
        )
        self.assertEqual(
            expected_cell0.get_circ_mod().get_auxin(), found_cell0.get_circ_mod().get_auxin()
        )
        self.assertEqual(
            expected_cell0.get_circ_mod().get_left_pin(), found_cell0.get_circ_mod().get_left_pin()
        )
        # test cell1
        found_cell1 = cell_dict["c1"]
        self.assertEqual(expected_cell1.get_id(), found_cell1.get_id())
        self.assertEqual(
            expected_cell1.get_quad_perimeter().get_area(),
            found_cell1.get_quad_perimeter().get_area(),
        )

        # check that cell0 is nongrowing and has continuous circulator
        self.assertEqual(found_cell0.growing, False)
        self.assertTrue(isinstance(found_cell0.get_circ_mod(), BaseCirculateModuleCont))

        # check that cell1 is nongrowing and has discrete circulator
        self.assertEqual(found_cell1.growing, False)
        self.assertTrue(isinstance(found_cell1.get_circ_mod(), BaseCirculateModuleCont))

    def test_get_neighbors(self):
        sim = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, 1, 400, False)
        input = Input(
            "tests/unit/plantem/test_csv/init_vals.csv",
            "tests/unit/plantem/test_csv/vertex.csv",
            sim,
        )
        v0 = Vertex(10, 300)
        v1 = Vertex(10, 330)
        v2 = Vertex(30, 300)
        v3 = Vertex(30, 330)
        v4 = Vertex(10, 360)
        v5 = Vertex(30, 360)
        cell_dict = input.create_cells()
        expected_cell0 = GrowingCell(sim, [v0, v1, v2, v3], make_init_vals(), 0)
        expected_cell1 = GrowingCell(sim, [v1, v3, v4, v5], make_init_vals(), 1)
        found_neighbors_dict = input.get_neighbors(cell_dict)
        found_cell0_neighbors = found_neighbors_dict["c0"]
        found_cell1_neighbors = found_neighbors_dict["c1"]
        expected_cell0_neighbors = [expected_cell1]
        expected_cell1_neighbors = [expected_cell0]
        # check cell0
        for cell in range(len(expected_cell0_neighbors)):
            self.assertEqual(
                expected_cell0_neighbors[cell].get_id(), found_cell0_neighbors[cell].get_id()
            )
        # check cell1
        for cell in range(len(expected_cell1_neighbors)):
            self.assertEqual(
                expected_cell1_neighbors[cell].get_id(), found_cell1_neighbors[cell].get_id()
            )

    def test_update_neighbors(self):
        sim = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, 1, 400, False)
        input = Input(
            "tests/unit/plantem/test_csv/init_vals.csv",
            "tests/unit/plantem/test_csv/vertex.csv",
            sim,
        )
        v0 = Vertex(10, 300)
        v1 = Vertex(10, 330)
        v2 = Vertex(30, 300)
        v3 = Vertex(30, 330)
        v4 = Vertex(10, 360)
        v5 = Vertex(30, 360)
        cell_dict = input.create_cells()
        expected_cell0 = GrowingCell(sim, [v0, v1, v2, v3], make_init_vals(), 0)
        expected_cell1 = GrowingCell(sim, [v1, v3, v4, v5], make_init_vals(), 1)
        expected_cell0.add_neighbor(expected_cell1)
        expected_cell1.add_neighbor(expected_cell0)
        neighbors = input.get_neighbors(cell_dict)
        input.update_neighbors(neighbors, cell_dict)
        # test cell0
        for i in range(len(expected_cell0.get_a_neighbors())):
            found = neighbors["c0"][i]
            expected = expected_cell0.get_a_neighbors()[i]
            self.assertEqual(expected.get_id(), found.get_id())
        # test cell1
        for i in range(len(expected_cell1.get_b_neighbors())):
            found = neighbors["c1"][i]
            expected = expected_cell1.get_b_neighbors()[i]
            self.assertEqual(expected.get_id(), found.get_id())

    def test_input(self):
        sim = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, 1, 400, False)
        sim2 = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, 1, 400, False)
        input = Input(
            "tests/unit/plantem/test_csv/init_vals.csv",
            "tests/unit/plantem/test_csv/vertex.csv",
            sim,
        )
        v0 = Vertex(10, 300)
        v1 = Vertex(10, 330)
        v2 = Vertex(30, 300)
        v3 = Vertex(30, 330)
        v4 = Vertex(10, 360)
        v5 = Vertex(30, 360)
        input.make_cells_from_input_files()
        found_cell_list = sim.get_cell_list()
        expected_cell0 = GrowingCell(sim2, [v0, v1, v2, v3], make_init_vals(), 0)
        expected_cell1 = GrowingCell(sim2, [v1, v3, v4, v5], make_init_vals(), 1)
        expected_cell_list = sim2.get_cell_list()
        expected_cell_list.append(expected_cell0)
        expected_cell_list.append(expected_cell1)
        for i in range(len(expected_cell_list)):
            self.assertEqual(expected_cell_list[i].get_id(), found_cell_list[i].get_id())
            self.assertEqual(
                expected_cell_list[i].get_quad_perimeter().get_area(),
                found_cell_list[i].get_quad_perimeter().get_area(),
            )
            self.assertEqual(
                expected_cell_list[i].get_circ_mod().get_auxin(),
                found_cell_list[i].get_circ_mod().get_auxin(),
            )

    def test_replace_default_to_gparam(self):
        gparam_file = "src/plantem/sim/input/default_input_gparam.csv"
        full_gparam_df = pandas.read_csv(gparam_file)
        for index, row in full_gparam_df.iterrows():
            this_sim_gparam_series = row
            this_sim = GrowingSim(
                SCREEN_WIDTH,
                SCREEN_HEIGHT,
                SCREEN_TITLE,
                1,
                400,
                False,
                cell_val_file="tests/unit/plantem/test_csv/init_vals.csv",
                v_file="tests/unit/plantem/test_csv/vertex.csv",
            )
            # check to make sure that cells have gparams instead of cell_val_file params
            # this_input = Input(
            #    "tests/unit/plantem/test_csv/init_vals.csv",
            #    "tests/unit/plantem/test_csv/vertex.csv",
            #    this_sim
            # )
            this_input = this_sim.input
            this_input.replace_default_to_gparam(this_sim_gparam_series)
            for _, row_df in this_input.init_vals_input.iterrows():
                for index_s, value in this_sim_gparam_series.items():
                    if index_s != "tau":
                        self.assertEqual(row_df[index_s], value)
                    else:
                        self.assertEqual(len(row_df["arr_hist"]), value)


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
        "k5": 1,
        "k6": 1,
        "k_s": 0.005,
        "k_d": 0.0015,
        "k_al": 1,
        "k_pin": 1,
        "arr_hist": [0.1, 0.2, 0.3],
        "growing": False,
        "circ_mod": "cont",
    }
    return init_vals
