import unittest
from src.plantem.agent.cell import GrowingCell
from src.plantem.loc.vertex.vertex import Vertex
from src.plantem.loc.quad_perimeter.quad_perimeter import QuadPerimeter
from src.plantem.sim.simulation.sim import GrowingSim

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Starting Template"

class TestGrowingCell(unittest.TestCase):
    def test_get_area(self):
        timestep = 1
        root_midpoint_x = 400
        simulation = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, root_midpoint_x)
        v1 = Vertex(100, 100)
        v2 = Vertex(100, 300)
        v3 = Vertex(300, 300)
        v4 = Vertex(300, 100)
        cell1 = GrowingCell(simulation, [v1, v2, v3, v4], 0)
        self.assertEqual(40000, cell1.get_area())

    def test_add_neighbor(self):
        timestep = 1
        root_midpoint_x = 400
        simulation = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, root_midpoint_x)
        v1 = Vertex(100, 100)
        v2 = Vertex(100, 300)
        v3 = Vertex(300, 300)
        v4 = Vertex(300, 100)
        cell1 = GrowingCell(simulation, [v1, v2, v3, v4], 0)
        v5 = Vertex(100, 400)
        v6 = Vertex(300, 400)
        a_neighbor = GrowingCell(simulation, [v2, v3, v5, v6], 0)
        v7 = Vertex(1, 100)
        v8 = Vertex(1, 300)
        l_neighbor = GrowingCell(simulation, [v7, v8, v1, v2], 0)
        v9 = Vertex(100, 1)
        v10 = Vertex(300, 1)
        b_neighbor = GrowingCell(simulation, [v9, v10, v1, v4], 0)
        v11 = Vertex(500, 100)
        v12 = Vertex(500, 300)
        m_neighbor = GrowingCell(simulation, [v11, v12, v4, v3], 0)
        cell1.add_neighbor(a_neighbor)
        cell1.add_neighbor(l_neighbor)
        cell1.add_neighbor(b_neighbor)
        cell1.add_neighbor(m_neighbor)
        self.assertEqual(cell1.get_a_neighbors(), [a_neighbor])
        self.assertEqual(cell1.get_b_neighbors(), [b_neighbor])
        self.assertEqual(cell1.get_l_neighbors(), [l_neighbor])
        self.assertEqual(cell1.get_m_neighbors(), [m_neighbor])
        with self.assertRaises(ValueError):
            cell1.add_neighbor(a_neighbor)

    def test_remove_neighbor(self):
        timestep = 1
        root_midpoint_x = 400
        simulation = GrowingSim(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, root_midpoint_x)
        v1 = Vertex(100, 100)
        v2 = Vertex(100, 300)
        v3 = Vertex(300, 300)
        v4 = Vertex(300, 100)
        cell1 = GrowingCell(simulation, [v1, v2, v3, v4], 0)
        v5 = Vertex(100, 400)
        v6 = Vertex(300, 400)
        a_neighbor = GrowingCell(simulation, [v2, v3, v5, v6], 0)
        v7 = Vertex(1, 100)
        v8 = Vertex(1, 300)
        l_neighbor = GrowingCell(simulation, [v7, v8, v1, v2], 0)
        v9 = Vertex(100, 1)
        v10 = Vertex(300, 1)
        b_neighbor = GrowingCell(simulation, [v9, v10, v1, v4], 0)
        v11 = Vertex(500, 100)
        v12 = Vertex(500, 300)
        m_neighbor = GrowingCell(simulation, [v11, v12, v4, v3], 0)
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
        with self.assertRaises(ValueError):
            cell1.remove_neighbor(a_neighbor)