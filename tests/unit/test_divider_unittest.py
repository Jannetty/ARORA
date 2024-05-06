import os
import platform

if platform.system() == "Linux":
    os.environ["ARCADE_HEADLESS"] = "True"
import unittest
from src.sim.divider.divider import Divider
from src.agent.cell import Cell
from src.sim.simulation.sim import GrowingSim
from src.loc.vertex.vertex import Vertex

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Starting Template"


class TestDivider(unittest.TestCase):

    init_vals = {
        "auxin": 2,
        "arr": 3,
        "al": 3,
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
        "growing": True,
        "circ_mod": "cont",
    }

    def test_get_new_vs(self):
        timestep = 1
        simulation = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, False)
        v1 = Vertex(10, 10)
        v2 = Vertex(10, 30)
        v3 = Vertex(30, 30)
        v4 = Vertex(30, 10)
        cell1 = Cell(simulation, [v1, v2, v3, v4], self.init_vals, simulation.get_next_cell_id())
        new_vs = simulation.get_divider().get_new_vs(cell1)
        self.assertEqual([10, 20], new_vs[0].get_xy())
        self.assertEqual([30, 20], new_vs[1].get_xy())

    def test_check_neighbors_for_v_existence(self):
        timestep = 1
        simulation = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, False)
        v1 = Vertex(10, 10)
        v2 = Vertex(10, 30)
        v3 = Vertex(30, 30)
        v4 = Vertex(30, 10)
        cell1 = Cell(simulation, [v1, v2, v3, v4], self.init_vals, simulation.get_next_cell_id())
        v5 = Vertex(10, 20)
        thisv = simulation.get_divider().check_neighbors_for_v_existence(cell1, v5)
        self.assertEqual(v5, thisv)
        v6 = Vertex(30, 20)
        cell2 = Cell(simulation, [v5, v6, v4, v1], self.init_vals, simulation.get_next_cell_id())
        cell1.add_neighbor(cell2)
        cell2.add_neighbor(cell1)
        v7 = Vertex(100, 100)
        thisv2 = simulation.get_divider().check_neighbors_for_v_existence(cell1, Vertex(30, 20))
        thisv3 = simulation.get_divider().check_neighbors_for_v_existence(cell1, v7)
        self.assertEqual(v6, thisv2)
        self.assertEqual(v7, thisv3)

    def test_swap_neighbors(self):
        timestep = 1
        simulation = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, False)
        v1 = Vertex(10, 10)
        v2 = Vertex(10, 30)
        v3 = Vertex(30, 30)
        v4 = Vertex(30, 10)
        cell1 = Cell(simulation, [v1, v2, v3, v4], self.init_vals, simulation.get_next_cell_id())
        v5 = Vertex(10, 40)
        v6 = Vertex(30, 40)
        a_neighbor = Cell(
            simulation, [v2, v3, v5, v6], self.init_vals, simulation.get_next_cell_id()
        )
        v7 = Vertex(10, 15)
        v8 = Vertex(30, 15)
        new_neighbor = Cell(
            simulation, [v7, v8, v2, v3], self.init_vals, simulation.get_next_cell_id()
        )
        cell1.add_neighbor(a_neighbor)
        a_neighbor.add_neighbor(cell1)
        simulation.get_divider().swap_neighbors(new_neighbor, a_neighbor, cell1)
        self.assertEqual(1, len(a_neighbor.get_all_neighbors()))
        self.assertEqual(1, len(new_neighbor.get_all_neighbors()))
        self.assertEqual(new_neighbor, a_neighbor.get_all_neighbors()[0])
        self.assertEqual(a_neighbor, new_neighbor.get_all_neighbors()[0])

    def test_set_one_side_neighbors(self):
        timestep = 1
        simulation = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, False)
        v12 = Vertex(110, 10)
        v13 = Vertex(110, 30)
        simulation.vertex_list.extend([v12, v13])
        v1 = Vertex(10, 10)
        v2 = Vertex(10, 30)
        v3 = Vertex(30, 30)
        v4 = Vertex(30, 10)
        cell = Cell(simulation, [v1, v2, v3, v4], self.init_vals, simulation.get_next_cell_id())
        v5 = Vertex(10, 20)
        v6 = Vertex(30, 20)
        new_top_cell = Cell(
            simulation, [v2, v3, v5, v6], self.init_vals, simulation.get_next_cell_id()
        )
        new_bottom_cell = Cell(
            simulation, [v1, v4, v5, v6], self.init_vals, simulation.get_next_cell_id()
        )
        simulation.get_divider().set_one_side_neighbors(
            new_top_cell, new_bottom_cell, cell.get_l_neighbors(), cell
        )
        simulation.get_divider().set_one_side_neighbors(
            new_top_cell, new_bottom_cell, cell.get_m_neighbors(), cell
        )
        self.assertEqual([], cell.get_all_neighbors())
        self.assertEqual([], new_top_cell.get_all_neighbors())
        self.assertEqual([], new_bottom_cell.get_all_neighbors())

        v7 = Vertex(1, 10)
        v8 = Vertex(1, 30)
        l_neighbor = Cell(
            simulation, [v7, v8, v1, v2], self.init_vals, simulation.get_next_cell_id()
        )
        cell.add_neighbor(l_neighbor)
        l_neighbor.add_neighbor(cell)
        self.assertEqual([], new_top_cell.get_l_neighbors())
        self.assertEqual([], new_bottom_cell.get_l_neighbors())
        self.assertEqual([l_neighbor], cell.get_l_neighbors())
        self.assertEqual([cell], l_neighbor.get_m_neighbors())
        simulation.get_divider().set_one_side_neighbors(
            new_top_cell, new_bottom_cell, cell.get_l_neighbors(), cell
        )

        self.assertEqual([l_neighbor], cell.get_l_neighbors())
        self.assertEqual([l_neighbor], new_top_cell.get_l_neighbors())
        self.assertEqual([l_neighbor], new_bottom_cell.get_l_neighbors())

        v9 = Vertex(60, 10)
        v10 = Vertex(60, 20)
        v11 = Vertex(60, 30)
        m_top_neighbor = Cell(
            simulation, [v3, v11, v6, v10], self.init_vals, simulation.get_next_cell_id()
        )
        m_lower_neighbor = Cell(
            simulation, [v9, v10, v6, v4], self.init_vals, simulation.get_next_cell_id()
        )
        cell.add_neighbor(m_top_neighbor)
        m_top_neighbor.add_neighbor(cell)
        cell.add_neighbor(m_lower_neighbor)
        m_lower_neighbor.add_neighbor(cell)
        self.assertEqual([], new_top_cell.get_m_neighbors())
        self.assertEqual([], new_bottom_cell.get_m_neighbors())
        simulation.get_divider().set_one_side_neighbors(
            new_top_cell, new_bottom_cell, cell.get_m_neighbors(), cell
        )
        self.assertEqual([m_top_neighbor, m_lower_neighbor], cell.get_m_neighbors())
        self.assertEqual([m_top_neighbor], new_top_cell.get_m_neighbors())
        self.assertEqual([m_lower_neighbor], new_bottom_cell.get_m_neighbors())
        self.assertEqual([new_top_cell], m_top_neighbor.get_l_neighbors())
        self.assertEqual([new_bottom_cell], m_lower_neighbor.get_l_neighbors())

    def test_update_neighbor_lists(self):
        timestep = 1
        simulation = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, False)
        v1 = Vertex(10, 10)
        v2 = Vertex(10, 30)
        v3 = Vertex(30, 30)
        v4 = Vertex(30, 10)
        v5 = Vertex(10, 20)
        v6 = Vertex(30, 20)
        v7 = Vertex(1, 10)
        v8 = Vertex(1, 30)
        v9 = Vertex(60, 10)
        v10 = Vertex(60, 20)
        v11 = Vertex(60, 30)
        v12 = Vertex(110, 10)
        v13 = Vertex(110, 30)
        simulation.vertex_list.extend([v12, v13])

        cell = Cell(simulation, [v1, v2, v3, v4], self.init_vals, simulation.get_next_cell_id())
        m_top_neighbor = Cell(
            simulation, [v3, v11, v6, v10], self.init_vals, simulation.get_next_cell_id()
        )
        m_lower_neighbor = Cell(
            simulation, [v9, v10, v6, v4], self.init_vals, simulation.get_next_cell_id()
        )
        l_neighbor = Cell(
            simulation, [v7, v8, v1, v2], self.init_vals, simulation.get_next_cell_id()
        )

        cell.add_neighbor(l_neighbor)
        l_neighbor.add_neighbor(cell)
        cell.add_neighbor(m_top_neighbor)
        m_top_neighbor.add_neighbor(cell)
        cell.add_neighbor(m_lower_neighbor)
        m_lower_neighbor.add_neighbor(cell)

        new_top_cell = Cell(
            simulation, [v2, v3, v5, v6], self.init_vals, simulation.get_next_cell_id()
        )
        new_bottom_cell = Cell(
            simulation, [v1, v4, v5, v6], self.init_vals, simulation.get_next_cell_id()
        )
        simulation.get_divider().update_neighbor_lists(new_top_cell, new_bottom_cell, cell)
        self.assertEqual([l_neighbor], new_top_cell.get_l_neighbors())
        self.assertEqual([l_neighbor], new_bottom_cell.get_l_neighbors())
        self.assertEqual([new_top_cell, new_bottom_cell], l_neighbor.get_m_neighbors())
        self.assertEqual([m_top_neighbor], new_top_cell.get_m_neighbors())
        self.assertEqual([m_lower_neighbor], new_bottom_cell.get_m_neighbors())
        self.assertEqual([new_top_cell], m_top_neighbor.get_l_neighbors())
        self.assertEqual([new_bottom_cell], m_lower_neighbor.get_l_neighbors())

    def test_update(self):
        timestep = 1
        simulation = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, False)
        v1 = Vertex(10, 10)
        v2 = Vertex(10, 30)
        v3 = Vertex(30, 30)
        v4 = Vertex(30, 10)
        v5 = Vertex(10, 20)
        v6 = Vertex(30, 20)
        v7 = Vertex(1, 10)
        v8 = Vertex(1, 30)
        v9 = Vertex(60, 10)
        v10 = Vertex(60, 20)
        v11 = Vertex(60, 30)
        v12 = Vertex(110, 10)
        v13 = Vertex(110, 30)
        simulation.vertex_list.extend([v12, v13])
        cell = Cell(simulation, [v1, v2, v3, v4], self.init_vals, simulation.get_next_cell_id())
        m_top_neighbor = Cell(
            simulation, [v3, v11, v6, v10], self.init_vals, simulation.get_next_cell_id()
        )
        m_lower_neighbor = Cell(
            simulation, [v9, v10, v6, v4], self.init_vals, simulation.get_next_cell_id()
        )
        l_neighbor = Cell(
            simulation, [v7, v8, v1, v2], self.init_vals, simulation.get_next_cell_id()
        )

        cell.add_neighbor(l_neighbor)
        l_neighbor.add_neighbor(cell)
        cell.add_neighbor(m_top_neighbor)
        m_top_neighbor.add_neighbor(cell)
        cell.add_neighbor(m_lower_neighbor)
        m_lower_neighbor.add_neighbor(cell)

        simulation.get_divider().add_cell(cell)

        self.assertEqual(1, len(m_top_neighbor.get_l_neighbors()))
        self.assertEqual(1, len(m_lower_neighbor.get_l_neighbors()))
        self.assertEqual(m_top_neighbor.get_l_neighbors(), m_lower_neighbor.get_l_neighbors())

        cell.set_dev_zone("meristematic")
        simulation.get_divider().update()

        self.assertEqual(1, len(m_top_neighbor.get_l_neighbors()))
        self.assertEqual(1, len(m_lower_neighbor.get_l_neighbors()))
        self.assertNotEqual(m_top_neighbor.get_l_neighbors(), m_lower_neighbor.get_l_neighbors())
        self.assertEqual(
            m_top_neighbor.get_l_neighbors()[0].get_quad_perimeter().get_bottom_left().get_xy(),
            [10, 20],
        )
