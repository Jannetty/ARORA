import unittest
from src.plantem.sim.mover.vertex_mover import VertexMover
from src.plantem.loc.vertex.vertex import Vertex
from src.plantem.loc.quad_perimeter.quad_perimeter import QuadPerimeter
from src.plantem.agent.cell import GrowingCell
from src.plantem.sim.simulation.sim import GrowingSim

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Starting Template"


class TestVertexMover(unittest.TestCase):
    def test_add_cell_delta_val(self):
        timestep = 1
        root_midpoint_x = 400
        simulation = GrowingSim(
            SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, root_midpoint_x, False
        )
        v1 = Vertex(100, 100)
        v2 = Vertex(100, 300)
        v3 = Vertex(300, 300)
        v4 = Vertex(300, 100)
        cell1 = GrowingCell(simulation, [v1, v2, v3, v4], 0)
        simulation.setup()
        simulation.get_vertex_mover().add_cell_delta_val(cell1, 1.5)
        self.assertEqual(1.5, simulation.get_vertex_mover().get_cell_delta_val(cell1))

    def test_add_cell_b_vertices_to_vertex_deltas(self):
        timestep = 1
        root_midpoint_x = 400
        simulation = GrowingSim(
            SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, root_midpoint_x, False
        )
        v1 = Vertex(100, 100)
        v2 = Vertex(100, 300)
        v3 = Vertex(300, 300)
        v4 = Vertex(300, 100)
        cell1 = GrowingCell(simulation, [v1, v2, v3, v4], 0)
        simulation.setup()
        simulation.get_vertex_mover().add_cell_b_vertices_to_vertex_deltas(cell1, 1.5)
        self.assertEqual(1.5, simulation.get_vertex_mover().get_vertex_delta_val(v1))
        self.assertEqual(1.5, simulation.get_vertex_mover().get_vertex_delta_val(v4))

    def test_propogate_deltas(self):
        timestep = 1
        root_midpoint_x = 400
        simulation = GrowingSim(
            SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, root_midpoint_x, False
        )
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
        simulation.setup()
        cell1.add_neighbor(a_neighbor)
        cell1.add_neighbor(l_neighbor)
        cell1.add_neighbor(b_neighbor)
        cell1.add_neighbor(m_neighbor)
        a_neighbor.add_neighbor(cell1)
        self.assertEqual(a_neighbor.get_b_neighbors(), [cell1])
        self.assertEqual(cell1.get_b_neighbors(), [b_neighbor])
        self.assertEqual(cell1.get_a_neighbors(), [a_neighbor])
        simulation.get_vertex_mover().add_cell_delta_val(a_neighbor, 1.5)
        simulation.get_vertex_mover().propogate_deltas()
        self.assertEqual(1.5, simulation.get_vertex_mover().get_vertex_delta_val(v1))
        self.assertEqual(1.5, simulation.get_vertex_mover().get_vertex_delta_val(v2))
        self.assertEqual(1.5, simulation.get_vertex_mover().get_vertex_delta_val(v3))
        self.assertEqual(1.5, simulation.get_vertex_mover().get_vertex_delta_val(v4))
        self.assertEqual(1.5, simulation.get_vertex_mover().get_vertex_delta_val(v9))
        self.assertEqual(1.5, simulation.get_vertex_mover().get_vertex_delta_val(v10))

    def test_execute_vertex_movement(self):
        timestep = 1
        root_midpoint_x = 400
        simulation = GrowingSim(
            SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, root_midpoint_x, False
        )
        v1 = Vertex(100, 100)
        v2 = Vertex(100, 300)
        v3 = Vertex(300, 300)
        v4 = Vertex(300, 100)
        cell1 = GrowingCell(simulation, [v1, v2, v3, v4], 0)
        v5 = Vertex(100, 400)
        v6 = Vertex(300, 400)
        a_neighbor = GrowingCell(simulation, [v2, v3, v5, v6], 0)
        v9 = Vertex(100, 1)
        v10 = Vertex(300, 1)
        b_neighbor = GrowingCell(simulation, [v9, v10, v1, v4], 0)
        simulation.setup()
        cell1.add_neighbor(a_neighbor)
        cell1.add_neighbor(b_neighbor)
        a_neighbor.add_neighbor(cell1)
        simulation.get_vertex_mover().add_cell_delta_val(a_neighbor, 1.5)
        simulation.get_vertex_mover().propogate_deltas()
        simulation.get_vertex_mover().execute_vertex_movement()
        self.assertAlmostEqual(100 + 1.5, v1.get_y())
        self.assertAlmostEqual(300 + 1.5, v2.get_y())
        self.assertAlmostEqual(300 + 1.5, v3.get_y())
        self.assertAlmostEqual(100 + 1.5, v4.get_y())
        self.assertAlmostEqual(1 + 1.5, v9.get_y())
        self.assertAlmostEqual(1 + 1.5, v10.get_y())

    def test_update(self):
        timestep = 1
        root_midpoint_x = 400
        simulation = GrowingSim(
            SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, timestep, root_midpoint_x, False
        )
        v1 = Vertex(100, 100)
        v2 = Vertex(100, 300)
        v3 = Vertex(300, 300)
        v4 = Vertex(300, 100)
        cell1 = GrowingCell(simulation, [v1, v2, v3, v4], 0)
        v5 = Vertex(100, 400)
        v6 = Vertex(300, 400)
        a_neighbor = GrowingCell(simulation, [v2, v3, v5, v6], 0)
        v9 = Vertex(100, 1)
        v10 = Vertex(300, 1)
        b_neighbor = GrowingCell(simulation, [v9, v10, v1, v4], 0)
        simulation.setup()
        cell1.add_neighbor(a_neighbor)
        cell1.add_neighbor(b_neighbor)
        a_neighbor.add_neighbor(cell1)
        simulation.get_vertex_mover().add_cell_delta_val(a_neighbor, 1.5)
        simulation.get_vertex_mover().update()
        self.assertAlmostEqual(100 + 1.5, v1.get_y())
        self.assertAlmostEqual(300 + 1.5, v2.get_y())
        self.assertAlmostEqual(300 + 1.5, v3.get_y())
        self.assertAlmostEqual(100 + 1.5, v4.get_y())
        self.assertAlmostEqual(1 + 1.5, v9.get_y())
        self.assertAlmostEqual(1 + 1.5, v10.get_y())
