import os
import unittest
from src.plantem.agent.cell import Cell
from src.plantem.loc.vertex.vertex import Vertex
from src.plantem.loc.quad_perimeter.quad_perimeter import QuadPerimeter
from src.plantem.sim.simulation.sim import GrowingSim

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Starting Template"


class TestCell(unittest.TestCase):

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

    @classmethod
    def setUpClass(cls):
        super(TestCell, cls).setUpClass()
        os.environ["ARCADE_HEADLESS"] = "True"

    @classmethod
    def teadDownClass(cls):
        del os.environ["ARCADE_HEADLESS"]
        super(TestCell, cls).tearDownClass()

    def test_get_area(self):
        timestep = 1
        root_midpoint_x = 40
        simulation = GrowingSim(
            SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, root_midpoint_x, False
        )
        v1 = Vertex(10, 10)
        v2 = Vertex(10, 30)
        v3 = Vertex(30, 30)
        v4 = Vertex(30, 10)
        cell1 = Cell(simulation, [v1, v2, v3, v4], self.init_vals, simulation.get_next_cell_id())
        self.assertEqual(400, cell1.get_area())

    def test_add_neighbor(self):
        timestep = 1
        root_midpoint_x = 60
        simulation = GrowingSim(
            SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, root_midpoint_x, False
        )
        init_id = simulation.get_next_cell_id()
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
        v7 = Vertex(1, 10)
        v8 = Vertex(1, 30)
        l_neighbor = Cell(
            simulation, [v7, v8, v1, v2], self.init_vals, simulation.get_next_cell_id()
        )
        v9 = Vertex(10, 1)
        v10 = Vertex(30, 1)
        b_neighbor = Cell(
            simulation, [v9, v10, v1, v4], self.init_vals, simulation.get_next_cell_id()
        )
        v11 = Vertex(50, 10)
        v12 = Vertex(50, 30)
        m_neighbor = Cell(
            simulation, [v11, v12, v4, v3], self.init_vals, simulation.get_next_cell_id()
        )
        cell1.add_neighbor(a_neighbor)
        cell1.add_neighbor(l_neighbor)
        cell1.add_neighbor(b_neighbor)
        cell1.add_neighbor(m_neighbor)
        self.assertEqual(cell1.get_a_neighbors(), [a_neighbor])
        self.assertEqual(cell1.get_b_neighbors(), [b_neighbor])
        self.assertEqual(cell1.get_l_neighbors(), [l_neighbor])
        self.assertEqual(cell1.get_m_neighbors(), [m_neighbor])
        self.assertEqual(cell1.get_c_id(), init_id)
        self.assertEqual(a_neighbor.get_c_id(), init_id + 1)
        self.assertEqual(l_neighbor.get_c_id(), init_id + 2)
        self.assertEqual(b_neighbor.get_c_id(), init_id + 3)
        self.assertEqual(m_neighbor.get_c_id(), init_id + 4)
        with self.assertRaises(ValueError):
            cell1.add_neighbor(a_neighbor)

    def test_remove_neighbor(self):
        timestep = 1
        root_midpoint_x = 40
        simulation = GrowingSim(
            SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, root_midpoint_x, False
        )
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
        v7 = Vertex(1, 10)
        v8 = Vertex(1, 30)
        l_neighbor = Cell(
            simulation, [v7, v8, v1, v2], self.init_vals, simulation.get_next_cell_id()
        )
        v9 = Vertex(10, 1)
        v10 = Vertex(30, 1)
        b_neighbor = Cell(
            simulation, [v9, v10, v1, v4], self.init_vals, simulation.get_next_cell_id()
        )
        v11 = Vertex(50, 10)
        v12 = Vertex(50, 30)
        m_neighbor = Cell(
            simulation, [v11, v12, v4, v3], self.init_vals, simulation.get_next_cell_id()
        )
        cell1.add_neighbor(a_neighbor)
        cell1.add_neighbor(l_neighbor)
        cell1.add_neighbor(b_neighbor)
        cell1.add_neighbor(m_neighbor)
        self.assertEqual(cell1.get_a_neighbors(), [a_neighbor])
        self.assertEqual(cell1.get_b_neighbors(), [b_neighbor])
        self.assertEqual(cell1.get_l_neighbors(), [l_neighbor])
        self.assertEqual(cell1.get_m_neighbors(), [m_neighbor])

        cell1.remove_neighbor(a_neighbor)
        self.assertEqual(cell1.get_a_neighbors(), [])
        cell1.remove_neighbor(b_neighbor)
        self.assertEqual(cell1.get_b_neighbors(), [])
        cell1.remove_neighbor(l_neighbor)
        self.assertEqual(cell1.get_l_neighbors(), [])
        cell1.remove_neighbor(m_neighbor)
        self.assertEqual(cell1.get_m_neighbors(), [])
        # with self.assertRaises(ValueError):
        #    cell1.remove_neighbor(a_neighbor)
